#!/usr/bin/env python3

import time, os, stat, subprocess, pprint
from pathlib import Path
import cv2
import depthai as dai
import keyboard
from dataclasses import dataclass
from utils import bcolors, load_cfg, get_datetime
import matplotlib.pyplot as plt
from run_gps import get_gps
import psutil

# print(f"{bcolors.OKGREEN}     {bcolors.ENDC}")

@dataclass
class SetupFP:
    usb_base_path: str = ''
    dir_images_unprocessed: str = ''
    usb_none: str = ''
    usb_1: str = ''
    usb_2: str = ''
    usb_3: str = ''
    usb_4: str = ''
    usb_5: str = ''
    usb_6: str = ''

    has_1_usb: bool = False
    has_2_usb: bool = False
    has_3_usb: bool = False
    has_4_usb: bool = False
    has_5_usb: bool = False
    has_6_usb: bool = False
    save_to_boot: bool = False ######### currrently this overrides the config file

    session_time: str = ''
    name_session_csv: str = ''
    name_total_csv: str = 'FieldPrism_Data.csv'

    dir_data_none: str = ''
    dir_data_1: str = ''
    dir_data_2: str = ''
    dir_data_3: str = ''
    dir_data_4: str = ''
    dir_data_5: str = ''
    dir_data_6: str = ''
    dir_data_session_none: str = ''
    dir_data_session_1: str = ''
    dir_data_session_2: str = ''
    dir_data_session_3: str = ''
    dir_data_session_4: str = ''
    dir_data_session_5: str = ''
    dir_data_session_6: str = ''

    def __post_init__(self) -> None:
        self.usb_base_path = '/media/'# OR '/media/pi/' # os.path.join('media','pi')
        self.dir_images_unprocessed = os.path.join('FieldPrism','Images_Unprocessed')

        self.session_time = get_datetime()
        self.dir_data = os.path.join('FieldPrism','Images_Unprocessed')
        self.dir_data_session = os.path.join('FieldPrism','Images_Unprocessed')


        print(f"{bcolors.HEADER}Base USB Path: {self.usb_base_path}{bcolors.ENDC}")
        print(f"{bcolors.OKCYAN}       Possible USB Devices: {os.listdir(self.usb_base_path)}{bcolors.ENDC}")     
        print(f"")
        print(f"{bcolors.HEADER}Veryifying USB Storage Mount Points...{bcolors.ENDC}")
        print(f"{bcolors.OKCYAN}       /dev/sda1  should pair with  /media/USB1{bcolors.ENDC}")
        print(f"{bcolors.OKCYAN}       /dev/sdb1  should pair with  /media/USB2{bcolors.ENDC}")
        print(f"{bcolors.OKCYAN}       /dev/sdc1  should pair with  /media/USB3{bcolors.ENDC}")
        print(f"{bcolors.OKCYAN}       /dev/sdd1  should pair with  /media/USB4{bcolors.ENDC}")
        print(f"{bcolors.OKCYAN}       /dev/sde1  should pair with  /media/USB5{bcolors.ENDC}")
        print(f"{bcolors.OKCYAN}       /dev/sdf1  should pair with  /media/USB6{bcolors.ENDC}")
        print(f"")
        verify_mount_usb_locations()     
        print(f"")  

        # USB save to all
        device_count = 0
        list_drives = ["/dev/sda1", "/dev/sdb1", "/dev/sdc1", "/dev/sdd1", "/dev/sde1", "/dev/sdf1"]
        list_has_usb = [self.has_1_usb, self.has_2_usb, self.has_3_usb, self.has_4_usb, self.has_5_usb, self.has_6_usb]
        list_usb = [self.usb_1, self.usb_2, self.usb_3, self.usb_4, self.usb_5, self.usb_6]
        for num, p in enumerate(list_drives):
            if isblockdevice(p):
                # if p == "/dev/sda1":
                drive_num = num+1
                path_to_drive = "".join(['/media/USB',str(drive_num),'/'])
                drive_name = "".join(['USB',str(drive_num)])
                if os.path.ismount(path_to_drive):
                    print(f"{bcolors.OKGREEN}       Storage Drive Exists({p}): [{isblockdevice(p)}] and is mounted to ({path_to_drive}): [{os.path.ismount(path_to_drive)}]{bcolors.ENDC}")
                    print(f'self.usb_1 {self.usb_1}')
                    print(f'self.has_1_usb {self.has_1_usb}')
                    exec("%s = %d" % (list_has_usb[num], True))
                    exec("%s = %d" % (list_usb[num], os.path.join(self.usb_base_path, drive_name, self.dir_images_unprocessed)))
                    #
                    #  vars()[list_has_usb[num]] = True
                    # vars()[list_usb[num]] = os.path.join(self.usb_base_path, drive_name, self.dir_images_unprocessed)
                    print(f'self.usb_1 {self.usb_1}')
                    print(f'self.has_1_usb {self.has_1_usb}')
                    print(f"{bcolors.OKGREEN}              Path to USB {str(drive_num)} [{drive_name}]: {list_usb[num]}{bcolors.ENDC}")
                # elif p == "/dev/sdb1":
                #     if os.path.ismount('/media/USB2/'):
                #         print(f"{bcolors.OKGREEN}       Storage Drive Exists({p}): [{isblockdevice(p)}] and is mounted to (/media/USB2/): [{os.path.ismount('/media/USB2/')}]{bcolors.ENDC}")
                #         self.has_2_usb = True
                #         self.usb_2 = os.path.join(self.usb_base_path,'USB2',self.dir_images_unprocessed)
                #         print(f"{bcolors.OKGREEN}              Path to USB 2 [USB2]: {self.usb_2}{bcolors.ENDC}")
                # elif p == "/dev/sdc1":
                #     if os.path.ismount('/media/USB3/'):
                #         print(f"{bcolors.OKGREEN}       Storage Drive Exists({p}): [{isblockdevice(p)}] and is mounted to (/media/USB3/): [{os.path.ismount('/media/USB3/')}]{bcolors.ENDC}")
                #         self.has_3_usb = True
                #         self.usb_3 = os.path.join(self.usb_base_path,'USB3',self.dir_images_unprocessed)
                #         print(f"{bcolors.OKGREEN}              Path to USB 3 [USB3]: {self.usb_3}{bcolors.ENDC}")
                # elif p == "/dev/sdd1":
                #     if os.path.ismount('/media/USB4/'):
                #         print(f"{bcolors.OKGREEN}       Storage Drive Exists({p}): [{isblockdevice(p)}] and is mounted to (/media/USB4/): [{os.path.ismount('/media/USB4/')}]{bcolors.ENDC}")
                #         self.has_4_usb = True
                #         self.usb_4 = os.path.join(self.usb_base_path,'USB4',self.dir_images_unprocessed)
                #         print(f"{bcolors.OKGREEN}              Path to USB 4 [USB4]: {self.usb_4}{bcolors.ENDC}")
                # elif p == "/dev/sde1":
                #     if os.path.ismount('/media/USB5/'):
                #         print(f"{bcolors.OKGREEN}       Storage Drive Exists({p}): [{isblockdevice(p)}] and is mounted to (/media/USB5/): [{os.path.ismount('/media/USB5/')}]{bcolors.ENDC}")
                #         self.has_5_usb = True
                #         self.usb_5 = os.path.join(self.usb_base_path,'USB5',self.dir_images_unprocessed)
                #         print(f"{bcolors.OKGREEN}              Path to USB 5 [USB5]: {self.usb_5}{bcolors.ENDC}")
                # elif p == "/dev/sdf1":
                #     if os.path.ismount('/media/USB6/'):
                #         print(f"{bcolors.OKGREEN}       Storage Drive Exists({p}): [{isblockdevice(p)}] and is mounted to (/media/USB6/): [{os.path.ismount('/media/USB6/')}]{bcolors.ENDC}")
                #         self.has_6_usb = True
                #         self.usb_6 = os.path.join(self.usb_base_path,'USB6',self.dir_images_unprocessed)
                #         print(f"{bcolors.OKGREEN}              Path to USB 6 [USB6]: {self.usb_6}{bcolors.ENDC}")
        device_count = sum([self.save_to_boot, self.has_1_usb, self.has_2_usb, self.has_3_usb, self.has_4_usb, self.has_5_usb, self.has_6_usb])
        print(f"{bcolors.HEADER}Number of storage drives: {device_count}{bcolors.ENDC}")

        if device_count == 0:
            self.print_usb_error()
            self.usb_none = os.path.join('/home','pi','FieldPrism','Data','Images_Unprocessed')
            print(f"{bcolors.FAIL}       {self.usb_none}{bcolors.ENDC}")
            # self.save_to_boot = True
        else:
            print(f"{bcolors.HEADER}Creating Save Directories{bcolors.ENDC}")
            # Will only save to boot device
            if not self.has_1_usb and not self.has_2_usb and not self.has_3_usb and not self.has_4_usb and not self.has_5_usb and not self.has_6_usb and self.save_to_boot:
                print(f"{bcolors.WARNING}WARNING: Only saving to microSD card. Recommend adding USB storage and trying again!{bcolors.ENDC}")
                print(f"{bcolors.WARNING}       Creating (or verifying): {self.usb_none}{bcolors.ENDC}")
                Path(self.usb_none).mkdir(parents=True, exist_ok=True)
            # No storage selected
            elif not self.has_1_usb and not self.has_2_usb  and not self.has_3_usb  and not self.has_4_usb  and not self.has_5_usb  and not self.has_6_usb and not self.save_to_boot:
                print(f"{bcolors.FAIL}ERROR: NO STORAGE DETECTED. DATA WILL NOT BE SAVED ANYWHERE!!!{bcolors.ENDC}")
                print(f"{bcolors.FAIL}       Power off device, add storage, try again. Or edit FieldPrism.yaml: always_save_to_boot = True{bcolors.ENDC}")
            if self.has_1_usb:
                print(f"{bcolors.OKGREEN}       Creating (or verifying): {self.usb_1}{bcolors.ENDC}")
                Path(self.usb_1).mkdir(parents=True, exist_ok=True)
            if self.has_2_usb:
                print(f"{bcolors.OKGREEN}       Creating (or verifying): {self.usb_2}{bcolors.ENDC}")
                Path(self.usb_2).mkdir(parents=True, exist_ok=True)
            if self.has_3_usb:
                print(f"{bcolors.OKGREEN}       Creating (or verifying): {self.usb_3}{bcolors.ENDC}")
                Path(self.usb_3).mkdir(parents=True, exist_ok=True)
            if self.has_4_usb:
                print(f"{bcolors.OKGREEN}       Creating (or verifying): {self.usb_4}{bcolors.ENDC}")
                Path(self.usb_4).mkdir(parents=True, exist_ok=True)
            if self.has_5_usb:
                print(f"{bcolors.OKGREEN}       Creating (or verifying): {self.usb_5}{bcolors.ENDC}")
                Path(self.usb_5).mkdir(parents=True, exist_ok=True)
            if self.has_6_usb:
                print(f"{bcolors.OKGREEN}       Creating (or verifying): {self.usb_6}{bcolors.ENDC}")
                Path(self.usb_6).mkdir(parents=True, exist_ok=True)

    def print_usb_error(self) -> None:
        print(f"{bcolors.FAIL}ERROR: USB device/s not mounted correctly. {bcolors.ENDC}")
        print(f"")
        print(f"{bcolors.FAIL}       For 1 USB use command: {bcolors.ENDC}")
        print(f"{bcolors.FAIL}              udisksctl mount -b /dev/sda1{bcolors.ENDC}")
        print(f"{bcolors.FAIL}       For 2 USBs use commands: {bcolors.ENDC}")
        print(f"{bcolors.FAIL}              udisksctl mount -b /dev/sda1{bcolors.ENDC}")
        print(f"{bcolors.FAIL}              udisksctl mount -b /dev/sdb1{bcolors.ENDC}")
        print(f"")
        print(f"{bcolors.FAIL}       Quit and mount USB device/s otherwise images will{bcolors.ENDC}")
        print(f"{bcolors.FAIL}       save to boot device (microSD card) in:{bcolors.ENDC}")

