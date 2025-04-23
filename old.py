from PIL import ImageGrab
from datetime import datetime
import time
import math
import pyautogui
import random
import keyboard

# EXIT SCRIPT
listening_commands = False
script_running = True
toggle = True

def exit_script():
    global script_running

    if not listening_commands:
        return
    
    script_running = False
    print("\n'ctrl + q' pressed. Exiting...")

def toggle_script():
    global toggle

    if not listening_commands:
        return

    toggle = not toggle
    print(f"{'Starting' if toggle else 'Stopping'} fishing bot.")

def activate_commands():
    global listening_commands

    listening_commands = True

def deactivate_commands():
    global listening_commands

    listening_commands = False

def on_press(event):
    if event.name == 'ctrl':
        activate_commands()
    elif event.name == 'q':
        exit_script()
    elif event.name == 'y':
        toggle_script()

def on_release(event):
    if event.name == 'ctrl':
        deactivate_commands()

def handle_key_event(event):
    if event.event_type == keyboard.KEY_DOWN:
        on_press(event)
    elif event.event_type == keyboard.KEY_UP:
        on_release(event)

keyboard.hook(handle_key_event)

# CONSTS
SCREEN_WIDTH, SCREEN_HEIGHT = ImageGrab.grab().size
INDICATOR_COLOR = (248, 39, 39)
INDICATOR_BACKGROUND_COLOR = (255, 255, 255)
INDICATOR_X = SCREEN_WIDTH // 2
INDICATOR_Y = 10
COLOR_THRESHOLD = 15
SLEEP_TIME = 0.2
EAT_DELAY = 1

FISH_MAIN_COLOR = (255, 255, 0)
FISH_TITLE_X = 1796
FISH_TITLE_Y = 867
TREASURE_TITLE_X = 1736
TREASURE_TITLE_Y = 870
JUNK_TITLE_X = 1755
JUNK_TITLE_Y = 866

START_TIME = datetime.now()
MAX_IDLE_SECONDS = 240
MAX_REELING_SECONDS = 30
ROD_SLOT = 4

FOOD_SLOT = 7
HUNGER_X = 135
HUNGER_Y = 987
HUNGER_COLOR = (123, 84, 38)

def color_difference(color1, color2):
    return math.sqrt(sum((color1[i] - color2[i]) ** 2 for i in range(3)))

def detect_fish(px):
    for dx in range(-5, 6):
        for dy in range(-5, 6):
            x = INDICATOR_X + dx
            y = INDICATOR_Y + dy
            if (
                color_difference(px[x, y], INDICATOR_COLOR) <= COLOR_THRESHOLD or
                color_difference(px[x, y], INDICATOR_BACKGROUND_COLOR) <= COLOR_THRESHOLD
            ):
                return True

    return False 


def detect_catch(px):
    return (
        color_difference(px[FISH_TITLE_X, FISH_TITLE_Y], FISH_MAIN_COLOR) <= COLOR_THRESHOLD or
        color_difference(px[TREASURE_TITLE_X, TREASURE_TITLE_Y], FISH_MAIN_COLOR) <= COLOR_THRESHOLD or
        color_difference(px[JUNK_TITLE_X, JUNK_TITLE_Y], FISH_MAIN_COLOR) <= COLOR_THRESHOLD
    )

def is_hungry(px):
    return color_difference(px[HUNGER_X, HUNGER_Y], HUNGER_COLOR) >= COLOR_THRESHOLD


# SESSION
total_fish = 0
is_reeling = False
reeling_start = None
eating = False
time_since_last_fish = datetime.now()

def random_click(bypass=False, instant=False):
    global is_reeling, eating
    
    # random click delay
    if not instant:
        time.sleep((SLEEP_TIME // 2)* random.random())

    if not bypass and not eating and not is_reeling:
        return

    x_click = SCREEN_WIDTH // 2 + random.randint(-50, 50)
    y_click = SCREEN_HEIGHT // 2 + random.randint(-50, 50)
    original_x, original_y = pyautogui.position()

    pyautogui.click(x=x_click, y=y_click)
    pyautogui.moveTo(original_x, original_y)  

# cast rod while it is still here, TODO: figure out if rod is selected or not. that way you can get perfect recasting.
"""
def recast_rod():
    print("recasting rod")
    keyboard.press_and_release(str(ROD_SLOT))
    time.sleep(0.5)
    keyboard.press_and_release(str(ROD_SLOT))
    time.sleep(0.5)
    random_click(bypass=True, instant=True)
"""

def reel(px):
    global is_reeling, time_since_last_fish, reeling_start

    now = datetime.now()
    time_since_last_reel = now - reeling_start

    if time_since_last_reel.total_seconds() >= MAX_REELING_SECONDS:
        print(f"Reeling took too long. Ending reel.")
        time_since_last_fish = now
        is_reeling = False
        return
    
    if detect_catch(px):
        diff = now - time_since_last_fish
        print(f"Successfully caught fish #{total_fish} after {diff.total_seconds()}s.")

        # PLEASE RECAST
        time.sleep(0.5)
        random_click(bypass=True)

        is_reeling = False
        time_since_last_fish = datetime.now()
    else:
        random_click()

def eat(px):
    global eating

    if is_hungry(px):
        print("Taking a bite.")
        random_click()
    else:
        print(f"Done eating. Switching to rod slot {ROD_SLOT}.")
        eating = False
        keyboard.press_and_release(str(ROD_SLOT))
        time.sleep(2)
        random_click(bypass=True)

print("Fishing bot started. Press 'ctrl + q' to exit. Press 'ctrl y' to start/stop fishing.")
while script_running:
    if not toggle:
        time.sleep(SLEEP_TIME)
        continue

    px = ImageGrab.grab().load()

    if not is_reeling and not eating and is_hungry(px):
        print(f"Pressing {FOOD_SLOT}. Eating...")
        eating = True
        random_click(instant=True)
        keyboard.press_and_release(str(FOOD_SLOT))
    
    if eating:
        eat(px)
        time.sleep(EAT_DELAY) # Account for food bar animation
        continue

    if is_reeling:
        reel(px)
    elif detect_fish(px) and not detect_catch(px):
        total_fish += 1
        print(f"Fish #{total_fish} detected. Fishing")
        reeling_start = datetime.now()
        is_reeling = True
        random_click()
    else:
        now = datetime.now()
        diff = now - time_since_last_fish
        if diff.total_seconds() >= MAX_IDLE_SECONDS:
            print(f"No fish detected for {MAX_IDLE_SECONDS} seconds. Clicking.")
            random_click(bypass=True, instant=True)
            time_since_last_fish = now
    
    time.sleep(SLEEP_TIME)

duration = datetime.now() - START_TIME
hours = duration.seconds // 3600
minutes = (duration.seconds % 3600) // 60
seconds = duration.seconds % 60

print(f"Fishing bot exited. Caught {total_fish} fish over {hours}hr {minutes}min {seconds}s.")




