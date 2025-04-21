import rumps
from record import MouseRecorder, StatusBarApp
from play import MousePlayer
from pynput import keyboard
import threading

class AutoMouseApp(rumps.App):
    def __init__(self):
        super().__init__("🐭")  # Back to mouse emoji
        
        self.status_app = StatusBarApp()
        self.recorder = MouseRecorder(self.status_app)
        self.player = MousePlayer()
        
        # Menu items
        self.record_button = rumps.MenuItem("Start Recording (F6)", callback=self.toggle_recording)
        self.play_button = rumps.MenuItem("Play Recording", callback=self.play_recording)
        self.repeat_play_button = rumps.MenuItem("Repeat Play...", callback=self.repeat_play)
        self.about_button = rumps.MenuItem("About", callback=self.show_about)
        
        # Add items to menu (no need for quit, rumps adds it automatically)
        self.menu = [self.record_button, self.play_button, self.repeat_play_button, None, self.about_button]

        # Setup keyboard listener
        self.keyboard_listener = keyboard.Listener(on_press=self.on_key_press)
        self.keyboard_listener.start()

    def on_key_press(self, key):
        try:
            if key == keyboard.Key.f6:
                # We need to run this on the main thread
                rumps.Timer(0, self.toggle_recording).start()
        except AttributeError:
            pass

    def toggle_recording(self, sender=None):
        if not self.status_app.is_recording:
            self.title = "🔴"  # Red dot for recording
            self.record_button.title = "Stop Recording (F6)"
            self.recorder.start_recording()
        else:
            # Remove the last click event before stopping
            self.recorder.remove_last_click()
            self.title = "🐭"  # Back to mouse emoji
            self.record_button.title = "Start Recording (F6)"
            self.recorder.stop_recording()

    def play_recording(self, sender):
        self.player.play_recording()

    def repeat_play(self, sender):
        window = rumps.Window(
            message="Enter number of times to repeat:",
            title="Repeat Play",
            default_text="1",
            dimensions=(100, 20),  # Make the input field smaller
            ok="Play",
            cancel="Cancel"
        )
        response = window.run()
        if response.clicked:
            try:
                repeat_count = int(response.text)
                if repeat_count > 0:
                    window.close()  # Close the window before starting playback
                    self.player.play_recording(repeat_count)
                else:
                    rumps.alert("Error", "Please enter a number greater than 0")
            except ValueError:
                rumps.alert("Error", "Please enter a valid number")

    def show_about(self, sender):
        window = rumps.Window(
            message="PyAutoMouse lets you record and replay mouse movements.",
            title="About PyAutoMouse",
            default_text="Version 1.0\nCreated with ❤️",
            ok="Close"
        )
        window.run()

    def clicked(self):
        # Override the default click behavior
        if self.status_app.is_recording:
            self.toggle_recording()
        else:
            super().clicked()

    @rumps.clicked('Quit')
    def quit_app(self, sender):
        if self.keyboard_listener:
            self.keyboard_listener.stop()
        self.recorder.cleanup()
        rumps.quit_application()

if __name__ == "__main__":
    app = AutoMouseApp()
    app.run() 