from .motion import DetectMotion
from pathlib import Path 
from telegram_bot.send_presence_message import send_message
from sound.sound import Sound
import os

class Camera():
    def __init__(self):
        pass

    def start(self):
        DetectMotion(self._presenceCallback)
    
    def _presenceCallback(self, presence: bool, picture_path: str) -> None:
        print(f'presence: {presence}')
        send_message('Une présence étrangère a été détectée chez vous.', picture_path)
        # s = Sound()
        # s.alarm()
