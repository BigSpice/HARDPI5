# REQUIRED



# RPi.GPIO

# SPI   ON



from time import sleep

from enum import Enum

import sys

import time

from datetime import datetime

import os



global CurrentMouseID, NumberOfTests, StartupTime, MiceEvaluated, SessionID, ProfileID, MaxTestTime, MinTestTime, ArmHoldWaitingTime, RFID_PORT, ARDUINO_PORT,CurrentMouseTagRFID





def install_package(package_name):

    """

    Check if a package is installed, and install it if it isn't.



    Args:

        package_name (str): Name of the package to install



    Returns:

        bool: True if package is/was installed successfully, False otherwise

    """

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





except ImportError:

    # List of required packages

    required_packages = ["RPi.GPIO", "asyncio", "asgiref", "serial"]



    # Install each required package

    for package in required_packages:

        install_package(package)





class VideoRecorder:

    def __init__(self, width=640, height=360, fps=200, duration_seconds=10, output_dir='recordings'):



        self.width = width

        self.height = height

        self.fps = fps

        self.duration_seconds = duration_seconds

        self.output_dir = output_dir



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

    

    

    def home_motors():

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

        

    def generate_session_id(mouse_id, test_number, date=None):

        if date is None:

            date = datetime.now()

        year_digit = str(date.year)[-1]

        test_letter = chr(64 + test_number) if test_number <= 26 else 'Z'

        day_digit = str(((date.day - 1) % 9) + 1)

        month_digit = str(((date.month - 1) % 9) + 1)

        mouse_digit = str(mouse_id)[-1]

        session_id = f"{year_digit}{test_letter}{month_digit}{day_digit}{mouse_digit}"

        return session_id

    def check_ir_breaker():

        try:

            # GPIO.input returns 1 if beam is intact, 0 if broken

            #  invert it so True means the beam is broken

            return not bool(GPIO.input(IRBreakerPin))

        except Exception as e:

            print(f"Error reading IR breaker: {str(e)}")

            return False

            

    def READTAG():

        reader = RFIDReader(port='/dev/ttyUSB1')

        if reader.connect():

            tag_id = reader.read_tag_id()

            if tag_id:

                print(f"Single read - Tag ID: {tag_id}")

                return tag_id

                # reader.Endless_print_tag_id()    

            

    def extend_actuator():

        GPIO.output(relay1, GPIO.HIGH)

        GPIO.output(relay2, GPIO.LOW)

    

    

    def retract_actuator():

        GPIO.output(relay1, GPIO.LOW)

        GPIO.output(relay2, GPIO.HIGH)

    

    

    def stop_actuator():

        GPIO.output(relay1, GPIO.HIGH)

        GPIO.output(relay2, GPIO.HIGH)

    

    

    

    

    

    def test_actuator_cycle():

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





# Configuration Constants

STEPS_PER_REV = 200

StepperA_enable = 4

StepperB_enable = 22



home_switch1 = 13

home_switch2 = 19



DISTANCE = 3200  # Total number of steps to move

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



# Camera settings

CAMERA_RESOLUTION = (640, 480)

CAMERA_FRAMERATE = 100

RECORDING_DURATION = 8  # seconds

SEQUENCE_ITERATIONS = 5

IRState = False

ProfileID = " -Defualt"

# Recording directory

RECORDING_DIR = "recordings"

os.makedirs(RECORDING_DIR, exist_ok=True)





def setup():

    """Initialize GPIO settings"""

    GPIO.setmode(GPIO.BCM)



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



    Periphals.extend_actuator()

@async_to_sync

async def present_pellet(CurrentMouseID,NumberOfTests,ProfileID):

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

        output_dir = RECORDING_DIR+CurrentMouseID + Periphals.generate_session_id(CurrentMouseID, NumberOfTests, datetime.now()) + ProfileID

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



    print("MOUSE LEFT")

    Periphals.extend_actuator()

    

