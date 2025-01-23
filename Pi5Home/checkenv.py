import time
import gpiozero

# Configurable pin definitions
STEP_PIN = 20
DIRECTION_PIN = 21

# Configurable motor parameters
TOTAL_STEPS = 200
PULSE_WIDTH = 0.05  # seconds
STEP_DELAY = 0.1   # seconds
one_rot = 200
l = 1 * one_rot
delay = 30/(2*float(l))
steps = l/6 #rotato to 5 sec
def setup_stepper_motor(step_pin, direction_pin):

   
    # Set up GPIO pins
    step_pin_device = gpiozero.OutputDevice(step_pin)
    direction_pin_device = gpiozero.OutputDevice(direction_pin)
    
    # Reset pins to initial state
    step_pin_device.off()
    direction_pin_device.off()
    
    return step_pin_device, direction_pin_device

def move_stepper(step_pin, direction_pin, total_steps, direction, pulse_width, step_delay):
    """
    
    Args:
        step_pin (gpiozero.OutputDevice): Step control pin
        direction_pin (gpiozero.OutputDevice): Direction control pin
        total_steps (int): Number of steps to move
        direction (bool): True for forward, False for backward
        pulse_width (float): Duration of step pulse
        step_delay (float): Delay between steps
    """
    # Set direction
    direction_pin.on() if direction else direction_pin.off()
    
    # Determine direction string for printing
    direction_str = "forward" if direction else "backward"
    print(f"Moving {direction_str}")
    
    # Execute step sequence
    for current_step in range(total_steps):
        # Generate step pulse
        step_pin.on()
        time.sleep(pulse_width)  # Pulse width
        step_pin.off()
        
        # Delay between steps
        time.sleep(step_delay)
        
        # Print current step progress
        print(f"{direction_str.capitalize()} step: {current_step + 1}/{total_steps}", end='\r')
    
    print(f"\n{direction_str.capitalize()} movement complete")

def main(step_pin_num=STEP_PIN, 
         direction_pin_num=DIRECTION_PIN, 
         total_steps=TOTAL_STEPS,
         pulse_width=PULSE_WIDTH,
         step_delay=STEP_DELAY):
    
    try:
        # Set up motor pins
        step_pin, direction_pin = setup_stepper_motor(step_pin_num, direction_pin_num)
        
        while True:
            # Move forward
            move_stepper(step_pin, direction_pin, total_steps, True, pulse_width, step_delay)
            
            # Pause between direction changes
            time.sleep(0.5)
            
            # Move backward
            move_stepper(step_pin, direction_pin, total_steps, False, pulse_width, step_delay)
            
            # Pause between direction changes
            time.sleep(0.5)
    
    except KeyboardInterrupt:
        # Clean up GPIO pins when the program is interrupted
        step_pin.off()
        direction_pin.off()
        print("\nStepper motor control stopped")

# Allow direct running of the script
if __name__ == "__main__":
    main()
