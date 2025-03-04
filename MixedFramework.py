#!/usr/bin/env python3
# Mouse Behavior System Script
#todo, move trial logs to the mouse folder
# REQUIRED
# RPi.GPIO
# SPI   ON
from time import sleep

from enum import Enum

import sys

import time

from datetime import datetime

import os

import importlib


# Global variables
global CurrentMouseID, NumberOfTests, StartupTime, MiceEvaluated, SessionID, ProfileID, MaxTestTime, MinTestTime, ArmHoldWaitingTime, RFID_PORT, ARDUINO_PORT,CurrentMouseTagRFID
global RFID_TAG_RAW,CONFIG_FILE_PATH,CONFIG_DIR,HOME_DIR,MAPPING_FILE,TRACKING_FILE,debug_mode,admin_Open
CONFIG_FILE_PATH = "Silasi-Mice/Config-Global/mouse_behavior_config.ini"
debug_mode = False
CONFIG_DIR = "Silasi-Mice/Config-Global"
HOME_DIR = "Silasi-Mice/Mice"
MAPPING_FILE = os.path.join(CONFIG_DIR, "mouse_id_mapping.csv")
TRACKING_FILE = os.path.join(CONFIG_DIR, "mouse_tracking.csv")

try:

    import RPi.GPIO as GPIO

    import threading

    import asyncio

    from asgiref.sync import async_to_sync

    import serial

    import queue

    import cv2

    import importlib.util

    import subprocess

    import configparser

    import select

    import csv





except ImportError:

    # List of required packages

    required_packages = ["RPi.GPIO", "asyncio", "asgiref", "serial", "configparser"]



    # Install each required package

    for package in required_packages:

        install_package(package)




