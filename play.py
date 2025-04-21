import os
from pynput.mouse import Button, Controller
import rumps
import json
import time
from pathlib import Path
import sys
from ApplicationServices import (
    AXIsProcessTrustedWithOptions,
)
from CoreFoundation import (
    CFStringCreateWithCString,
    CFDictionaryCreate,
    kCFStringEncodingUTF8,
    kCFBooleanTrue,
    kCFTypeDictionaryKeyCallBacks,
    kCFTypeDictionaryValueCallBacks,
)

def check_accessibility_permissions(prompt=True):
    """Check if the app has accessibility permissions.
    
    Args:
        prompt (bool): If True, show the system permission dialog if needed
    """
    try:
        if prompt:
            # Create options dictionary to show prompt
            options_key = CFStringCreateWithCString(None, b"AXTrustedCheckOptionPrompt", kCFStringEncodingUTF8)
            options = CFDictionaryCreate(
                None,
                (options_key,),
                (kCFBooleanTrue,),
                1,
                kCFTypeDictionaryKeyCallBacks,
                kCFTypeDictionaryValueCallBacks,
            )
            return AXIsProcessTrustedWithOptions(options)
        else:
            return AXIsProcessTrustedWithOptions(None)
    except Exception as e:
        print(f"Error checking accessibility permissions: {e}")
        return False

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
        print("Starting play_recording...")  # Debug log
        
        if not self.recording_file.exists():
            print(f"Recording file not found at: {self.recording_file}")  # Debug log
            return False, "No recording found. Please record something first."

        try:
            print(f"Reading recording file: {self.recording_file}")  # Debug log
            with open(self.recording_file, 'r') as f:
                events = json.load(f)
                print(f"Successfully loaded {len(events)} events")  # Debug log
        except json.JSONDecodeError as e:
            print(f"Failed to parse recording file: {e}")  # Debug log
            return False, "The recording file is corrupted or invalid."
        except Exception as e:
            print(f"Error reading recording file: {e}")  # Debug log
            return False, f"Failed to read recording: {str(e)}"

        if not events:
            print("No events found in recording")  # Debug log
            return False, "The recording is empty. Please record something first."

        try:
            print(f"Starting playback of {len(events)} events")  # Debug logging
            for i in range(repeat_count):
                print(f"Starting playback iteration {i+1}/{repeat_count}")  # Debug log
                # Get the initial time
                start_time = time.time()
                last_event_time = 0

                for event in events:
                    try:
                        # Wait for the appropriate time
                        current_time = time.time() - start_time
                        wait_time = event['time'] - last_event_time
                        if wait_time > 0:
                            time.sleep(wait_time)

                        # Execute the event
                        if event['type'] == 'move':
                            print(f"Moving mouse to {event['x']}, {event['y']}")  # Debug log
                            self.mouse.position = (event['x'], event['y'])
                        elif event['type'] == 'click':
                            print(f"Click event at {event['x']}, {event['y']}, button: {event['button']}, pressed: {event['pressed']}")  # Debug log
                            self.mouse.position = (event['x'], event['y'])
                            button = Button.left if 'left' in event['button'].lower() else Button.right
                            if event['pressed']:
                                self.mouse.press(button)
                            else:
                                self.mouse.release(button)

                        last_event_time = event['time']
                    except Exception as e:
                        print(f"Error during event playback: {str(e)}, event: {event}")  # More detailed error logging
                        continue  # Try to continue with next event
                
                print(f"Completed iteration {i+1}/{repeat_count}")  # Debug log
                # Add a small delay between repetitions
                if repeat_count > 1 and i < repeat_count - 1:
                    time.sleep(0.5)

            print("Playback completed successfully")  # Debug logging
            return True, None

        except Exception as e:
            error_msg = f"Playback error: {str(e)}"
            print(f"Error: {error_msg}")  # Debug logging
            return False, error_msg

if __name__ == "__main__":
    player = MousePlayer()
    try:
        player.play_recording()
    except KeyboardInterrupt:
        rumps.notification("Info", "Playback terminated by user.", "") 