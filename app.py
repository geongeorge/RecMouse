import rumps
from record import MouseRecorder, StatusBarApp
from play import MousePlayer
import threading

class AutoMouseApp(rumps.App):
    def __init__(self):
        super().__init__("🐭")  # Back to mouse emoji
        
        self.status_app = StatusBarApp()
        self.recorder = MouseRecorder(self.status_app)
        self.player = MousePlayer()
        
        # Menu items
        self.record_button = rumps.MenuItem("Start Recording", callback=self.toggle_recording)
        self.play_button = rumps.MenuItem("Play Recording", callback=self.play_recording)
        self.repeat_play_button = rumps.MenuItem("Repeat Play...", callback=self.repeat_play)
        self.about_button = rumps.MenuItem("About", callback=self.show_about)
        
        # Add items to menu (no need for quit, rumps adds it automatically)
        self.menu = [self.record_button, self.play_button, self.repeat_play_button, None, self.about_button]

    def toggle_recording(self, sender=None):
        if not self.status_app.is_recording:
            self.title = "🔴"  # Red dot for recording
            self.record_button.title = "Stop Recording"
            self.recorder.start_recording()
        else:
            # Remove the last click event before stopping
            self.recorder.remove_last_click()
            self.title = "🐭"  # Back to mouse emoji
            self.record_button.title = "Start Recording"
            self.recorder.stop_recording()

    def play_recording(self, sender):
        # Disable play buttons during playback
        self.play_button.set_callback(None)
        self.repeat_play_button.set_callback(None)
        
        def play_thread():
            try:
                self.title = "🐭 ▶️"
                success = self.player.play_recording()
                
                # Restore mouse icon and re-enable buttons
                self.title = "🐭"
                self.play_button.set_callback(self.play_recording)
                self.repeat_play_button.set_callback(self.repeat_play)
            except Exception as e:
                rumps.notification("Error", "Playback Error", str(e))
                self.title = "🐭"
                self.play_button.set_callback(self.play_recording)
                self.repeat_play_button.set_callback(self.repeat_play)
        
        # Start playback in a background thread
        threading.Thread(target=play_thread).start()

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
                    # Disable play buttons during playback
                    self.play_button.set_callback(None)
                    self.repeat_play_button.set_callback(None)
                    
                    # Store original title to restore later
                    original_title = self.title
                    
                    def play_thread():
                        try:
                            for i in range(repeat_count):
                                self.title = f"🐭 ▶️ [{i+1}/{repeat_count}]"
                                success = self.player.play_recording()
                                if not success:  # If playback was interrupted
                                    break
                            
                            # Restore mouse icon and re-enable buttons
                            self.title = "🐭"
                            self.play_button.set_callback(self.play_recording)
                            self.repeat_play_button.set_callback(self.repeat_play)
                        except Exception as e:
                            rumps.notification("Error", "Playback Error", str(e))
                            self.title = "🐭"
                            self.play_button.set_callback(self.play_recording)
                            self.repeat_play_button.set_callback(self.repeat_play)
                    
                    # Start playback in a background thread
                    threading.Thread(target=play_thread).start()
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

    def clicked(self, sender):
        # When recording, clicking the status menu item stops the recording
        if self.status_app.is_recording:
            self.toggle_recording()
            return True  # Prevent menu from showing
        # Only show menu when not recording
        return super().clicked(sender)

    @rumps.clicked('Quit')
    def quit_app(self, sender):
        rumps.quit_application()

if __name__ == "__main__":
    app = AutoMouseApp()
    app.run() 