def install_package(package_name):

    # Check if the package is already installed

    if importlib.util.find_spec(package_name) is None:

        print(f"{package_name} not found. Installing...")

        try:

            # Install the package using pip

            subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])

            print(f"Successfully installed {package_name}")

            return True

        except subprocess.CalledProcessError as e:

            print(f"Error installing {package_name}: {e}")

            return False

    else:

        print(f"{package_name} is already installed")

        return True
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
            'X_HOME_POS': '600',
            'Y_HOME_POS': '500',
            'ARM_HEIGHT_POS': '0',
            'SPEED_XY': '0',
            'MAX_RECORDING_TIME_MIN': '3',
            'RECORDING_DELAY_SEC': '2',
            'PIEZO_THRESHOLD': '4.0',
            'NUM_TRIALS_PER_MOUSE': '10',
            'SAVE_DATA_PATH': '/home/user/mouse_data_',
            'PREFERRED_PAW': 'Right',
            'DAILY_TRIAL_CAP': '10',
            'MAX_DAILY_TIME_MIN': '10',
            'DEBUG': '0',
            'CAMERA_RESOLUTION':'640x480',
            'RPI_PIN_StepperA_enable': '4',
            'RPI_PIN_StepperB_enable': '22',
            'RPI_PIN_StepperA_STEP_PIN': '2',
            'RPI_PIN_StepperB_STEP_PIN': '17',
            'RPI_PIN_StepperA_DIR_PIN': '3',
            'RPI_PIN_StepperB_DIR_PIN': '27',
            'RPI_PIN_home_switch1': '13',
            'RPI_PIN_home_switch2': '19',
            'RPI_PIN_relay1': '16',
            'RPI_PIN_relay2': '21',
            'RPI_PIN_IRBreakerPin': '26',
            'RPI_PIN_PiezoPin': '6',
            'DISTANCE_STEPPER_IN_STEPS': '3200',
            'STEPS_PER_REV': '200',
            'CAMERA_TARGET_FRAMERATE': '100',

        }

        with open(CONFIG_FILE_PATH, 'w') as configfile:
            config.write(configfile)

    def load_config(self):
        global X_HOME_POS, Y_HOME_POS, ARM_HEIGHT_POS, SPEED_XY
        global MAX_RECORDING_TIME_MIN, RECORDING_DELAY_SEC, PIEZO_THRESHOLD
        global NUM_TRIALS_PER_MOUSE, SAVE_DATA_PATH, PREFERRED_PAW
        global DAILY_TRIAL_CAP, MAX_DAILY_TIME_MIN, DEBUG
        global RPI_PIN_StepperA_enable, RPI_PIN_StepperB_enable, RPI_PIN_StepperA_STEP_PIN,RPI_PIN_StepperB_STEP_PIN,RPI_PIN_StepperA_DIR_PIN,RPI_PIN_StepperB_DIR_PIN,RPI_PIN_home_switch1
        global RPI_PIN_home_switch2,RPI_PIN_relay1,RPI_PIN_relay2,RPI_PIN_IRBreakerPin,RPI_PIN_PiezoPin,DISTANCE_STEPPER_IN_STEPS,CAMERA_TARGET_FRAMERATE,STEPS_PER_REV,CAMERA_RESOLUTION

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
        RPI_PIN_StepperA_enable = int(config['SYSTEM_SETTINGS']['RPI_PIN_StepperA_enable'])
        RPI_PIN_StepperB_enable = int(config['SYSTEM_SETTINGS']['RPI_PIN_StepperB_enable'])
        RPI_PIN_StepperA_STEP_PIN = int(config['SYSTEM_SETTINGS']['RPI_PIN_StepperA_STEP_PIN'])
        RPI_PIN_StepperB_STEP_PIN = int(config['SYSTEM_SETTINGS']['RPI_PIN_StepperB_STEP_PIN'])
        RPI_PIN_StepperA_DIR_PIN = int(config['SYSTEM_SETTINGS']['RPI_PIN_StepperA_DIR_PIN'])
        RPI_PIN_StepperB_DIR_PIN = int(config['SYSTEM_SETTINGS']['RPI_PIN_StepperB_DIR_PIN'])
        RPI_PIN_home_switch1 = int(config['SYSTEM_SETTINGS']['RPI_PIN_home_switch1'])
        RPI_PIN_home_switch2 = int(config['SYSTEM_SETTINGS']['RPI_PIN_home_switch2'])
        RPI_PIN_relay1 = int(config['SYSTEM_SETTINGS']['RPI_PIN_relay1'])
        RPI_PIN_relay2 = int(config['SYSTEM_SETTINGS']['RPI_PIN_relay2'])
        RPI_PIN_IRBreakerPin = int(config['SYSTEM_SETTINGS']['RPI_PIN_IRBreakerPin'])
        RPI_PIN_PiezoPin = int(config['SYSTEM_SETTINGS']['RPI_PIN_PiezoPin'])
        DISTANCE_STEPPER_IN_STEPS = int(config['SYSTEM_SETTINGS']['DISTANCE_STEPPER_IN_STEPS'])
        STEPS_PER_REV = int(config['SYSTEM_SETTINGS']['STEPS_PER_REV'])
        CAMERA_TARGET_FRAMERATE = int(config['SYSTEM_SETTINGS']['CAMERA_TARGET_FRAMERATE'])
        CAMERA_RESOLUTION = str(config['SYSTEM_SETTINGS']['CAMERA_RESOLUTION'])



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
class VideoRecorder:

    def parse_camera_resolution(self, resolution_str):
        """Parse a resolution string in the format 'WIDTHxHEIGHT' into a tuple (WIDTH, HEIGHT)."""
        width, height = map(int, resolution_str.split('x'))
        return (width, height)


    def __init__(self, width=640, height=360, fps=200, duration_seconds=10, output_dir='recordings'):

        Camera_Parsed_Resoloution = VideoRecorder.parse_camera_resolution(CAMERA_RESOLUTION)


        if Camera_Parsed_Resoloution is None:

            self.width = width

            self.height = height

            self.fps = fps

            self.duration_seconds = duration_seconds

            self.output_dir = output_dir

        self.width, self.height = Camera_Parsed_Resoloution
        self.fps = CAMERA_FRAMERATE
        self.duration_seconds = RECORDING_DURATION
        self.output_dir = RECORDING_DIR

        # Thread-safe queue for frames

        self.frame_queue = queue.Queue(maxsize=3000)  # Limit queue size to prevent memory issues

        # Threading flags and events

        self.is_recording = threading.Event()

        self.stop_event = threading.Event()

        # Performance tracking

        self.frame_count = 0

        self.dropped_frames = 0

    def setup_camera(self):

        cap = cv2.VideoCapture(0)  # 0 is usually the first USB camera

        # Set resolution

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)

        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)

        # Set FPS

        cap.set(cv2.CAP_PROP_FPS, self.fps)

        # Check actual parameters achieved

        actual_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)

        actual_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

        actual_fps = cap.get(cv2.CAP_PROP_FPS)

        print(f"Requested settings: {self.width}x{self.height} at {self.fps}fps")

        print(f"Actual settings: {actual_width}x{actual_height} at {actual_fps}fps")

        return cap

    def capture_frames(self, cap):

        try:

            while not self.stop_event.is_set():

                ret, frame = cap.read()

                if not ret:
                    print("Error: Couldn't read frame")

                    break

                try:

                    if not self.frame_queue.full():

                        self.frame_queue.put_nowait(frame)

                        self.frame_count += 1



                    else:

                        print(f"Dropped at {self.frame_count} in capture thread.")

                        self.dropped_frames += 1

                except queue.Full:

                    self.dropped_frames += 1

                    print(f"Dropped at {self.frame_count} in Queu Full.")





        except Exception as e:

            print(f"Error in capture thread: {e}")



        finally:

            self.is_recording.clear()

            cap.release()

    def write_frames(self, out):

        try:

            while not self.stop_event.is_set() or not self.frame_queue.empty():

                try:

                    frame = self.frame_queue.get(timeout=1)

                    out.write(frame)

                except queue.Empty:

                    continue



        except Exception as e:

            print(f"Error in writer thread: {e}")



        finally:

            out.release()

    def record_video(self):

        os.makedirs(self.output_dir, exist_ok=True)

        cap = self.setup_camera()

        if not cap.isOpened():
            print("Error: Could not open camera")

            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        output_file = os.path.join(self.output_dir, f'recording_{timestamp}.mp4')

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')

        out = cv2.VideoWriter(output_file, fourcc, self.fps, (self.width, self.height))

        self.frame_count = 0

        self.dropped_frames = 0

        start_time = time.time()

        self.is_recording.clear()

        self.stop_event.clear()

        try:

            capture_thread = threading.Thread(target=self.capture_frames, args=(cap,))

            writer_thread = threading.Thread(target=self.write_frames, args=(out,))

            writer_thread.start()

            capture_thread.start()

            time.sleep(self.duration_seconds)

            self.stop_event.set()

            capture_thread.join()

            writer_thread.join()



        # except KeyboardInterrupt:

        # print("\nRecording stopped by user")

        finally:

            elapsed_time = time.time() - start_time

            average_fps = self.frame_count / elapsed_time

            print(f"\nRecording finished:")

            print(f"Saved to: {output_file}")

            print(f"Average FPS: {average_fps:.2f}")

            print(f"Total frames captured: {self.frame_count}")

            print(f"Dropped frames: {self.dropped_frames}")

            print(f"Duration: {elapsed_time:.2f} seconds")
