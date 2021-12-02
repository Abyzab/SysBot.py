import os
import json

from typing import List

class JsonHandler:

    def __init__(self, path: str, changeDir: bool = False) -> None:
        if changeDir:
            self.dir_path = path
        else:
            self.dir_path = f"{os.path.abspath(os.curdir)}/bots/utils/jsons/{path}.json"
        with open(self.dir_path, 'r') as file:
            self.settings = json.loads(file.read())

    def __getitem__(self, key: str) -> str:
        return self.settings[key]
    
    def __setitem__(self, key: str, value: str) -> str:
        self.settings[key] = value
        self.updateSettings()
  
    def getSettings(self) -> List:
        return self.settings
    
    def updateSettings(self) -> None:     
        with open(self.dir_path, 'w') as file:
            json.dump(self.settings, file, indent=4)
