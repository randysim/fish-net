from core import Singleton
from ..player.client_state import ClientState

class EventHandler(metaclass=Singleton):
    def __init__(self):
        self.client_state = ClientState()
        self._events = {}
    
    def bind(self, event_name, callback):
        self._events[event_name] = self._events.get(event_name, []) + [callback]
    
    def emit(self, event_name, *args, message=""):
        self.client_state.discord_running = True

        for callback in self._events.get(event_name, []):
            callback(*args, message=message)
        self.client_state.discord_running = False