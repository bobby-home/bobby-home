import pygame
from subprocess import call

# set volume to max. It's raspberry dependent.
call('amixer set PCM 150% >> /dev/null', shell=True)

pygame.mixer.init()
pygame.mixer.music.set_volume(150.0)
pygame.mixer.music.load("voice-male.mp3")
pygame.mixer.music.play()
while pygame.mixer.music.get_busy() == True:
    continue

pygame.mixer.music.load("alarm-siren.mp3")
pygame.mixer.music.play()
while pygame.mixer.music.get_busy() == True:
    continue