class RFIDReader:

    def __init__(self, port='/dev/ttyUSB1', baudrate=9600, timeout=1):

        self.port = port

        self.baudrate = baudrate

        self.timeout = timeout

        self.serial = None

    def connect(self):

        try:

            self.serial = serial.Serial(

                port=self.port,

                baudrate=self.baudrate,

                timeout=self.timeout

            )

            print(f"Successfully connected to {self.port}")

            return True

        except serial.SerialException as e:

            print(f"Error connecting to {self.port}: {str(e)}")

            return False

    def disconnect(self):

        if self.serial and self.serial.is_open:
            self.serial.close()

            print("Disconnected from RFID reader")

    def read_tag_id(self):

        tagdata = None

        if not self.serial or not self.serial.is_open:
            print("Error: Serial connection not established")

            return ''

        try:

            while True:

                self.serial.reset_input_buffer()

                data = self.serial.read(12)

                if len(data) == 12:
                    tag_id = data[4:9].hex().upper()

                    return tag_id

                # return ''



        except serial.SerialException as e:

            print(f"Error reading tag: {str(e)}")

            return ''

    def Endless_print_tag_id(self):

        try:

            print("Starting tag reading. Press Ctrl+C to stop.")

            while True:

                tag_id = self.read_tag_id()

                if tag_id:
                    print(f"Tag detected - ID: {tag_id}")

                time.sleep(2)



        except KeyboardInterrupt:  # Change to beam breaker

            print("\nStopping tag reading")

            self.disconnect()
