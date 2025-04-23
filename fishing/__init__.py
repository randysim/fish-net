from .fishing_client import FishingClient
from .display.display_config import DisplayConfig
from .discord.event_handler import EventHandler
from core import ConfigLoader, InputListener
from logger import Logger

def create_fishing_client(config_path):
    print("Creating Fishing Client.")

    # Initialize Singletons
    ConfigLoader(config_path=config_path)
    InputListener()
    Logger(EventHandler())
    DisplayConfig()

    return FishingClient()