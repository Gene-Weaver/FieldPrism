import os, time
from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame

class Sounds():
    sound_init = None
    sound_complete = None
    sound_leave = None
    volume = None

    def __init__(self, dir_root, cfg_user) -> None:
        pygame.mixer.init() # add this line
        self.sound_init = pygame.mixer.Sound(os.path.join(dir_root,'fieldstation','sound', 'beep.ogg'))
        self.sound_complete = pygame.mixer.Sound(os.path.join(dir_root,'fieldstation','sound', 'sharp.wav'))
        self.sound_leave = pygame.mixer.Sound(os.path.join(dir_root,'fieldstation','sound', 'blurp.wav'))
        self.volume = set_volume(cfg_user)

def set_volume(cfg_user):
    volume_user = cfg_user['fieldstation']['sound']['volume']
    if volume_user == 'high':
        volume = 1.0
    elif volume_user == 'mid':
        volume = 0.50
    elif volume_user == 'low':
        volume = 0.20
    else:
        volume = 0.50
    return volume

def sound_start(S):
    pygame.mixer.Sound.play(S.sound_init).set_volume(S.volume)
    time.sleep(0.75)
    pygame.mixer.Sound.play(S.sound_init).set_volume(S.volume)

def sound_taking_photo(S):
    pygame.mixer.Sound.play(S.sound_init).set_volume(S.volume)

def sound_storage_error(S):
    pygame.mixer.Sound.play(S.sound_leave).set_volume(S.volume)
    time.sleep(.5)
    pygame.mixer.Sound.play(S.sound_leave).set_volume(S.volume)
    time.sleep(.5)
    pygame.mixer.Sound.play(S.sound_leave).set_volume(S.volume)
    time.sleep(.5)
    pygame.mixer.Sound.play(S.sound_leave).set_volume(S.volume)
    time.sleep(.5)

def sound_photo_complete(S):
    pygame.mixer.Sound.play(S.sound_init).set_volume(S.volume)
    time.sleep(0.75)
    pygame.mixer.Sound.play(S.sound_init).set_volume(S.volume)

def sound_exit(S):
    pygame.mixer.Sound.play(S.sound_leave).set_volume(S.volume)
    time.sleep(.5)
    pygame.mixer.Sound.play(S.sound_leave).set_volume(S.volume)
    time.sleep(.5)
    pygame.mixer.Sound.play(S.sound_leave).set_volume(S.volume)
    time.sleep(.5)
    pygame.mixer.Sound.play(S.sound_leave).set_volume(S.volume)
    time.sleep(.5)

def sound_gps_fail(S):
    pygame.mixer.Sound.play(S.sound_leave).set_volume(S.volume)
    time.sleep(.5)
    pygame.mixer.Sound.play(S.sound_leave).set_volume(S.volume)
    time.sleep(.5)
    pygame.mixer.Sound.play(S.sound_leave).set_volume(S.volume)
    time.sleep(.5)
    pygame.mixer.Sound.play(S.sound_leave).set_volume(S.volume)

def sound_gps_success(S):
    pygame.mixer.Sound.play(S.sound_init).set_volume(S.volume)
    time.sleep(0.75)
    pygame.mixer.Sound.play(S.sound_init).set_volume(S.volume)