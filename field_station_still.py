#!/usr/bin/env python3

import time, os, stat, subprocess, pprint
from pathlib import Path
import cv2
import depthai as dai
import keyboard
from dataclasses import dataclass
from utils import bcolors, load_cfg
import matplotlib.pyplot as plt
from run_gps import get_gps
import psutil

# print(f"{bcolors.OKGREEN}     {bcolors.ENDC}")

@dataclass
class SetupFP():
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

    def __post_init__(self) -> None:
        self.usb_base_path = '/media/'# OR '/media/pi/' # os.path.join('media','pi')
        self.dir_images_unprocessed = os.path.join('FieldPrism','Images_Unprocessed')

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
        for p in ["/dev/sda1", "/dev/sdb1", "/dev/sdc1", "/dev/sdd1", "/dev/sde1", "/dev/sdf1"]:
            if isblockdevice(p):
                if p == "/dev/sda1":
                    if os.path.ismount('/media/USB1/'):
                        print(f"{bcolors.OKGREEN}       Storage Drive Exists({p}): [{isblockdevice(p)}] and is mounted to (/media/USB1/): [{os.path.ismount('/media/USB1/')}]{bcolors.ENDC}")
                        self.has_1_usb = True
                        self.usb_1 = os.path.join(self.usb_base_path,'USB1',self.dir_images_unprocessed)
                        print(f"{bcolors.OKGREEN}              Path to USB 1 [USB1]: {self.usb_1}{bcolors.ENDC}")
                elif p == "/dev/sdb1":
                    if os.path.ismount('/media/USB2/'):
                        print(f"{bcolors.OKGREEN}       Storage Drive Exists({p}): [{isblockdevice(p)}] and is mounted to (/media/USB2/): [{os.path.ismount('/media/USB2/')}]{bcolors.ENDC}")
                        self.has_2_usb = True
                        self.usb_2 = os.path.join(self.usb_base_path,'USB2',self.dir_images_unprocessed)
                        print(f"{bcolors.OKGREEN}              Path to USB 2 [USB2]: {self.usb_2}{bcolors.ENDC}")
                elif p == "/dev/sdc1":
                    if os.path.ismount('/media/USB3/'):
                        print(f"{bcolors.OKGREEN}       Storage Drive Exists({p}): [{isblockdevice(p)}] and is mounted to (/media/USB3/): [{os.path.ismount('/media/USB3/')}]{bcolors.ENDC}")
                        self.has_3_usb = True
                        self.usb_3 = os.path.join(self.usb_base_path,'USB3',self.dir_images_unprocessed)
                        print(f"{bcolors.OKGREEN}              Path to USB 3 [USB3]: {self.usb_3}{bcolors.ENDC}")
                elif p == "/dev/sdd1":
                    if os.path.ismount('/media/USB4/'):
                        print(f"{bcolors.OKGREEN}       Storage Drive Exists({p}): [{isblockdevice(p)}] and is mounted to (/media/USB4/): [{os.path.ismount('/media/USB4/')}]{bcolors.ENDC}")
                        self.has_4_usb = True
                        self.usb_4 = os.path.join(self.usb_base_path,'USB4',self.dir_images_unprocessed)
                        print(f"{bcolors.OKGREEN}              Path to USB 4 [USB4]: {self.usb_4}{bcolors.ENDC}")
                elif p == "/dev/sde1":
                    if os.path.ismount('/media/USB5/'):
                        print(f"{bcolors.OKGREEN}       Storage Drive Exists({p}): [{isblockdevice(p)}] and is mounted to (/media/USB5/): [{os.path.ismount('/media/USB5/')}]{bcolors.ENDC}")
                        self.has_5_usb = True
                        self.usb_5 = os.path.join(self.usb_base_path,'USB5',self.dir_images_unprocessed)
                        print(f"{bcolors.OKGREEN}              Path to USB 5 [USB5]: {self.usb_5}{bcolors.ENDC}")
                elif p == "/dev/sdf1":
                    if os.path.ismount('/media/USB6/'):
                        print(f"{bcolors.OKGREEN}       Storage Drive Exists({p}): [{isblockdevice(p)}] and is mounted to (/media/USB6/): [{os.path.ismount('/media/USB6/')}]{bcolors.ENDC}")
                        self.has_6_usb = True
                        self.usb_6 = os.path.join(self.usb_base_path,'USB6',self.dir_images_unprocessed)
                        print(f"{bcolors.OKGREEN}              Path to USB 6 [USB6]: {self.usb_6}{bcolors.ENDC}")
        device_count = sum([self.save_to_boot, self.has_1_usb, self.has_2_usb, self.has_3_usb, self.has_4_usb, self.has_5_usb, self.has_6_usb])
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

        # # USB
        # usb_dir = os.listdir(self.usb_base_path)
        # for d in usb_dir:
        #     print(f'd = {d}')
        #     if 'USB' in d:
        #         try: 
        #             print(d.split('USB'))
        #             print(d.split('USB')[1])
        #             # os.mkdir(os.path.join(self.usb_base_path, d, self.dir_images_unprocessed, 'EmptyFolder'))
        #             if '1' in d:
        #                 print('try loop2')
        #                 new_dir1 = os.path.join(self.usb_base_path, d, self.dir_images_unprocessed, 'EmptyFolder')
        #                 print(f'making dir = {new_dir1}')
        #                 os.mkdir(os.path.join(self.usb_base_path, d, self.dir_images_unprocessed, 'EmptyFolder'))
        #                 os.rmdir(os.path.join(self.usb_base_path, d, self.dir_images_unprocessed, 'EmptyFolder'))
        #                 self.has_1_usb = True
        #                 print('pass try loop2')
        #             elif '2' in d:
        #                 print('try loop3')
        #                 new_dir2 = os.path.join(self.usb_base_path, d, self.dir_images_unprocessed, 'EmptyFolder')
        #                 print(f'making dir = {new_dir2}')
        #                 os.mkdir(os.path.join(self.usb_base_path, d, self.dir_images_unprocessed, 'EmptyFolder'))
        #                 os.rmdir(os.path.join(self.usb_base_path, d, self.dir_images_unprocessed, 'EmptyFolder'))
        #                 self.has_2_usb = True
        #                 print('pass try loop3')
        #         except Exception as e:
        #             print(f'Fail try loop {e}')
        #             pass
        #     else:
        #         print(f'(USB) not in {d}')

        # if self.has_1_usb and not self.has_2_usb:
        #     self.usb_1 = os.path.join(self.usb_base_path,os.listdir(self.usb_base_path)[0],self.dir_images_unprocessed)
        #     print(f"{bcolors.OKGREEN}       Path to USB 1 [USB1]: {self.usb_1}{bcolors.ENDC}")

        # elif self.has_2_usb and not self.has_1_usb:
        #     self.usb_2 = os.path.join(self.usb_base_path,os.listdir(self.usb_base_path)[1],self.dir_images_unprocessed)
        #     print(f"{bcolors.OKGREEN}       Path to USB 1 [USB2]: {self.usb_2}{bcolors.ENDC}")

        # elif self.has_2_usb and self.has_1_usb:
        #     self.usb_1 = os.path.join(self.usb_base_path,'USB1',self.dir_images_unprocessed)
        #     self.usb_2 = os.path.join(self.usb_base_path,'USB2',self.dir_images_unprocessed)
        #     print(f"{bcolors.OKGREEN}       Path to USB 1 [USB1]: {self.usb_1}{bcolors.ENDC}")
        #     print(f"{bcolors.OKGREEN}       Path to USB 2 [USB2]: {self.usb_2}{bcolors.ENDC}")

        # else:
        #     self.print_usb_error()
        #     self.usb_none = os.path.join('/home','pi','FieldPrism','Data','Images_Unprocessed')
        #     print(f"{bcolors.FAIL}            {self.usb_none}{bcolors.ENDC}")
        #     self.save_to_boot = True

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
    # pprint.pprint(d)

    # result = subprocess.run(["sh", "./check_mounts.sh"], stderr=subprocess.PIPE, text=True)
    # print(result.stderr) # normal to see an error if this is printed, but usually there is no concern

