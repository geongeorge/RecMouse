from pynput import mouse, keyboard
from time import time, sleep
import logging
from colorama import Fore, Style, init
import threading
import sys
import rumps

# Initialize colorama
init()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format=f'{Fore.GREEN}%(asctime)s{Style.RESET_ALL} - %(message)s',
    datefmt='%H:%M:%S'
)

class StatusBarApp(rumps.App):
    def __init__(self):
        super().__init__("◉", quit_button=None)  # Using a circle character as the title
        self.recording = False
        self.recorder = None
        self.menu = ["Stop Recording", "Quit"]
        self.menu["Stop Recording"].state = False

    @rumps.clicked("Stop Recording")
    def toggle_recording(self, _):
        if self.recorder:
            self.recorder.toggle_recording_from_menu()

    @rumps.clicked("Quit")
    def quit(self, _):
        if self.recorder:
            self.recorder.cleanup()
        rumps.quit_application()

    def set_recording(self, is_recording):
        self.recording = is_recording
        if is_recording:
            self.title = "⚫ REC"  # Red circle when recording
            self.menu["Stop Recording"].state = True
        else:
            self.title = "◉"  # Regular circle when not recording
            self.menu["Stop Recording"].state = False

class MouseRecorder:
    def __init__(self, status_app):
        self.recording = False
        self.last_time = None
        self.recorded_events = []
        self.mouse_listener = mouse.Listener(on_click=self.on_click)
        self.keyboard_listener = keyboard.Listener(on_press=self.on_press)
        self.status_app = status_app
        self.status_app.recorder = self

    def on_click(self, x, y, button, pressed):
        if not self.recording or not pressed:
            return
        
        current_time = time()
        if self.last_time is not None:
            wait_time = int((current_time - self.last_time) * 1000)  # Convert to milliseconds
            if wait_time > 50:  # Only record waits longer than 50ms
                self.recorded_events.append(f"WAIT {wait_time}")
        
        self.recorded_events.append(f"CLICK {int(x)},{int(y)}")
        self.last_time = current_time

    def on_press(self, key):
        try:
            if key == keyboard.Key.f6:
                self.toggle_recording()
        except AttributeError:
            pass

    def toggle_recording_from_menu(self):
        # Called from the menu item
        self.toggle_recording()

    def toggle_recording(self):
        self.recording = not self.recording
        if self.recording:
            self.recorded_events = []
            self.last_time = time()
            self.status_app.set_recording(True)
            logging.info(f"{Fore.YELLOW}Recording started! Press F6 to stop recording.{Style.RESET_ALL}")
        else:
            self.status_app.set_recording(False)
            if self.recorded_events:
                self.save_recording()
                logging.info(f"{Fore.CYAN}Recording saved to record.txt!{Style.RESET_ALL}")
            else:
                logging.info(f"{Fore.RED}Recording stopped with no events!{Style.RESET_ALL}")

    def save_recording(self):
        with open("record.txt", "w") as f:
            for event in self.recorded_events:
                f.write(event + "\n")

    def cleanup(self):
        if self.recording:
            self.toggle_recording()
        self.mouse_listener.stop()
        self.keyboard_listener.stop()

    def start(self):
        self.mouse_listener.start()
        self.keyboard_listener.start()
        logging.info(f"{Fore.YELLOW}Mouse Recorder started! Press F6 to start/stop recording.{Style.RESET_ALL}")

def main():
    status_app = StatusBarApp()
    recorder = MouseRecorder(status_app)
    recorder.start()
    status_app.run()

if __name__ == "__main__":
    main() 