#!/usr/bin/env python3
# Mouse Behavior System Script

import threading
import asyncio
import configparser
import time
import os
from asgiref.sync import async_to_sync
from enum import Enum
import sys
import select
import csv
from datetime import datetime


# Global variables
global RFID_TAG_RAW
global CONFIG_FILE_PATH
CONFIG_FILE_PATH = "Silasi-Mice/Config-Global/mouse_behavior_config.ini"
global admin_Open



CONFIG_DIR = "Silasi-Mice/Config-Global"
MAPPING_FILE = os.path.join(CONFIG_DIR, "mouse_id_mapping.csv")
TRACKING_FILE = os.path.join(CONFIG_DIR, "mouse_tracking.csv")

# Define enums
class PawPreference(Enum):
    LEFT = "Left"
    RIGHT = "Right"


# Configuration variables
X_HOME_POS = 0
Y_HOME_POS = 0
ARM_HEIGHT_POS = 0
SPEED_XY = 0
MAX_RECORDING_TIME = 0
RECORDING_DELAY = 0
PIEZO_THRESHOLD = 0.0
NUM_TRIALS_PER_MOUSE = 0
SAVE_DATA_PATH = ""
PREFERRED_PAW = PawPreference.RIGHT


def display_welcome_banner():
    print("""

 ___       ________  ________          ________  ___  ___       ________  ________  ___     
|\  \     |\   __  \|\   __  \        |\   ____\|\  \|\  \     |\   __  \|\   ____\|\  \    
\ \  \    \ \  \|\  \ \  \|\ /_       \ \  \___|\ \  \ \  \    \ \  \|\  \ \  \___|\ \  \   
 \ \  \    \ \   __  \ \   __  \       \ \_____  \ \  \ \  \    \ \   __  \ \_____  \ \  \  
  \ \  \____\ \  \ \  \ \  \|\  \       \|____|\  \ \  \ \  \____\ \  \ \  \|____|\  \ \  \ 
   \ \_______\ \__\ \__\ \_______\        ____\_\  \ \__\ \_______\ \__\ \__\____\_\  \ \__\
    \|_______|\|__|\|__|\|_______|       |\_________\|__|\|_______|\|__|\|__|\_________\|__|
                                         \|_________|                       \|_________|    



    """)

#TODO -----  Add a flashing led synced to the threshold on the arduino
#Use the arduino to flash the signal for the LED

