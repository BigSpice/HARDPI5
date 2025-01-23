import cv2
import time
import os
from threading import Thread
from datetime import datetime

class WebcamStream:
    def __init__(self, stream_id=0, record_fps=100, record_folder='recordings'):
        self.stream_id = stream_id   # default is 0 for primary camera 
        
        # Create recordings folder if it doesn't exist
        self.record_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), record_folder)
        os.makedirs(self.record_folder, exist_ok=True)
        
        # Set recording parameters
        self.record_fps = record_fps
        self.is_recording = False
        self.video_writer = None
        
        # opening video capture stream 
        self.vcap = cv2.VideoCapture(self.stream_id)
        if self.vcap.isOpened() is False:
            print("[Exiting]: Error accessing webcam stream.")
            exit(0)
        
        # Get input stream FPS
        fps_input_stream = int(self.vcap.get(cv2.CAP_PROP_FPS))
        print(f"FPS of webcam hardware/input stream: {fps_input_stream}")
        
        # Get video capture properties
        self.width = int(self.vcap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.vcap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # reading a single frame from vcap stream for initializing 
        self.grabbed, self.frame = self.vcap.read()
        if self.grabbed is False:
            print('[Exiting] No more frames to read')
            exit(0)
        
        # self.stopped is set to False when frames are being read from self.vcap stream 
        self.stopped = True 
        
        # reference to the thread for reading next available frame from input stream 
        self.t = Thread(target=self.update, args=())
        self.t.daemon = True # daemon threads keep running in the background while the program is executing 
        
    def start(self):
        self.stopped = False
        self.t.start() 
    
    def update(self):
        while True:
            if self.stopped is True:
                break
            self.grabbed, self.frame = self.vcap.read()
            if self.grabbed is False:
                print('[Exiting] No more frames to read')
                self.stopped = True
                break 
        self.vcap.release()
    
    def read(self):
        return self.frame
    
    def stop(self):
        self.stopped = True 
        if self.video_writer:
            self.video_writer.release()
    
    def start_recording(self):
        # Generate unique filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = os.path.join(self.record_folder, f'recording_{timestamp}.avi')
        
        # Define the codec and create VideoWriter object
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.video_writer = cv2.VideoWriter(
            output_filename, 
            fourcc, 
            self.record_fps, 
            (self.width, self.height)
        )
        self.is_recording = True
        print(f"Started recording to {output_filename}")
    
    def stop_recording(self):
        if self.video_writer:
            self.video_writer.release()
            self.is_recording = False
            print("Stopped recording")
    
    def write_frame(self, frame):
        if self.is_recording and self.video_writer:
            self.video_writer.write(frame)

# Main execution
def main():
    # initializing and starting multi-threaded webcam capture input stream 
    webcam_stream = WebcamStream(stream_id=0, record_fps=30)  # stream_id = 0 is for primary camera 
    webcam_stream.start()
    
    # processing frames in input stream
    num_frames_processed = 0 
    start = time.time()
    
    try:
        while True:
            if webcam_stream.stopped is True:
                break
            else:
                frame = webcam_stream.read() 
            
            # Display frame
            cv2.imshow('frame', frame)
            
            # Handle key presses
            key = cv2.waitKey(1)
            
            # Start recording when 'r' is pressed
            if key == ord('r'):
                webcam_stream.start_recording()
            
            # Stop recording when 's' is pressed
            elif key == ord('s'):
                webcam_stream.stop_recording()
            
            # Write frame if recording
            if webcam_stream.is_recording:
                webcam_stream.write_frame(frame)
            
            # Quit when 'q' is pressed
            if key == ord('q'):
                break
            
            num_frames_processed += 1
            
            # Control frame rate (optional)
            time.sleep(1/30)  # 30 FPS
    
    finally:
        # Cleanup
        webcam_stream.stop()
        cv2.destroyAllWindows()
    
    # Calculate and print performance metrics
    end = time.time()
    elapsed = end - start
    fps = num_frames_processed / elapsed 
    print(f"FPS: {fps}, Elapsed Time: {elapsed}, Frames Processed: {num_frames_processed}")

if __name__ == "__main__":
    main()
