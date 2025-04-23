from core import ConfigLoader, InputSimulator
from logger import Logger
from ..display.display_config import DisplayConfig
from ..display.screen_grabber import ScreenGrabber
from .client_state import ClientState
from datetime import datetime

class FoodHelper:
    def __init__(self, player_session, screen_state):
        self.config = ConfigLoader().config["client"]
        self.player_session = player_session
        self.screen_state = screen_state
        self.display_config = DisplayConfig()
        self.screen_grabber = ScreenGrabber()

        self.food_eaten = 0
        self.current_food_eaten = 0
        self.current_food_index = 0

        # get listen to quit and toggle faster
        self.client_state = ClientState()
        self.logger = Logger()

    def eat(self, callback, failure_callback):
        if self.current_food_eaten >= self.config['eating']['max_food_tried']:
            self.current_food_index += 1
            self.current_food_eaten = 0

            if self.current_food_index >= len(self.config['eating']['food_slots']):
                self.logger.log_error("Failed to eat food. Here is the last screen. Qutting game.", self.screen_grabber.last_screen)
                failure_callback()
            else:
                self._validate_food_slot()
                self.logger.log_action(
                    f"Ran out of food on slot. Moving to slot {self.config['eating']['food_slots'][self.current_food_index]}",
                    self.screen_grabber.crop_segment(
                        self.display_config.get_item_slot_bound(
                            self.config['eating']['food_slots'][self.current_food_index]
                        )
                    )
                )
            return

        if not self.player_session.hungry:
            self.logger.log_action(
                f"Finished eating {self.food_eaten} items!",
                self.screen_grabber.crop_segment(self.display_config.hunger_bar_bounds)
            )
            self.player_session.last_fish = datetime.now() # reset to not count eating towards counter
            self.player_session.eating = False

            # Don't go back to rod if not fishing
            if self.client_state.discord_toggle and not self.player_session.sleeping:
                callback()
            
        else:
            self._food_click()
        
    def begin_eating(self):
        self.logger.log_action(
            "Player is hungry. Begin eating...",
            self.screen_grabber.crop_segment(self.display_config.hunger_bar_bounds)
        )
        
        self.player_session.eating = True
        self.current_food_eaten = 0

        self._validate_food_slot()

    def reset(self):
        self.food_eaten = 0
        self.current_food_eaten = 0
        self.current_food_index = 0
    
    def _validate_food_slot(self):
        if self.current_food_index >= len(self.config["eating"]["food_slots"]):
            return

        InputSimulator.queue_inputs(
            inputs=["click", '0', self.config["eating"]["food_slots"][self.current_food_index]],
            delay=self.config["sleep_time"]
        )

    def _can_eat(self):
        if self.player_session.hungry and self.client_state.running:
            self.food_eaten += 1
            self.current_food_eaten += 1
            return True
        
        return False

    def _food_click(self):
        InputSimulator.random_click(
            bounds=self.display_config.get_center_box_bound(
                width=self.config["random_click_width"],
                height=self.config["random_click_width"]
            ),
            validate_func=self._can_eat
        )


