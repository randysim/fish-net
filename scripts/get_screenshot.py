from PIL import ImageGrab
import time
import keyboard
import os

script_running = True
def exit_script():
    global script_running

    script_running = False
    print("\n'q' pressed. Exiting...")

def get_screenshot():
    img = ImageGrab.grab()
    print("Screenshot taken.")

    file_name = "screenshot"
    i = 0
    while os.path.exists(f"{file_name}_{i}.png"):
        i += 1

    img.save(f"{file_name}_{i}.png")

keyboard.add_hotkey('q', exit_script)
keyboard.add_hotkey('v', get_screenshot)

print("Screenshot script started. Press 'v' to take a screenshot or 'q' to exit.")

while script_running:
    time.sleep(1)

print("Screenshot script exited.")