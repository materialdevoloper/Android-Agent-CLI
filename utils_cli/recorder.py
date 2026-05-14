import os
import sys
import time
import subprocess
import threading

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import adb_core

class ScreenRecorder:
    def __init__(self, output_dir="output", filename="record.mp4"):
        self.output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), output_dir)
        os.makedirs(self.output_dir, exist_ok=True)
        self.local_filepath = os.path.join(self.output_dir, filename)
        self.device_filepath = f"/data/local/tmp/{filename}"
        self.process = None

    def start(self):
        """Start recording screen on the device."""
        print(f"Starting screen recording on device: {self.device_filepath}")
        cmd = [
            adb_core.ADB_PATH,
            "-s", adb_core.DEVICE_ID,
            "shell", f"screenrecord {self.device_filepath}"
        ]
        self.process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("Recording started in background.")

    def stop(self):
        """Stop recording and pull the file."""
        print("Stopping screen recording...")
        if self.process:
            # Kill the screenrecord process safely with SIGINT (2)
            adb_core.run_adb("shell pkill -2 screenrecord")
            
            # Wait for adb to finish gracefully (up to 10s) instead of terminating
            try:
                self.process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                print("Warning: screenrecord did not exit cleanly, forcing terminate.")
                self.process.terminate()
            
            # Give device a tiny bit of time to flush the file to storage
            time.sleep(2)
            
            print(f"Pulling video to {self.local_filepath}...")
            adb_core.run_adb(f"pull {self.device_filepath} {self.local_filepath}")
            adb_core.run_adb(f"shell rm {self.device_filepath}")
            print(f"Video saved to {self.local_filepath}")
        else:
            print("No recording process found.")

if __name__ == "__main__":
    # Test script
    recorder = ScreenRecorder(filename="test_recording.mp4")
    recorder.start()
    print("Doing some fake work for 10 seconds to ensure a valid video...")
    for i in range(10):
        adb_core.run_adb("shell input swipe 540 1800 540 400")
        time.sleep(1)
    recorder.stop()
