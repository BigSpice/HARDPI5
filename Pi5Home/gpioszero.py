#!/usr/bin/python
# -*- coding: utf-8 -*-
from gpiozero import OutputDevice
import time

class EasyDriver:
    def __init__(self, pin_step=None, delay=0.1, pin_direction=None, 
                 pin_ms1=None, pin_ms2=None, pin_ms3=None, 
                 pin_sleep=None, pin_enable=None, pin_reset=None, 
                 name="Stepper"):
        """
        Initialize the EasyDriver stepper motor control.
        
        :param pin_step: GPIO pin number for step control
        :param delay: Delay between step pulses (default 0.1 seconds)
        :param pin_direction: GPIO pin number for direction control
        :param pin_ms1: GPIO pin number for microstep mode 1
        :param pin_ms2: GPIO pin number for microstep mode 2
        :param pin_ms3: GPIO pin number for microstep mode 3
        :param pin_sleep: GPIO pin number for sleep mode
        :param pin_enable: GPIO pin number for motor enable
        :param pin_reset: GPIO pin number for motor reset
        :param name: Optional name for the stepper motor
        """
        self.name = name
        self.delay = delay / 2
        
        # Initialize GPIO pins using gpiozero OutputDevice
        self.step_pin = OutputDevice(pin_step) if pin_step is not None else None
        self.direction_pin = OutputDevice(pin_direction) if pin_direction is not None else None
        
        # Microstep mode pins
        self.ms1_pin = OutputDevice(pin_ms1) if pin_ms1 is not None else None
        self.ms2_pin = OutputDevice(pin_ms2) if pin_ms2 is not None else None
        self.ms3_pin = OutputDevice(pin_ms3) if pin_ms3 is not None else None
        
        # Additional control pins
        self.sleep_pin = OutputDevice(pin_sleep) if pin_sleep is not None else None
        self.enable_pin = OutputDevice(pin_enable) if pin_enable is not None else None
        self.reset_pin = OutputDevice(pin_reset) if pin_reset is not None else None
        
        # Set initial states
        if self.direction_pin:
            self.direction_pin.on()  # Default direction
        
        # Set default microstep mode (full step)
        self.set_full_step()
        
        # Wake and enable the motor by default
        if self.sleep_pin:
            self.wake()
        if self.enable_pin:
            self.enable()
        if self.reset_pin:
            self.reset()
    
    def step(self):
        """
        Perform a single step of the stepper motor.
        """
        if not self.step_pin:
            raise RuntimeError("Step pin not configured")
        
        self.step_pin.on()
        time.sleep(self.delay)
        self.step_pin.off()
        time.sleep(self.delay)
    
    def set_direction(self, direction):
        """
        Set the direction of rotation.
        
        :param direction: True for one direction, False for the other
        """
        if not self.direction_pin:
            raise RuntimeError("Direction pin not configured")
        
        self.direction_pin.value = direction
    
    def set_full_step(self):
        """
        Set the motor to full step mode.
        """
        self._set_microstep_mode(False, False, False)
    
    def set_half_step(self):
        """
        Set the motor to half step mode.
        """
        self._set_microstep_mode(True, False, False)
    
    def set_quarter_step(self):
        """
        Set the motor to quarter step mode.
        """
        self._set_microstep_mode(False, True, False)
    
    def set_eighth_step(self):
        """
        Set the motor to eighth step mode.
        """
        self._set_microstep_mode(True, True, False)
    
    def set_sixteenth_step(self):
        """
        Set the motor to sixteenth step mode.
        """
        self._set_microstep_mode(True, True, True)
    
    def _set_microstep_mode(self, ms1, ms2, ms3):
        """
        Internal method to set microstep mode.
        
        :param ms1: State of MS1 pin
        :param ms2: State of MS2 pin
        :param ms3: State of MS3 pin
        """
        if not all([self.ms1_pin, self.ms2_pin, self.ms3_pin]):
            raise RuntimeError("Microstep pins not fully configured")
        
        self.ms1_pin.value = ms1
        self.ms2_pin.value = ms2
        self.ms3_pin.value = ms3
    
    def sleep(self):
        """
        Put the motor into sleep mode.
        """
        if not self.sleep_pin:
            raise RuntimeError("Sleep pin not configured")
        
        self.sleep_pin.off()
    
    def wake(self):
        """
        Wake the motor from sleep mode.
        """
        if not self.sleep_pin:
            raise RuntimeError("Sleep pin not configured")
        
        self.sleep_pin.on()
    
    def disable(self):
        """
        Disable the motor driver.
        """
        if not self.enable_pin:
            raise RuntimeError("Enable pin not configured")
        
        self.enable_pin.on()
    
    def enable(self):
        """
        Enable the motor driver.
        """
        if not self.enable_pin:
            raise RuntimeError("Enable pin not configured")
        
        self.enable_pin.off()
    
    def reset(self):
        """
        Reset the motor driver.
        """
        if not self.reset_pin:
            raise RuntimeError("Reset pin not configured")
        
        self.reset_pin.off()
        time.sleep(1)
        self.reset_pin.on()
    
    def set_delay(self, delay):
        """
        Set the delay between step pulses.
        
        :param delay: New delay value
        """
        self.delay = delay / 2

# Example usage:
if __name__ == "__main__":
    # Example initialization (adjust pin numbers as needed)
    stepper = EasyDriver(
        pin_step=20,       # GPIO pin for step
        pin_direction=21,  # GPIO pin for direction
        pin_ms1=25,        # GPIO pin for MS1
        pin_ms2=8,        # GPIO pin for MS2
        pin_ms3=7,        # GPIO pin for MS3
        pin_sleep=1,      # GPIO pin for sleep
        pin_enable=23,     # GPIO pin for enable
        pin_reset=24        # GPIO pin for reset
    )
    
    # Example of using the stepper motor
    try:
        # Set direction
        stepper.set_direction(True)
        
        # Set microstep mode
        stepper.set_full_step()
        
        # Perform 200 steps (typical for a stepper motor)
        for _ in range(2000):
            stepper.step()
            print("stepping")
    
    except KeyboardInterrupt:
        print("Stepper motor operation stopped")
