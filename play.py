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
            logging.error(f"{Fore.RED}No recording found! Please record something first.{Style.RESET_ALL}")
            return False

        try:
            with open(self.recording_file, 'r') as f:
                events = json.load(f)
        except json.JSONDecodeError:
            logging.error(f"{Fore.RED}Invalid recording file! Please record again.{Style.RESET_ALL}")
            return False

        if not events:
            logging.error(f"{Fore.RED}Recording is empty! Please record something.{Style.RESET_ALL}")
            return False

        logging.info(f"{Fore.YELLOW}Starting playback (repeating {repeat_count} times)...{Style.RESET_ALL}")
        
        try:
            for i in range(repeat_count):
                if repeat_count > 1:
                    logging.info(f"{Fore.CYAN}Playing iteration {i + 1} of {repeat_count}{Style.RESET_ALL}")
                
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

            logging.info(f"{Fore.GREEN}Playback completed successfully!{Style.RESET_ALL}")
            return True

        except Exception as e:
            logging.error(f"{Fore.RED}Error during playback: {str(e)}{Style.RESET_ALL}")
            return False

if __name__ == "__main__":
    player = MousePlayer()
    try:
        player.play_recording()
    except KeyboardInterrupt:
        logging.info(f"{Fore.RED}Playback terminated by user.{Style.RESET_ALL}") 