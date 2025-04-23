import keyboard
import time
import pyautogui

script_running = True
def exit_script():
    global script_running

    script_running = False
    print("\n'q' pressed. Exiting...")

def simulate_key():
    print("Simulating key presses.")
    # keyboard.press_and_release(str(key_to_simulate))

    pyautogui.click(x=500, y=500)
    pyautogui.vscroll(10)

    print("Finished simulating key presses.")

keyboard.add_hotkey('q', exit_script)
keyboard.add_hotkey('v', simulate_key)

print("Keyboard test started. Press 'v' to simulate key. Press 'q' to exit.")

while script_running:
    time.sleep(0.1)

print("Simulate key script exited.")