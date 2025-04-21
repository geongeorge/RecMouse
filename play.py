import os
from pynput.mouse import Button, Controller
import rumps
import json
import time
from pathlib import Path
import sys

def get_app_data_path():
    """Get the application data directory path."""
    # Use Application Support on macOS
    app_support = Path.home() / "Library" / "Application Support" / "RecMouse"
    app_support.mkdir(parents=True, exist_ok=True)
    return app_support

class MousePlayer:
    def __init__(self):
        self.mouse = Controller()
        # Use Application Support directory for storing recordings
        self.recording_file = get_app_data_path() / "recording.json"

    def play_recording(self, repeat_count=1):
        if not self.recording_file.exists():
            error_msg = f"No recording found at {self.recording_file}"
            print(f"Error: {error_msg}")  # Debug logging
            rumps.notification("Error", "No Recording", error_msg)
            return False

        try:
            with open(self.recording_file, 'r') as f:
                events = json.load(f)
        except json.JSONDecodeError as e:
            error_msg = f"Invalid recording format: {str(e)}"
            print(f"Error: {error_msg}")  # Debug logging
            rumps.notification("Error", "Invalid Recording", error_msg)
            return False
        except Exception as e:
            error_msg = f"Failed to read recording: {str(e)}"
            print(f"Error: {error_msg}")  # Debug logging
            rumps.notification("Error", "Read Error", error_msg)
            return False

        if not events:
            rumps.notification("Error", "Empty Recording", "Please record something.")
            return False

        try:
            print(f"Starting playback of {len(events)} events")  # Debug logging
            for i in range(repeat_count):
                # Get the initial time
                start_time = time.time()
                last_event_time = 0

                for event in events:
                    # Wait for the appropriate time
                    current_time = time.time() - start_time
                    wait_time = event['time'] - last_event_time
                    if wait_time > 0:
                        time.sleep(wait_time)

                    # Execute the event
                    if event['type'] == 'move':
                        self.mouse.position = (event['x'], event['y'])
                    elif event['type'] == 'click':
                        self.mouse.position = (event['x'], event['y'])
                        button = Button.left if 'left' in event['button'].lower() else Button.right
                        if event['pressed']:
                            self.mouse.press(button)
                        else:
                            self.mouse.release(button)

                    last_event_time = event['time']
                
                # Add a small delay between repetitions
                if repeat_count > 1 and i < repeat_count - 1:
                    time.sleep(0.5)

            print("Playback completed successfully")  # Debug logging
            return True

        except Exception as e:
            error_msg = f"Playback error: {str(e)}"
            print(f"Error: {error_msg}")  # Debug logging
            rumps.notification("Error", "Playback Error", error_msg)
            return False

if __name__ == "__main__":
    player = MousePlayer()
    try:
        player.play_recording()
    except KeyboardInterrupt:
        rumps.notification("Info", "Playback terminated by user.", "") 