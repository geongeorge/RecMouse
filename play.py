import os
from pynput.mouse import Button, Controller
import rumps
import json
import time
from pathlib import Path
import sys
import logging
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
        logging.error(f"Error checking accessibility permissions: {e}")
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
        logging.info(f"MousePlayer initialized with recording file: {self.recording_file}")

    def play_recording(self, repeat_count=1):
        logging.info("Starting play_recording...")
        
        if not self.recording_file.exists():
            logging.warning(f"Recording file not found at: {self.recording_file}")
            return False, "No recording found. Please record something first."

        try:
            logging.info(f"Reading recording file: {self.recording_file}")
            with open(self.recording_file, 'r') as f:
                events = json.load(f)
                logging.info(f"Successfully loaded {len(events)} events")
        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse recording file: {e}")
            return False, "The recording file is corrupted or invalid."
        except Exception as e:
            logging.error(f"Error reading recording file: {e}")
            return False, f"Failed to read recording: {str(e)}"

        if not events:
            logging.warning("No events found in recording")
            return False, "The recording is empty. Please record something first."

        try:
            logging.info(f"Starting playback of {len(events)} events")
            for i in range(repeat_count):
                logging.info(f"Starting playback iteration {i+1}/{repeat_count}")
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
                            logging.debug(f"Moving mouse to {event['x']}, {event['y']}")
                            self.mouse.position = (event['x'], event['y'])
                        elif event['type'] == 'click':
                            logging.info(f"Click event at {event['x']}, {event['y']}, button: {event['button']}, pressed: {event['pressed']}")
                            self.mouse.position = (event['x'], event['y'])
                            button = Button.left if 'left' in event['button'].lower() else Button.right
                            if event['pressed']:
                                self.mouse.press(button)
                            else:
                                self.mouse.release(button)

                        last_event_time = event['time']
                    except Exception as e:
                        logging.error(f"Error during event playback: {str(e)}, event: {event}")
                        continue  # Try to continue with next event
                
                logging.info(f"Completed iteration {i+1}/{repeat_count}")
                # Add a small delay between repetitions
                if repeat_count > 1 and i < repeat_count - 1:
                    time.sleep(0.5)

            logging.info("Playback completed successfully")
            return True, None

        except Exception as e:
            error_msg = f"Playback error: {str(e)}"
            logging.error(error_msg)
            return False, error_msg

if __name__ == "__main__":
    player = MousePlayer()
    try:
        player.play_recording()
    except KeyboardInterrupt:
        rumps.notification("Info", "Playback terminated by user.", "") 