class ImageData:
    # Path data
    path_to_saved: str = ''
    path_from_fp: str = ''
    path: str = ''
    filename_all: str = ''
    filename_short: str = ''
    filename_ext: str = ''

    # GPS data
    current_time: float = -888
    latitude: float = -888
    longitude: float = -888    
    
    altitude: float = -888
    climb: float = -888
    speed: float = -888

    lat_error_est: float = -888
    lon_error_est: float = -888
    alt_error_est: float = -888

    def __init__(self, path_to_saved: str, GPS_data: object):
        self.path_to_saved = path_to_saved
        self.current_time = GPS_data.current_time
        self.latitude = GPS_data.latitude
        self.longitude = GPS_data.longitude
        self.altitude = GPS_data.altitude
        self.climb = GPS_data.climb
        self.speed = GPS_data.speed
        self.lat_error_est = GPS_data.lat_error_est
        self.lon_error_est = GPS_data.lon_error_est
        self.alt_error_est = GPS_data.alt_error_est

    def __post_init__(self) -> None:
        self.path, self.filename_all = os.path.split(self.path_to_saved)
        self.filename_short = self.filename_all.split('.')[0]
        self.filename_ext = self.filename_all.split('.')[1]
        self.path_from_fp = self.path_to_saved.split(os.path.sep)[3:]
        print(f'self.path_from_fp = {self.path_from_fp}')

