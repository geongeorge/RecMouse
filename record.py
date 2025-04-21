from pynput import mouse, keyboard
from time import time, sleep
import logging
from colorama import Fore, Style, init

# Initialize colorama
init()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format=f'{Fore.GREEN}%(asctime)s{Style.RESET_ALL} - %(message)s',
    datefmt='%H:%M:%S'
)

class MouseRecorder:
    def __init__(self):
        self.recording = False
        self.last_time = None
        self.recorded_events = []
        self.mouse_listener = mouse.Listener(on_click=self.on_click)
        self.keyboard_listener = keyboard.Listener(on_press=self.on_press)

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
            # Use Ctrl+Alt+R as the toggle shortcut
            if key == keyboard.Key.f6:
                self.toggle_recording()
        except AttributeError:
            pass

    def toggle_recording(self):
        self.recording = not self.recording
        if self.recording:
            self.recorded_events = []
            self.last_time = time()
            logging.info(f"{Fore.YELLOW}Recording started! Press F6 to stop recording.{Style.RESET_ALL}")
        else:
            if self.recorded_events:
                self.save_recording()
                logging.info(f"{Fore.CYAN}Recording saved to record.txt!{Style.RESET_ALL}")
            else:
                logging.info(f"{Fore.RED}Recording stopped with no events!{Style.RESET_ALL}")

    def save_recording(self):
        with open("record.txt", "w") as f:
            for event in self.recorded_events:
                f.write(event + "\n")

    def start(self):
        self.mouse_listener.start()
        self.keyboard_listener.start()
        logging.info(f"{Fore.YELLOW}Mouse Recorder started! Press F6 to start/stop recording.{Style.RESET_ALL}")
        self.mouse_listener.join()
        self.keyboard_listener.join()

if __name__ == "__main__":
    recorder = MouseRecorder()
    try:
        recorder.start()
    except KeyboardInterrupt:
        logging.info(f"{Fore.RED}Recording terminated by user.{Style.RESET_ALL}") 