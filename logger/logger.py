from core import Singleton
from .discord_bot import DiscordAPI
import asyncio

class Logger(metaclass=Singleton):
    def __init__(self, event_handler):
        self.discord_api = DiscordAPI(event_handler)

        self.log("Waiting for discord api...")
        self.discord_api.ready_event.wait()
        self.log("Discord API finished!")
        
    def log_action(self, action, img=None):
        self.log(action)
        self.discord_api.log_action(action, img)
    
    def log_error(self, error, img=None):
        self.log(error)
        self.discord_api.log_error(error, img)
    
    def log_fish(self, description, img=None):
        self.log(description)
        self.discord_api.log_fish(description, img)

    def log(self, msg):
        print(msg)