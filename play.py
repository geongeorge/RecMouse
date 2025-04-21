from pynput.mouse import Button, Controller
from pynput import keyboard
from time import sleep
import logging
from colorama import Fore, Style, init
import sys
import threading

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

    def on_press(self, key):
        try:
            if key == keyboard.Key.f6:
                self.ready_to_play = True
        except AttributeError:
            pass

    def play_recording(self, filename="record.txt"):
        try:
            with open(filename, "r") as f:
                commands = f.readlines()
        except FileNotFoundError:
            logging.error(f"{Fore.RED}Could not find {filename}. Please record some actions first.{Style.RESET_ALL}")
            return

        logging.info(f"{Fore.YELLOW}Press F6 to start playback...{Style.RESET_ALL}")
        
        # Wait for F6 press
        while not self.ready_to_play:
            sleep(0.1)
        
        logging.info(f"{Fore.YELLOW}Starting playback in 3 seconds...{Style.RESET_ALL}")
        sleep(3)  # Give user time to prepare

        for command in commands:
            command = command.strip()
            if not command:
                continue

            parts = command.split()
            action = parts[0]

            if action == "CLICK":
                try:
                    x, y = map(int, parts[1].split(","))
                    logging.info(f"{Fore.CYAN}Clicking at position ({x}, {y}){Style.RESET_ALL}")
                    self.mouse.position = (x, y)
                    self.mouse.click(Button.left)
                except (ValueError, IndexError):
                    logging.error(f"{Fore.RED}Invalid CLICK command: {command}{Style.RESET_ALL}")

            elif action == "WAIT":
                try:
                    ms = int(parts[1])
                    seconds = ms / 1000
                    logging.info(f"{Fore.MAGENTA}Waiting for {seconds:.2f} seconds{Style.RESET_ALL}")
                    sleep(seconds)
                except (ValueError, IndexError):
                    logging.error(f"{Fore.RED}Invalid WAIT command: {command}{Style.RESET_ALL}")

            else:
                logging.warning(f"{Fore.RED}Unknown command: {command}{Style.RESET_ALL}")

        logging.info(f"{Fore.GREEN}Playback completed!{Style.RESET_ALL}")
        self.keyboard_listener.stop()

if __name__ == "__main__":
    player = MousePlayer()
    filename = "record.txt"
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    try:
        player.play_recording(filename)
    except KeyboardInterrupt:
        logging.info(f"{Fore.RED}Playback terminated by user.{Style.RESET_ALL}")
        player.keyboard_listener.stop() 