class StepperManager:

    def step_motor(stepper_pin, dir_pin, enable_pin, direction, steps):

        """stepper motor control function"""

        GPIO.output(enable_pin, GPIO.LOW)  # Enable the motor

        GPIO.output(dir_pin, GPIO.HIGH if direction else GPIO.LOW)

        for _ in range(steps):
            GPIO.output(stepper_pin, GPIO.HIGH)

            sleep(0.001)  # 1ms delay

            GPIO.output(stepper_pin, GPIO.LOW)

            sleep(0.001)

        GPIO.output(enable_pin, GPIO.HIGH)  # Disable the motor

    def home_motors(self):

        """Home both motors using limit switches"""

        # Home motor 2

        GPIO.output(StepperB_enable, GPIO.LOW)

        GPIO.output(StepperB_DIR_PIN, GPIO.LOW)

        while GPIO.input(home_switch1) == GPIO.HIGH:
            GPIO.output(StepperB_STEP_PIN, GPIO.HIGH)

            sleep(0.001)

            GPIO.output(StepperB_STEP_PIN, GPIO.LOW)

            sleep(0.001)

        GPIO.output(StepperB_enable, GPIO.HIGH)

        sleep(1)

        # Home motor 1

        GPIO.output(StepperA_enable, GPIO.LOW)

        GPIO.output(StepperA_DIR_PIN, GPIO.LOW)

        while GPIO.input(home_switch2) == GPIO.HIGH:
            GPIO.output(StepperA_STEP_PIN, GPIO.HIGH)

            sleep(0.001)

            GPIO.output(StepperA_STEP_PIN, GPIO.LOW)

            sleep(0.001)

        GPIO.output(StepperA_enable, GPIO.HIGH)
class Periphals:

    def generate_session_id(mouse_id, test_number):

        date = datetime.now()

        year_digit = str(date.year)[-1]

        test_letter = chr(64 + test_number) if test_number <= 26 else 'Z'

        day_digit = str(((date.day - 1) % 9) + 1)

        month_digit = str(((date.month - 1) % 9) + 1)

        mouse_digit = str(mouse_id)[-1]

        session_id = f"{year_digit}{test_letter}{month_digit}{day_digit}{mouse_digit}"

        return session_id

    async def quick_ir_check(self):

        while True:

            if GPIO.input(IRBreakerPin) == GPIO.HIGH:

                print(".....Awaiting MOUSE")

                IRState = False

                return False

            else:

                print("MOUSE IN!....Awaiting RFID TAG")

                IRState = True

                return True

            time.sleep(0.5)

    async def check_ir_breaker(self):

        try:

            # GPIO.input returns 1 if beam is intact, 0 if broken

            #  invert it so True means the beam is broken

            return not bool(GPIO.input(IRBreakerPin))

        except Exception as e:

            print(f"Error reading IR breaker: {str(e)}")

            return False

    async def READTAG(self):

        RFID_TAG_RAW = None
        reader = RFIDReader(port='/dev/ttyUSB1')

        while RFID_TAG_RAW == None:
            if reader.connect():

                tag_id = reader.read_tag_id()

                if tag_id:
                    RFID_TAG_RAW = tag_id
                    print(f"Single read - Tag ID: {tag_id}")

                    return True

                    # reader.Endless_print_tag_id()

    def extend_actuator(self):

        GPIO.output(relay1, GPIO.HIGH)

        GPIO.output(relay2, GPIO.LOW)

    def retract_actuator(self):

        GPIO.output(relay1, GPIO.LOW)

        GPIO.output(relay2, GPIO.HIGH)

    def stop_actuator(self):

        GPIO.output(relay1, GPIO.HIGH)

        GPIO.output(relay2, GPIO.HIGH)

    def test_actuator_cycle(self):

        """Test actuator by running through extend/retract cycle twice"""

        try:

            for cycle in range(2):
                print(f"\nStarting cycle {cycle + 1}/2")

                print("Extending actuator...")

                extend_actuator()

                sleep(0.8)  # Wait for extension

                stop_actuator()

                sleep(1)  # Wait for extension

                print("Retracting actuator...")

                retract_actuator()

                sleep(0.8)  # Wait for retraction

                print("Stopping actuator...")

                stop_actuator()

                sleep(1)  # Pause between cycles

            print("\nActuator test completed successfully")



        except Exception as e:

            print(f"Error during actuator test: {e}")

            # Ensure actuator is stopped in case of error

            stop_actuator()
class Stepper(Enum):
    STP_A = 1  # STEPPER A

    STP_B = 2  # STEPPER B


ProfileID = " -Defualt"

# Recording directory





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


#new
# Camera settings
CAMERA_FRAMERATE = 100
RECORDING_DURATION = 8  # seconds
SEQUENCE_ITERATIONS = 5
IRState = False
# Configuration Constants

StepperA_enable = 4
StepperB_enable = 22
home_switch1 = 13
home_switch2 = 19


StepperA_STEP_PIN = 2  # Changed to match Arduino pin 3
StepperB_STEP_PIN = 17  # Changed to match Arduino pin 5
StepperA_DIR_PIN = 3  # Changed to match Arduino pin 2
StepperB_DIR_PIN = 27  # Changed to match Arduino pin 4

