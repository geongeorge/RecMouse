from pynput.mouse import Button, Controller
from pynput import keyboard
from time import sleep
import logging
from colorama import Fore, Style, init
import sys
import threading
import json
import time
from pathlib import Path

# Initialize colorama
init()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format=f'{Fore.GREEN}%(asctime)s{Style.RESET_ALL} - %(message)s',
    datefmt='%H:%M:%S'
)

class MousePlayer:
    def __init__(self):
        self.mouse = Controller()
        self.ready_to_play = False
        self.keyboard_listener = keyboard.Listener(on_press=self.on_press)
        self.keyboard_listener.start()
        self.recording_file = Path("recording.json")

    def on_press(self, key):
        try:
            if key == keyboard.Key.f6:
                self.ready_to_play = True
        except AttributeError:
            pass

    def play_recording(self):
        if not self.recording_file.exists():
            print("No recording found!")
            return

        with open(self.recording_file, 'r') as f:
            events = json.load(f)

        if not events:
            print("Recording is empty!")
            return

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

if __name__ == "__main__":
    player = MousePlayer()
    try:
        player.play_recording()
    except KeyboardInterrupt:
        logging.info(f"{Fore.RED}Playback terminated by user.{Style.RESET_ALL}")
        player.keyboard_listener.stop() 