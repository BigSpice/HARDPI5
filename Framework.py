#!/usr/bin/env python3
# Mouse Behavior System Script
#todo, move trial logs to the mouse folder 
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
debug_mode = False


CONFIG_DIR = "Silasi-Mice/Config-Global"
HOME_DIR = "Silasi-Mice/Mice"
MAPPING_FILE = os.path.join(CONFIG_DIR, "mouse_id_mapping.csv")
TRACKING_FILE = os.path.join(CONFIG_DIR, "mouse_tracking.csv")
class GlobalMouseTracker:
    def __init__(self):
        self.lock = threading.Lock()
        self.trial_log_file = os.path.join(HOME_DIR, "trial_logs.csv")
        self._ensure_trial_log_exists()
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
                        'test_time': float(row['test_time']),
                        'last_seen': row['last_seen']
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

            'last_seen': datetime.now().strftime("%d-%m-%Y")
        })

        self.tracking_data[normal_id]['trial_count'] += trials
        self.tracking_data[normal_id]['test_time'] += test_time
        self.tracking_data[normal_id]['last_seen'] = datetime.now().strftime("%d-%m-%Y ")

        self._save_tracking_data()

    def _save_tracking_data(self):
        with open(TRACKING_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['normal_id', 'trial_count', 'test_time', 'last_seen'])
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
        return {'daily_trial_cap': NUM_TRIALS_PER_MOUSE, 'max_daily_time': (MAX_RECORDING_TIME * NUM_TRIALS_PER_MOUSE)}

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
            'MAX_DAILY_TIME_MIN': '10',
            'DEBUG': '0'

        }

        with open(CONFIG_FILE_PATH, 'w') as configfile:
            config.write(configfile)

    def load_config(self):
        global X_HOME_POS, Y_HOME_POS, ARM_HEIGHT_POS, SPEED_XY
        global MAX_RECORDING_TIME_MIN, RECORDING_DELAY_SEC, PIEZO_THRESHOLD
        global NUM_TRIALS_PER_MOUSE, SAVE_DATA_PATH, PREFERRED_PAW
        global DAILY_TRIAL_CAP, MAX_DAILY_TIME_MIN, DEBUG

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
        DEBUG = int(config['SYSTEM_SETTINGS']['DEBUG'])
        if DEBUG == 1:
            debug_mode = True
        else:
            debug_mode = False

    def _ensure_trial_log_exists(self):
        with self.lock:
            if not os.path.exists(self.trial_log_file):
                with open(self.trial_log_file, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['last_seen', 'normal_id', 'raw_id',
                                     'trial_duration', 'completed', 'interrupted'])

    def log_trial(self, raw_id, trial_duration, completed, interrupted):
        normal_id = self._get_normal_id(raw_id)
        last_seen = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

        with self.lock:
            with open(self.trial_log_file, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    last_seen,
                    normal_id,
                    raw_id,
                    round(trial_duration, 2),
                    int(completed),
                    int(interrupted)
                ])
# Define enums
class PawPreference(Enum):
    LEFT = "Left"
    RIGHT = "Right"
class Trail_Element:
    def __init__(self, TNumber=0, TTime=0.0):
        self.Trail_Number = TNumber
        self.Trail_Time = TTime

class SingleTrackedData:
    def __init__(self):
        self.trial_count = 0
        self.test_time = 0
        self.raw_id = ""
        self.last_seen = datetime(2024, 1, 1)
        self.normal_id = ""
        self.tracker = GlobalMouseTracker
        self.Trails_Times_Completed_In_current_Session = []
        self.total_trail_time = 0.0
        self.trail_num_total = 0

    def add_trail_element(self, Element: Trail_Element):
        if isinstance(Element, Trail_Element):
            self.Trails_Times_Completed_In_current_Session.append(Element)
            self.total_trail_time += Element.Trail_Time
            self.trail_num_total = len(self.Trails_Times_Completed_In_current_Session)
        else:
            raise TypeError("Only Trail_Element objects can be added to Trails_Times_Completed_In_current_Session")





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

#Use the arduino to flash the signal for the LED
def open_folder(folder_path):
    # Check if the folder exists
    if os.path.exists(folder_path):
        # Open the folder in the file explorer
        if platform.system() == "Windows":
            subprocess.run(["explorer", folder_path])
        elif platform.system() == "Linux":
            subprocess.run(["xdg-open", folder_path])
        else:
            print("Unsupported operating system.")
    else:
        print(f"Folder does not exist: {folder_path}")


def admin_menu():
    admin_Open = True
    print("\nADMIN MENU")
    print("1. Modify configuration settings in explorer")
    print("2. Run HomeCage Self Test")
    print("3. Home all Axes")
    print("4. Open Camera Feed")
    print("Q. Quit to welcome screen")

    choice = input("Enter your choice: ")
    if choice.lower() == '1':
        open_folder(CONFIG_FILE_PATH)
        return

    if choice.lower() == 'q':
        admin_Open = False
        return

    #laceholder

    return


