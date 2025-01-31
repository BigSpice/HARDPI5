import cv2
import time
from datetime import datetime
import os
import threading
import queue
#Final
class VideoRecorder:
    def __init__(self, width=640, height=360, fps=200, duration_seconds=10, output_dir='recordings'):
       

        self.width = width
        self.height = height
        self.fps = fps
        self.duration_seconds = duration_seconds
        self.output_dir = output_dir
        
        # Thread-safe queue for frames
        self.frame_queue = queue.Queue(maxsize=3000)  # Limit queue size to prevent memory issues
        
        # Threading flags and events
        self.is_recording = threading.Event()
        self.stop_event = threading.Event()
        
        # Performance tracking
        self.frame_count = 0
        self.dropped_frames = 0

    def setup_camera(self):
        cap = cv2.VideoCapture(0)  # 0 is usually the first USB camera
        
        # Set resolution
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        
        # Set FPS
        cap.set(cv2.CAP_PROP_FPS, self.fps)
        
        # Check actual parameters achieved
        actual_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        actual_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        actual_fps = cap.get(cv2.CAP_PROP_FPS)
        
        print(f"Requested settings: {self.width}x{self.height} at {self.fps}fps")
        print(f"Actual settings: {actual_width}x{actual_height} at {actual_fps}fps")
        
        return cap

    def capture_frames(self, cap):
        
        try:
            while not self.stop_event.is_set():
                ret, frame = cap.read()
                if not ret:
                    print("Error: Couldn't read frame")
                    break
                
                try:
                    if not self.frame_queue.full():
                        self.frame_queue.put_nowait(frame)
                        self.frame_count += 1

                    else:  
                        print(f"Dropped at {self.frame_count} in capture thread.")
                        self.dropped_frames += 1
                except queue.Full:
                    self.dropped_frames += 1
                    print(f"Dropped at {self.frame_count} in Queu Full.")

        
        except Exception as e:
            print(f"Error in capture thread: {e}")
        
        finally:
            self.is_recording.clear()
            cap.release()

    def write_frames(self, out):
       
        try:
            while not self.stop_event.is_set() or not self.frame_queue.empty():
                try:
                    frame = self.frame_queue.get(timeout=1)
                    out.write(frame)
                except queue.Empty:
                    continue
        
        except Exception as e:
            print(f"Error in writer thread: {e}")
        
        finally:
            out.release()

    def record_video(self):
 
        os.makedirs(self.output_dir, exist_ok=True)
    
        cap = self.setup_camera()
        
        if not cap.isOpened():
            print("Error: Could not open camera")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(self.output_dir, f'recording_{timestamp}.mp4')
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_file, fourcc, self.fps, (self.width, self.height))
        self.frame_count = 0
        self.dropped_frames = 0
        start_time = time.time()
        self.is_recording.clear()
        self.stop_event.clear()
        
        try:
            capture_thread = threading.Thread(target=self.capture_frames, args=(cap,))
            writer_thread = threading.Thread(target=self.write_frames, args=(out,))
            writer_thread.start()
            capture_thread.start()
            time.sleep(self.duration_seconds)
            self.stop_event.set()
            capture_thread.join()
            writer_thread.join()
        
        except KeyboardInterrupt:
            print("\nRecording stopped by user")
        
        finally:
            elapsed_time = time.time() - start_time
            average_fps = self.frame_count / elapsed_time
            
            print(f"\nRecording finished:")
            print(f"Saved to: {output_file}")
            print(f"Average FPS: {average_fps:.2f}")
            print(f"Total frames captured: {self.frame_count}")
            print(f"Dropped frames: {self.dropped_frames}")
            print(f"Duration: {elapsed_time:.2f} seconds")

def main():
    recorder = VideoRecorder(duration_seconds=10, fps=320)
    recorder.record_video()

if __name__ == "__main__":
    main()