class GlobalMouseTracker:
    def __init__(self):
        os.makedirs(CONFIG_DIR, exist_ok=True)
        self.raw_to_normal = self._load_id_mapping()
        self.tracking_data = self._load_tracking_data()
        self.next_id = self._calculate_next_id()

    def _load_id_mapping(self):
        mapping = {}
        if os.path.exists(MAPPING_FILE):
            with open(MAPPING_FILE, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    mapping[row['raw_id']] = row['normal_id']
        return mapping

    def _load_tracking_data(self):
        data = {}
        if os.path.exists(TRACKING_FILE):
            with open(TRACKING_FILE, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    data[row['normal_id']] = {
                        'trial_count': int(row['trial_count']),
                        'test_time': int(row['test_time']),
                        'last_seen': row['timestamp']
                    }
        return data

    def _calculate_next_id(self):
        max_id = 0
        for normal_id in self.raw_to_normal.values():
            num = int(normal_id.replace("Mouse", ""))
            max_id = max(max_id, num)
        return max_id + 1

    def _get_normal_id(self, raw_id):
        if raw_id not in self.raw_to_normal:
            normal_id = f"Mouse{self.next_id:03d}"
            self.raw_to_normal[raw_id] = normal_id
            self.next_id += 1
            print("\n" + "=" * 50)
            print(f"NEW MOUSE REGISTRATION\nRAW ID: {raw_id}\nASSIGNED ID: {normal_id}")
            print("=" * 50 + "\n")
            time.sleep(5)

            self._save_mapping(raw_id, normal_id)

        return self.raw_to_normal[raw_id]

    def _save_mapping(self, raw_id, normal_id):
        file_exists = os.path.exists(MAPPING_FILE)
        with open(MAPPING_FILE, 'a', newline='') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(['raw_id', 'normal_id'])
            writer.writerow([raw_id, normal_id])

    def update_tracking(self, raw_id, trials=0, test_time=0):
        normal_id = self._get_normal_id(raw_id)

        self.tracking_data.setdefault(normal_id, {
            'trial_count': 0,
            'test_time': 0,
            'last_seen': datetime.now().isoformat()
        })

        self.tracking_data[normal_id]['trial_count'] += trials
        self.tracking_data[normal_id]['test_time'] += test_time
        self.tracking_data[normal_id]['last_seen'] = datetime.now().isoformat()

        self._save_tracking_data()

    def _save_tracking_data(self):
        with open(TRACKING_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['normal_id', 'trial_count', 'test_time', 'timestamp'])
            for normal_id, data in self.tracking_data.items():
                writer.writerow([
                    normal_id,
                    data['trial_count'],
                    data['test_time'],
                    data['last_seen']
                ])

    def get_mouse_data(self, raw_id=None, normal_id=None):
        if raw_id:
            normal_id = self._get_normal_id(raw_id)
        return self.tracking_data.get(normal_id, {
            'trial_count': 0,
            'test_time': 0,
            'last_seen': None
        })

    def get_daily_limits(self):
        return {'daily_trial_cap': 10, 'max_daily_time': 60}

    def create_default_config(self):
        os.makedirs(os.path.dirname(CONFIG_FILE_PATH), exist_ok=True)

        config = configparser.ConfigParser()
        config['SYSTEM_SETTINGS'] = {
            'X_HOME_POS': '0',
            'Y_HOME_POS': '0',
            'ARM_HEIGHT_POS': '0',
            'SPEED_XY': '0',
            'MAX_RECORDING_TIME_MIN': '0',
            'RECORDING_DELAY_SEC': '2',
            'PIEZO_THRESHOLD': '0.0',
            'NUM_TRIALS_PER_MOUSE': '10',
            'SAVE_DATA_PATH': '/home/user/mouse_data_',
            'PREFERRED_PAW': 'Right',
            'DAILY_TRIAL_CAP': '10',
            'MAX_DAILY_TIME_MIN': '10'
        }

        with open(CONFIG_FILE_PATH, 'w') as configfile:
            config.write(configfile)

    def load_config(self):
        global X_HOME_POS, Y_HOME_POS, ARM_HEIGHT_POS, SPEED_XY
        global MAX_RECORDING_TIME_MIN, RECORDING_DELAY_SEC, PIEZO_THRESHOLD
        global NUM_TRIALS_PER_MOUSE, SAVE_DATA_PATH, PREFERRED_PAW
        global DAILY_TRIAL_CAP, MAX_DAILY_TIME_MIN

        if not os.path.exists(CONFIG_FILE_PATH):
           self.create_default_config()

        config = configparser.ConfigParser()
        config.read(CONFIG_FILE_PATH)

        X_HOME_POS = int(config['SYSTEM_SETTINGS']['X_HOME_POS'])
        Y_HOME_POS = int(config['SYSTEM_SETTINGS']['Y_HOME_POS'])
        ARM_HEIGHT_POS = int(config['SYSTEM_SETTINGS']['ARM_HEIGHT_POS'])
        SPEED_XY = int(config['SYSTEM_SETTINGS']['SPEED_XY'])
        MAX_RECORDING_TIME_MIN = int(config['SYSTEM_SETTINGS']['MAX_RECORDING_TIME_MIN'])
        RECORDING_DELAY_SEC = int(config['SYSTEM_SETTINGS']['RECORDING_DELAY_SEC'])
        PIEZO_THRESHOLD = float(config['SYSTEM_SETTINGS']['PIEZO_THRESHOLD'])
        NUM_TRIALS_PER_MOUSE = int(config['SYSTEM_SETTINGS']['NUM_TRIALS_PER_MOUSE'])
        SAVE_DATA_PATH = config['SYSTEM_SETTINGS']['SAVE_DATA_PATH']
        PREFERRED_PAW = PawPreference(config['SYSTEM_SETTINGS']['PREFERRED_PAW'])
        DAILY_TRIAL_CAP = int(config['SYSTEM_SETTINGS']['DAILY_TRIAL_CAP'])
        MAX_DAILY_TIME_MIN = int(config['SYSTEM_SETTINGS']['MAX_DAILY_TIME_MIN'])



def admin_menu():
    admin_Open = True
    print("\nADMIN MENU")
    print("1. Modify configuration settings")
    print("2. Run system diagnostics")
    print("3. View system logs")
    print("4. Return to main screen")
    print("Q. Quit to welcome screen")

    choice = input("Enter your choice: ")

    if choice.lower() == 'q':
        admin_Open = False
        return

    #laceholder

    return


def RFID_TAG_CHECK():
    global RFID_TAG_RAW
    try:
        RFID_TAG_RAW = "MOUSE_ID_12345"
        print(f"\n TAG FOUND - {RFID_TAG_RAW}")
        return True
    except:
        print("TAG READ FAILED!")
        return False
    return False

def RETURN_RFID_TAG_CHECK():
    if RFID_TAG_RAW is not None:
        F_Val = str(RFID_TAG_RAW)
    return F_Val
async def BeamBreakCheck():

    return True


def wait_for_mouse():
    print("Waiting for mouse...")
    beam_break_result = async_to_sync(BeamBreakCheck)()
    RFID_TF = RFID_TAG_CHECK()
    print(f"Beam Broken - {beam_break_result}")
    print(f"RFID - {beam_break_result}")

    if beam_break_result and not RFID_TF:
        print("\nBeam Broken, Checking for MOUSE ID....\n")
        #beam is broken but we don't have RFID


    return beam_break_result


def main():

    trials_completed = 0

    # frst check if mouse is still present
    if not async_to_sync(BeamBreakCheck)():
        return

    print(f"Starting trials for mouse with RFID: {RFID_TAG_RAW}")

    while trials_completed < NUM_TRIALS_PER_MOUSE:
        if not async_to_sync(BeamBreakCheck)():
            print("Mouse has left - ending session")
            break

        time.sleep(5)

        trials_completed += 1

        print(f"Completed trial {trials_completed} of {NUM_TRIALS_PER_MOUSE}")

    print(f"Session complete: {trials_completed} trials")
    return trials_completed


async def save_session_data():

    print(f"Saving data to {SAVE_DATA_PATH}")
    return True


def run_system():
    #Ld config
    tracker = GlobalMouseTracker()
    tracker.load_config()
    admin_Open = False
    while True:

        display_welcome_banner()
        print("Press any key for admin menu (waiting 5 seconds)...")
        timeout = time.time() + 1
        while time.time() < timeout:
            if input_available():
                admin_menu()
                break

        # Wait for mouse
        while admin_Open == False:
            global RFID_TAG_RAW
            if wait_for_mouse():
                mouse_id = RFID_TAG_RAW  # Function to get the current mouse ID
                tracker.update_tracking(RFID_TAG_RAW, trials=0, test_time=0)
                CurrentMousedata = tracker.get_mouse_data(raw_id=RFID_TAG_RAW)# tracker.get_mouse_data(normal_id="Mouse001")


                if CurrentMousedata != None:
                    print(f"Trials: {CurrentMousedata['trial_count']}, Time: {CurrentMousedata['test_time']} \n\n")

                if CurrentMousedata['trial_count'] < NUM_TRIALS_PER_MOUSE or CurrentMousedata[
                    'test_time'] < MAX_RECORDING_TIME:
                    trials_completed = main()

                    if trials_completed > 0:
                        async_to_sync(save_session_data)()
                        mouse_trial_count_new += trials_completed
                        mouse_test_time_new  += calculate_test_time(
                            trials_completed)  # Function to calculate test time based on trials
                        tracker.update_tracking(RFID_TAG_RAW, mouse_trial_count_new, mouse_test_time_new)
                        print(f"Last seen: {CurrentMousedata['last_seen']}")
                    RFID_TAG_RAW = None
                else:
                    print(f"Mouse ID {mouse_id} has exceeded daily trials or test time.")

            time.sleep(2)


def input_available():
    import os
    import sys
    # Check platform
    if os.name == 'nt':  # Windows
        try:
            import msvcrt
            return msvcrt.kbhit()
        except:
            import threading
            import time

            class KeyPress:
                def __init__(self):
                    self.key_pressed = False

                def check_key(self):
                    try:
                        if input():
                            self.key_pressed = True
                    except:
                        pass

            key_check = KeyPress()
            t = threading.Thread(target=key_check.check_key)
            t.daemon = True
            t.start()
            time.sleep(0.1)  # Brief pause to check
            return key_check.key_pressed
    else:  # Unix-like systems (Linux, macOS)
        import select
        #print("\n \n Found - Linux \n \n ")
        # Use select with a timeout of 0 seconds
        rlist, _, _ = select.select([sys.stdin], [], [], 0)
        return bool(rlist)

if __name__ == "__main__":
    run_system()
