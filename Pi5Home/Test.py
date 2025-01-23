import RPi.GPIO as GPIO           # import RPi.GPIO module  
from time import sleep
number_of_steps = 3200 
step_delay = 60 / number_of_steps / 240

GPIO.setmode(GPIO.BCM)            # choose BCM or BOARD  
GPIO.setup(16, GPIO.OUT) # set a port/pin as an output   
GPIO.output(16, 1)       # set port/pin value to 1/GPIO.HIGH/True
sleep(1)
GPIO.output(16, 0)       # set port/pin value to 0/GPIO.LOW/False  
