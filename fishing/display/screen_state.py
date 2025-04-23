from core import ConfigLoader
from logger import Logger
from .display_config import DisplayConfig
import math

class ScreenState():
    def __init__(self):
        self._config = ConfigLoader().config

        self.screen_colors = self._config["display"]["screen_colors"]
        self.color_threshold = self._config["display"]["color_threshold"]
        self.display_config = DisplayConfig()

        self.health_threshold = self._config["client"]["player"]["health_threshold"]
        self.hunger_threshold = self._config["client"]["player"]["hunger_threshold"]

        self.fish_indicator_present = False
        self.catch_indicator_present = False
        self.sunken_indicator_present = False
        self.hunger_indicator_present = False
        self.hurt_indicator_present = False

        self.logger = Logger()

    def update_state(self, px):
        self.fish_indicator_present = self._detect_fish(px)
        self.catch_indicator_present, self.sunken_indicator_present = self._detect_catch(px)
        self.hunger_indicator_present = self._detect_hunger(px)
        self.hurt_indicator_present = self._detect_hurt(px)

    def _detect_fish(self, px):
        indicator_bounds = self.display_config.fishing_indicator_bounds
        y_jump = (indicator_bounds[1][1] - indicator_bounds[0][1]) // 10
        
        red_indicator_present = False
        white_indicator_present = False

        for y in range(indicator_bounds[0][1], indicator_bounds[1][1], y_jump):
            for x in range(indicator_bounds[0][0], indicator_bounds[1][0]):
                red_indicator_present = (
                    red_indicator_present or 
                    (self._color_difference(self.screen_colors["fishing_indicator"], px[x, y]) < self.color_threshold)
                )
                white_indicator_present = (
                    white_indicator_present or
                    (self._color_difference(self.screen_colors["fishing_indicator_background"], px[x, y]) < self.color_threshold * 1.5)
                )
                
                if red_indicator_present and white_indicator_present:
                    return True
        
        return False

    def _detect_catch(self, px):
        indicator_bounds = self.display_config.catch_title_bounds
        y_jump = (indicator_bounds[1][1] - indicator_bounds[0][1]) // 5
        x_end = ((indicator_bounds[1][0] - indicator_bounds[0][0]) // 2) + indicator_bounds[0][0]
        
        for y in range(indicator_bounds[0][1], indicator_bounds[1][1], y_jump):
            for x in range(indicator_bounds[0][0], x_end):
                if self._color_difference(self.screen_colors["catch_title"], px[x, y]) <= self.color_threshold:
                    return True, False
                if self._color_difference(self.screen_colors["sunken_treasure"], px[x, y]) <= self.color_threshold:
                    return True, True
            
        return False

    def _detect_hunger(self, px):
        indicator_bounds = self.display_config.hunger_bar_bounds

        relative_x = (indicator_bounds[1][0] - indicator_bounds[0][0]) * self.hunger_threshold + indicator_bounds[0][0]
        
        for y in range(indicator_bounds[0][1], indicator_bounds[1][1]):
            # Need to test two browns because brown can be represented by various rgb combinations
            if (
                self._color_difference(self.screen_colors["hunger_bar"], px[relative_x, y]) <= self.color_threshold or
                self._color_difference(self.screen_colors["hunger_bar_2"], px[relative_x, y]) <= self.color_threshold
            ):
                return False

        return True
        

    def _detect_hurt(self, px):
        indicator_bounds = self.display_config.health_bar_bounds

        relative_x = (indicator_bounds[1][0] - indicator_bounds[0][0]) * self.health_threshold + indicator_bounds[0][0]
        
        for y in range(indicator_bounds[0][1], indicator_bounds[1][1]):
            if self._color_difference(self.screen_colors["health_bar"], px[relative_x, y]) <= self.color_threshold:
                return False

        return True

    def _color_difference(self, color1, color2):
        return math.sqrt(sum((color1[i] - color2[i]) ** 2 for i in range(3)))