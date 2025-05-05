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





    import configparser



    import select



    import csv

except ImportError:



    # List of required packages



    required_packages = ["rpi-lgpio","aiofiles","aiocsv", "asyncio", "asgiref", "pyserial", "configparser"]







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

        self.data_queue = queue.Queue(maxsize=900000)  # Buffer up to 10,000 data points

        self.writer_thread = None

        self.running = False

        self.file_path = None

        self.BOOL = True



        

    def create_directory(self, base_path, mouse_var, test_number):

        date = str(datetime.now().strftime("%d-%m-%Y"))

        dir_path = os.path.join(base_path, mouse_var, f"Piezo Data-{date}- Test Number - {test_number}")

        os.makedirs(dir_path, exist_ok=True)

        return dir_path

    

    def get_file_path(self, dir_path, mouse_var, start_time):

        timestamp = start_time.strftime("%H-%M")

        mouse_var = str(mouse_var)

        return os.path.join(dir_path, f"Piezo{str(timestamp)}"+f"-MOUSE:{mouse_var}.csv")

    

    def format_timestamp(self, elapsed_seconds):

        minutes = int(elapsed_seconds // 60)

        seconds = int(elapsed_seconds % 60)

        milliseconds = int((elapsed_seconds * 1000) % 1000)

        return f"{minutes:02d}:{seconds:02d}:{milliseconds:03d}"

    

    def write_header(self, file_path):

        with open(file_path, 'w', newline='') as f:

            writer = csv.writer(f)

            writer.writerow(["Time Minutes", "Data", "HIT CHECK"])

    

    def append_data(self, timestamp, data_out, is_hit):

        hit_status = "HIT" if is_hit else "NO"

        self.data_queue.put([timestamp, f"{data_out:.2f}", hit_status])



    def Stop(self):
        
        self.running = False
        THRESHOLD_EXCEEDED.clear() 

    async def write_data(self, batch):
        if batch and self.file_path:
            async with aiofiles.open(self.file_path, mode='a', newline='') as file:
                writer = aiocsv.AsyncWriter(file)  # No async with
                await writer.writerows(batch)  # Await writing data   

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

   


        

    def Record_PelletData(self, MOUSEID, test_number, base_path, Cam_Thread):

       

        global Interrupt_

        global THRESHOLD_EXCEEDED
        
        global USE_PEZO_TRIGGER
        
        HOLD_DATA = 0.0
        USE_PEZO_TRIGGER = False
        try:

            # Setup serial connection

            ser = serial.Serial(self.SERIAL_PORT, self.BAUD_RATE, timeout=1)

            ser.reset_input_buffer()

            

            # Create directory and file

            dir_path = self.create_directory(str(base_path), str(MOUSEID), str(test_number))

            start_time = datetime.now()

            self.file_path = self.get_file_path(dir_path, MOUSEID, start_time)

            

            # Write header if new file

            if not os.path.exists(self.file_path):

                self.write_header(self.file_path)

            

            # Start writer thread

            self.running = True

            self.writer_thread = threading.Thread(target=self.writer_task)

            self.writer_thread.daemon = True

            self.writer_thread.start()
            
            THRESHOLD_EXCEEDED.clear()

            while self.running == True:

                if ser.in_waiting > 0:

                    line = ser.readline().rstrip()

                    try:

                        time.sleep(0.5)

                        elapsed_time = (datetime.now() - start_time).total_seconds()

                        timestamp = self.format_timestamp(elapsed_time)
                        
                        Data_Out = float(line)

                        is_hit = Data_Out > self.THRESHOLD
                        
                        self.append_data(timestamp, Data_Out, is_hit)
                        
                        if is_hit and USE_PEZO_TRIGGER == True:
                            HOLD_DATA = Data_Out
                            THRESHOLD_EXCEEDED.set()
                            Data_Out = 0.0
                            is_hit = Data_Out
                            #Cam_Thread.STOP()
                            self.STOP()
                            break
                            
                        if elapsed_time > MAX_RECORDING_TIME_MIN:
                            break

                    except ValueError as e:

                        print(f"Error parsing data: {e}")

                    except Exception as e:

                        print(f"Unexpected error: {e}")

            else:

                print(f"Test Suspended: {HOLD_DATA:.2f}")
                
                self.running = False

                if self.writer_thread and self.writer_thread.is_alive():
    
                    self.writer_thread.join(timeout=2.0)  
                
    
                remaining_data = []
    
                while not self.data_queue.empty():
    
                    try:
    
                        remaining_data.append(self.data_queue.get_nowait())
    
                        self.data_queue.task_done()
    
                    except queue.Empty:
    
                        break
    
                
                
    
                asyncio.run(self.write_data(batch))
 
                        
                        
                if 'ser' in locals() and ser.is_open:
    
                    ser.close()
    
                    print("Serial port closed")


                        

        except serial.SerialException as e:

            print(f"Serial port error: {e}")

        except KeyboardInterrupt:

            pass

        finally:


            self.running = False

            if self.writer_thread and self.writer_thread.is_alive():

                self.writer_thread.join(timeout=2.0)  

            
            remaining_data = []

            while not self.data_queue.empty():

                try:

                    remaining_data.append(self.data_queue.get_nowait())

                    self.data_queue.task_done()

                except queue.Empty:

                    break

            


            asyncio.run(self.write_data(remaining_data))


            
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
        try:
            if os.path.exists(TRACKING_FILE):
    
                with open(TRACKING_FILE, 'r') as f