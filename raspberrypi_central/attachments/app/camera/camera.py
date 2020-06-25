from camera.motion import DetectMotion
from pathlib import Path 
from tasks import send_telegram_message
from sound.sound import Sound

class Camera():
    def __init__(self):
        pass

    def start(self):
        DetectMotion(self._presenceCallback)

    def _presenceCallback(self, presence: bool, picture_path: str):
        print(f'presence: {presence}')
        send_telegram_message.apply_async(args=['Une présence étrangère a été détectée chez vous.', picture_path])
        # s = Sound()
        # s.alarm()
