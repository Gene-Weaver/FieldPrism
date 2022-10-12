#!/usr/bin/env python3

import time, os
from pathlib import Path
import cv2
import depthai as dai
import keyboard
from dataclasses import dataclass
from utils import bcolors

# print(f"{bcolors.OKGREEN}     {bcolors.ENDC}")

@dataclass
class SetupFP():
    usb_base_path: str = ''
    dir_images_unprocessed: str = ''
    usb_none: str = ''
    usb_1: str = ''
    usb_2: str = ''

    has_1_usb: bool = False
    has_2_usb: bool = False
    save_to_boot: bool = False

    def __post_init__(self) -> None:
        self.usb_base_path = '/media/pi/'#os.path.join('media','pi')
        self.dir_images_unprocessed = os.path.join('FieldPrism','Images_Unprocessed')

        print(f"{bcolors.WARNING}Base USB Path: {self.usb_base_path}{bcolors.ENDC}")
        print(f"{bcolors.WARNING}     Available USB Devices{os.listdir(self.usb_base_path)}{bcolors.ENDC}")

        if os.listdir(self.usb_base_path) is None:
            print(f"{bcolors.FAIL}ERROR: USB device/s not mounted correctly. {bcolors.ENDC}")
            print(f"{bcolors.FAIL}       Quit and mount USB device/s otherwise images will{bcolors.ENDC}")
            print(f"{bcolors.FAIL}       save to boot device (microSD card) in:{bcolors.ENDC}")
            print(f"{bcolors.FAIL}            home/pi/FieldPrism/Data/Images_Unprocessed{bcolors.ENDC}")
            self.usb_none = os.path.join('Data','Images_Unprocessed')
            self.save_to_boot = True

        elif len(os.listdir(self.usb_base_path)) == 1:
            self.usb_1 = os.path.join(self.usb_base_path,os.listdir(self.usb_base_path)[0],self.dir_images_unprocessed)
            self.has_1_usb = True
            print(f"{bcolors.OKGREEN}     Path to USB 1: {self.usb_1}{bcolors.ENDC}")

        elif len(os.listdir(self.usb_base_path)) == 2:
            self.usb_1 = os.path.join(self.usb_base_path,os.listdir(self.usb_base_path)[0],self.dir_images_unprocessed)
            self.usb_2 = os.path.join(self.usb_base_path,os.listdir(self.usb_base_path)[1],self.dir_images_unprocessed)
            self.has_1_usb = True
            self.has_2_usb = True 
            print(f"{bcolors.OKGREEN}     Path to USB 1: {self.usb_1}{bcolors.ENDC}")
            print(f"{bcolors.OKGREEN}     Path to USB 2: {self.usb_2}{bcolors.ENDC}")
        
        print(f"{bcolors.WARNING}Creating Save Directories{bcolors.ENDC}")
        if not self.has_1_usb and not self.has_2_usb and self.save_to_boot:
            Path(self.dir_images_unprocessed).mkdir(parents=True, exist_ok=True)
        elif self.has_1_usb and not self.has_2_usb:
            Path(self.usb_1).mkdir(parents=True, exist_ok=True)
        elif self.has_1_usb and self.has_2_usb:
            Path(self.usb_1).mkdir(parents=True, exist_ok=True)
            Path(self.usb_2).mkdir(parents=True, exist_ok=True)

def save_image(save_frame, name_time, save_dir):
    fname = "".join([name_time,'.jpg'])
    fname = os.path.join(save_dir,fname)
    cv2.imwrite(fname, save_frame)
    print(f"{bcolors.BOLD}     Image Saved: {fname}{bcolors.ENDC}")

def route_save_image(Setup,save_frame):
    name_time = str(int(time.time() * 1000))
    if not Setup.has_1_usb and not Setup.has_2_usb:
        save_image(save_frame, name_time, Setup.usb_none)

    elif Setup.has_1_usb and not Setup.has_2_usb:
        save_image(save_frame, name_time, Setup.usb_1)

    elif Setup.has_1_usb and Setup.has_2_usb:
        save_image(save_frame, name_time, Setup.usb_1)
        save_image(save_frame, name_time, Setup.usb_2)

def main():
    # Create pipeline
    pipeline = dai.Pipeline()

    # Define sources and outputs
    camRgb = pipeline.create(dai.node.ColorCamera)
    camRgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_4_K)
    camRgb.setIspScale(2,6) # 1080P -> 720P
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
    # camRgb.setVideoSize(3140, 2160)
    camRgb.setVideoSize(1280, 720)
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
            vidFrames = videoQueue.tryGetAll()
            for vidFrame in vidFrames:
                frame = vidFrame.getCvFrame()
                frame = cv2.pyrDown(frame)
                frame = cv2.pyrDown(frame)
                cv2.imshow('video', frame)

            ispFrames = ispQueue.get()
            # ispFrames = ispQueue.tryGetAll()
            # for ispFrame in ispFrames:
            #     # time.sleep(0.1)
            #     pass
                # cv2.imshow('isp', ispFrame.getCvFrame())

            if TAKE_PHOTO:
                stillFrames = stillQueue.tryGetAll()
                if len(stillFrames) == 1:
                    print("if")
                    for stillFrame in stillFrames:
                        print("STILL STILL STILL")
                        # Decode JPEG
                        save_frame = cv2.imdecode(stillFrame.getData(), cv2.IMREAD_UNCHANGED)
                        # Display
                        cv2.imshow('still', save_frame)
                        # Save
                        route_save_image(cfg,save_frame)
                        TAKE_PHOTO = False
                else:
                    print('else')
                    # pkt = ispQueue.get()
                    save_frame = ispFrames.getCvFrame()
                    save_frame = cv2.rotate(save_frame, cv2.ROTATE_180)
                    cv2.imshow('still', save_frame)
                    # Save
                    route_save_image(cfg,save_frame)
                    TAKE_PHOTO = False

            # Update screen (1ms pooling rate)
            key = cv2.waitKey(1)
            if keyboard.is_pressed('6'):
                break
            elif keyboard.is_pressed('1'):
                ctrl = dai.CameraControl()
                ctrl.setCaptureStill(True)
                controlQueue.send(ctrl)
                TAKE_PHOTO = True
                print("Sent 'still' event to the camera!")
                time.sleep(3)

if __name__ == '__main__':
    main()