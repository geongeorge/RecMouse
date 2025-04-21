from pynput.mouse import Button, Controller
import rumps
import json
import time
from pathlib import Path

class MousePlayer:
    def __init__(self):
        self.mouse = Controller()
        self.recording_file = Path("recording.json")

    def play_recording(self, repeat_count=1):
        if not self.recording_file.exists():
            rumps.notification("Error", "No Recording", "Please record something first.")
            return False

        try:
            with open(self.recording_file, 'r') as f:
                events = json.load(f)
        except json.JSONDecodeError:
            rumps.notification("Error", "Invalid Recording", "Please record again.")
            return False

        if not events:
            rumps.notification("Error", "Empty Recording", "Please record something.")
            return False

        try:
            for i in range(repeat_count):
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

            return True

        except Exception as e:
            rumps.notification("Error", "Playback Error", str(e))
            return False

if __name__ == "__main__":
    player = MousePlayer()
    try:
        player.play_recording()
    except KeyboardInterrupt:
        rumps.notification("Info", "Playback terminated by user.", "") 