#!/usr/bin/env python3

# Mouse Behavior System Script

# REQUIRED

# RPi.GPIO

# SPI   ON

#multiprocessing
from time import sleep

from enum import Enum

import sys

import time

from datetime import datetime

import os

import importlib

import importlib.util

from datetime import datetime

import subprocess

import asyncio



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

global THRESHOLD_EXCEEDED

global RFID_USB_SERIAL_IDENTIFICATION_STRING, ARDUINO_USB_SERIAL_IDENTIFICATION_STRING, CAMERA_USB_SERIAL_IDENTIFICATION_STRING

global RPI_PIN_IR_LED_ARRAY , USE_PEZO_TRIGGER



IRState = False

Interrupt_ = False
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



def Interrupt():

   global Interrupt_

   Interrupt_ = True

try:



    import RPi.GPIO as GPIO



    import threading



    import asyncio



    from asgiref.sync import async_to_sync

    import aiofiles


    import serial

    import inspect


    import queue



    import cv2


    import aiocsv



    import numpy as np

    import configparser



    import select



    import csv

except ImportError:



    # List of required packages



    required_packages = ["rpi-lgpio","aiofiles","aiocsv", "asyncio", "asgiref", "pyserial", "configparser","numpy"]







    # Install each required package



    for package in required_packages:



        install_package(package)


def setup(tracker):
    try:
  
         # Define global variables
    
        global X_HOME_POS, Y_HOME_POS, ARM_HEIGHT_POS, SPEED_XY
    
        global MAX_RECORDING_TIME_MIN, RECORDING_DELAY_SEC, PIEZO_THRESHOLD
    
        global NUM_TRIALS_PER_MOUSE, SAVE_DATA_PATH, PREFERRED_PAW
    
        global DAILY_TRIAL_CAP, MAX_DAILY_TIME_MIN
    
        global StepperA_enable, StepperB_enable, StepperA_STEP_PIN, StepperB_STEP_PIN, StepperA_DIR_PIN, StepperB_DIR_PIN
    
        global home_switch1, home_switch2, relay1, relay2, IRBreakerPin, PiezoPin
    
        global DISTANCE_STEPPER_IN_STEPS, CAMERA_TARGET_FRAMERATE, STEPS_PER_REV, CAMERA_RESOLUTION
    
        global DEBUG
    
        global THRESHOLD_EXCEEDED
    
        global RFID_USB_SERIAL_IDENTIFICATION_STRING, ARDUINO_USB_SERIAL_IDENTIFICATION_STRING, CAMERA_USB_SERIAL_IDENTIFICATION_STRING
    
        global RPI_PIN_IR_LED_ARRAY , USE_PEZO_TRIGGER
    
        Add_Tracker_Data_To_Global_Sheet(tracker)
    
        #Initialize GPIO settings
    
        GPIO.setmode(GPIO.BCM)
    
        periphals_instance = Periphals()
        #home/m9686/Desktop/projects/projectsenv/bin/./
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
      
    except ImportError:
    
        del periphals_instance

    

def Add_Tracker_Data_To_Global_Sheet(tracker):

    # Define global variables

    global X_HOME_POS, Y_HOME_POS, ARM_HEIGHT_POS, SPEED_XY

    global MAX_RECORDING_TIME_MIN, RECORDING_DELAY_SEC, PIEZO_THRESHOLD

    global NUM_TRIALS_PER_MOUSE, SAVE_DATA_PATH, PREFERRED_PAW

    global DAILY_TRIAL_CAP, MAX_DAILY_TIME_MIN

    global StepperA_enable, StepperB_enable, StepperA_STEP_PIN, StepperB_STEP_PIN, StepperA_DIR_PIN, StepperB_DIR_PIN

    global home_switch1, home_switch2, relay1, relay2, IRBreakerPin, PiezoPin

    global DISTANCE_STEPPER_IN_STEPS, CAMERA_TARGET_FRAMERATE, STEPS_PER_REV, CAMERA_RESOLUTION

    global DEBUG

    global THRESHOLD_EXCEEDED

    global RFID_USB_SERIAL_IDENTIFICATION_STRING, ARDUINO_USB_SERIAL_IDENTIFICATION_STRING, CAMERA_USB_SERIAL_IDENTIFICATION_STRING

    global RPI_PIN_IR_LED_ARRAY , USE_PEZO_TRIGGER

  

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

    RPI_PIN_IR_LED_ARRAY = tracker.RPI_PIN_IR_LED_ARRAY

    

    DISTANCE_STEPPER_IN_STEPS = tracker.DISTANCE_STEPPER_IN_STEPS

    STEPS_PER_REV = tracker.STEPS_PER_REV

    CAMERA_TARGET_FRAMERATE = tracker.CAMERA_TARGET_FRAMERATE

    CAMERA_RESOLUTION = tracker.CAMERA_RESOLUTION

    

    DEBUG = tracker.DEBUG
    USE_PEZO_TRIGGER = tracker.USE_PEZO_TRIGGER
    

    THRESHOLD_EXCEEDED = threading.Event()

    RFID_USB_SERIAL_IDENTIFICATION_STRING = tracker.RFID_USB_SERIAL_IDENTIFICATION_STRING

    ARDUINO_USB_SERIAL_IDENTIFICATION_STRING = tracker.ARDUINO_USB_SERIAL_IDENTIFICATION_STRING

    print("Called INTO-"+inspect.stack()[0][3])


    

