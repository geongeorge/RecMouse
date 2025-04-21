import rumps
from record import MouseRecorder, StatusBarApp
from play import MousePlayer

class AutoMouseApp(rumps.App):
    def __init__(self):
        super().__init__("🐭")  # Back to mouse emoji
        
        self.status_app = StatusBarApp()
        self.recorder = MouseRecorder(self.status_app)
        self.player = MousePlayer()
        
        # Menu items
        self.record_button = rumps.MenuItem("Start Recording", callback=self.toggle_recording)
        self.play_button = rumps.MenuItem("Play Recording", callback=self.play_recording)
        self.about_button = rumps.MenuItem("About", callback=self.show_about)
        
        # Add items to menu
        self.menu = [self.record_button, self.play_button, None, self.about_button]

    def toggle_recording(self, sender):
        if not self.status_app.is_recording:
            self.title = "🔴"  # Red dot for recording
            self.record_button.title = "Stop Recording"
            self.recorder.start_recording()
        else:
            self.title = "🐭"  # Back to mouse emoji
            self.record_button.title = "Start Recording"
            self.recorder.stop_recording()

    def play_recording(self, sender):
        self.player.play_recording()

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
            self.toggle_recording(None)
        else:
            super().clicked()

    @rumps.clicked('Quit')
    def quit_app(self, sender):
        self.recorder.cleanup()
        rumps.quit_application()

if __name__ == "__main__":
    app = AutoMouseApp()
    app.run() 