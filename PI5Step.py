#REQUIRED 

#RPi.GPIO
# SPI   ON

from time import sleep
from enum import Enum
import sys
import subprocess
import importlib.util

try:
    import RPi.GPIO as GPIO
except ImportError:
 # List of required packages
    required_packages = ["RPi.GPIO"]
    
    # Install each required package
    for package in required_packages:
        install_package(package)


class Stepper(Enum):
    STP_A = 1  # STEPPER A#fix
    STP_B = 2  # STEPPER B#fix


# Configuration Constants
STEPS_PER_REV = 200  # fix
StepperA_enable = 24  # 9 white, 11 black#fix
StepperB_enable = 25  # 10 white, 9 black#fix

home_switch1 = 8  # fix
home_switch2 = 7  # fix

DISTANCE = 3200  # Total number of steps to move#fix
StepperA_STEP_PIN = 17  # Changed to match Arduino pin 3#fix
StepperB_STEP_PIN = 23  # Changed to match Arduino pin 5#fix

StepperA_DIR_PIN = 27  # Changed to match Arduino pin 2#fix
StepperB_DIR_PIN = 22  # Changed to match Arduino pin 4#fix

# PELLET ARM MOTOR PINS
relay1 = 6 # Arduino pin that triggers relay #1#fix
relay2 = 5 # Arduino pin that triggers relay #2#fix
IRBreakerPin = 26  # fix
IRState = False



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

    # Initialize enable pins
    GPIO.output(StepperA_enable, GPIO.HIGH)
    GPIO.output(StepperB_enable, GPIO.HIGH)


def extend_actuator():
    GPIO.output(relay1, GPIO.HIGH)
    GPIO.output(relay2, GPIO.LOW)


def retract_actuator():
    GPIO.output(relay1, GPIO.LOW)
    GPIO.output(relay2, GPIO.HIGH)


def stop_actuator():
    GPIO.output(relay1, GPIO.HIGH)
    GPIO.output(relay2, GPIO.HIGH)


def present_pellet():
    """Handle pellet presentation sequence"""
    while GPIO.input(IRBreakerPin) == GPIO.LOW:  # while mouse IN
        print("EXTEND")
        extend_actuator()
        sleep(5)

        print("RETRACT")
        retract_actuator()
        sleep(1.3)

        print("STOP")
        stop_actuator()
        sleep(5)  # Simplified from AnalogAsync

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
    # Home motor 1
    GPIO.output(StepperA_enable, GPIO.LOW)
    GPIO.output(StepperA_DIR_PIN, GPIO.LOW)

    while GPIO.input(home_switch2) == GPIO.HIGH:
        GPIO.output(StepperA_STEP_PIN, GPIO.HIGH)
        sleep(0.001)
        GPIO.output(StepperA_STEP_PIN, GPIO.LOW)
        sleep(0.001)

    GPIO.output(StepperA_enable, GPIO.HIGH)
    sleep(1)

    # Home motor 2
    GPIO.output(StepperB_enable, GPIO.LOW)
    GPIO.output(StepperB_DIR_PIN, GPIO.LOW)

    while GPIO.input(home_switch1) == GPIO.HIGH:
        GPIO.output(StepperB_STEP_PIN, GPIO.HIGH)
        sleep(0.001)
        GPIO.output(StepperB_STEP_PIN, GPIO.LOW)
        sleep(0.001)

    GPIO.output(StepperB_enable, GPIO.HIGH)


def main_loop():
    """Main loop"""
    try:
        while True:
            print(f"home_switch1 --> {GPIO.input(home_switch1)}")
            print(f"home_switch2 --> {GPIO.input(home_switch2)}")

            if GPIO.input(IRBreakerPin) == GPIO.HIGH:
                print("MOUSE LEFT")
                IRState = False
            else:
                print("MOUSE IN")
                IRState = True

                char = sys.stdin.read(1)

                if char == 'b':
                    step_motor(StepperA_STEP_PIN, StepperA_DIR_PIN, StepperA_enable, True, 100)
                elif char == 'a':
                    step_motor(StepperA_STEP_PIN, StepperA_DIR_PIN, StepperA_enable, False, 100)
                elif char == 'd':
                    step_motor(StepperB_STEP_PIN, StepperB_DIR_PIN, StepperB_enable, True, 100)
                elif char == 'c':
                    step_motor(StepperB_STEP_PIN, StepperB_DIR_PIN, StepperB_enable, False, 100)
                elif char == 'i':
                    # HASRA 2024 STEPPER TEST sequence
                    print("HASRA 2024 STEPPER TEST")
                    for _ in range(8):
                        step_motor(StepperB_STEP_PIN, StepperB_DIR_PIN, StepperB_enable, True, 100)
                    for _ in range(8):
                        step_motor(StepperA_STEP_PIN, StepperA_DIR_PIN, StepperA_enable, True, 100)
                    present_pellet()
                else:
                    home_motors()

            sleep(0.4)  # Main loop delay

    except KeyboardInterrupt:
        GPIO.cleanup()
        print("\nProgram terminated by user")
    except Exception as e:
        print(f"Error: {e}")
        GPIO.cleanup()


if __name__ == "__main__":
    try:
        setup()
        main_loop()
    finally:
        GPIO.cleanup()
