import uuid
import os

class TempImage:
    def __init__(self, base_path="./pictures", ext=".jpg"):
        rand = uuid.uuid4()
        self.path = os.path.join(base_path , f'{rand}{ext}')

    def cleanup(self):
        # remove the file
        os.remove(self.path)
