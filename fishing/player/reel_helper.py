from core import ConfigLoader, InputSimulator
from logger import Logger
from ..display.display_config import DisplayConfig
from ..display.screen_grabber import ScreenGrabber
from .client_state import ClientState
from datetime import datetime
import random

class ReelHelper:
    def __init__(self, player_session, screen_state):
        self.config = ConfigLoader().config["client"]
        self.discord_id = ConfigLoader().config["discord"]["user_id"]
        self.display_config = DisplayConfig()
        self.player_session = player_session
        self.screen_state = screen_state
        self.screen_grabber = ScreenGrabber()

        self.client_state = ClientState()
        self.logger = Logger()
        
    def reel(self):
        if self.player_session.time_since_last_reel >= self.config["fishing"]["max_reeling_seconds"]:
            self.logger.log_error(
                f"Reeling took over {self.config['fishing']['max_reeling_seconds']}s. Here is the image of the detection screen.",
                self.screen_grabber.last_fish_img
            )

            self.player_session.reeling = False
            self.player_session.last_fish = datetime.now()

            self.recast_rod()
            return
        
        if self.screen_state.catch_indicator_present:
            self.screen_grabber.save_catch()

            item_bounds = self.display_config.combine_bounds(
                self.display_config.catch_title_bounds,
                self.display_config.catch_background_bounds
            )

            self.logger.log_fish(
                f"Successfully caught fish #{self.player_session.total_fish_encountered} after {self.player_session.time_since_last_fish}s.",
                self.screen_grabber.crop_segment(item_bounds)
            )

            if self.screen_state.sunken_indicator_present:
                self.logger.log_fish(
                    f"**CAUGHT A SUNKEN TREASURE** <@{self.discord_id}>"
                )

            self.player_session.total_fish_caught += 1
            self.player_session.reeling = False
            self.player_session.last_fish = datetime.now()
            self.player_session.consecutive_idles = 0
            self.recast_rod()
        else:
            self._reel_click()
    
    def begin_reel(self):
        self.logger.log("Beginning reeling sequence...")
        self.player_session.last_reel = datetime.now()
        self.player_session.reeling = True
        InputSimulator.click()
        self.logger.log_action("Reeling...")

    def recast_rod(self, bypass=None):
        self.logger.log_action("Recasting rod...")

        InputSimulator.queue_inputs(
            inputs=[
                "click", 
                '0', 
                self.config["fishing"]["rod_slot"], 
                "click"
            ],
            delay=0.3,
            validate_func=lambda:(self.client_state.running and not self.player_session.eating) or bypass
        )
    
    def uncast_rod(self, bypass=None):
        self.logger.log_action("Uncasting rod...")

        InputSimulator.queue_inputs(
            inputs=[
                "click", 
                '0', 
                self.config["fishing"]["rod_slot"]
            ],
            delay=0.3,
            validate_func=lambda:(self.client_state.running and not self.player_session.eating) or bypass
        )
    
    def _can_reel(self):
        if self.player_session.reeling and self.client_state.running and not self.player_session.eating:
            self.logger.log("Reeling...")
            return True
        return False

    def _reel_click(self, bypass=False):
        InputSimulator.random_click(
            bounds=self.display_config.get_center_box_bound(
                width=self.config["random_click_width"],
                height=self.config["random_click_width"]
            ),
            delay=self.config["fishing"]["reel_click_delay"] * random.random(),
            validate_func=None if bypass else self._can_reel
        )
    