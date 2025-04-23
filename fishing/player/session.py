from core import Singleton
from logger import Logger
from datetime import datetime
from .client_state import ClientState

class Session(metaclass=Singleton):
    def __init__(self):
        # STATUS
        self.hurt = False
        self.hungry = False
        self.reeling = False
        self.eating = False

        # META
        self.total_fish_encountered = 0
        self.total_fish_caught = 0
        self.last_fish = datetime.now()
        self.last_reel = None
        self.consecutive_idles = 0

        # Random Sleep
        self.random_sleep = False
        self.last_wake = None
        self.sleeping = False
        self.sleep_begin = None

        self.min_active = None
        self.max_active = None
        self.sleep_duration = None
        self.next_active = None

        # LOGGER
        self.logger = Logger()
        self.client_state = ClientState()
    
    @property
    def time_since_last_reel(self):
        if not self.last_reel:
            return -1

        now = datetime.now()
        duration = now - self.last_reel

        return duration.total_seconds()

    @property
    def time_since_last_fish(self):
        now = datetime.now()
        duration = now - self.last_fish

        return duration.total_seconds()
    
    def update_health(self, screen_state):
        self.hurt = screen_state.hurt_indicator_present
        self.hungry = screen_state.hunger_indicator_present
    
    def reset_session(self):
        self.__init__()
    
    def log_state(self, message=None):
        now = datetime.now()
        state_str = f"""**CLIENT**
- toggle = {self.client_state.toggle}
- discord toggle = {self.client_state.discord_toggle}

**STATUS**
- hurt = {self.hurt}
- hungry = {self.hungry}
- reeling = {self.reeling}
- eating = {self.eating}

**SESSION**
- fish encountered = {self.total_fish_encountered}
- fish caught = {self.total_fish_caught}
- last fish = {(now - self.last_fish).total_seconds()}s ago
- last reel = {"-1" if not self.last_reel else (now - self.last_reel).total_seconds()}s ago

**RANDOM SLEEP**
- enabled = {self.random_sleep}
- sleeping = {self.sleeping}
- last wake = {"-1" if not self.last_wake else (now - self.last_wake).total_seconds()}s ago
- sleep begin = {"-1" if not self.sleep_begin else (now - self.sleep_begin).total_seconds()}s ago
- min active = {self.min_active}min
- max active = {self.max_active}min
- sleep duration = {self.sleep_duration}min"""
        
        self.logger.log_action(state_str)