def isblockdevice(path):
  return os.path.exists(path) and stat.S_ISBLK(os.stat(path).st_mode)

def save_image(save_frame, name_time, save_dir):
    fname = "".join([name_time,'.jpg'])
    fname = os.path.join(save_dir,fname)
    cv2.imwrite(fname, save_frame)
    print(f"{bcolors.OKGREEN}       Image Saved: {fname}{bcolors.ENDC}")

def route_save_image(Setup,save_frame):
    name_time = str(int(time.time() * 1000))
    if Setup.save_to_boot:
        save_image(save_frame, name_time, Setup.usb_none)
    if Setup.has_1_usb:
        save_image(save_frame, name_time, Setup.usb_1)
    if Setup.has_2_usb:
        save_image(save_frame, name_time, Setup.usb_2)
    if Setup.has_3_usb:
        save_image(save_frame, name_time, Setup.usb_3)
    if Setup.has_4_usb:
        save_image(save_frame, name_time, Setup.usb_4)
    if Setup.has_5_usb:
        save_image(save_frame, name_time, Setup.usb_5)
    if Setup.has_6_usb:
        save_image(save_frame, name_time, Setup.usb_6)

def align_camera():
    # Create pipeline
    pipeline = dai.Pipeline()

    # Define source and output
    camRgb = pipeline.create(dai.node.ColorCamera)
    xoutRgb = pipeline.create(dai.node.XLinkOut)

    xoutRgb.setStreamName("preview")
    camRgb.setPreviewSize(426,240)
    camRgb.setInterleaved(False)
    camRgb.setColorOrder(dai.ColorCameraProperties.ColorOrder.RGB)
    camRgb.setFps(12)

    # Linking
    camRgb.preview.link(xoutRgb.input)

    # Connect to device and start pipeline
    with dai.Device(pipeline) as device:
        qRgb = device.getOutputQueue('preview', maxSize=1, blocking=False)

        while True:
            
            inRgb = qRgb.get()
            # plt.imshow(cv2.rotate(inRgb.getCvFrame(), cv2.ROTATE_180))
            cv2.imshow("rgb", cv2.rotate(inRgb.getCvFrame(), cv2.ROTATE_180))
            # time.sleep(1)

            # if inRgb is not None:
            #     save_frame = inRgb.getCvFrame()
            #     # 4k / 4
            #     # frame = cv2.pyrDown(save_frame)
            #     # frame = cv2.pyrDown(frame)
            #     cv2.imshow("rgb", cv2.rotate(save_frame, cv2.ROTATE_180))

            # cv2.imshow("rgb", inRgb.getCvFrame())
            key = cv2.waitKey(50)
            if keyboard.is_pressed('6'):
                break
