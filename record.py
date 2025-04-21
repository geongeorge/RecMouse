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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format=f'{Fore.GREEN}%(asctime)s{Style.RESET_ALL} - %(message)s',
    datefmt='%H:%M:%S'
)

class StatusBarApp:
    def __init__(self):
        self.recorder = None
        self.is_recording = False

    def set_recording(self, is_recording):
        self.is_recording = is_recording

class MouseRecorder:
    def __init__(self, status_app):
        self.recording = []
        self.start_time = None
        self.mouse_listener = None
        # Use Application Support directory for storing recordings
        self.recording_file = get_app_data_path() / "recording.json"
        self.status_app = status_app
        self.status_app.recorder = self
        print(f"Recording file path: {self.recording_file}")  # Debug logging

    def on_move(self, x, y):
        if self.start_time is None:
            return
        
        event = {
            'type': 'move',
            'x': x,
            'y': y,
            'time': time() - self.start_time
        }
        self.recording.append(event)

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
        print(f"Recorded click: {event}")  # Debug logging

    def remove_last_click(self):
        # Remove the last click events (both press and release) from recording
        if not self.recording:
            return
            
        # Remove events from the end until we've removed both press and release of the last click
        removed_press = False
        removed_release = False
        while self.recording and not (removed_press and removed_release):
            if self.recording[-1]['type'] == 'click':
                if self.recording[-1]['pressed'] and not removed_press:
                    self.recording.pop()
                    removed_press = True
                elif not self.recording[-1]['pressed'] and not removed_release:
                    self.recording.pop()
                    removed_release = True
            else:
                # Keep removing move events until we find click events
                self.recording.pop()
        
        # Also remove the last 2 seconds of events
        self.remove_last_seconds(2)

    def remove_last_seconds(self, seconds):
        if not self.recording:
            return
            
        # Get the time of the last event
        last_time = self.recording[-1]['time']
        cutoff_time = last_time - seconds
        
        # Remove all events in the last 'seconds' seconds
        while self.recording and self.recording[-1]['time'] > cutoff_time:
            self.recording.pop()

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
            print("Recording started successfully")  # Debug logging
            logging.info(f"{Fore.YELLOW}Recording started!{Style.RESET_ALL}")
        except Exception as e:
            error_msg = f"Failed to start recording: {str(e)}"
            print(f"Error: {error_msg}")  # Debug logging
            rumps.notification("Error", "Recording Error", error_msg)

    def stop_recording(self):
        if self.mouse_listener:
            try:
                self.mouse_listener.stop()
                self.mouse_listener = None
                self.start_time = None
                
                # Save recording to file
                print(f"Saving recording to: {self.recording_file}")  # Debug logging
                print(f"Number of events: {len(self.recording)}")  # Debug logging
                
                # Ensure directory exists
                self.recording_file.parent.mkdir(parents=True, exist_ok=True)
                
                with open(self.recording_file, 'w') as f:
                    json.dump(self.recording, f)
                self.status_app.set_recording(False)
                logging.info(f"{Fore.CYAN}Recording saved to {self.recording_file}!{Style.RESET_ALL}")
            except Exception as e:
                error_msg = f"Failed to save recording: {str(e)}"
                print(f"Error: {error_msg}")  # Debug logging
                rumps.notification("Error", "Save Error", error_msg)

    def toggle_recording(self):
        if self.status_app.is_recording:
            self.stop_recording()
        else:
            self.start_recording()

    def cleanup(self):
        self.stop_recording()

def main():
    status_app = StatusBarApp()
    recorder = MouseRecorder(status_app)
    recorder.start_recording()
    status_app.run()

if __name__ == "__main__":
    main() 