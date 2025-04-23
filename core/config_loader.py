from .singleton import Singleton
from copy import deepcopy
import json
import os
import time
import threading

# Loads config and listens for changes
class ConfigLoader(metaclass=Singleton):
    def __init__(self, config_path):
        self.config_path = config_path
        self.config = None
        self.last_modified = None
        self._on_modify_binds = []

        self.load()

        self.config_thread = threading.Thread(target=self._listen_config_changes)
        self.config_thread.daemon = True
        self.config_thread.start()

    def load(self):
        with open(self.config_path, 'r') as f:
            if self.config:
                self._deep_update(self.config, json.load(f))
            else:
                self.config = json.load(f)

            self.last_modified = os.path.getmtime(self.config_path)
    
    def bind(self, callback):
        self._on_modify_binds.append(callback)

    def _listen_config_changes(self):
            while True:
                if self._did_file_change():
                    print("Config file changed. Reloading.")
                    self._call_modify_binds()
                    self.load()
                time.sleep(1)

    def _did_file_change(self):
        last_modified = os.path.getmtime(self.config_path)
        return last_modified != self.last_modified
    
    def _deep_update(self, original, update):
        for key, value in update.items():
            if isinstance(value, dict) and key in original and isinstance(original[key], dict):
                self._deep_update(original[key], value)
            else:
                original[key] = deepcopy(value)
    
    def _call_modify_binds(self):
        for callback in self._on_modify_binds:
            callback()