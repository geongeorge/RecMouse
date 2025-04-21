import rumps
from record import MouseRecorder, StatusBarApp
from play import MousePlayer, check_accessibility_permissions
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
        self.is_playing = False  # Track playback state
        self._ui_update_timer = None  # Instance variable for UI update timer
        
        # Menu items
        self.record_button = rumps.MenuItem("Start Recording", callback=self.toggle_recording)
        self.play_button = rumps.MenuItem("Play Recording", callback=self.play_recording)
        self.repeat_play_button = rumps.MenuItem("Repeat Play...", callback=self.repeat_play)
        self.about_button = rumps.MenuItem("About", callback=self.show_about)
        
        # Add items to menu (no need for quit, rumps adds it automatically)
        self.menu = [
            self.record_button,
            self.play_button,
            self.repeat_play_button,
            None,
            self.about_button
        ]
        
        # Initially disable play buttons if no recording exists
        self.update_play_buttons()

    def update_play_buttons(self):
        """Enable/disable play buttons based on recording existence."""
        has_recording = self.player.recording_file.exists()
        self.play_button.set_callback(self.play_recording if has_recording else None)
        self.repeat_play_button.set_callback(self.repeat_play if has_recording else None)

    def schedule_ui_update(self, update_func):
        """Schedule a UI update to run on the main thread."""
        # Stop previous timer if it exists
        if self._ui_update_timer is not None:
            try:
                self._ui_update_timer.stop()
            except Exception:
                pass  # Ignore any timer-related errors
            self._ui_update_timer = None

        # Create a new timer that runs for a short duration to ensure update is applied
        @rumps.timer(0.1)  # Run for a short duration
        def update_timer(_):
            try:
                update_func()
            except Exception as e:
                print(f"Error in UI update: {e}")  # Debug log
            finally:
                update_timer.stop()
                self._ui_update_timer = None

        self._ui_update_timer = update_timer

    def check_permissions(self):
        """Check if we have accessibility permissions."""
        if not check_accessibility_permissions(prompt=True):
            rumps.alert(
                "Permission Required",
                "RecMouse needs accessibility permissions.\n\n" +
                "1. Open System Settings\n" +
                "2. Go to Privacy & Security > Accessibility\n" +
                "3. Find and enable RecMouse\n" +
                "4. Try again"
            )
            return False
        return True

    def toggle_recording(self, sender=None):
        if not self.status_app.is_recording:
            # Check permissions before starting recording
            if not self.check_permissions():
                return
            
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

    def reset_ui_state(self, _=None):
        """Reset the UI state after playback."""
        print("Executing UI state reset")  # Debug log
        
        def do_reset():
            print("Resetting UI state")  # Debug log
            self.is_playing = False
            self.title = ""  # Clear the play icon
            has_recording = self.player.recording_file.exists()
            if has_recording:
                self.play_button.set_callback(self.play_recording)
                self.repeat_play_button.set_callback(self.repeat_play)
            print("UI state reset complete")  # Debug log

        # Direct call since this works reliably
        do_reset()

    def play_recording(self, _=None):
        print("Play button clicked")  # Debug log
        
        if self.is_playing:
            print("Already playing, ignoring click")  # Debug log
            return
            
        if not self.check_permissions():
            print("Permission check failed")  # Debug log
            return
            
        if not self.player.recording_file.exists():
            print("No recording file exists")  # Debug log
            rumps.alert("Error", "Please record something first.")
            return

        print("Starting playback process")  # Debug log
        # Disable play buttons during playback
        self.is_playing = True
        self.play_button.set_callback(None)
        self.repeat_play_button.set_callback(None)
        
        # Set play emoji immediately on main thread
        self.title = "▶️"
        
        def play_thread():
            try:
                print("Play thread started")  # Debug log
                success, error_msg = self.player.play_recording()
                print(f"Playback completed - success: {success}, error: {error_msg}")  # Debug log
                
                if not success and error_msg:
                    def show_error():
                        print("Showing error")  # Debug log
                        rumps.alert("Error", error_msg)
                        self.reset_ui_state()
                    self.schedule_ui_update(show_error)
                else:
                    self.reset_ui_state()

            except Exception as e:
                print(f"Exception in play thread: {e}")  # Debug log
                def show_error():
                    print("Showing error after exception")  # Debug log
                    rumps.alert("Playback Error", str(e))
                    self.reset_ui_state()
                self.schedule_ui_update(show_error)
        
        # Start playback in a background thread
        print("Starting background thread for playback")  # Debug log
        threading.Thread(target=play_thread).start()

    def repeat_play(self, _=None):
        if self.is_playing:
            print("Already playing, ignoring click")  # Debug log
            return
            
        if not self.check_permissions():
            return
            
        if not self.player.recording_file.exists():
            rumps.alert("Error", "Please record something first.")
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
                    self.is_playing = True
                    self.play_button.set_callback(None)
                    self.repeat_play_button.set_callback(None)
                    
                    # Set initial play emoji immediately on main thread
                    self.title = f"▶️ [1/{repeat_count}]"
                    
                    def play_thread():
                        try:
                            for i in range(repeat_count):
                                if i > 0:  # Skip first update since we set it above
                                    def update_title(i=i):
                                        self.title = f"▶️ [{i+1}/{repeat_count}]"
                                    self.schedule_ui_update(update_title)
                                
                                success, error_msg = self.player.play_recording()
                                if not success:  # If playback was interrupted
                                    def show_error():
                                        print("Showing error during repeat")  # Debug log
                                        if error_msg:
                                            rumps.alert("Error", error_msg)
                                        self.reset_ui_state()
                                    self.schedule_ui_update(show_error)
                                    break
                            
                            if success:  # Only reset if we completed successfully
                                self.reset_ui_state()
                        
                        except Exception as e:
                            print(f"Exception in repeat play thread: {e}")  # Debug log
                            def show_error():
                                print("Showing error after repeat exception")  # Debug log
                                rumps.alert("Playback Error", str(e))
                                self.reset_ui_state()
                            self.schedule_ui_update(show_error)
                    
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