import pygame
from subprocess import call

class Sound():
    def __init__(self):
        # set volume to max. It's raspberry dependent.
        # call('amixer set PCM 150% >> /dev/null', shell=True)

        pygame.mixer.init()
        pygame.mixer.music.set_volume(150.0)

    def alarm(self):
        # doesn't work without the while loop.
        # but this is strange...

        pygame.mixer.music.load("sound/voice-male.mp3")
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy() == True:
            continue

        while True:
            pygame.mixer.music.load("sound/alarm-siren.mp3")
            pygame.mixer.music.play(1)
            while pygame.mixer.music.get_busy() == True:
                continue
