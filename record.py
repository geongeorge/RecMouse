from pynput import mouse, keyboard
from time import time, sleep
import logging
from colorama import Fore, Style, init
import threading
import sys
import rumps
import json
from pathlib import Path
import os

# Initialize colorama
init()

def get_app_data_path():
    """Get the application data directory path."""
    # Use Application Support on macOS
    app_support = Path.home() / "Library" / "Application Support" / "RecMouse"
    app_support.mkdir(parents=True, exist_ok=True)
    return app_support

def setup_logging():
    """Configure logging to write to both file and console."""
    app_data = get_app_data_path()
    log_file = app_data / "recmouse.log"
    
    # Delete old log file if it exists
    try:
        if log_file.exists():
            log_file.unlink()
            logging.info(f"Deleted old log file")
    except Exception as e:
        print(f"Error deleting old log file: {e}")
    
    # Create a formatter that includes timestamps
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    
    # Set up file handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    
    # Set up console handler with color
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    logging.info(f"Logging initialized. Log file: {log_file}")
    logging.info(f"App data directory: {app_data}")

# Configure logging
setup_logging()

class StatusBarApp:
    def __init__(self):
        self.recorder = None
        self.is_recording = False
        logging.info("StatusBarApp initialized")

    def set_recording(self, is_recording):
        self.is_recording = is_recording
        logging.info(f"Recording state changed to: {is_recording}")

class MouseRecorder:
    def __init__(self, status_app):
        try:
            self.recording = []
            self.start_time = None
            self.mouse_listener = None
            self.last_move_time = 0  # For throttling move events
            self.move_throttle = 0.016  # ~60fps, adjust if needed
            # Use Application Support directory for storing recordings
            self.recording_file = get_app_data_path() / "recording.json"
            self.status_app = status_app
            self.status_app.recorder = self
            logging.info(f"MouseRecorder initialized")
            logging.info(f"Recording file path: {self.recording_file}")
            logging.info(f"Recording file exists: {self.recording_file.exists()}")
            if self.recording_file.exists():
                logging.info(f"Recording file permissions: {oct(self.recording_file.stat().st_mode)}")
        except Exception as e:
            logging.error(f"Error in MouseRecorder initialization: {e}", exc_info=True)
            raise

    def on_move(self, x, y):
        if self.start_time is None:
            return
        
        current_time = time() - self.start_time
        # Throttle movement events
        if current_time - self.last_move_time < self.move_throttle:
            return
            
        event = {
            'type': 'move',
            'x': x,
            'y': y,
            'time': current_time
        }
        self.recording.append(event)
        self.last_move_time = current_time
        logging.debug(f"Recorded move: {event}")  # Use debug level for move events

    def on_click(self, x, y, button, pressed):
        if self.start_time is None:
            return
            
        event = {
            'type': 'click',
            'x': x,
            'y': y,
            'button': str(button),
            'pressed': pressed,
            'time': time() - self.start_time
        }
        self.recording.append(event)
        logging.info(f"Recorded click: {event}")

    def start_recording(self):
        try:
            self.recording = []
            self.start_time = time()
            self.mouse_listener = mouse.Listener(
                on_move=self.on_move,
                on_click=self.on_click
            )
            self.mouse_listener.start()
            self.status_app.set_recording(True)
            logging.info("Recording started successfully")
        except Exception as e:
            error_msg = f"Failed to start recording: {str(e)}"
            logging.error(error_msg, exc_info=True)
            rumps.notification("Error", "Recording Error", error_msg)

    def stop_recording(self):
        if self.mouse_listener:
            try:
                self.mouse_listener.stop()
                self.mouse_listener = None
                self.start_time = None
                
                # Save recording to file
                logging.info(f"Saving recording to: {self.recording_file}")
                logging.info(f"Number of events: {len(self.recording)}")
                logging.info(f"Current working directory: {os.getcwd()}")
                
                # Ensure directory exists
                self.recording_file.parent.mkdir(parents=True, exist_ok=True)
                
                try:
                    with open(self.recording_file, 'w') as f:
                        json.dump(self.recording, f)
                    logging.info("Successfully saved recording")
                    logging.info(f"File size after save: {self.recording_file.stat().st_size} bytes")
                except Exception as e:
                    logging.error(f"Error writing to recording file: {e}", exc_info=True)
                    raise
                    
                self.status_app.set_recording(False)
                logging.info(f"Recording saved to {self.recording_file}")
            except Exception as e:
                error_msg = f"Failed to save recording: {str(e)}"
                logging.error(error_msg, exc_info=True)
                rumps.notification("Error", "Save Error", error_msg)

    def remove_last_seconds(self, seconds):
        if not self.recording:
            return
            
        # Get the time of the last event
        last_time = self.recording[-1]['time']
        cutoff_time = last_time - seconds
        
        # Find the index where we should cut
        cut_index = len(self.recording)
        for i in range(len(self.recording) - 1, -1, -1):
            if self.recording[i]['time'] <= cutoff_time:
                cut_index = i + 1
                break
        
        # Remove events only after the cutoff time
        self.recording = self.recording[:cut_index]
        logging.info(f"Removed events from last {seconds} seconds, remaining events: {len(self.recording)}")

    def remove_last_click(self):
        """Remove the last click events (both press and release) from recording."""
        if not self.recording:
            return
            
        # Find the last click events
        last_press_index = -1
        last_release_index = -1
        
        for i in range(len(self.recording) - 1, -1, -1):
            event = self.recording[i]
            if event['type'] == 'click':
                if event['pressed'] and last_press_index == -1:
                    last_press_index = i
                elif not event['pressed'] and last_release_index == -1:
                    last_release_index = i
                if last_press_index != -1 and last_release_index != -1:
                    break
        
        # If we found both press and release, remove them and any moves in between
        if last_press_index != -1 and last_release_index != -1:
            start_index = min(last_press_index, last_release_index)
            end_index = max(last_press_index, last_release_index)
            del self.recording[start_index:end_index + 1]
            logging.info(f"Removed last click events, remaining events: {len(self.recording)}")
        
        # Also remove the last 2 seconds of events
        self.remove_last_seconds(2)

def main():
    status_app = StatusBarApp()
    recorder = MouseRecorder(status_app)
    recorder.start_recording()
    status_app.run()

if __name__ == "__main__":
    main() 