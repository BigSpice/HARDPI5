

import easydriver as ed


# Direction of rotation is dependent on how the motor is connected.
# If the motor runs the wrong way swap the values of cw and ccw.
cw = True
ccw = False

"""
Arguments to pass or set up after creating the instance.

Step GPIO pin number.
Delay between step pulses in seconds.
Direction GPIO pin number.
Microstep 1 GPIO pin number.
Microstep 2 GPIO pin number.
Microstep 3 GPIO pin number.
Sleep GPIO pin number.
Enable GPIO pin number.
Reset GPIO pin number.
Name as a string.
"""

# Create an instance of the easydriver class.
# Not using sleep, enable or reset in this example.
stepper = ed.easydriver(23, 0.001, 24, 21, 17, 25)

# Set motor direction to clockwise.
stepper.set_direction(cw)

# Set the motor to run in 1/8 of a step per pulse.
stepper.set_full_step()

# Do some steps.
for i in range(0,5200):
    print("forward")

    stepper.step()

# Clean up (just calls GPIO.cleanup() function.)
stepper.finish()