class IRLedControl:

    def __init__(self, pin=6):

        GPIO.setmode(GPIO.BCM)

        GPIO.setup(RPI_PIN_IR_LED_ARRAY, GPIO.OUT)

        self.pin = pin or RPI_PIN_IR_LED_ARRAY  

        self._state = False

        

    def on(self):

        GPIO.output(self.pin, GPIO.HIGH)

        self._state = True

        return self



    def off(self):

        GPIO.output(self.pin, GPIO.LOW)

        self._state = False

        return self



    def __del__(self):

        try:

            GPIO.cleanup(self.pin)

        except:

            pass

            

class SerialDeviceFinder:



    def get_tty_serial_to_port_conn(self, device_name_pattern):
        


        serial_path = '/dev/serial/by-id'



        try:

            available_devices = os.listdir(serial_path)



            matching_devices = [

                device for device in available_devices

                if device_name_pattern in device

            ]



            if not matching_devices:

                raise ValueError(f"No serial device found matching '{device_name_pattern}'")



            #If multiple matches, choose the first one and warn

            if len(matching_devices) > 1:

                print(f"Warning: Multiple devices match '{device_name_pattern}'. Using the first match.")



            matched_device = matching_devices[0]

            full_device_path = os.path.realpath(os.path.join(serial_path, matched_device))



            return full_device_path



        except FileNotFoundError:

            raise ValueError(f"Serial device directory {serial_path} not found")

        except PermissionError:

            raise PermissionError("Insufficient permissions to access serial devices")



    def Tie_serial_connection(self, device_name_pattern):

        try:

            # Find the device path

            device_path = self.get_tty_serial_to_port_conn(device_name_pattern)

            print(f"Successfully Found the device: {device_path}")

            return ser



        except (serial.SerialException, ValueError) as e:

            print(f"Error connecting to serial device: {e}")

            return None

            