def verify_mount_usb_locations():
    print(f"{bcolors.HEADER}List of mounted devices:{bcolors.ENDC}")
    partitions = psutil.disk_partitions()

    for p in partitions:
        print(p.mountpoint)

    print(f"{bcolors.HEADER}Mount Pairs: {bcolors.ENDC}")
    d = {}
    for l in open('/proc/mounts'):
        if l[0] == '/':
            l = l.split()
            print(f"{l[0]} --> {l[1]}")
            d[l[0]] = l[1]


def isblockdevice(path):
  return os.path.exists(path) and stat.S_ISBLK(os.stat(path).st_mode)

def save_image(save_frame, name_time, save_dir):
    fname = "".join([name_time,'.jpg'])
    fname = os.path.join(save_dir,fname)
    cv2.imwrite(fname, save_frame)
    print(f"{bcolors.OKGREEN}       Image Saved: {fname}{bcolors.ENDC}")
    path_to_saved = fname
    return path_to_saved

def route_save_image(Setup,save_frame):
    name_time = str(int(time.time() * 1000))
    if Setup.save_to_boot:
        path_to_saved = save_image(save_frame, name_time, Setup.usb_none)
    if Setup.has_1_usb:
        path_to_saved = save_image(save_frame, name_time, Setup.usb_1)
    if Setup.has_2_usb:
        path_to_saved = save_image(save_frame, name_time, Setup.usb_2)
    if Setup.has_3_usb:
        path_to_saved = save_image(save_frame, name_time, Setup.usb_3)
    if Setup.has_4_usb:
        path_to_saved = save_image(save_frame, name_time, Setup.usb_4)
    if Setup.has_5_usb:
        path_to_saved = save_image(save_frame, name_time, Setup.usb_5)
    if Setup.has_6_usb:
        path_to_saved = save_image(save_frame, name_time, Setup.usb_6)
    return path_to_saved

