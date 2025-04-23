import pyautogui
import keyboard
import time
import random

class InputSimulator:
    @staticmethod
    def click(x=960, y=540):
        original_x, original_y = pyautogui.position()
        pyautogui.click(x=x, y=y)
        pyautogui.moveTo(original_x, original_y) 

    @staticmethod
    def random_click(bounds, delay=None, validate_func=None):
        if delay:
            time.sleep(delay)

        if not validate_func or validate_func():
            x_click = random.randint(bounds[0][0], bounds[1][0])
            y_click = random.randint(bounds[0][1], bounds[1][1])

            InputSimulator.click(x=x_click, y=y_click)
    
    @staticmethod
    def key_press_and_release(key):
        keyboard.press_and_release(str(key))
    
    @staticmethod
    def queue_inputs(inputs, delay=None, validate_func=None):
        for inp in inputs:
            if delay:
                time.sleep(delay)

            if not validate_func or validate_func():
                if inp == 'click':
                    InputSimulator.click()
                else:
                    InputSimulator.key_press_and_release(inp)