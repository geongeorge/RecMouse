import pyautogui
import time
from typing import Tuple

# Enable failsafe - moving mouse to corner will stop the script
pyautogui.FAILSAFE = True

class MouseController:
    def __init__(self):
        # Add a small pause between automated movements
        pyautogui.PAUSE = 0.5
        # Get screen size
        self.screen_width, self.screen_height = pyautogui.size()

    def get_mouse_position(self) -> Tuple[int, int]:
        """Get current mouse position"""
        x, y = pyautogui.position()
        return (x, y)

    def move_mouse(self, x: int, y: int, duration: float = 0.5):
        """
        Move mouse to specific coordinates
        
        Args:
            x (int): X coordinate
            y (int): Y coordinate
            duration (float): Time taken to move to the position
        """
        try:
            pyautogui.moveTo(x, y, duration=duration)
        except pyautogui.FailSafeException:
            print("Failsafe triggered - Mouse moved to corner")
            raise

    def click_at_position(self, x: int, y: int, clicks: int = 1):
        """
        Click at specific coordinates
        
        Args:
            x (int): X coordinate
            y (int): Y coordinate
            clicks (int): Number of clicks (default: 1)
        """
        try:
            pyautogui.click(x=x, y=y, clicks=clicks)
        except pyautogui.FailSafeException:
            print("Failsafe triggered - Mouse moved to corner")
            raise

def main():
    controller = MouseController()
    
    try:
        # Example usage
        print("Current mouse position:", controller.get_mouse_position())
        
        # Move to center of screen
        center_x = controller.screen_width // 2
        center_y = controller.screen_height // 2
        
        print(f"Moving mouse to center of screen ({center_x}, {center_y})")
        controller.move_mouse(center_x, center_y)
        time.sleep(1)
        
        # Click at center
        print("Clicking at center")
        controller.click_at_position(center_x, center_y)
        
    except KeyboardInterrupt:
        print("\nScript terminated by user")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main() 