def align_camera():
    # Create pipeline
    pipeline = dai.Pipeline()
    # Define source and output
    camRgb = pipeline.create(dai.node.ColorCamera)
    camRgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_4_K)
    xoutRgb = pipeline.create(dai.node.XLinkOut)
    camRgb.setIspScale(2,17)
    xoutRgb.setStreamName("preview")
    camRgb.setPreviewSize(426,240)
    camRgb.setInterleaved(False)
    camRgb.setColorOrder(dai.ColorCameraProperties.ColorOrder.RGB)
    # Linking
    camRgb.preview.link(xoutRgb.input)
    # Connect to device and start pipeline
    with dai.Device(pipeline) as device:
        qRgb = device.getOutputQueue('preview', maxSize=1, blocking=False)
        while True: 
            inRgb = qRgb.get()
            cv2.imshow("rgb", cv2.rotate(inRgb.getCvFrame(), cv2.ROTATE_180))
            key = cv2.waitKey(50)
            if keyboard.is_pressed('6'):
                print("main: 1")
                print("align_camera: 3")
                print("Exit: 6")
                break
'''
TODO
    - starting headless
        * restarting main() without power cycle?
    - add redo to key 4
        * overwrite previous image
    - see if USB hub will work 

'''
def main():
    cfg_user = load_cfg()
    # Create pipeline
    pipeline = dai.Pipeline()

    # Define sources and outputs
    camRgb = pipeline.create(dai.node.ColorCamera)
    camRgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_12_MP)
    camRgb.setFps(30)

    ispOut = pipeline.create(dai.node.XLinkOut)
    videoOut = pipeline.create(dai.node.XLinkOut)

    ispOut.setStreamName('isp')
    videoOut.setStreamName('video')

    # Properties
    camRgb.setVideoSize(426, 240)

    # Linking
    camRgb.isp.link(ispOut.input)
    camRgb.video.link(videoOut.input)

    # Connect to device and start pipeline
    with dai.Device(pipeline) as device:
        print('Connected cameras: ', device.getConnectedCameras())
        # Print out usb speed
        print('Usb speed: ', device.getUsbSpeed().name)

        # Make sure the destination path is present before starting to store the examples
        cfg = SetupFP()

        # Get data queues
        ispQueue = device.getOutputQueue('isp', maxSize=1, blocking=False)
        videoQueue = device.getOutputQueue('video', maxSize=1, blocking=False)

        TAKE_PHOTO = False
        while True:
            vidFrames = videoQueue.tryGetAll()
            for vidFrame in vidFrames:
                vframe = vidFrame.getCvFrame()
                vframe = cv2.rotate(vframe, cv2.ROTATE_180)
                cv2.imshow('preview', vframe)

            ispFrames = ispQueue.get()
            isp = ispFrames.getCvFrame()

            if TAKE_PHOTO:
                print(f"       Capturing Image")
                ispFrames = ispQueue.get()
                save_frame = ispFrames.getCvFrame()
                save_frame = cv2.rotate(save_frame, cv2.ROTATE_180)
                # Save
                path_to_saved = route_save_image(cfg,save_frame)
                cv2.imshow('Saved Image', cv2.pyrDown(cv2.pyrDown(cv2.pyrDown(cv2.imread(path_to_saved)))))
                print(f"       GPS Activated")
                GPS_data = get_gps(cfg_user['fieldprism']['gps']['speed'])
                ImageData(path_to_saved,GPS_data)
                TAKE_PHOTO = False
                print(f"{bcolors.OKGREEN}Ready{bcolors.ENDC}")

            key = cv2.waitKey(50)
            if keyboard.is_pressed('6'):
                print(f"{bcolors.HEADER}Stopping...{bcolors.ENDC}")
                print("main: 1")
                print("align_camera: 3")
                print("Exit: 6")
                break
            elif keyboard.is_pressed('1'):
                TAKE_PHOTO = True
                print(f"       Camera Activated")




    

 
def route():
    print("main: 1")
    print("align_camera: 3")
    print("Exit: 6")
    while True:
        key = cv2.waitKey(1)
        if keyboard.is_pressed('6'):
            print(f"{bcolors.HEADER}Exiting FieldPrism{bcolors.ENDC}")
            break
        elif keyboard.is_pressed('1'):
            print("Entering main()")
            main()
        elif keyboard.is_pressed('3'):
            print("Entering align_camera()")
            align_camera()

if __name__ == '__main__':
    route()