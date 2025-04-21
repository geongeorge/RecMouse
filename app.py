import rumps
from record import MouseRecorder, StatusBarApp
from play import MousePlayer
import threading
from AppKit import NSApplication
import os
import sys
from pathlib import Path

def get_resource_path(filename):
    """Get the correct path for a resource file, whether running from source or in a bundle."""
    if getattr(sys, 'frozen', False):
        # Running in a bundle
        bundle_dir = Path(os.path.dirname(sys.executable)).parent / 'Resources'
        return str(bundle_dir / filename)
    else:
        # Running from source
        return str(Path(__file__).parent / filename)

class AutoMouseApp(rumps.App):
    def __init__(self):
        icon_path = get_resource_path('mouse-status-icon.png')
        super().__init__("", icon=icon_path)  # Empty title initially, will be set based on state
        
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
        
        # Initially disable play buttons if no recording exists
        self.update_play_buttons()

    def update_play_buttons(self):
        # Enable/disable play buttons based on recording existence
        has_recording = self.player.recording_file.exists()
        self.play_button.set_callback(self.play_recording if has_recording else None)
        self.repeat_play_button.set_callback(self.repeat_play if has_recording else None)

    def toggle_recording(self, sender=None):
        if not self.status_app.is_recording:
            self.title = "🔴"  # Red circle for recording
            self.record_button.title = "Stop Recording"
            self.recorder.start_recording()
        else:
            # Remove the last click event before stopping
            self.recorder.remove_last_click()
            self.title = ""  # Remove indicator when not recording
            self.record_button.title = "Start Recording"
            self.recorder.stop_recording()
            # Update play buttons state after recording
            self.update_play_buttons()

    def play_recording(self, sender):
        if not self.player.recording_file.exists():
            rumps.notification("Error", "No Recording", "Please record something first.")
            return

        # Disable play buttons during playback
        self.play_button.set_callback(None)
        self.repeat_play_button.set_callback(None)
        
        def play_thread():
            try:
                self.title = "▶️"  # Play emoji during playback
                success = self.player.play_recording()
                
                # Restore state and re-enable buttons
                self.title = "🔴" if self.status_app.is_recording else ""  # Restore recording indicator if recording
                self.play_button.set_callback(self.play_recording)
                self.repeat_play_button.set_callback(self.repeat_play)
            except Exception as e:
                rumps.notification("Error", "Playback Error", str(e))
                self.title = "🔴" if self.status_app.is_recording else ""  # Restore recording indicator if recording
                self.play_button.set_callback(self.play_recording)
                self.repeat_play_button.set_callback(self.repeat_play)
        
        # Start playback in a background thread
        threading.Thread(target=play_thread).start()

    def repeat_play(self, sender):
        if not self.player.recording_file.exists():
            rumps.notification("Error", "No Recording", "Please record something first.")
            return

        window = rumps.Window(
            message="Enter number of times to repeat:",
            title="Repeat Play",
            default_text="1",
            dimensions=(100, 20),  # Make the input field smaller
            ok="Play",
            cancel="Cancel"
        )
        NSApplication.sharedApplication().activateIgnoringOtherApps_(True)
        response = window.run()
        if response.clicked:
            try:
                repeat_count = int(response.text)
                if repeat_count > 0:
                    # Disable play buttons during playback
                    self.play_button.set_callback(None)
                    self.repeat_play_button.set_callback(None)
                    
                    def play_thread():
                        try:
                            for i in range(repeat_count):
                                self.title = f"▶️ [{i+1}/{repeat_count}]"  # Play emoji with count
                                success = self.player.play_recording()
                                if not success:  # If playback was interrupted
                                    break
                            
                            # Restore state and re-enable buttons
                            self.title = "🔴" if self.status_app.is_recording else ""  # Restore recording indicator if recording
                            self.play_button.set_callback(self.play_recording)
                            self.repeat_play_button.set_callback(self.repeat_play)
                        except Exception as e:
                            rumps.notification("Error", "Playback Error", str(e))
                            self.title = "🔴" if self.status_app.is_recording else ""  # Restore recording indicator if recording
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
            message="RecMouse lets you record and replay mouse movements.\nVersion 1.0\nCreated with ❤️\n\nrecmouse.com",
            title="About RecMouse", 
            default_text="Currently RecMouse only supports clicks. Other gestures are not supported",
            ok="Close"
        )
        NSApplication.sharedApplication().activateIgnoringOtherApps_(True)
        window.icon = "mouse-icon.png"  # Set window icon to the app icon
        window.run()

    @rumps.clicked
    def on_click(self, sender):
        if self.status_app.is_recording:
            self.toggle_recording()
            return True
        return False

if __name__ == "__main__":
    app = AutoMouseApp()
    app.run() 