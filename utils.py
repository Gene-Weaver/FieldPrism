#!/usr/bin/env python3
import os, yaml, datetime, cv2

# https://stackoverflow.com/questions/287871/how-do-i-print-colored-text-to-the-terminal
'''
CEND      = '\33[0m'
CBOLD     = '\33[1m'
CITALIC   = '\33[3m'
CURL      = '\33[4m'
CBLINK    = '\33[5m'
CBLINK2   = '\33[6m'
CSELECTED = '\33[7m'

CBLACK  = '\33[30m'
CRED    = '\33[31m'
CGREEN  = '\33[32m'
CYELLOW = '\33[33m'
CBLUE   = '\33[34m'
CVIOLET = '\33[35m'
CBEIGE  = '\33[36m'
CWHITE  = '\33[37m'

CBLACKBG  = '\33[40m'
CREDBG    = '\33[41m'
CGREENBG  = '\33[42m'
CYELLOWBG = '\33[43m'
CBLUEBG   = '\33[44m'
CVIOLETBG = '\33[45m'
CBEIGEBG  = '\33[46m'
CWHITEBG  = '\33[47m'

CGREY    = '\33[90m'
CRED2    = '\33[91m'
CGREEN2  = '\33[92m'
CYELLOW2 = '\33[93m'
CBLUE2   = '\33[94m'
CVIOLET2 = '\33[95m'
CBEIGE2  = '\33[96m'
CWHITE2  = '\33[97m'

CGREYBG    = '\33[100m'
CREDBG2    = '\33[101m'
CGREENBG2  = '\33[102m'
CYELLOWBG2 = '\33[103m'
CBLUEBG2   = '\33[104m'
CVIOLETBG2 = '\33[105m'
CBEIGEBG2  = '\33[106m'
CWHITEBG2  = '\33[107m'
'''

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    REDBG = '\033[101m'
    GREENBG = '\033[102m'

def validate_dir(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)

def load_cfg():
    with open("FieldPrism.yaml", "r") as ymlfile:
        cfg = yaml.full_load(ymlfile)
    return cfg

def get_datetime():
    day = "_".join([str(datetime.datetime.now().strftime("%Y")),str(datetime.datetime.now().strftime("%m")),str(datetime.datetime.now().strftime("%d"))])
    time = "-".join([str(datetime.datetime.now().strftime("%H")),str(datetime.datetime.now().strftime("%M")),str(datetime.datetime.now().strftime("%S"))])
    new_time = "__".join([day,time])
    return new_time

def print_options():
    print("Run FieldPrism: 1")
    print("Test/Wake GPS: 2")
    print("Align Camera: 3")
    print("Redo Previous Image: 4")
    print("Exit: 6")

def rotate_image_options(image,cfg_user):
    # Rotate Camera
    # Can rotate 270 by setting both to True
    if cfg_user['fieldprism']['rotate_camera_180']:
        image = cv2.rotate(image, cv2.ROTATE_180)
    if cfg_user['fieldprism']['rotate_camera_90_clockwise']:
        image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
    return image