import RPi.GPIO as GPIO  # Import Raspberry Pi GPIO library
from time import sleep   # Import sleep function for timing delays

# Configuration
DISTANCE = 3200        # Total number of steps to move
STEP_PIN = 20           # GPIO pin connected to the stepper motor step control
DIR_PIN = 21        # GPIO pin used to trigger stepping

def setup():
    """
    Initialize GPIO settings for the stepper motor control.
    
    This function:
    1. Sets the GPIO mode to BCM (Broadcom SOC channel)
    2. Sets up the step pin as an output
    3. Sets up the trigger pin as an input
    4. Ensures initial state is LOW (no step)
    """
    GPIO.setmode(GPIO.BCM)         # Use Broadcom pin numbering
    GPIO.setup(2, GPIO.OUT)  # Set step pin as output
    GPIO.setup(3, GPIO.OUT) # set a port/pin as an output   
    GPIO.setup(22, GPIO.OUT) # set a port/pin as an output   
    GPIO.setup(4, GPIO.OUT) 
    GPIO.output(3, 0)       # set port/pin value to 1/GPIO.HIGH/True

def step_motor():
    """
    Control the stepper motor stepping sequence.
    
    Mimics the original Arduino logic:
    1. Wait for trigger (low signal)
    2. Step the motor for a specified distance
    3. Reset when full distance is reached
    """
    step_counter = 0

    try:
        while True:
                GPIO.output(4, 1)

            # Check if trigger is activated (pulled low)
                # Pulse the step pin
                GPIO.output(2, 1)
                GPIO.output(3, 1)       # set port/pin value to 1/GPIO.HIGH/True

                sleep(0.008)  # Short delay equivalent to original delay(1)
                GPIO.output(2, 0)
                sleep(0.001)  # Short delay equivalent to original delay(1)

                GPIO.output(2, 1)

                GPIO.output(2, 0)
                GPIO.output(3, 0)       # set port/pin value to 1/GPIO.HIGH/True

                sleep(0.01)
                step_counter += 1
                print(step_counter)
                # Check if full distance is reached
                if step_counter == DISTANCE:
                    step_counter = 0
                    GPIO.output(22, 0)
                    GPIO.output(4, 0)       # set port/pin value to 1/GPIO.HIGH/True

                    break
                    
    except KeyboardInterrupt:
        # Clean up GPIO on keyboard interrupt
        GPIO.cleanup()
        GPIO.output(22, 0)
        GPIO.output(4, 0)       # set port/pin value to 1/GPIO.HIGH/True


def main():
    """
    Main function to set up and run the stepper motor control.
    """
    try:
        setup()

        step_motor()
    finally:
        # Ensure GPIO is cleaned up even if an error occurs
        GPIO.cleanup()
        GPIO.output(22, 0)
        GPIO.output(4, 0)  

if __name__ == "__main__":
    main()

# Note: 
# 1. This script requires running with sudo privileges on a Raspberry Pi
# 2. Ensure you have RPi.GPIO library installed (pip install RPi.GPIO)
# 3. Connect your stepper motor driver's step pin to GPIO 23
# 4. Connect the DIR pin to GPIO 24