def automated_sequence(CurrentMouseID,NumberOfTests,ProfileID):

    """Execute the full automated sequence"""

    try:



        # First home both motors

        print("Homing motors...")

        StepperManager.home_motors()

        sleep(1)



        # Move to stage home coordinates

        print("Moving to stage home position...")

        StepperManager.step_motor(StepperA_STEP_PIN, StepperA_DIR_PIN, StepperA_enable, True, STAGE_HOME_A)

        StepperManager.step_motor(StepperB_STEP_PIN, StepperB_DIR_PIN, StepperB_enable, True, STAGE_HOME_B)

        sleep(1)

        

        # Repeat sequence 5 times

        for iteration in range(5):

            print(f"Starting iteration {iteration + 1}/5")

            # Present pellet

            print("Presenting pellet...")

            present_pellet(CurrentMouseID,NumberOfTests,ProfileID)

            # Wait between iterations

            sleep(2)



        # Return to home position

        print("Returning to home position...")

        StepperManager.home_motors()



        # Clean up

        print("Sequence completed successfully")

    

    except Exception as e:

        print(f"Error during sequence: {e}")

        

def quick_ir_check():

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

def main_loop():

    """Main loop"""

    try:

        IRState = False

         #startIR Check

        while IRState == False:  # Note: changed != to == to wait for non-empty

            IRState = quick_ir_check()

            time.sleep(0.5) 

        CurrentMouseTagRFID = ''

        while CurrentMouseTagRFID == '':  # Note: changed != to == to wait for non-empty

            CurrentMouseTagRFID = Periphals.READTAG()

            time.sleep(0.5)  

        print(f"Got MOUSE TAG: {CurrentMouseTagRFID} \n\nStarting!\n\n")

        CurrentMouseID = CurrentMouseTagRFID#Temporary, create method to compare the ID value to Known mouse var

        NumberOfTests = 1 #readnuberofmice tests here

        Periphals.generate_session_id(CurrentMouseID, NumberOfTests, datetime.now())

        while True:

            print("\nCurrent Status:")

            print(f"home_switch1 --> {GPIO.input(home_switch1)}")

            print(f"home_switch2 --> {GPIO.input(home_switch2)}")

            print("\nCommands:")

            print("a - Move Stepper A forward")

            print("b - Move Stepper A backward")

            print("c - Move Stepper B forward")

            print("d - Move Stepper B backward")

            print("r - Run HASRA 2024 STEPPER TEST")

            print("s - Run Automated Sequence")

            print("h - Home motors")

            print("o - Test Actuator")

            print("q - Quit")



            



            char = input("Enter command: ").lower()



            if char == 'a':

                 StepperManager.step_motor(StepperA_STEP_PIN, StepperA_DIR_PIN, StepperA_enable, True, 100)

            elif char == 'b':

                 StepperManager.step_motor(StepperA_STEP_PIN, StepperA_DIR_PIN, StepperA_enable, False, 100)

            elif char == 'c':

                 StepperManager.step_motor(StepperB_STEP_PIN, StepperB_DIR_PIN, StepperB_enable, True, 100)

            elif char == 'd':

                 StepperManager.step_motor(StepperB_STEP_PIN, StepperB_DIR_PIN, StepperB_enable, False, 100)

            elif char == 'r':

                # HASRA 2024 STEPPER TEST sequence

                print("HASRA 2024 STEPPER TEST")

                for _ in range(8):

                     StepperManager.step_motor(StepperB_STEP_PIN, StepperB_DIR_PIN, StepperB_enable, True, 100)

                for _ in range(8):

                     StepperManager.step_motor(StepperA_STEP_PIN, StepperA_DIR_PIN, StepperA_enable, True, 100)

                Periphals.present_pellet()

            elif char == 's':

                print("Starting Automated Sequence...")

                automated_sequence(CurrentMouseID,NumberOfTests,ProfileID)

            elif char == 'h':

                 StepperManager.home_motors()

            elif char == 'o':

                Periphals.test_actuator_cycle()

                # async_to_sync(present_pellet())

            elif char == 'q':

                print("Quitting program...")

                break

            else:

                print("Invalid command")



            sleep(0.4)  # Main loop delay



    except KeyboardInterrupt:

        GPIO.cleanup()

        print("\nProgram terminated by user")

    except Exception as e:

        print(f"Error: {e}")

        GPIO.cleanup()

    finally:

        GPIO.cleanup()





if __name__ == "__main__":

    try:

        setup()

        main_loop()

    finally:

        GPIO.cleanup()

