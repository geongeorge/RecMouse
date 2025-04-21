from pynput.mouse import Button, Controller
import logging
from colorama import Fore, Style, init
import sys
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
        self.recording_file = Path("recording.json")

    def play_recording(self, repeat_count=1):
        if not self.recording_file.exists():
            print("No recording found!")
            return

        with open(self.recording_file, 'r') as f:
            events = json.load(f)

        if not events:
            print("Recording is empty!")
            return

        for _ in range(repeat_count):
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
            if repeat_count > 1 and _ < repeat_count - 1:
                time.sleep(0.5)

if __name__ == "__main__":
    player = MousePlayer()
    try:
        player.play_recording()
    except KeyboardInterrupt:
        logging.info(f"{Fore.RED}Playback terminated by user.{Style.RESET_ALL}") 