# PELLET ARM MOTOR PINS
relay1 = 16  # Arduino pin that triggers relay #1
relay2 = 21  # Arduino pin that triggers relay #2
IRBreakerPin = 26
PiezoPin = 6
# Stage home coordinates (you can adjust these values based on your needs)
STAGE_HOME_A = 600  # Steps from home position for motor A
STAGE_HOME_B = 500  # Steps from home position for motor B
STEPS_PER_REV = 200
DISTANCE = 3200  # Total number of steps to move

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
    beam_break_result = async_to_sync(Periphals.quick_ir_check())
    RFID_TF =  async_to_sync(Periphals.READTAG())
    if beam_break_result and not RFID_TF:
        print("\nBeam Broken, Checking for MOUSE ID....\n")
        #beam is broken but we don't have RFID
        RFID_TF = async_to_sync(Periphals.READTAG())

    print(f"RFID - {RFID_TAG_RAW}")
    return beam_break_result


async def present_pellet(CurrentMouseID,NumberOfTests):

    """Handle pellet presentation sequence"""

    cnn = 0

    while cnn != 2:

        # while GPIO.input(IRBreakerPin) == GPIO.LOW:  # while mouse IN

        print("EXTEND")

        Periphals.extend_actuator()

        await asyncio.sleep(3)

        print("RETRACT")

        Periphals.retract_actuator()

        await asyncio.sleep(1.3)

        Periphals.stop_actuator()

        await asyncio.sleep(1.3)

        # Start recording

        output_dir = RECORDING_DIR + CurrentMouseID + Periphals.generate_session_id(CurrentMouseID, NumberOfTests)

        recorder = VideoRecorder(duration_seconds=10, fps=320)

        print("Starting camera recording...")

        t1 = threading.Thread(recorder.record_video())

        t1.start()

        print(f"Recording to: {output_dir}")

        # t2 = threading.Thread(Read_Piezo())

        # t2.start()

        await asyncio.sleep(10)



        print("STOP")

        Periphals.stop_actuator()

        t1.join()

        # t2.join()

        await asyncio.sleep(3)

        cnn += 1



    print("TEST COMPLETE")
    if not async_to_sync(BeamBreakCheck)():
        print("MOUSE LEFT")
        Periphals.extend_actuator()
        return False

    Periphals.extend_actuator()

# Modified main function
def main(SingleTrackedData):


    trials_completed_today = SingleTrackedData.trial_count
    tracker = SingleTrackedData.tracker
    if tracker == None:
        tracker = GlobalMouseTracker()


    if IRState == False:
        return 0


    print(f"Starting trials for mouse with RFID: {RFID_TAG_RAW}")

    print("Starting Automated Sequence...")

    while trials_completed_today < NUM_TRIALS_PER_MOUSE:
        # Initial presence check
        if not async_to_sync(BeamBreakCheck)():
            print("Mouse has left - ending session")
            break

        trial_start = time.time()
        max_duration = MAX_RECORDING_TIME_MIN * 60
        completed = False
        interrupted = False
        print("Homing motors...")

        StepperManager.home_motors()
        time.sleep(1)

        RECORDING_DIR = os.path.join(CONFIG_DIR, "Vid_Recordings")
        os.makedirs(RECORDING_DIR, exist_ok=True)
        try:
            # Move to stage home coordinates

            print("Moving to stage home position...")

            StepperManager.step_motor(StepperA_STEP_PIN, StepperA_DIR_PIN, StepperA_enable, True, STAGE_HOME_A)

            StepperManager.step_motor(StepperB_STEP_PIN, StepperB_DIR_PIN, StepperB_enable, True, STAGE_HOME_B)

            time.sleep(1)

            while True:

                # Present pellet

                print("Presenting pellet...")

                if present_pellet(SingleTrackedData.normal_id, NumberOfTests, ProfileID) == False:
                    print("Returning to home position...")
                    print("Sequence Failed")
                    StepperManager.home_motors()
                    interrupted = True

                    # Clean up


                # Wait between iterations

                time.sleep(1.5)

                # Check for beam break
                if not async_to_sync(Periphals.quick_ir_check()):
                    interrupted = True
                    break

                # Check for time limit
                if (time.time() - trial_start) >= max_duration:
                    completed = True
                    break

        finally:
            trial_end = time.time()
            trial_duration = trial_end - trial_start
            # Return to home position

            print("Returning to home position...")

            StepperManager.home_motors()

            # Clean up

            print("Sequence completed successfully")

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
