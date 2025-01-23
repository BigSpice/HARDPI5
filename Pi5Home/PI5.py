# REQUIRED

# RPi.GPIO
# SPI   ON

from time import sleep
from enum import Enum
import sys
import subprocess
import importlib.util
import cv2
import time
from datetime import datetime
import os

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

except ImportError:
    # List of required packages
    required_packages = ["RPi.GPIO","asyncio","asgiref","serial"]

    # Install each required package
    for package in required_packages:
        install_package(package)


class Stepper(Enum):
    STP_A = 1  # STEPPER A#fix
    STP_B = 2  # STEPPER B#fix


# Configuration Constants
STEPS_PER_REV = 200  # fix
StepperA_enable = 4  # 9 white, 11 black#fix
StepperB_enable = 22  # 10 white, 9 black#fix

home_switch1 = 13  # fix
home_switch2 = 19  # fix

DISTANCE = 3200  # Total number of steps to move#fix
StepperA_STEP_PIN = 2  # Changed to match Arduino pin 3#fix
StepperB_STEP_PIN = 17  # Changed to match Arduino pin 5#fix

StepperA_DIR_PIN = 3  # Changed to match Arduino pin 2#fix
StepperB_DIR_PIN = 27  # Changed to match Arduino pin 4#fix

# PELLET ARM MOTOR PINS
relay1 = 16  # Arduino pin that triggers relay #1#fix
relay2 = 21  # Arduino pin that triggers relay #2#fix
IRBreakerPin = 26  # fix
IRState = False
PiezoPin = 6
# Stage home coordinates (you can adjust these values based on your needs)
STAGE_HOME_A = 600  # Steps from home position for motor A
STAGE_HOME_B = 500  # Steps from home position for motor B

# Camera settings
CAMERA_RESOLUTION = (640, 480)
CAMERA_FRAMERATE = 100
RECORDING_DURATION = 8  # seconds
SEQUENCE_ITERATIONS = 5

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

    extend_actuator()
    
def extend_actuator():
    GPIO.output(relay1, GPIO.HIGH)
    GPIO.output(relay2, GPIO.LOW)


def retract_actuator():
    GPIO.output(relay1, GPIO.LOW)
    GPIO.output(relay2, GPIO.HIGH)


def stop_actuator():
    GPIO.output(relay1, GPIO.HIGH)
    GPIO.output(relay2, GPIO.HIGH)

@async_to_sync
async def present_pellet():
    """Handle pellet presentation sequence"""
    cnn = 0
    while cnn != 2:
    #while GPIO.input(IRBreakerPin) == GPIO.LOW:  # while mouse IN
        print("EXTEND")
        extend_actuator()
        await asyncio.sleep(3)        
        print("RETRACT")
        retract_actuator()
        await asyncio.sleep(1.3)
        stop_actuator()
        await asyncio.sleep(1.3)

        # Start recording
        print("Starting camera recording...")
        t1 = threading.Thread(record_video(duration_seconds=10))
        t1.start()
        print(f"Recording to: {RECORDING_DIR}")
       # t2 = threading.Thread(Read_Piezo())
       # t2.start()
        await asyncio.sleep(10)

            
        print("STOP")
        stop_actuator()
        t1.join()
        #t2.join()
        await asyncio.sleep(3)
        cnn += 1
        
    print("MOUSE LEFT")
    extend_actuator()


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



def setup_camera(width=640, height=480, fps=120):
    """Initialize camera with specified parameters."""
    cap = cv2.VideoCapture(0)  # 0 is usually the first USB camera
    
    # Set resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    
    # Set FPS
    cap.set(cv2.CAP_PROP_FPS, fps)
    
    # Check actual parameters achieved
    actual_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    actual_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    actual_fps = cap.get(cv2.CAP_PROP_FPS)
    
    print(f"Requested settings: {width}x{height} at {fps}fps")
    print(f"Actual settings: {actual_width}x{actual_height} at {actual_fps}fps")
    
    return cap

