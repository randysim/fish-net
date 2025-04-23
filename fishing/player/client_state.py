from core import Singleton

class ClientState(metaclass=Singleton):
    def __init__(self):
        self._toggle = False
        self._discord_toggle = False

        self.quit = False
        self.discord_running = False
    
    @property
    def toggle(self):
        return self._toggle
    
    @toggle.setter
    def toggle(self, new_value):
        self._toggle = new_value
        self._discord_toggle = new_value
    
    @property
    def discord_toggle(self):
        return self._discord_toggle and self._toggle
    
    @discord_toggle.setter
    def discord_toggle(self, new_value):
        if self._toggle:
            self._discord_toggle = new_value
        else:
            self._discord_toggle = False

    @property
    def running(self):
        return self.toggle and not self.quit and not self.discord_running