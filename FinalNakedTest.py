#!/usr/bin/env python3
import serial
from time import sleep
import os
from datetime import datetime
import time
import csv

def create_directory(mouse_var, test_number):
    """Create directory structure if it doesn't exist"""
    base_path = os.path.join(os.path.expanduser('~'), 'PiezoTests')
    dir_path = os.path.join(base_path, mouse_var, f"Piezo-{test_number}-")
    os.makedirs(dir_path, exist_ok=True)
    return dir_path

def get_file_path(dir_path, mouse_var, start_time):
    """Generate file path with timestamp"""
    timestamp = start_time.strftime("%Y%m%d%H%M")
    return os.path.join(dir_path, f"Piezo{timestamp}"+f"-MOUSE:{mouse_var}.csv")  # Added .csv extension

def format_timestamp(elapsed_seconds):
    """Format elapsed time as minutes:seconds:milliseconds"""
    minutes = int(elapsed_seconds // 60)
    seconds = int(elapsed_seconds % 60)
    milliseconds = int((elapsed_seconds * 1000) % 1000)
    return f"{minutes:02d}:{seconds:02d}:{milliseconds:03d}"

def write_header(file_path):
    """Write CSV headers to the file"""
    with open(file_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Time Minutes", "Data", "HIT CHECK"])

def append_data(file_path, timestamp, data_out, is_hit):
    """Append data row to CSV file"""
    hit_status = "HIT" if is_hit else "NO"
    with open(file_path, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, f"{data_out:.2f}", hit_status])

def Record_PelletData(mouse_var,test_number):
    # Configuration
    SERIAL_PORT = '/dev/ttyUSB0'
    BAUD_RATE = 500000
    THRESHOLD = 1.20
    
    # Get user input
    mouse_var = str(mouse_var)
    test_number = str(test_number)
    
    try:
        # Setup serial connection
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        ser.reset_input_buffer()
        
        # Create directory and file
        dir_path = create_directory(mouse_var, test_number)
        start_time = datetime.now()
        file_path = get_file_path(dir_path, mouse_var, start_time)
        
        # Write header if new file
        if not os.path.exists(file_path):
            write_header(file_path)
        
        print(f"Recording data to: {file_path}")
        print("Press Ctrl+C to stop recording")
        
        while True:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8').rstrip()
                
                try:
                    Data_Out = float(line)
                    elapsed_time = (datetime.now() - start_time).total_seconds()
                    timestamp = format_timestamp(elapsed_time)
                    is_hit = Data_Out > THRESHOLD
                    
                    # Print to console
                    print(f"Time: {timestamp}, Data: {Data_Out:.2f}, {'HIT!!!' if is_hit else 'NO'}")
                    
                    # Write to CSV file
                    append_data(file_path, timestamp, Data_Out, is_hit)
                    
                    if is_hit:
                        Data_Out = 0.0
                        sleep(0.5)
                        
                except ValueError as e:
                    print(f"Error parsing data: {e}")
                except Exception as e:
                    print(f"Unexpected error: {e}")
                    
    except serial.SerialException as e:
        print(f"Serial port error: {e}")
    except KeyboardInterrupt:
        # Add recording duration to filename
        elapsed_time = (datetime.now() - start_time).total_seconds()
        base, ext = os.path.splitext(file_path)
        new_file_path = f"{base}_{int(elapsed_time)}s{ext}"
        os.rename(file_path, new_file_path)
        print(f"Data saved to: {new_file_path}")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("Serial port closed")

if __name__ == '__main__':
    Record_PelletData(1,2)
