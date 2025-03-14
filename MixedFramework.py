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

global RFID_TAG_RAW,CONFIG_FILE_PATH,CONFIG_DIR,HOME_DIR,MAPPING_FILE,TRACKING_FILE,debug_mode,admin_Open,IRState



CONFIG_FILE_PATH = "Silasi-Mice/Config-Global/mouse_behavior_config.ini"

debug_mode = False

CONFIG_DIR = "Silasi-Mice/Config-Global"

HOME_DIR = "Silasi-Mice/Mice"

MAPPING_FILE = os.path.join(CONFIG_DIR, "mouse_id_mapping.csv")

TRACKING_FILE = os.path.join(CONFIG_DIR, "mouse_tracking.csv")





# Define global variables

global X_HOME_POS, Y_HOME_POS, ARM_HEIGHT_POS, SPEED_XY

global MAX_RECORDING_TIME_MIN, RECORDING_DELAY_SEC, PIEZO_THRESHOLD

global NUM_TRIALS_PER_MOUSE, SAVE_DATA_PATH, PREFERRED_PAW

global DAILY_TRIAL_CAP, MAX_DAILY_TIME_MIN

global StepperA_enable, StepperB_enable, StepperA_STEP_PIN, StepperB_STEP_PIN, StepperA_DIR_PIN, StepperB_DIR_PIN

global home_switch1, home_switch2, relay1, relay2, IRBreakerPin, PiezoPin

global DISTANCE_STEPPER_IN_STEPS, CAMERA_TARGET_FRAMERATE, STEPS_PER_REV, CAMERA_RESOLUTION

global DEBUG

global Interrupt_



# # Assign values from tracker

# X_HOME_POS = tracker.X_HOME_POS

# Y_HOME_POS = tracker.Y_HOME_POS

# ARM_HEIGHT_POS = tracker.ARM_HEIGHT_POS

# SPEED_XY = tracker.SPEED_XY



# MAX_RECORDING_TIME_MIN = tracker.MAX_RECORDING_TIME_MIN

# RECORDING_DELAY_SEC = tracker.RECORDING_DELAY_SEC

# PIEZO_THRESHOLD = tracker.PIEZO_THRESHOLD



# NUM_TRIALS_PER_MOUSE = tracker.NUM_TRIALS_PER_MOUSE

# SAVE_DATA_PATH = tracker.SAVE_DATA_PATH

# PREFERRED_PAW = tracker.PREFERRED_PAW



# DAILY_TRIAL_CAP = tracker.DAILY_TRIAL_CAP

# MAX_DAILY_TIME_MIN = tracker.MAX_DAILY_TIME_MIN



# StepperA_enable = tracker.StepperA_enable

# StepperB_enable = tracker.StepperB_enable

# StepperA_STEP_PIN = tracker.StepperA_STEP_PIN

# StepperB_STEP_PIN = tracker.StepperB_STEP_PIN

# StepperA_DIR_PIN = tracker.StepperA_DIR_PIN

# StepperB_DIR_PIN = tracker.StepperB_DIR_PIN



# home_switch1 = tracker.home_switch1

# home_switch2 = tracker.home_switch2

# relay1 = tracker.relay1

# relay2 = tracker.relay2

# IRBreakerPin = tracker.IRBreakerPin

# PiezoPin = tracker.PiezoPin



# DISTANCE_STEPPER_IN_STEPS = tracker.DISTANCE_STEPPER_IN_STEPS

# STEPS_PER_REV = tracker.STEPS_PER_REV

# CAMERA_TARGET_FRAMERATE = tracker.CAMERA_TARGET_FRAMERATE

# CAMERA_RESOLUTION = tracker.CAMERA_RESOLUTION



# DEBUG = tracker.DEBUG

IRState = False

Interrupt_ = False



def Interrupt():

   global Interrupt_

   Interrupt_ = True

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

