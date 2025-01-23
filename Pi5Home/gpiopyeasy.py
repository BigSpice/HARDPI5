#!/usr/bin/env python3
import serial
from time import sleep
if __name__ == '__main__':
    ser = serial.Serial('/dev/ttyUSB0', 2000000, timeout=1)
    ser.reset_input_buffer()

    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').rstrip()
            print(line)  
            try:
                Data_Out = float(line)
            except:
                Data_Out = 0.0
            if Data_Out > 2.00:
                print("Hit!!!")
                Data_Out = 0.0
                sleep(2)            