'''
TODO
    - hotspot / offline
    - starting headless
        * restarting main() without power cycle?
    - add redo to key 4
        * overwrite previous image
    - add GPS
    - see if USB hub will work 

'''
def main():
    cfg_user = load_cfg()
    # Create pipeline
    pipeline = dai.Pipeline()

    # Define sources and outputs
    camRgb = pipeline.create(dai.node.ColorCamera)
    camRgb.setPreviewSize(426, 240)
    camRgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_12_MP)
    # camRgb.setIspScale(2,6) # 1080P -> 720P
    stillEncoder = pipeline.create(dai.node.VideoEncoder)

    controlIn = pipeline.create(dai.node.XLinkIn)
    configIn = pipeline.create(dai.node.XLinkIn)
    ispOut = pipeline.create(dai.node.XLinkOut)
    videoOut = pipeline.create(dai.node.XLinkOut)
    stillMjpegOut = pipeline.create(dai.node.XLinkOut)

    controlIn.setStreamName('control')
    configIn.setStreamName('config')
    ispOut.setStreamName('isp')
    videoOut.setStreamName('video')
    stillMjpegOut.setStreamName('still')

    # Properties
    # camRgb.setVideoSize(4032, 3040)
    camRgb.setVideoSize(426, 240)
    stillEncoder.setDefaultProfilePreset(1, dai.VideoEncoderProperties.Profile.MJPEG)

    # Linking
    camRgb.isp.link(ispOut.input)
    camRgb.still.link(stillEncoder.input)
    camRgb.video.link(videoOut.input)
    controlIn.out.link(camRgb.inputControl)
    configIn.out.link(camRgb.inputConfig)
    stillEncoder.bitstream.link(stillMjpegOut.input)

    # Connect to device and start pipeline
    with dai.Device(pipeline) as device:
        print('Connected cameras: ', device.getConnectedCameras())
        # Print out usb speed
        print('Usb speed: ', device.getUsbSpeed().name)

        # Make sure the destination path is present before starting to store the examples
        cfg = SetupFP()

        # Get data queues
        controlQueue = device.getInputQueue('control')
        configQueue = device.getInputQueue('config')
        ispQueue = device.getOutputQueue('isp', maxSize=1, blocking=False)
        videoQueue = device.getOutputQueue('video', maxSize=1, blocking=False)
        stillQueue = device.getOutputQueue('still', maxSize=1, blocking=True)

        # Output queue will be used to get the rgb frames from the output defined above
        # qRgb = device.getOutputQueue(name="rgb", maxSize=30, blocking=False)
        # qStill = device.getOutputQueue(name="still", maxSize=30, blocking=True)
        # qControl = device.getInputQueue(name="control")

        TAKE_PHOTO = False
        while True:
            # vidFrames = videoQueue.tryGetAll()
            # for vidFrame in vidFrames:
            #     vframe = vidFrame.getCvFrame()
            #     vframe2 = cv2.pyrDown(vframe)
            #     vframe2 = cv2.pyrDown(vframe2)
            #     vframe2 = cv2.rotate(vframe2, cv2.ROTATE_180)
            #     cv2.imshow('video', vframe2)

            ispFrames = ispQueue.tryGetAll()
            # ispFrames = ispQueue.tryGetAll()
            for ispFrame in ispFrames:
                # time.sleep(0.1)
                pass
                # cv2.imshow('isp', ispFrame.getCvFrame())

            # if TAKE_PHOTO:
                # stillFrames = stillQueue.tryGetAll()
                # if len(stillFrames) >= 1:
                #     for stillFrame in stillFrames:
                #         print(f"       Capturing Still")
                #         # Decode JPEG
                #         save_frame = cv2.imdecode(stillFrame.getData(), cv2.IMREAD_UNCHANGED)
                #         save_frame = cv2.rotate(save_frame, cv2.ROTATE_180)
                #         # Display
                #         frame = cv2.pyrDown(save_frame)
                #         frame = cv2.pyrDown(frame)  
                #         cv2.imshow('still', frame)
                #         # Save
                #         route_save_image(cfg,save_frame)
                #         TAKE_PHOTO = False
                # else:
                # print(f"       Capturing Image")
                # save_frame = ispFrames.getCvFrame()
                # save_frame = cv2.rotate(save_frame, cv2.ROTATE_180)
                # frame = cv2.pyrDown(save_frame)
                # frame = cv2.pyrDown(frame)  
                # # plt.imshow(frame)
                # cv2.imshow('still', frame)
                # # Save
                # print(f"       GPS Activated")
                # route_save_image(cfg,save_frame)
                # GPS_data = get_gps(cfg_user['fieldprism']['gps']['speed'])
                # TAKE_PHOTO = False
                # time.sleep(0.1)
                # print(f"{bcolors.FAIL}Ready{bcolors.ENDC}")

            key = cv2.waitKey(50)
            if keyboard.is_pressed('6'):
                break
            elif keyboard.is_pressed('1'):
                ctrl = dai.CameraControl()
                ctrl.setCaptureStill(True)
                configQueue.send(ctrl)
                # TAKE_PHOTO = True
                print(f"       Camera Activated")
                print(f"       Capturing Image")
                # for ispFrame in ispFrames:
                ispFrames = ispQueue.get()
                save_frame = ispFrames.getCvFrame()
                save_frame = cv2.rotate(save_frame, cv2.ROTATE_180)
                frame = cv2.pyrDown(save_frame)
                frame = cv2.pyrDown(frame)  
                # plt.imshow(frame)
                cv2.imshow('still', frame)
                # Save
                print(f"       GPS Activated")
                route_save_image(cfg,save_frame)
                GPS_data = get_gps(cfg_user['fieldprism']['gps']['speed'])
                # TAKE_PHOTO = False
                # time.sleep(0.1)
                print(f"{bcolors.FAIL}Ready{bcolors.ENDC}")
                # time.sleep(3)

def route():
    print("main: 1")
    print("align_camera: 3")
    print("Exit: 6")
    while True:
        key = cv2.waitKey(1)
        if keyboard.is_pressed('6'):
            break
        elif keyboard.is_pressed('1'):
            print("Entering main()")
            main()
        elif keyboard.is_pressed('3'):
            print("Entering align_camera()")
            align_camera()

if __name__ == '__main__':
    route()