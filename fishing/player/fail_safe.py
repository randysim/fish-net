from core import ConfigLoader, InputSimulator
from logger import Logger
from ..display.screen_grabber import ScreenGrabber
from .client_state import ClientState
from datetime import datetime
import random
import time

class FailSafe:
    def __init__(self, player_session, reel_helper, quit_func):
        self.config = ConfigLoader().config["client"]
        self.player_session = player_session
        self.client_state = ClientState()
        self.reel_helper = reel_helper
        self._quit_client = quit_func
        self.screen_grabber = ScreenGrabber()

        self.logger = Logger()

    def test_fish_idle(self):
        if self.player_session.time_since_last_fish >= self.config["fishing"]["max_idle_seconds"]:
            if self.player_session.consecutive_idles >= self.config["fishing"]["max_consecutive_idles"]:
                self.logger.log_error(
                    "Program Idled. Here is the last screen. Exiting Roblox...", 
                    self.screen_grabber.last_screen
                )
                self.quit_game()
                return

            self.logger.log_error(
                f"No fish detected for {self.config['fishing']['max_idle_seconds']} seconds. Here is the last screen.",
                self.screen_grabber.last_screen
            )
            self.player_session.last_fish = datetime.now()
            self.reel_helper.recast_rod()
            self.player_session.consecutive_idles += 1
            self.logger.log_error(f"Client encountered {self.player_session.consecutive_idles} consecutives idles...")

    def next_fish_possible(self):
        return self.player_session.time_since_last_fish >= self.config["fishing"]["min_idle_seconds"]
    
    def quit_game(self, message=None):
        InputSimulator.queue_inputs(
            inputs=["click", "esc", "l", "enter"],
            delay=1
        )
        self._quit_client()
    
    def send_message(self, message=""):
        message = " ".join(message.split(" ")[1:])
        self.logger.log_action("Sending Message: " + message)
        InputSimulator.queue_inputs(
            inputs=["click", "/"] + list(message) + ["enter"],
            delay=0.1
        )

        if (
            self.client_state.discord_toggle and
            not self.player_session.eating and
            not self.player_session.sleeping
        ):
            time.sleep(0.2)
            self.reel_helper.recast_rod(bypass=True) 

    def randomsleep(self, min_active, max_active, sleep_duration, message=None):
        if not min_active.isnumeric() or not max_active.isnumeric() or not sleep_duration.isnumeric():
            self.logger.log_error("Invalid random sleep parameters provided.")
            return

        if self.player_session.random_sleep:
            self.logger.log_error("Random sleep is already enabled. Please disable it to re-enable it.")
            return

        min_active = int(min_active)
        max_active = int(max_active)
        sleep_duration = int(sleep_duration)

        self.player_session.min_active = min_active
        self.player_session.max_active = max_active
        self.player_session.next_active = random.randint(min_active, max_active)
        self.player_session.sleep_duration = sleep_duration
        
        self.player_session.random_sleep = True
        self.player_session.last_wake = datetime.now()

        self.logger.log_action(f"Random sleeping with following params:\n- min_active={min_active}min\n- max_active={max_active}min\n- sleep_duration={sleep_duration}min")
    
    def parse_randomsleep(self):
        now = datetime.now()
        
        if not self.player_session.sleeping:
            diff = now - self.player_session.last_wake
            minutes = diff.total_seconds() / 60

            if minutes >= self.player_session.next_active:
                self.player_session.sleeping = True
                self.player_session.sleep_begin = now
                self.logger.log_action(f"Random sleeping for {self.player_session.sleep_duration}min")

                if not self.player_session.eating:
                    self.reel_helper.uncast_rod(bypass=True)
        else:
            diff = now - self.player_session.sleep_begin
            minutes = diff.total_seconds() / 60

            if minutes >= self.player_session.sleep_duration:
                self.player_session.next_active = random.randint(self.player_session.min_active, self.player_session.max_active)
                self.player_session.sleeping = False
                self.player_session.last_wake = now
                self.logger.log_action(f"Waking up for {self.player_session.next_active}min")

                if not self.player_session.eating:
                    self.reel_helper.recast_rod(bypass=True)

    def disablerandomsleep(self, message=None):
        if not self.player_session.random_sleep:
            self.logger.log_error("Random sleeping is not enabled.")
            return

        old_sleep = self.player_session.sleeping

        self.player_session.random_sleep = False
        self.player_session.last_wake = None
        self.player_session.sleeping = False
        self.player_session.sleep_begin = None

        self.player_session.min_active = None
        self.player_session.max_active = None
        self.player_session.next_active = None
        self.player_session.sleep_duration = None

        self.logger.log_action("Random sleep disabled.")

        if old_sleep and not self.player_session.eating and self.client_state.discord_toggle:
            self.reel_helper.recast_rod(bypass=True)
    
    def screenshot(self, message=None):
        if not self.screen_grabber.last_screen:
            self.screen_grabber.grab_screen()
        self.logger.log_action("Took a screenshot!", self.screen_grabber.last_screen)