class PiezoRecorder:

    global Interrupt_

    global THRESHOLD_EXCEEDED
    global USE_PEZO_TRIGGER




    def __init__(self):

        self.SERIAL_PORT = Get_usb_devices(ARDUINO_USB_SERIAL_IDENTIFICATION_STRING)
        
        if self.SERIAL_PORT == None:
            
            self.SERIAL_PORT = '/dev/ttyUSB0'

        self.BAUD_RATE = 230400

        self.THRESHOLD = PIEZO_THRESHOLD
        self._data_queue = queue.Queue() 
        self._stop_event = threading.Event()  
        self._writer_thread = None
        self._collected_data = [] # Buffer to accumulate data before saving to .npy
        # Define mapping for event types to numerical codes (adjust as needed)
        self._event_type_map = {
            "data": 0,
            "threshold_exceeded": 1,
            "pellet_dispensed": 2,
            # Add any other event types you use
        }
        self._next_event_code = len(self._event_type_map) # For new, unmapped event types

        self.running = False

        self.file_path = None

        self.BOOL = True

        self.ser = None

    def _get_event_code(self, event_type):
        if event_type not in self._event_type_map:
            print(f"Warning: New event type '{event_type}' encountered. Assigning code {self._next_event_code}")
            self._event_type_map[event_type] = self._next_event_code
            self._next_event_code += 1
        return self._event_type_map[event_type]

    def _prepare_file_path(self, base_path, mouse_var, test_number):
        mouse_dir = os.path.join(base_path,str(datetime.now().strftime("%H:%M.%f")))
        print(mouse_dir)
        os.makedirs(mouse_dir, exist_ok=True)
        
        # Use .npy extension
        file_name = f"trial_{str(test_number)}_piezo_data.npy"
        self._file_path = os.path.join(mouse_dir, file_name)

    def _writer_loop(self):
        print(f"Piezo writer thread started for file: {self._file_path}")
        while not self._stop_event.is_set() or not self._data_queue.empty():
            try:
                # Get data with a timeout to allow checking stop event
                timestamp_str, piezo_value, event_type = self._data_queue.get(timeout=0.1)
                
                # Convert timestamp to Unix timestamp (float)
                # Assuming timestamp_str is in '%Y-%m-%d %H:%M:%S.%f' format
                timestamp_dt = datetime.strptime(timestamp_str, '%d-%m-%Y %H:%M:%S.%f')
                numerical_timestamp = timestamp_dt.timestamp()

                # Convert event_type to numerical code
                numerical_event_type = self._get_event_code(event_type)

                self._collected_data.append([numerical_timestamp, piezo_value, numerical_event_type])
                self._data_queue.task_done()
            except queue.Empty:
                continue # No data in queue, check stop event again or wait
            except ValueError as e:
                print(f"Error parsing timestamp or data: {e} for row: {timestamp_str}, {piezo_value}, {event_type}")
            except Exception as e:
                print(f"Error in piezo writer thread while collecting data: {e}")
                return
        # After stop signal and queue is empty, save the accumulated data
        if self._collected_data:
            try:
                # Convert list of lists to a NumPy array
                data_array = np.array(self._collected_data, dtype=np.float64) 
                # Save the array to .npy file
                np.save(self._file_path, data_array)
                print(f"Piezo data saved successfully to {self._file_path}")
                
                # Optionally save the event_type_map to reconstruct strings
                map_file_path = self._file_path.replace('.npy', '_event_map.json')
                import json
                with open(map_file_path, 'w') as f:
                    # Invert the map for easier lookup when reading
                    inverted_map = {v: k for k, v in self._event_type_map.items()}
                    json.dump(inverted_map, f, indent=4)
                print(f"Event type map saved to {map_file_path}")

            except Exception as e:
                print(f"Error saving piezo data to .npy file {self._file_path}: {e}")
        else:
            print("No piezo data collected to save.")
            
        print("Piezo writer thread finished.")    


    def writer_task(self):

        batch_size = 50  # Write 50 entries at a time for efficiency

        while self.running:

            try:

                batch = []

                # Try to collect a batch of data or wait for new data

                try:

                    # Always get at least one item (blocking)

                    batch.append(self.data_queue.get(timeout=0.5))

                    self.data_queue.task_done()

                    

                    # Then try to get more items without blocking

                    for _ in range(batch_size - 1):

                        if not self.running:

                            break

                        try:

                            batch.append(self.data_queue.get_nowait())

                            self.data_queue.task_done()

                        except queue.Empty:

                            break

                except queue.Empty:

                    # No data in queue, just continue the loop

                    continue

                

                asyncio.run(self.write_data(batch))
              

            except Exception as e:

                print(f"Error in writer thread: {e}")

   
    def add_data_point(self, timestamp_str, piezo_value, event_type="data"):
        """
        Adds a data point to the queue to be processed by the background thread.
        timestamp_str should be a string (e.g., from datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')).
        """
        if self.running:
            self._data_queue.put([timestamp_str, piezo_value, event_type])
        else:
            print("Warning: PiezoRecorder is not running. Data point not added.")
    def Close(self):
        if not self.running:
            print("Device was not active or already closed. No cleanup needed.")
            return

        print("Attempting to close MyHardwareDevice resources...")
        
        # 1. Signal the thread to stop its internal loop
        if self.running:
            self.running = False 
            print("Signaled read thread to stop...")

            if self._writer_thread and self._writer_thread.is_alive():
                print("Waiting for read thread to finish (max 5 seconds)...")
                self._writer_thread.join(timeout=5) # Wait for the thread to complete
                if self._writer_thread.is_alive():
                    print("Warning: Read thread did not terminate gracefully within timeout!")
                else:
                    print("Read thread has successfully closed.")
            else:
                print("Read thread was not running or already finished.")
            
        # 3. Close other resources (e.g., serial connection, GPIO)
        if self.ser: # Replace with 'if self.serial_connection and self.serial_connection.is_open:' for real serial
            ser.close()
        
        self.running = False # Mark as inactive after successful closing
        print("Piezo resources closed.")
        
    def STOP(self):
        """
        Signals the writer thread to stop, waits for it to finish processing remaining data,
        and ensures the .npy file is saved.
        """
        if not self.running:
            print("Piezo recording is not active.")
            return

        print("Signaling piezo writer thread to stop and save remaining data...")
        self._stop_event.set() # Signal the writer thread to stop
        self.running = False # Update recording status

        # Wait for the writer thread to finish and terminate cleanly
        if self._writer_thread and self._writer_thread.is_alive():
            # Give the thread some time to process remaining items and save the file
            self._writer_thread.join(timeout=30) # Increased timeout for potential large data saves
            if self._writer_thread.is_alive():
                print("Warning: Piezo writer thread did not terminate gracefully.")
            else:
                print("Piezo writer thread stopped successfully.")
        else:
            print("Piezo writer thread was not running or already stopped.")
        if 'ser' in locals() and ser.is_open:

            ser.close()

            print("Serial port closed")


        

    def Record_PelletData(self, MOUSEID, test_number, base_path, Cam_Thread,StepperManager_):

        global Interrupt_

        global THRESHOLD_EXCEEDED
        
        global USE_PEZO_TRIGGER
        
        HOLD_DATA = 0.0
        USE_PEZO_TRIGGER = False
        if self.running:
            print("Piezo recording already active for this instance. Call Stop() first.")
            return
        try:            
            self.running = True

            # Setup serial connection
            ser = serial.Serial(self.SERIAL_PORT, self.BAUD_RATE, timeout=1)
            self.ser = ser
            ser.reset_input_buffer()
            start_time_ = time.time()
            # Start writer thread
            self._stop_event.clear() # Ensure the stop event is clear for a new recording
            # Re-initialize queue and collected data buffer for a new recording session
            self._data_queue = queue.Queue() 
            self._collected_data = []
            # Prepare the file path for writing
            self._prepare_file_path(base_path, MOUSEID, test_number)
            # Start the background writer thread
            self._writer_thread = threading.Thread(target=self._writer_loop, name="PiezoWriterThread")
            # Set as daemon so it doesn't prevent main program from exiting if not explicitly stopped
            self._writer_thread.daemon = True 
            self._writer_thread.start()
            THRESHOLD_EXCEEDED.clear()
            print("Recording Data \n")
            while self.running == True:

                if ser.in_waiting > 0:

                    line = ser.readline().rstrip()

                    try:

                        elapsed_time = (time.time()  - start_time_)

                        timestamp_str = datetime.now().strftime('%d-%m-%Y %H:%M:%S.%f')
                        self.add_data_point(timestamp_str, float(line), "data")
                        
                        Data_Out = float(line)

                        is_hit = Data_Out > self.THRESHOLD
                        

                        if is_hit and USE_PEZO_TRIGGER == True:
                            HOLD_DATA = Data_Out
                            THRESHOLD_EXCEEDED.set()
                            Data_Out = 0.0
                            is_hit = Data_Out
                            #Cam_Thread.STOP()
                            self.STOP()
                            
                            break
                            
                        if elapsed_time > MAX_RECORDING_TIME_MIN:
                           
                            self.STOP()

                            break

                    except ValueError as e:
                        self.STOP()

                        print(f"Error parsing data: {e}")

                    except Exception as e:
                        self.STOP()


                        print(f"Unexpected error: {e}")

            
        except serial.SerialException as e:
            if 'ser' in locals() and ser.is_open:
    
                ser.close()
    
                print("Serial port closed")
            print(f"Serial port error: {e}")
            return

        except KeyboardInterrupt:

            pass

        finally:


            self.running = False
            self.STOP()
        
            if 'ser' in locals() and ser.is_open:

                ser.close()

                print("Serial port closed")
                
                return
    

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

        self.StepperB_DIR_PIN = None

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

        self.RFID_USB_SERIAL_IDENTIFICATION_STRING = None

        self.ARDUINO_USB_SERIAL_IDENTIFICATION_STRING = None

        self.CAMERA_USB_SERIAL_IDENTIFICATION_STRING = None

        self.RAW_ID = None

        self.RPI_PIN_IR_LED_ARRAY = None
        
        self.USE_PEZO_TRIGGER = None

   

    

    

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
                    try:
                        # Corrected parsing of 'last_seen'
                        last_seen_datetime = datetime.strptime(row['last_seen'], '%d-%m-%Y %H:%M:%S')
                        last_seen_seconds = last_seen_datetime.timestamp()
                        
                        data[row['normal_id']] = {
                            'trial_count': int(row['trial_count']),
                            'test_time': float(row['test_time']),
                            'last_seen': last_seen_seconds
                        }
                    except (ValueError, KeyError) as e:
                        print(f"Warning: Skipping malformed row in {TRACKING_FILE}: {row}. Error: {e}")
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

            threads = []

            #thread = self._save_mapping(raw_id, normal_id)

            thread = threading.Thread(target=self._save_mapping, args=(raw_id, normal_id))

            thread.start()  

            threads.append(thread)

            for thread in threads:

              thread.join()

            #self._save_mapping(raw_id, normal_id)

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


        last_seen_datetime_str = datetime.now().strftime('%d-%m-%Y %H:%M:%S')

        last_seen_datetime = datetime.strptime(last_seen_datetime_str, '%d-%m-%Y %H:%M:%S')

        
        self.tracking_data.setdefault(normal_id, {

            'trial_count': 0,

            'test_time': 0,



            'last_seen': datetime.now().strftime("%d-%m-%Y")

        })

        print(datetime.now().strftime("%d-%m-%Y"))

        self.tracking_data[normal_id]['trial_count'] += trials

        self.tracking_data[normal_id]['test_time'] += test_time

        self.tracking_data[normal_id]['last_seen'] = last_seen_datetime



        self._save_tracking_data()



    def _save_tracking_data(self):

        with open(TRACKING_FILE, 'a', newline='') as f:

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

            'MAX_RECORDING_TIME_MIN': '30',

            'RECORDING_DELAY_SEC': '2',

            'PIEZO_THRESHOLD': '8',

            'NUM_TRIALS_PER_MOUSE': '2',

            'SAVE_DATA_PATH': '/home/user/mouse_data_',

            'PREFERRED_PAW': 'Right',

            'DAILY_TRIAL_CAP': '10',

            'MAX_DAILY_TIME_MIN': '10',

            'CAMERA_RESOLUTION':'640x480',

            'RPI_PIN_StepperA_enable': '2',

            'RPI_PIN_StepperB_enable': '17',

            'RPI_PIN_StepperA_STEP_PIN': '3',

            'RPI_PIN_StepperB_STEP_PIN': '27',

            'RPI_PIN_StepperA_DIR_PIN': '4',

            'RPI_PIN_StepperB_DIR_PIN': '22',

            'RPI_PIN_home_switch1': '13',

            'RPI_PIN_home_switch2': '19',

            'RPI_PIN_relay1': '16',

            'RPI_PIN_relay2': '21',

            'RPI_PIN_IRBreakerPin': '26',

            'RPI_PIN_PiezoPin': '6',

            'DISTANCE_STEPPER_IN_STEPS': '3200',

            'STEPS_PER_REV': '200',

            'CAMERA_TARGET_FRAMERATE': '100',

            'RFID_USB_SERIAL_IDENTIFICATION_STRING': 'FTDI_FT232R_USB_UART',

            'ARDUINO_USB_SERIAL_IDENTIFICATION_STRING': '1a86_USB' ,

            'CAMERA_USB_SERIAL_IDENTIFICATION_STRING': 'Gearway Electronics' ,

            'RPI_PIN_IR_LED_ARRAY': '6',
            }
        
        config['FEATURES'] = {
            'USE_PEZO_TRIGGER': 'yes',
            'DEBUG': 'no',
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

        self.RFID_USB_SERIAL_IDENTIFICATION_STRING = str(config['SYSTEM_SETTINGS']['RFID_USB_SERIAL_IDENTIFICATION_STRING'])

        self.ARDUINO_USB_SERIAL_IDENTIFICATION_STRING = str(config['SYSTEM_SETTINGS']['ARDUINO_USB_SERIAL_IDENTIFICATION_STRING'])

        self.CAMERA_USB_SERIAL_IDENTIFICATION_STRING = str(config['SYSTEM_SETTINGS']['CAMERA_USB_SERIAL_IDENTIFICATION_STRING'])

        self.RPI_PIN_IR_LED_ARRAY = str(config['SYSTEM_SETTINGS']['RPI_PIN_IR_LED_ARRAY'])

        self.DEBUG = str(config['FEATURES']['DEBUG'])
        
        self.USE_PEZO_TRIGGER = str(config['FEATURES']['USE_PEZO_TRIGGER'])


        print(f"\nConfig at {os.path.basename(CONFIG_FILE_PATH)} has been Loaded \n")



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
        
        last_seen_datetime_str = datetime.now().strftime('%d-%m-%Y %H:%M:%S')

        last_seen_datetime = datetime.strptime(last_seen_datetime_str, '%d-%m-%Y %H:%M:%S')

        last_seen_seconds = last_seen_datetime.timestamp()
        
        last_seen = last_seen_seconds
        
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
    def __init__(self, width=640, height=360, fps=200, duration_seconds=10, output_dir='recordings'):
        self.width = width
        self.height = height
        self.requested_fps = fps # Store the requested FPS
        self.duration_seconds = duration_seconds
        self.output_dir = output_dir
        
        # Thread-safe queue for frames
        self.frame_queue = queue.Queue(maxsize=1024)  # Increased queue size for better buffering
        
        # Threading events
        self.stop_event = threading.Event()
        
        # Performance tracking
        self.frames_written = 0
        self.dropped_frames = 0
        self.actual_fps = 0 # To be determined by the camera

    def Stop(self):
        """Signals the recording threads to stop."""
        self.stop_event.set()
        
    def setup_camera(self):
        """Initializes the camera and sets its properties."""
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Error: Could not open camera.")
            return None, 0
        if Interrupt_:
            self.Stop()
            return None, 0
        # Set desired properties
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        cap.set(cv2.CAP_PROP_FPS, self.requested_fps)
        
        # --- KEY CHANGE: Get the ACTUAL parameters the camera settled on ---
        self.width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.actual_fps = cap.get(cv2.CAP_PROP_FPS)

        # Handle cases where camera returns 0 for FPS
        if self.actual_fps == 0:
            print("Warning: Camera reported 0 FPS. Defaulting to 30 FPS.")
            self.actual_fps = 30.0

        print(f"Camera Initialized:")
        print(f"  Requested: {self.requested_fps} FPS")
        print(f"  Actual:    {self.actual_fps:.2f} FPS")
        print(f"  Resolution: {self.width}x{self.height}")
        
        return cap

    def capture_frames(self, cap):
        """Capture frames from the camera and put them in the queue."""
        frames_to_capture = int(self.actual_fps * self.duration_seconds)
        
        while not self.stop_event.is_set() and Interrupt_ != True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Couldn't read frame. Stopping capture.")
                break
            
            try:
                # Add frame to queue if there's space, otherwise drop it
                self.frame_queue.put_nowait(frame)
            except queue.Full:
                self.dropped_frames += 1

            # --- ROBUSTNESS IMPROVEMENT: Stop after enough frames are captured ---
            # This is more reliable than time.sleep()
            if self.frames_written >= frames_to_capture:
                self.stop_event.set()
        
        cap.release()
        print("Capture thread finished.")

    def write_frames(self, out):
        """Get frames from the queue and write them to the video file."""
        while not self.stop_event.is_set() or not self.frame_queue.empty():
            try:
                frame = self.frame_queue.get(timeout=1) # Wait up to 1 sec for a frame
                out.write(frame)
                self.frames_written += 1
                self.frame_queue.task_done()
            except queue.Empty:
                # If the queue is empty and the stop signal is set, we can exit
                if self.stop_event.is_set() or Interrupt_:
                    break
                continue
            except Exception as e:
                print(f"Error in writer thread: {e}")
                break
        
        out.release()
        print("Writer thread finished.")

    def record_video(self):
        """Main method to orchestrate the video recording process."""
        self.stop_event.clear()
        self.frame_queue = queue.Queue(maxsize=1024) # Reset queue
        self.frames_written = 0
        self.dropped_frames = 0

        os.makedirs(self.output_dir, exist_ok=True)
        
        cap = self.setup_camera()
        if not cap:
            return

        # Define video codec and create VideoWriter object
        timestamp = datetime.now().strftime("%d-%m-%Y_%H%M%S")
        output_file = os.path.join(self.output_dir, f'recording_{timestamp}.mp4')
        fourcc = cv2.VideoWriter_fourcc(*'mp4v') # 'mp4v' is a good choice for .mp4

        # --- KEY FIX: Use the ACTUAL FPS for the VideoWriter ---
        out = cv2.VideoWriter(output_file, fourcc, self.actual_fps, (self.width, self.height))

        if not out.isOpened():
            print("Error: Could not open VideoWriter.")
            cap.release()
            return
            
        start_time = time.time()
        
        if Interrupt_:
            self.Stop()
            return
        # Start the capture and writer threads
        capture_thread = threading.Thread(target=self.capture_frames, args=(cap,))
        writer_thread = threading.Thread(target=self.write_frames, args=(out,))
        
        capture_thread.start()
        writer_thread.start()
        
        # Wait for threads to complete (they will self-terminate based on stop_event)
        capture_thread.join()
        writer_thread.join()
        
        elapsed_time = time.time() - start_time
        
        print(f"\n--- Recording Finished ---")
        print(f"  Saved to: {output_file}")
        print(f"  Target Duration: {self.duration_seconds:.2f} seconds")
        print(f"  Actual Duration: {elapsed_time:.2f} seconds")
        print(f"  Frames Written: {self.frames_written}")
        print(f"  Dropped Frames: {self.dropped_frames}")
        if elapsed_time > 0:
            effective_fps = self.frames_written / elapsed_time
            print(f"  Effective Average FPS: {effective_fps:.2f}")

        Interrupt()
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

    global Interrupt_

    global IRState

    def __init__(self):
        
        self.RFID_SER = None


    def INIT_RFID(self):
        
        self.RFID_SER = Get_usb_devices(RFID_USB_SERIAL_IDENTIFICATION_STRING)

        if self.RFID_SER == None:

            self.RFID_SER = '/dev/ttyUSB0'


    def Thread_ir_check(self):      

        global Interrupt_, IRState,IRBreakerPin
        try:
            while True:
                if GPIO.input(IRBreakerPin) == GPIO.HIGH:
                    IRState = False
                    Interrupt_ = True
                    #print("\nBeam OPEN, NO SUBJECT!\n")
                else:
                    IRState = True
                    Interrupt_ = False
                    #print("\nBeam Closed\n")
    
                time.sleep(3)  
        except Exception as e:
            print(f"Error reading IR breaker: {str(e)}")
            return False


        

        
    def quick_ir_check_V2(self):
        global Interrupt_, IRState,IRBreakerPin
        try:
            while GPIO.input(IRBreakerPin) == GPIO.HIGH:
                IRState = False
                Interrupt_ = True
            else:
                print("MOUSE IN!")
                IRState = True
                Interrupt_ = False
                return True
            time.sleep(1)  
        except Exception as e:
            print(f"Error reading IR breaker: {str(e)}")
            return False




    async def READTAG(self):

        global RFID_TAG_RAW

        RFID_TAG_RAW = None

        reader = RFIDReader(port=self.RFID_SER)

        print(self.RFID_SER)



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
    
 ___  ____  __      __    ___  ____    _   _    __    ___  ____    __      
/ __)(_  _)(  )    /__\  / __)(_  _)  ( )_( )  /__\  / __)(  _ \  /__\     
\__ \ _)(_  )(__  /(__)\ \__ \ _)(_    ) _ (  /(__)\ \__ \ )   / /(__)\    
(___/(____)(____)(__)(__)(___/(____)  (_) (_)(__)(__)(___/(_)\_)(__)(__)   
    
    """)

def open_folder(folder_path):

    if os.path.exists(folder_path):

        subprocess.run(["xdg-open", folder_path])

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


    return

def Get_usb_devices(device_search):

    serial_finder = SerialDeviceFinder()

    device_serial_conn = None
    #print(f"Method A was called by: {get_caller_method()}")

    if device_search == None:

        print(f"Cannont Search For NoneType Device!: {device_search}")

        time.sleep(5)

        return device_serial_conn

    try:

        device_serial_conn = serial_finder.get_tty_serial_to_port_conn(device_search)

        print(f"Found device: {device_search} under the serial: {device_serial_conn}")



    except Exception as e:

        print(f"Looking For{device_search}. \nError during Connection Search : {e}")

        time.sleep(5)

        return device_serial_conn

    finally:

        return device_serial_conn

def wait_for_mouse(RFID_TAG_RAW,peripheral_instance = None):

    global Interrupt_
    global IRState
    

    
    
    print("Waiting for mouse...")
    if peripheral_instance == None:

        peripheral_instance = Periphals()
        IRState = peripheral_instance.quick_ir_check_V2()
    

    RFID_TF = None
    
    if IRState != False:
         print("\nBeam Broken, Checking for MOUSE ID....\n")
         while RFID_TF == None:
            print("\nWaiting For Tag")
            RFID_TF = async_to_sync(peripheral_instance.READTAG)()
         else:
            print(f"RFID - {RFID_TAG_RAW}")
            return True
    
    return False

@async_to_sync
async def present_pellet(self, CurrentMouseID, NUM_TRIALS_PER_MOUSE, periphals_instance, Trail_Number, PIEZO_DIR,StepperManager_):
    global RECORDING_DIR
    global THRESHOLD_EXCEEDED
    global IRState
    global Interrupt_
    
    periphals_instance = Periphals()

    print(f"IRSate={IRState}")
    while not Interrupt_:
        
        print("EXTEND")
        periphals_instance.extend_actuator()
        await asyncio.sleep(3)
        if Interrupt_:
            StepperManager_.home_motors()
            time.sleep(1)
            return False
        print("RETRACT")
        periphals_instance.retract_actuator()
        await asyncio.sleep(1.5)
        periphals_instance.stop_actuator()
        
        #Start recording
        threads = []
        print("Starting camera recording...")
        print(f"Recording to: {RECORDING_DIR}")

        # Start recording threads
        recorder = VideoRecorder(duration_seconds=10, fps=320, output_dir=RECORDING_DIR)
        PiezoRecorder_ = PiezoRecorder()
        
        camera_completed = threading.Event()
        piezo_completed = threading.Event()
        if Interrupt_:
            StepperManager_.home_motors()
            time.sleep(1)
            return False
        def camera_thread_function():
            try:
                recorder.record_video()
            finally:
                camera_completed.set()
        
        def piezo_thread_function():
            try:
                PiezoRecorder_.Record_PelletData(CurrentMouseID, Trail_Number, PIEZO_DIR, recorder,StepperManager_)
            finally:
                #PiezoRecorder_.close() #vanilla python
                piezo_completed.set()
        
        Camera_thread = threading.Thread(target=camera_thread_function, name="Camera_Thread")
        Pizeo_thread = threading.Thread(target=piezo_thread_function, name="Piezo_Thread")
        
        Camera_thread.start()
        Pizeo_thread.start()
        
        start_recording_time = time.time()
        max_recording_duration = MAX_RECORDING_TIME_MIN * 60 # Convert minutes to seconds
        
        while not Interrupt_:
            #time.sleep(0.2)
            if THRESHOLD_EXCEEDED.is_set():
                print("Threshold exceeded, initiating graceful shutdown...")
                recorder.Stop()
                PiezoRecorder_.STOP()
                break # Exit the monitoring loop
        
            if (time.time() - start_recording_time) >= max_recording_duration:
                print("Maximum recording time reached, stopping recording.")
                recorder.Stop()
                PiezoRecorder_.STOP()
                break # Exit the monitoring loop
        
            if camera_completed.is_set() or piezo_completed.is_set():
                print("Both recording threads completed naturally.")
                break # Exit the monitoring loop
        
            await asyncio.sleep(0.5) # Non-blocking wait
        
        # Ensure all threads are joined before proceeding
        for thread in [Camera_thread,Pizeo_thread]:
            thread.join(timeout=10.0) # Give threads a bit more time to finish cleanly
            if thread.is_alive():
                print(f"Warning: {thread.name} did not terminate gracefully after stop signal.")
        
        periphals_instance.stop_actuator()
        THRESHOLD_EXCEEDED.clear()
            
        if PiezoRecorder_:
           del PiezoRecorder_
        return True
    else:
        StepperManager_.home_motors()
        time.sleep(1)
        
        if 'ser' in locals() and ser.is_open:
    
                ser.close()
        if PiezoRecorder_:
            del PiezoRecorder_
        return False
def main(SingleTrackedData,Mouse_Dir,periphals_instance):

    global RECORDING_DIR,NUM_TRIALS_PER_MOUSE,Interrupt_

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


    PIEZO_DIR = os.path.join(Mouse_Dir, "Piezo_Recordings")
    if Interrupt_:
            return False


    while not Interrupt_:

        trial_start = time.time()

        max_duration = MAX_RECORDING_TIME_MIN * 60

        completed = False

        interrupted = False

        print("Homing motors...")

        StepperManager_.home_motors()

        time.sleep(1.1)


        # Move to stage home coordinates

        print("Moving to stage Test position...")

        StepperManager_.step_motor(StepperA_STEP_PIN, StepperA_DIR_PIN, StepperA_enable, True, X_HOME_POS)

        StepperManager_.step_motor(StepperB_STEP_PIN, StepperB_DIR_PIN, StepperB_enable, True, Y_HOME_POS)

        time.sleep(1)

        while trials_completed_today < NUM_TRIALS_PER_MOUSE:
          if Interrupt_:
              StepperManager_.home_motors()
              time.sleep(1.1)
              print("IR beam broken, suspending test.")
              return trials_completed_today
          # Present pellet

          print("Presenting pellet...")
          if Interrupt_:
              StepperManager_.home_motors()
              time.sleep(1.1)
              return trials_completed_today
          if (present_pellet(RFID_TAG_RAW, NUM_TRIALS_PER_MOUSE, ProfileID,periphals_instance,trials_completed_today,PIEZO_DIR,StepperManager_)):

              print("Saving")

              completed = True

              interrupted = False

              trials_completed_today += 1

              trial_end = time.time()

              trial_duration = trial_end - trial_start

              new_trail_element = Trail_Element(trials_completed_today, trial_duration, completed, interrupted, RFID_TAG_RAW)

              Trail_Elements.append(new_trail_element)
            
              print("Iteration_Complete")


          else:

              if Interrupt_ :

                print("IR BREAK")
                StepperManager_.home_motors()

                time.sleep(1.1)
                

              print("Sequence Failed")

              completed = False

              interrupted = True

              trials_completed_today += 1

              trial_end = time.time()

              trial_duration = trial_end - trial_start

              new_trail_element = Trail_Element(trials_completed_today, trial_duration, completed, interrupted, RFID_TAG_RAW)

              Trail_Elements.append(new_trail_element)

              break

          # Wait between iterations

          time.sleep(2)

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

          time.sleep(0.5)

          #Interrupt()

          tracker.update_tracking(RFID_TAG_RAW,trials_completed_today, trial_duration)

          return trials_completed_today

            

        
    else:

      print("MOUSE LEFT!")
      print("Homing motors...")

      StepperManager_.home_motors()

      return trials_completed_today

async def save_session_data():



    print(f"Saving data to {SAVE_DATA_PATH}")

    return True

def get_caller_method():
    
    frame = inspect.currentframe()
    try:
        caller_frame = frame.f_back.f_back
        if caller_frame is None:
            return "No caller method (called from module level)"
        
        caller_method = caller_frame.f_code.co_name
        return caller_method
    finally:
        del frame

def run_system(tracker):

    admin_Open = False

    time.sleep(0.2)

    display_welcome_banner()

    global Interrupt_

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

    periphals_instance.INIT_RFID()
     
    Current_Mouse.tracker = tracker

    led = IRLedControl()

    led.off()

    # Start the IR breaker checking thread
    #ir_thread = threading.Thread(target=check_ir_breaker)periphals_instance.Thread_ir_check
    ir_thread = threading.Thread(target=periphals_instance.Thread_ir_check)
    ir_thread.daemon = True
    ir_thread.start()

    while True:
        while IRState == True:
    
              global RFID_TAG_RAW
              global mouse_id
              
              RFID_TAG_RAW = None
              mouse_id = None
              
              if wait_for_mouse(RFID_TAG_RAW,periphals_instance):
                    
                  mouse_id = None
                  mouse_id = RFID_TAG_RAW 
                  
                  if mouse_id == None:
                    break
                  
                  led.on()
    
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
    
              #if Current_Mouse.last_seen == str(datetime.now().strftime("%d-%m-%Y")):
    
              while not Interrupt_:
        
                    if Current_Mouse.trial_count < NUM_TRIALS_PER_MOUSE and Current_Mouse.test_time < MAX_DAILY_TIME_MIN:
        
                        trials_completed = main(Current_Mouse,MOUSE_DIR,periphals_instance)
        
                        print(f"Trails{trials_completed}")
        
                        if trials_completed >= 0:
        
                            tracker.update_tracking(RFID_TAG_RAW,Current_Mouse.trail_num_total , Current_Mouse.total_trail_time)
        
                        time.sleep(2)
        
                        print(f"\nMouse ID {mouse_id} has completed attempts, restarting.")
        
                        led.off()
        
                        break
        
                    else:
        
                        led.off()
        
                        print(f"\nMouse ID {mouse_id} has exceeded daily trials or test time.")
        
                        print(f"\nRechecking in 10 Seconds For another mouse Without the ID {mouse_id}\n\n\n")                
        
                        break
        
              else:
                    
                    led.off()
                    StepperManager_.home_motors()

                    time.sleep(1.1)
                    print(f"\n\nMouse ID {mouse_id} Interrupted")
    
                    print(f"\nRechecking in 10 Seconds For another mouse Without the ID {mouse_id}\n\n\n")
    
    
                    time.sleep(10)
                    led.off()

                    break
            
        else:
            
          print(f"\n\Waiting For Mouse")
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

            time.sleep(0.1) 

            return key_check.key_pressed

    else:  

        import select

        rlist, _, _ = select.select([sys.stdin], [], [], 0)

        return bool(rlist)

if __name__ == "__main__":

    tracker = GlobalMouseTracker()

    tracker.load_config()

    setup(tracker)

    run_system(tracker)
