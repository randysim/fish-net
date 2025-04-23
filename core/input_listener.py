from .singleton import Singleton
import keyboard

class InputListener(metaclass=Singleton):
    def __init__(self):
        self.binds = {}
        self.command = False

        keyboard.hook(self._handle_key_event)
    
    def bind(self, key, callback, command=False):
        func = callback
        if command:
            func = lambda: self.command and callback()

        self.binds[key] = self.binds.get(key, []) + [func]

    def _on_press(self, event):
        for callback in self.binds.get(event.name, []):
            callback()

    def _handle_key_event(self, event):
        if event.name == 'ctrl':
            self.command = event.event_type == keyboard.KEY_DOWN
            return

        if event.event_type == keyboard.KEY_DOWN:
            self._on_press(event)