def record_video(duration_seconds=10, output_dir='recordings'):
    """Record video for specified duration."""
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize camera
    cap = setup_camera()
    
    if not cap.isOpened():
        print("Error: Could not open camera")
        return
    
    # Get camera parameters
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    # Create output filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_dir, f'recording_{timestamp}.avi')
    
    # Initialize video writer
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(output_file, fourcc, fps, (width, height))
    
    # Variables for FPS calculation
    frame_count = 0
    start_time = time.time()
    
    try:
        while (time.time() - start_time) < duration_seconds:
            ret, frame = cap.read()
            if not ret:
                print("Error: Couldn't read frame")
                break
                
            # Write frame
            out.write(frame)
            frame_count += 1
            
            # Calculate and display current FPS
            if frame_count % 30 == 0:  # Update FPS every 30 frames
                current_fps = frame_count / (time.time() - start_time)
                print(f"\rCurrent FPS: {current_fps:.2f}", end='')
    
    except KeyboardInterrupt:
        print("\nRecording stopped by user")
    
    finally:
        # Clean up
        out.release()
        cap.release()
        
        # Final FPS calculation
        elapsed_time = time.time() - start_time
        average_fps = frame_count / elapsed_time
        print(f"\nRecording finished:")
        print(f"Saved to: {output_file}")
        print(f"Average FPS: {average_fps:.2f}")
        print(f"Total frames: {frame_count}")
        print(f"Duration: {elapsed_time:.2f} seconds")


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

def automated_sequence():
    """Execute the full automated sequence"""
    try:

        # First home both motors
        print("Homing motors...")
        home_motors()
        sleep(1)

        # Move to stage home coordinates
        print("Moving to stage home position...")
        step_motor(StepperA_STEP_PIN, StepperA_DIR_PIN, StepperA_enable, True, STAGE_HOME_A)
        step_motor(StepperB_STEP_PIN, StepperB_DIR_PIN, StepperB_enable, True, STAGE_HOME_B)
        sleep(1)

        # Repeat sequence 5 times
        for iteration in range(5):
            print(f"Starting iteration {iteration + 1}/5")

            # Present pellet
            print("Presenting pellet...")
            present_pellet()

            # Start recording
            # print("Starting camera recording...")
            #t1 = threading.Thread(record_video(duration_seconds=10))
            #t1.start()
            #print(f"Recording to: {RECORDING_DIR}")

            # Record for 8 seconds
            #sleep(10)

            # Drop pellet hand
            #print("Retracting actuator...")
            #retract_actuator()
            #sleep(1.3)
            #stop_actuator()

            # Stop recording
            #print("Recording stopped")

            # Wait between iterations
            sleep(2)

        # Return to home position
        print("Returning to home position...")
        home_motors()

        # Clean up
        print("Sequence completed successfully")

    except Exception as e:
        print(f"Error during sequence: {e}")
        # Ensure camera is properly closed in case of error
     


def main_loop():
    """Main loop"""
    try:
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

            if GPIO.input(IRBreakerPin) == GPIO.HIGH:
                print("MOUSE LEFT")
                IRState = False
            else:
                print("MOUSE IN")
                IRState = True

            char = input("Enter command: ").lower()

            if char == 'a':
                step_motor(StepperA_STEP_PIN, StepperA_DIR_PIN, StepperA_enable, True, 100)
            elif char == 'b':
                step_motor(StepperA_STEP_PIN, StepperA_DIR_PIN, StepperA_enable, False, 100)
            elif char == 'c':
                step_motor(StepperB_STEP_PIN, StepperB_DIR_PIN, StepperB_enable, True, 100)
            elif char == 'd':
                step_motor(StepperB_STEP_PIN, StepperB_DIR_PIN, StepperB_enable, False, 100)
            elif char == 'r':
                # HASRA 2024 STEPPER TEST sequence
                print("HASRA 2024 STEPPER TEST")
                for _ in range(8):
                    step_motor(StepperB_STEP_PIN, StepperB_DIR_PIN, StepperB_enable, True, 100)
                for _ in range(8):
                    step_motor(StepperA_STEP_PIN, StepperA_DIR_PIN, StepperA_enable, True, 100)
                present_pellet()
            elif char == 's':
                print("Starting Automated Sequence...")
                automated_sequence()
            elif char == 'h':
                home_motors()
            elif char == 'o':
                test_actuator_cycle()
                #async_to_sync(present_pellet())
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
