from sound.sound import Sound


class PlaySound():
    def __init__(self):
        self._start()

    def _start(self):
        s = Sound()
        s.alarm()
