from core import ConfigLoader, InputListener, Singleton
from logger import Logger
from .display.screen_grabber import ScreenGrabber
from .display.screen_state import ScreenState
from .player.session import Session
from .player.reel_helper import ReelHelper
from .player.food_helper import FoodHelper
from .player.fail_safe import FailSafe
from .player.client_state import ClientState
from .discord.event_handler import EventHandler
import time

class FishingClient(metaclass=Singleton):
    def __init__(self):
        # Your initialization code here
        self.config = ConfigLoader().config['client']

        # INPUT
        self.input_listener = InputListener()

        # DISPLAY
        self.screen_grabber = ScreenGrabber()
        self.screen_state = ScreenState()
        
        # PLAYER
        self.session = Session()
        self.reel_helper = ReelHelper(self.session, self.screen_state)
        self.food_helper = FoodHelper(self.session, self.screen_state)
        self.fail_safe = FailSafe(self.session, self.reel_helper, quit_func=self._quit)

        # CLIENT
        self.client_state = ClientState()
        self._bind_keys()

        # LOGGER
        self.logger = Logger()

        # DISCORD
        self.event_handler = EventHandler()
        self.event_handler.bind("toggle", self._discord_toggle)
        self.event_handler.bind("quitgame", self.fail_safe.quit_game)
        self.event_handler.bind("randomsleep", self.fail_safe.randomsleep)
        self.event_handler.bind("disablerandomsleep", self.fail_safe.disablerandomsleep)
        self.event_handler.bind("sendmessage", self.fail_safe.send_message)
        self.event_handler.bind("ss", self.fail_safe.screenshot)
        self.event_handler.bind("state", self.session.log_state)

    def run(self):
        # Your main loop code here
        self.logger.log_action("Running FishNet Client. Press ctrl + q to quit. Press ctrl + f1 to toggle.")

        while not self.client_state.quit:
            if not self.client_state.running:
                time.sleep(self.config['sleep_time'])
                continue
            
            px = self.screen_grabber.grab_screen()
            
            # update player health
            self.screen_state.update_state(px)
            self.session.update_health(self.screen_state)

            # EATING
            if self.session.eating:
                self.food_helper.eat(
                    callback=self.reel_helper.recast_rod,
                    failure_callback=self.fail_safe.quit_game
                )
                time.sleep(self.config['eating']['eat_delay'])
                continue
            
            # don't count random sleep when fishing is toggled
            if self.session.random_sleep and self.client_state.discord_toggle:
                self.fail_safe.parse_randomsleep()

            # REELING
            if self.session.reeling and self.client_state.discord_toggle and not self.session.sleeping:
                self.reel_helper.reel()
            elif ( # DETECTED A FISH
                self.screen_state.fish_indicator_present and 
                not self.screen_state.catch_indicator_present and
                self.fail_safe.next_fish_possible() and 
                self.client_state.discord_toggle and 
                not self.session.sleeping
            ):
                self.screen_grabber.save_fish()
                self.logger.log_action("Detected a fish!", self.screen_grabber.last_fish_img)
                self.session.total_fish_encountered += 1
                self.reel_helper.begin_reel()
            elif self.session.hungry: # DETECTED HUNGER
                self.food_helper.begin_eating()
            elif self.client_state.discord_toggle and not self.session.sleeping: # GENERIC FAIL TESTS
                self.fail_safe.test_fish_idle()

            time.sleep(self.config['sleep_time'])

    def _bind_keys(self):
        self.input_listener.bind(
            key='q',
            callback=self._quit,
            command=True
        )

        self.input_listener.bind(
            key='f1',
            callback=self._toggle,
            command=True
        )

    def _toggle(self):
        self.client_state.toggle = not self.client_state.toggle
        self.session.reset_session()
        self.food_helper.reset()

        toggle_str = f"Client is now {'On' if self.client_state.toggle else 'Off.'}"
        self.logger.log_action(toggle_str)

        if self.client_state.toggle:
            self.reel_helper.recast_rod()
        else:
            self.reel_helper.uncast_rod()

    def _discord_toggle(self, message=None):
        if not self.client_state.toggle:
            self.logger.log_action("Failed to toggle from discord. Client is off on computer.")
            return

        self.client_state.discord_toggle = not self.client_state.discord_toggle
        self.session.reset_session()
        self.food_helper.reset()

        toggle_str = f"Fishing is now {'On' if self.client_state.discord_toggle else 'Off. Will still eat food.'}"
        self.logger.log_action(toggle_str)

        # eating is still enabled within discord toggle, don't override it.
        if not self.session.eating:
            if self.client_state.discord_toggle:
                self.reel_helper.recast_rod(bypass=True) # need to bypass when running in separate thread
            else:
                self.reel_helper.uncast_rod(bypass=True)
    
    def _quit(self):
        self.logger.log_action("Qutting client...")
        self.client_state.quit = True