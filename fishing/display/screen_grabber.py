from PIL import ImageGrab
from core import Singleton

class ScreenGrabber(metaclass=Singleton):
    def __init__(self):
        self.last_screen = None
        self.last_fish_img = None
        self.last_catch_img = None
    
    def crop_segment(self, bounds):
        top = bounds[0][1]
        left = bounds[0][0]
        right = bounds[1][0]
        bottom = bounds[1][1]

        cropped = self.last_screen.crop((left, top, right, bottom))

        return cropped
    
    def grab_screen(self):
        screenshot = ImageGrab.grab()
        
        self.last_screen = screenshot
        px = screenshot.load()
        
        return px

    def save_fish(self):
        self.last_fish_img = self.last_screen
    
    def save_catch(self):
        self.last_catch_img = self.last_catch_img