def RFID_TAG_CHECK():
    global RFID_TAG_RAW
    try:
        RFID_TAG_RAW = "MOUSE_ID_12345"
        print(f"\nTAG FOUND - {RFID_TAG_RAW}")
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
    #sd
    x = 0
    return True


def wait_for_mouse():

    print("Waiting for mouse...")
    beam_break_result = async_to_sync(BeamBreakCheck)()
    RFID_TF = RFID_TAG_CHECK()
    print(f"RFID - {RFID_TAG_RAW}")
    if beam_break_result and not RFID_TF:
        print("\nBeam Broken, Checking for MOUSE ID....\n")
        #beam is broken but we don't have RFID

    return beam_break_result


# Modified main function
def main(SingleTrackedData):


    trials_completed_today = SingleTrackedData.trial_count
    tracker = SingleTrackedData.tracker
    if tracker == None:
        tracker = GlobalMouseTracker()


    if not async_to_sync(BeamBreakCheck)():
        return 0

    print(f"Starting trials for mouse with RFID: {RFID_TAG_RAW}")

    while trials_completed_today < NUM_TRIALS_PER_MOUSE:
        # Initial presence check
        if not async_to_sync(BeamBreakCheck)():
            print("Mouse has left - ending session")
            break

        trial_start = time.time()
        max_duration = MAX_RECORDING_TIME_MIN * 60
        completed = False
        interrupted = False

        try:
            while True:
                # Check every 0.5 seconds for better responsiveness
                time.sleep(0.5)

                # Check for beam break
                if not async_to_sync(BeamBreakCheck)():
                    interrupted = True
                    break

                # Check for time limit
                if (time.time() - trial_start) >= max_duration:
                    completed = True
                    break

        finally:
            trial_end = time.time()
            trial_duration = trial_end - trial_start

            # Log trial with safety flags
            tracker.log_trial(
                RFID_TAG_RAW,
                trial_duration,
                completed,
                interrupted
            )
            # Update aggregated tracking
            # tracker.update_tracking(RFID_TAG_RAW,trials=1,test_time=trial_duration)
            SingleTrackedData.add_trail_element(Trail_Element(SingleTrackedData.trial_count + 1, trial_duration))

            trials_completed_today += 1
            print(
                f"Trial {trials_completed_today} duration: {trial_duration:.2f} seconds, completed: {completed}, interrupted: {interrupted}")

    print(f"Session complete: {trials_completed_today} trials")
    return trials_completed_today


async def save_session_data():

    print(f"Saving data to {SAVE_DATA_PATH}")
    return True


def run_system():
    #Ld config
    tracker = GlobalMouseTracker()
    tracker.load_config()
    admin_Open = False

    while True:
        Current_Mouse = SingleTrackedData()
        Current_Mouse.tracker = tracker
        display_welcome_banner()
        if debug_mode:
            print("\n\n\nATTENTION\n\n !Debug_Mode_Enabled! \n -Verbose Output Enabled\n")
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
               # tracker.update_tracking(RFID_TAG_RAW, trials=0, test_time=0)
                Tracker_Data = Current_Mouse.tracker.get_mouse_data(mouse_id)
                Current_Mouse.raw_id = tracker.get_mouse_data()
                Current_Mouse.trial_count = Tracker_Data['trial_count']
                Current_Mouse.test_time = Tracker_Data['test_time']
                Current_Mouse.last_seen = Tracker_Data['last_seen']
                print(f"Mouse Last seen: {Current_Mouse.last_seen}")
                if Current_Mouse != None:
                    print(f"\nTrials: {Current_Mouse.trial_count}, Time: {Current_Mouse.test_time} \n")
                Old_Count =  Current_Mouse.trial_count
                Old_Test_time_today =  Current_Mouse.test_time

            if Current_Mouse.trial_count < NUM_TRIALS_PER_MOUSE or  Current_Mouse.test_time < MAX_RECORDING_TIME and datetime.strptime(Current_Mouse.last_seen, "%Y-%m-%d") != datetime.today().date():
                    trials_completed = main(Current_Mouse)
                    if trials_completed >= 0:
                       # async_to_sync(save_session_data)()
                        tracker.update_tracking(RFID_TAG_RAW,Current_Mouse.trail_num_total , Current_Mouse.total_trail_time)
                    # RFID_TAG_RAW = None
            else:
                print(f"Mouse ID {mouse_id} has exceeded daily trials or test time.")
                print(f"\nRechecking in 20 Seconds For another mouse Without the ID {mouse_id}")
                time.sleep(20)

            time.sleep(2)
        del Current_Mouse


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