def setup(tracker):

  

    Add_Tracker_Data_To_Global_Sheet()

    """Initialize GPIO settings"""

    GPIO.setmode(GPIO.BCM)

    periphals_instance = Periphals()

    # Setup stepper motor pins

    for pin in [StepperA_enable, StepperB_enable,

                StepperA_DIR_PIN, StepperB_DIR_PIN,

                StepperA_STEP_PIN, StepperB_STEP_PIN,

                relay1, relay2]:

        GPIO.setup(pin, GPIO.OUT)



    # Setup input pins

    GPIO.setup(home_switch1, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    GPIO.setup(home_switch2, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    GPIO.setup(IRBreakerPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    GPIO.setup(PiezoPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)



    # Initialize enable pins

    GPIO.output(StepperA_enable, GPIO.HIGH)

    GPIO.output(StepperB_enable, GPIO.HIGH)

    periphals_instance.extend_actuator()

    del periphals_instance

    

def Add_Tracker_Data_To_Global_Sheet():

    # Define global variables

    global X_HOME_POS, Y_HOME_POS, ARM_HEIGHT_POS, SPEED_XY

    global MAX_RECORDING_TIME_MIN, RECORDING_DELAY_SEC, PIEZO_THRESHOLD

    global NUM_TRIALS_PER_MOUSE, SAVE_DATA_PATH, PREFERRED_PAW

    global DAILY_TRIAL_CAP, MAX_DAILY_TIME_MIN

    global StepperA_enable, StepperB_enable, StepperA_STEP_PIN, StepperB_STEP_PIN, StepperA_DIR_PIN, StepperB_DIR_PIN

    global home_switch1, home_switch2, relay1, relay2, IRBreakerPin, PiezoPin

    global DISTANCE_STEPPER_IN_STEPS, CAMERA_TARGET_FRAMERATE, STEPS_PER_REV, CAMERA_RESOLUTION

    global DEBUG

    

    # Assign values from tracker

    X_HOME_POS = tracker.X_HOME_POS

    Y_HOME_POS = tracker.Y_HOME_POS

    ARM_HEIGHT_POS = tracker.ARM_HEIGHT_POS

    SPEED_XY = tracker.SPEED_XY

    

    MAX_RECORDING_TIME_MIN = tracker.MAX_RECORDING_TIME_MIN

    RECORDING_DELAY_SEC = tracker.RECORDING_DELAY_SEC

    PIEZO_THRESHOLD = tracker.PIEZO_THRESHOLD

    

    NUM_TRIALS_PER_MOUSE = tracker.NUM_TRIALS_PER_MOUSE

    SAVE_DATA_PATH = tracker.SAVE_DATA_PATH

    PREFERRED_PAW = tracker.PREFERRED_PAW

    

    DAILY_TRIAL_CAP = tracker.DAILY_TRIAL_CAP

    MAX_DAILY_TIME_MIN = tracker.MAX_DAILY_TIME_MIN

    

    StepperA_enable = tracker.StepperA_enable

    StepperB_enable = tracker.StepperB_enable

    StepperA_STEP_PIN = tracker.StepperA_STEP_PIN

    StepperB_STEP_PIN = tracker.StepperB_STEP_PIN

    StepperA_DIR_PIN = tracker.StepperA_DIR_PIN

    StepperB_DIR_PIN = tracker.StepperB_DIR_PIN

    

    home_switch1 = tracker.home_switch1

    home_switch2 = tracker.home_switch2

    relay1 = tracker.relay1

    relay2 = tracker.relay2

    IRBreakerPin = tracker.IRBreakerPin

    PiezoPin = tracker.PiezoPin

    

    DISTANCE_STEPPER_IN_STEPS = tracker.DISTANCE_STEPPER_IN_STEPS

    STEPS_PER_REV = tracker.STEPS_PER_REV

    CAMERA_TARGET_FRAMERATE = tracker.CAMERA_TARGET_FRAMERATE

    CAMERA_RESOLUTION = tracker.CAMERA_RESOLUTION

    

    DEBUG = tracker.DEBUG

   



class PiezoRecorder:

  

    def create_directory(base_path, mouse_var, test_number):

        """Create directory structure if it doesn't exist"""

        #base_path = os.path.join(os.path.expanduser('~'), 'PiezoTests')

        dir_path = os.path.join(base_path, mouse_var, f"Piezo-{test_number}-")

        os.makedirs(dir_path, exist_ok=True)

        return dir_path

    

    def get_file_path(dir_path, mouse_var, start_time):

        """Generate file path with timestamp"""

        timestamp = start_time.strftime("%Y%m%d%H%M")

        return os.path.join(dir_path, f"Piezo{timestamp}"+f"-MOUSE:{mouse_var}.csv")  # Added .csv extension

    

    def format_timestamp(elapsed_seconds):

        """Format elapsed time as minutes:seconds:milliseconds"""

        minutes = int(elapsed_seconds // 60)

        seconds = int(elapsed_seconds % 60)

        milliseconds = int((elapsed_seconds * 1000) % 1000)

        return f"{minutes:02d}:{seconds:02d}:{milliseconds:03d}"

    

    def write_header(file_path):

        """Write CSV headers to the file"""

        with open(file_path, 'w', newline='') as f:

            writer = csv.writer(f)

            writer.writerow(["Time Minutes", "Data", "HIT CHECK"])

    

    def append_data(file_path, timestamp, data_out, is_hit):

        """Append data row to CSV file"""

        hit_status = "HIT" if is_hit else "NO"

        with open(file_path, 'a', newline='') as f:

            writer = csv.writer(f)

            writer.writerow([timestamp, f"{data_out:.2f}", hit_status])

    

    def Record_PelletData(MOUSEID,test_number,base_path): 

        # Configuration

        SERIAL_PORT = '/dev/ttyUSB1'

        BAUD_RATE = 230400

        THRESHOLD = 5.00

             

        try:

            # Setup serial connection

            ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)

            ser.reset_input_buffer()

            

            # Create directory and file

            dir_path = create_directory(base_path,mouse_var, test_number)

            start_time = datetime.now()

            file_path = get_file_path(dir_path, mouse_var, start_time)

            

            # Write header if new file

            if not os.path.exists(file_path):

                write_header(file_path)

            

          #  print(f"Recording data to: {file_path}")

            

            while True:

                if ser.in_waiting > 0:

                    line = ser.readline().decode('utf-8').rstrip()

                    

                    try:

                        Data_Out = float(line)

                        elapsed_time = (datetime.now() - start_time).total_seconds()

                        timestamp = format_timestamp(elapsed_time)

                        is_hit = Data_Out > THRESHOLD

                        

                        # Print to console

                        #print(f"Time: {timestamp}, Data: {Data_Out:.2f}, {'HIT!!!' if is_hit else 'NO'}")

                        

                        # Write to CSV file

                        append_data(file_path, timestamp, Data_Out, is_hit)

                        

                        if is_hit:

                            Data_Out = 0.0

                            sleep(0.1)

                            

                    except ValueError as e:

                        print(f"Error parsing data: {e}")

                    except Exception as e:

                        print(f"Unexpected error: {e}")

                        

        except serial.SerialException as e:

            print(f"Serial port error: {e}")

        except KeyboardInterrupt:

            # Add recording duration to filename

            elapsed_time = (datetime.now() - start_time).total_seconds()

            base, ext = os.path.splitext(file_path)

            new_file_path = f"{base}_{int(elapsed_time)}s{ext}"

            os.rename(file_path, new_file_path)

            print(f"Data saved to: {new_file_path}")

        finally:

            if 'ser' in locals() and ser.is_open:

                ser.close()

                print("Serial port closed")

    

class GlobalMouseTracker:



    

    def __init__(self):

        self.lock = threading.Lock()

        os.makedirs(HOME_DIR, exist_ok=True)

        os.makedirs(CONFIG_DIR, exist_ok=True)

        self.trial_log_file = os.path.join(HOME_DIR, "trial_logs.csv")

        self.raw_to_normal = self._load_id_mapping()

        self.tracking_data = self._load_tracking_data()

        self.next_id = self._calculate_next_id()

        self.X_HOME_POS = None

        self.Y_HOME_POS = None

        self.ARM_HEIGHT_POS = None

        self.SPEED_XY = None

        self.MAX_RECORDING_TIME_MIN = None

        self.RECORDING_DELAY_SEC = None

        self.PIEZO_THRESHOLD = None

        self.NUM_TRIALS_PER_MOUSE = None

        self.SAVE_DATA_PATH = None

        self.PREFERRED_PAW = None

        self.DAILY_TRIAL_CAP = None

        self.MAX_DAILY_TIME_MIN = None

        self.StepperA_enable = None

        self.StepperB_enable = None

        self.StepperA_STEP_PIN = None

        self.StepperB_STEP_PIN = None

        self.StepperA_DIR_PIN = None

        StepperB_DIR_PIN = None

        self.home_switch1 = None

        self.home_switch2 = None

        self.relay1 = None

        self.relay2 = None

        self.IRBreakerPin = None

        self.PiezoPin = None

        self.DISTANCE_STEPPER_IN_STEPS = None

        self.STEPS_PER_REV = None

        self.CAMERA_TARGET_FRAMERATE = None

        self.CAMERA_RESOLUTION = None

        self.DEBUG = None

        

    

        self.RAW_ID = None



    

    

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

            RAW_ID = raw_id



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

        self.tracking_data[normal_id]['last_seen'] = datetime.now().strftime("%d-%m-%Y")



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

            self.RAW_ID = raw_id



        return self.tracking_data.get(normal_id, {

            'trial_count': 0,

            'test_time': 0,

            'last_seen': None

        })



    def get_daily_limits(self):

        return {'daily_trial_cap': NUM_TRIALS_PER_MOUSE, 'max_daily_time': (MAX_DAILY_TIME_MIN * NUM_TRIALS_PER_MOUSE)}



    def create_default_config(self):

        os.makedirs(os.path.dirname(CONFIG_FILE_PATH), exist_ok=True)



        config = configparser.ConfigParser()

        config['SYSTEM_SETTINGS'] = {

            'X_HOME_POS': '600',

            'Y_HOME_POS': '500',

            'ARM_HEIGHT_POS': '0',

            'SPEED_XY': '200',

            'MAX_RECORDING_TIME_MIN': '3',

            'RECORDING_DELAY_SEC': '2',

            'PIEZO_THRESHOLD': '4.0',

            'NUM_TRIALS_PER_MOUSE': '2',

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

        

        

        if not os.path.exists(CONFIG_FILE_PATH):

           self.create_default_config()



        config = configparser.ConfigParser()

        config.read(CONFIG_FILE_PATH)



        self.X_HOME_POS = int(config['SYSTEM_SETTINGS']['X_HOME_POS'])

        self.Y_HOME_POS = int(config['SYSTEM_SETTINGS']['Y_HOME_POS'])

        self.ARM_HEIGHT_POS = int(config['SYSTEM_SETTINGS']['ARM_HEIGHT_POS'])

        self.SPEED_XY = int(config['SYSTEM_SETTINGS']['SPEED_XY'])

        self.MAX_RECORDING_TIME_MIN = int(config['SYSTEM_SETTINGS']['MAX_RECORDING_TIME_MIN'])

        self.RECORDING_DELAY_SEC = int(config['SYSTEM_SETTINGS']['RECORDING_DELAY_SEC'])

        self.PIEZO_THRESHOLD = float(config['SYSTEM_SETTINGS']['PIEZO_THRESHOLD'])

        self.NUM_TRIALS_PER_MOUSE = int(config['SYSTEM_SETTINGS']['NUM_TRIALS_PER_MOUSE'])

        self.SAVE_DATA_PATH = config['SYSTEM_SETTINGS']['SAVE_DATA_PATH']

        self.PREFERRED_PAW = PawPreference(config['SYSTEM_SETTINGS']['PREFERRED_PAW'])

        self.DAILY_TRIAL_CAP = int(config['SYSTEM_SETTINGS']['DAILY_TRIAL_CAP'])

        self.MAX_DAILY_TIME_MIN = int(config['SYSTEM_SETTINGS']['MAX_DAILY_TIME_MIN'])

        self.StepperA_enable = int(config['SYSTEM_SETTINGS']['RPI_PIN_StepperA_enable'])

        self.StepperB_enable = int(config['SYSTEM_SETTINGS']['RPI_PIN_StepperB_enable'])

        self.StepperA_STEP_PIN = int(config['SYSTEM_SETTINGS']['RPI_PIN_StepperA_STEP_PIN'])

        self.StepperB_STEP_PIN = int(config['SYSTEM_SETTINGS']['RPI_PIN_StepperB_STEP_PIN'])

        self.StepperA_DIR_PIN = int(config['SYSTEM_SETTINGS']['RPI_PIN_StepperA_DIR_PIN'])

        self.StepperB_DIR_PIN = int(config['SYSTEM_SETTINGS']['RPI_PIN_StepperB_DIR_PIN'])

        self.home_switch1 = int(config['SYSTEM_SETTINGS']['RPI_PIN_home_switch1'])

        self.home_switch2 = int(config['SYSTEM_SETTINGS']['RPI_PIN_home_switch2'])

        self.relay1 = int(config['SYSTEM_SETTINGS']['RPI_PIN_relay1'])

        self.relay2 = int(config['SYSTEM_SETTINGS']['RPI_PIN_relay2'])

        self.IRBreakerPin = int(config['SYSTEM_SETTINGS']['RPI_PIN_IRBreakerPin'])

        self.PiezoPin = int(config['SYSTEM_SETTINGS']['RPI_PIN_PiezoPin'])

        self.DISTANCE_STEPPER_IN_STEPS = int(config['SYSTEM_SETTINGS']['DISTANCE_STEPPER_IN_STEPS'])

        self.STEPS_PER_REV = int(config['SYSTEM_SETTINGS']['STEPS_PER_REV'])

        self.CAMERA_TARGET_FRAMERATE = int(config['SYSTEM_SETTINGS']['CAMERA_TARGET_FRAMERATE'])

        self.CAMERA_RESOLUTION = str(config['SYSTEM_SETTINGS']['CAMERA_RESOLUTION'])

        self.DEBUG = str(config['SYSTEM_SETTINGS']['DEBUG'])

        print("\n Config Loaded \n")



        if self.DEBUG == 1:

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

            self.total_trail_time += Element.trial_duration

            self.trail_num_total = len(self.Trails_Times_Completed_In_current_Session)

        else:

            raise TypeError("Only Trail_Element objects can be added to Trails_Times_Completed_In_current_Session")

class VideoRecorder:



    def parse_camera_resolution(self, resolution_str):

        """Parse a resolution string in the format 'WIDTHxHEIGHT' into a tuple (WIDTH, HEIGHT)."""

        width, height = map(int, resolution_str.split('x'))

        return (width, height)



    def Cam_Thread(self, duration_seconds,fps):

            """Threaded version of my_method"""

            thread = threading.Thread(target=self.record_video, args=(duration_seconds,fps,))

            thread.start()

            return thread 

            

    def __init__(self, width=640, height=360, fps=200, duration_seconds=10, output_dir='recordings'):



        Camera_Parsed_Resoloution = VideoRecorder.parse_camera_resolution(self,CAMERA_RESOLUTION)

        self.result = None





        if Camera_Parsed_Resoloution is None:



            self.width = width



            self.height = height



            self.fps = fps



            self.duration_seconds = duration_seconds



            self.output_dir = output_dir



        self.width, self.height = Camera_Parsed_Resoloution

        self.fps = CAMERA_TARGET_FRAMERATE

        self.duration_seconds = MAX_RECORDING_TIME_MIN

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



    def record_video(self,duration,fps):



        os.makedirs(self.output_dir, exist_ok=True)



        cap = self.setup_camera()



        if not cap.isOpened():

            print("Error: Could not open camera")



            return



        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")#datetime.strptime(datetime.now(), "%Y-%m-%d")



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



    def __init__(self, port='/dev/ttyUSB0', baudrate=9600, timeout=1):



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



    def step_motor(self, stepper_pin, dir_pin, enable_pin, direction, steps):



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

class Trail_Element:

    def __init__(self, trial_number, trial_duration, completed, interrupted, rfid_tag):

        self.trial_number = trial_number

        self.trial_duration = trial_duration

        self.completed = completed

        self.interrupted = interrupted

        self.rfid_tag = rfid_tag



    def __repr__(self):

        return f"Trail_Element(trial_number={self.trial_number}, trial_duration={self.trial_duration}, completed={self.completed}, interrupted={self.interrupted}, rfid_tag={self.rfid_tag})"

class Periphals:



    def quick_ir_check(self):

        global IRState

        IRState = False

        if GPIO.input(IRBreakerPin) == GPIO.HIGH:

            IRState = False

        else:

            print("MOUSE IN!....Awaiting RFID TAG")

            IRState = True

            return True

            

    @async_to_sync

    async def async_quick_ir_check(self):

        global IRState

        IRState = False

        if GPIO.input(IRBreakerPin) == GPIO.HIGH:

            IRState = False

        else:

            print("MOUSE IN!....Awaiting RFID TAG")

            IRState = True

            return True

            

    def check_ir_breaker(self):

        try:

            global IRState

            if GPIO.input(IRBreakerPin) == GPIO.HIGH:

               return False 

            else:

               return True

        except Exception as e:

            print(f"Error reading IR breaker: {str(e)}")

            return False



    def constant_check_ir_breaker(self):

        try:

            global IRState

            while True:

                if GPIO.input(IRBreakerPin) == GPIO.HIGH:

                    IRState = False 

                else:

                    IRState = True

                    

                print(f"IR_CHECK_IN:{str(IRState)}")

                time.sleep(5)

        except Exception as e:

            print(f"Error reading IR breaker: {str(e)}")

            return False



    async def READTAG(self):

        global RFID_TAG_RAW

        RFID_TAG_RAW = None

        reader = RFIDReader(port='/dev/ttyUSB0')



        while RFID_TAG_RAW == None:

            if reader.connect():



                tag_id = reader.read_tag_id()



                if tag_id:

                    RFID_TAG_RAW = tag_id

                    print(f"Single read - Tag ID: {tag_id}")



                    return tag_id



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

def list_usb_devices():

    try:

        result = subprocess.run(['lsusb'], capture_output=True, text=True)

        print(result.stdout)

    except Exception as e:

        print(f"An error occurred: {e}")

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

def wait_for_mouse(RFID_TAG_RAW):

    

    print("Waiting for mouse...")

    peripheral_instance = Periphals()

    beam_break_result = peripheral_instance.quick_ir_check()

    #Thread = threading.Thread(peripheral_instance.constant_check_ir_breaker())

    #Thread.daemon = True

    #Thread.start()

    #Constant_Check = async_to_sync(peripheral_instance.constant_check_ir_breaker)()

    RFID_TAG_RAW =  async_to_sync(peripheral_instance.READTAG)()

    if beam_break_result and RFID_TAG_RAW == None:

        print("\nBeam Broken, Checking for MOUSE ID....\n")

        #beam is broken but we don't have RFID

        RFID_TF = async_to_sync(peripheral_instance.READTAG)()

    print(f"RFID - {RFID_TAG_RAW}")

    return True

@async_to_sync

async def present_pellet(self, CurrentMouseID,NUM_TRIALS_PER_MOUSE, periphals_instance, Trail_Number,PIEZO_DIR):

    global RECORDING_DIR

    """Handle pellet presentation sequence"""

    periphals_instance = Periphals()



    while periphals_instance.check_ir_breaker() != False :



        # while GPIO.input(IRBreakerPin) == GPIO.LOW:  # while mouse IN



        print("EXTEND")



        periphals_instance.extend_actuator()



        await asyncio.sleep(3)



        print("RETRACT")



        periphals_instance.retract_actuator()



        await asyncio.sleep(1.3)



        periphals_instance.stop_actuator()



        await asyncio.sleep(1.3)

        

        # Start recording

        threads = []



        print("Starting camera recording...")

        

        print(f"Recording to: {RECORDING_DIR}")

        recorder = VideoRecorder(duration_seconds=10, fps=320)



        # Start multiple threads

        print("recording_thread_started")

        thread = recorder.Cam_Thread(10,320)

        PiezoRecorder_ = PiezoRecorder()

        # brokenthread2 = PiezoRecorder_.Record_PelletData(CurrentMouseID,Trail_Number,PIEZO_DIR)

        threads.append(thread)

        threads.append(thread2)

        for thread in threads:

            thread.join()

        

        





        print("STOP")



        periphals_instance.stop_actuator()

     



        # t2.join()

        

        await asyncio.sleep(0.5)

        return True

    else:

        print(f"MOUSE LEFT \n Test Number {int(Trail_Number)+1} Failed! ")

        periphals_instance.extend_actuator()

        return False

        

# Modified main function

def main(SingleTrackedData,Mouse_Dir,periphals_instance):

    global RECORDING_DIR,NUM_TRIALS_PER_MOUSE

    RECORDING_DIR = os.path.join(Mouse_Dir, "Video_Recordings")

    StepperManager_ = StepperManager()

    try:

      os.makedirs(RECORDING_DIR, exist_ok=True)

    except Exception as e:

      print(f"An error occurred: {e}")



    trials_completed_today = SingleTrackedData.trial_count

    tracker = SingleTrackedData.tracker

    Trail_Elements = []  

    print(f"Starting trials for mouse with RFID: {RFID_TAG_RAW}")

    print("Starting Automated Sequence...")

    Interrupt_ = False

    PIEZO_DIR = os.path.join(Mouse_Dir, "Piezo_Recordings")

    while not Interrupt_:

        trial_start = time.time()

        max_duration = MAX_RECORDING_TIME_MIN * 60

        completed = False

        interrupted = False

        print("Homing motors...")

        StepperManager_.home_motors()

        time.sleep(1)

        try:

            # Move to stage home coordinates

            print("Moving to stage Test position...")

            StepperManager_.step_motor(StepperA_STEP_PIN, StepperA_DIR_PIN, StepperA_enable, True, X_HOME_POS)

            StepperManager_.step_motor(StepperB_STEP_PIN, StepperB_DIR_PIN, StepperB_enable, True, Y_HOME_POS)

            time.sleep(1)

            while trials_completed_today < NUM_TRIALS_PER_MOUSE:

              # Present pellet

              print("Presenting pellet...")

              if (present_pellet(SingleTrackedData.normal_id, NUM_TRIALS_PER_MOUSE, ProfileID,periphals_instance,trials_completed_today,PIEZO_DIR)):

                  print("Iteration_Complete")

                  completed = True

                  interrupted = False

                  trials_completed_today += 1

                  trial_end = time.time()

                  trial_duration = trial_end - trial_start

                  new_trail_element = Trail_Element(trials_completed_today, trial_duration, completed, interrupted, RFID_TAG_RAW)

                  Trail_Elements.append(new_trail_element)

              else:

                  if periphals_instance.check_ir_breaker() != False :

                    break

                  print("Sequence Failed")

                  completed = False

                  interrupted = True

                  trials_completed_today += 1

                  trial_end = time.time()

                  trial_duration = trial_end - trial_start

                  new_trail_element = Trail_Element(trials_completed_today, trial_duration, completed, interrupted, RFID_TAG_RAW)

                  Trail_Elements.append(new_trail_element)

                  

              # Wait between iterations

              time.sleep(1.5)

              # Check for time limit

              if (time.time() - trial_start) >= max_duration:

                  completed = True

                  interrupted = True

                  print("Time Exceeded! - Exiting!")

                  break

            else:

              trial_end = time.time()

              trial_duration = trial_end - trial_start

              # Return to home position

              # Clean up

              print("Sequences completed successfully")

              print(f"Sessions complete: {trials_completed_today} trials")

              print("Returning to home position...")

              periphals_instance.extend_actuator()

              StepperManager_.home_motors()

              for trail_element in Trail_Elements:

                  tracker.log_trial(

                      trail_element.rfid_tag,          # RFID_TAG_RAW

                      trail_element.trial_duration,   # trial_duration

                      trail_element.completed,        # completed

                      trail_element.interrupted       # interrupted

                  ) 

                  SingleTrackedData.add_trail_element(Trail_Element(trials_completed_today, trial_duration, completed, interrupted, RFID_TAG_RAW))

                  # tracker.update_tracking(RFID_TAG_RAW,trials=1,test_time=trial_duration)

              time.sleep(4)

              Interrupt()

              return trials_completed_today

                

                

        except ValueError as e:

            print(f"Error: {e}")

            return trials_completed_today

    else:

      print("MOUSE LEFT!")

      return trials_completed_today

    

   

async def save_session_data():



    print(f"Saving data to {SAVE_DATA_PATH}")

    return True

def run_system(tracker):

    admin_Open = False

    list_usb_devices()

    time.sleep(0.2)

    display_welcome_banner()

    if debug_mode:

        print("\n\n\nATTENTION\n\n !Debug_Mode_Enabled! \n -Verbose Output Enabled\n")

        print("Press any key for admin menu (waiting 5 seconds)...")

        timeout = time.time() + 1

        while time.time() < timeout:

            if input_available():

                admin_menu()

                break

    Current_Mouse = SingleTrackedData()

    periphals_instance = Periphals()

    Current_Mouse.tracker = tracker

    while True:

        while periphals_instance.check_ir_breaker() != False:

          global RFID_TAG_RAW

          RFID_TAG_RAW = None

          if wait_for_mouse(RFID_TAG_RAW):

              mouse_id = RFID_TAG_RAW 

               # Function to get the current mouse ID

             # tracker.update_tracking(RFID_TAG_RAW, trials=0, test_time=0)

              Tracker_Data = Current_Mouse.tracker.get_mouse_data(mouse_id)

              Current_Mouse.normal_id = tracker._get_normal_id(mouse_id)

              Current_Mouse.raw_id = tracker.RAW_ID

              Current_Mouse.trial_count = Tracker_Data['trial_count']

              Current_Mouse.test_time = Tracker_Data['test_time']

              Current_Mouse.last_seen = Tracker_Data['last_seen']

              print(f"Mouse Last seen: {Current_Mouse.last_seen}")

              if Current_Mouse != None:

                  print(f"\nTrials: {Current_Mouse.trial_count}, Time: {Current_Mouse.test_time} \n")

              Old_Count =  Current_Mouse.trial_count

              Old_Test_time_today =  Current_Mouse.test_time

          global MOUSE_DIR

          MOUSE_DIR = os.path.join(HOME_DIR, str(Current_Mouse.normal_id) +" - " + str(Current_Mouse.raw_id) + "/" + str(datetime.now().strftime("%d-%m-%Y")) )

          LOG_DIR = os.path.join(MOUSE_DIR, "Logs")

          try:

            os.makedirs(MOUSE_DIR, exist_ok=True)

            os.makedirs(LOG_DIR, exist_ok=True)

          except ValueError as e:

            print(f"Error: {e}")

            return

            

          tracker.trial_log_file = os.path.join(LOG_DIR, str(datetime.now().strftime("%d-%m-%Y")) + "_trial_logs_.csv")

          tracker._ensure_trial_log_exists()

          if Current_Mouse.trial_count < NUM_TRIALS_PER_MOUSE and Current_Mouse.test_time < MAX_DAILY_TIME_MIN:

            trials_completed = main(Current_Mouse,MOUSE_DIR,periphals_instance)

            print(f"Trails{trials_completed}")

            if trials_completed >= 0:

               # async_to_sync(save_session_data)()

                tracker.update_tracking(RFID_TAG_RAW,Current_Mouse.trail_num_total , Current_Mouse.total_trail_time)

          print(f"\nMouse ID {mouse_id} has exceeded daily trials or test time.")

          print(f"\nRechecking in 10 Seconds For another mouse Without the ID {mouse_id}\n\n\n")

          time.sleep(10)

        else:

           print(f"\n\nMouse ID {mouse_id} has Left")

           time.sleep(5)





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

    tracker = GlobalMouseTracker()

    tracker.load_config()

    setup(tracker)

    run_system(tracker)

