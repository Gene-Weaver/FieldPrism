import tkinter as tk
from tkinter import *
from tkinter import ttk, Canvas
import time, os, stat, csv
from pathlib import Path
import cv2
import depthai as dai
import keyboard
from dataclasses import dataclass, field
from utils import bcolors, load_cfg, get_datetime
import matplotlib.pyplot as plt
from run_gps import get_gps
import psutil
from PIL import Image, ImageTk
from threading import Thread
import pandas as pd

@dataclass
class SetupFP:
    storage_present = False

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

    def __post_init__(self) -> None:
        self.usb_base_path = '/media/'# OR '/media/pi/' # os.path.join('media','pi')
        self.dir_images_unprocessed = os.path.join('FieldPrism','Images_Unprocessed')

        self.session_time = get_datetime()
        self.dir_data = os.path.join('FieldPrism','Data')
        self.dir_data_session = os.path.join('FieldPrism','Data')
        self.name_session_csv = ''.join(['FieldPrism_Data__',self.session_time,'.csv'])

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
        # list_data = [self.dir_data_1, self.dir_data_2, self.dir_data_3, self.dir_data_4, self.dir_data_5, self.dir_data_6]
        # list_usb = [self.usb_1, self.usb_2, self.usb_3, self.usb_4, self.usb_5, self.usb_6]
        for num, p in enumerate(list_drives):
            if isblockdevice(p):
                # if p == "/dev/sda1":
                drive_num = num+1
                path_to_drive = "".join(['/media/USB',str(drive_num),'/'])
                drive_name = "".join(['USB',str(drive_num)])
                if os.path.ismount(path_to_drive):
                    print(f"{bcolors.OKGREEN}       Storage Drive Exists({p}): [{isblockdevice(p)}] and is mounted to ({path_to_drive}): [{os.path.ismount(path_to_drive)}]{bcolors.ENDC}")
                    # print(f'self.usb_1 {self.usb_1}')
                    # print(f'self.has_1_usb {self.has_1_usb}')
                    name_has = ''.join(['self.has_',str(drive_num),'_usb'])
                    name_is = ''.join(['self.usb_',str(drive_num)])
                    name_data = ''.join(['self.dir_data_',str(drive_num)])
                    exec("%s = %s" % (name_has, True))
                    exec("%s = %s" % (name_is, "os.path.join(self.usb_base_path, drive_name, self.dir_images_unprocessed)"))
                    exec("%s = %s" % (name_data, "os.path.join(self.usb_base_path, drive_name, self.dir_data_session)"))
                    # print(f'self.usb_1 {self.usb_1}')
                    # print(f'self.has_1_usb {self.has_1_usb}')
        if self.usb_1 != '':             
            print(f"{bcolors.OKGREEN}              Path to USB Images {str(drive_num)} [{drive_name}]: {self.usb_1}{bcolors.ENDC}")
            print(f"{bcolors.OKGREEN}              Path to USB Data {str(drive_num)} [{drive_name}]: {self.dir_data_1}{bcolors.ENDC}")
        if self.usb_2 != '':             
            print(f"{bcolors.OKGREEN}              Path to USB Images {str(drive_num)} [{drive_name}]: {self.usb_2}{bcolors.ENDC}")
            print(f"{bcolors.OKGREEN}              Path to USB Data {str(drive_num)} [{drive_name}]: {self.dir_data_2}{bcolors.ENDC}")
        if self.usb_3 != '':             
            print(f"{bcolors.OKGREEN}              Path to USB Images {str(drive_num)} [{drive_name}]: {self.usb_3}{bcolors.ENDC}")
            print(f"{bcolors.OKGREEN}              Path to USB Data {str(drive_num)} [{drive_name}]: {self.dir_data_3}{bcolors.ENDC}")
        if self.usb_4 != '':             
            print(f"{bcolors.OKGREEN}              Path to USB Images {str(drive_num)} [{drive_name}]: {self.usb_4}{bcolors.ENDC}")
            print(f"{bcolors.OKGREEN}              Path to USB Data {str(drive_num)} [{drive_name}]: {self.dir_data_4}{bcolors.ENDC}")
        if self.usb_5 != '':             
            print(f"{bcolors.OKGREEN}              Path to USB Images {str(drive_num)} [{drive_name}]: {self.usb_5}{bcolors.ENDC}")
            print(f"{bcolors.OKGREEN}              Path to USB Data {str(drive_num)} [{drive_name}]: {self.dir_data_5}{bcolors.ENDC}")
        if self.usb_6 != '':             
            print(f"{bcolors.OKGREEN}              Path to USB Images {str(drive_num)} [{drive_name}]: {self.usb_6}{bcolors.ENDC}")
            print(f"{bcolors.OKGREEN}              Path to USB Data {str(drive_num)} [{drive_name}]: {self.dir_data_6}{bcolors.ENDC}")

        device_count = sum([self.save_to_boot, self.has_1_usb, self.has_2_usb, self.has_3_usb, self.has_4_usb, self.has_5_usb, self.has_6_usb])
        print(f"{bcolors.HEADER}Number of storage drives: {device_count}{bcolors.ENDC}")

        if device_count == 0:
            self.print_usb_error()
            self.usb_none = os.path.join('/home','pi','FieldPrism','Data','Images_Unprocessed')
            self.dir_data_none = os.path.join('/home','pi','FieldPrism','Data','Data')
            print(f"{bcolors.FAIL}       {self.usb_none}{bcolors.ENDC}")
            print(f"{bcolors.FAIL}       {self.dir_data_none}{bcolors.ENDC}")
            # self.save_to_boot = True
        else:
            print(f"{bcolors.HEADER}Creating Save Directories{bcolors.ENDC}")
            # Will only save to boot device
            if not self.has_1_usb and not self.has_2_usb and not self.has_3_usb and not self.has_4_usb and not self.has_5_usb and not self.has_6_usb and self.save_to_boot:
                print(f"{bcolors.WARNING}WARNING: Only saving to microSD card. Recommend adding USB storage and trying again!{bcolors.ENDC}")
                print(f"{bcolors.WARNING}       Creating (or verifying): {self.usb_none}{bcolors.ENDC}")
                Path(self.usb_none).mkdir(parents=True, exist_ok=True)
                self.storage_present = True
            # ---------- No storage selected ------------ #
            elif not self.has_1_usb and not self.has_2_usb  and not self.has_3_usb  and not self.has_4_usb  and not self.has_5_usb  and not self.has_6_usb and not self.save_to_boot:
                print(f"{bcolors.FAIL}ERROR: NO STORAGE DETECTED. DATA WILL NOT BE SAVED ANYWHERE!!!{bcolors.ENDC}")
                print(f"{bcolors.FAIL}       Power off device, add storage, try again. Or edit FieldPrism.yaml: always_save_to_boot = True{bcolors.ENDC}")
                self.storage_present = False
            if self.has_1_usb:
                print(f"{bcolors.OKGREEN}       Creating (or verifying): {self.usb_1}{bcolors.ENDC}")
                print(f"{bcolors.OKGREEN}       Creating (or verifying): {self.dir_data_1}{bcolors.ENDC}")
                Path(self.usb_1).mkdir(parents=True, exist_ok=True)
                Path(self.dir_data_1).mkdir(parents=True, exist_ok=True)
                self.storage_present = True
            if self.has_2_usb:
                print(f"{bcolors.OKGREEN}       Creating (or verifying): {self.usb_2}{bcolors.ENDC}")
                print(f"{bcolors.OKGREEN}       Creating (or verifying): {self.dir_data_2}{bcolors.ENDC}")
                Path(self.usb_2).mkdir(parents=True, exist_ok=True)
                Path(self.dir_data_2).mkdir(parents=True, exist_ok=True)
                self.storage_present = True
            if self.has_3_usb:
                print(f"{bcolors.OKGREEN}       Creating (or verifying): {self.usb_3}{bcolors.ENDC}")
                print(f"{bcolors.OKGREEN}       Creating (or verifying): {self.dir_data_3}{bcolors.ENDC}")
                Path(self.usb_3).mkdir(parents=True, exist_ok=True)
                Path(self.dir_data_3).mkdir(parents=True, exist_ok=True)
                self.storage_present = True
            if self.has_4_usb:
                print(f"{bcolors.OKGREEN}       Creating (or verifying): {self.usb_4}{bcolors.ENDC}")
                print(f"{bcolors.OKGREEN}       Creating (or verifying): {self.dir_data_4}{bcolors.ENDC}")
                Path(self.usb_4).mkdir(parents=True, exist_ok=True)
                Path(self.dir_data_4).mkdir(parents=True, exist_ok=True)
                self.storage_present = True
            if self.has_5_usb:
                print(f"{bcolors.OKGREEN}       Creating (or verifying): {self.usb_5}{bcolors.ENDC}")
                print(f"{bcolors.OKGREEN}       Creating (or verifying): {self.dir_data_5}{bcolors.ENDC}")
                Path(self.usb_5).mkdir(parents=True, exist_ok=True)
                Path(self.dir_data_5).mkdir(parents=True, exist_ok=True)
                self.storage_present = True
            if self.has_6_usb:
                print(f"{bcolors.OKGREEN}       Creating (or verifying): {self.usb_6}{bcolors.ENDC}")
                print(f"{bcolors.OKGREEN}       Creating (or verifying): {self.dir_data_6}{bcolors.ENDC}")
                Path(self.usb_6).mkdir(parents=True, exist_ok=True)
                Path(self.dir_data_6).mkdir(parents=True, exist_ok=True)
                self.storage_present = True

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

@dataclass
class ImageData:
    # Path data
    path_to_saved: str = ''
    path_from_fp: str = ''
    path: str = ''
    filename: str = ''
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

    cfg: object = field(init=False)

    headers: list = field(init=False,default_factory=None)


    def __init__(self, cfg, path_to_saved: str, GPS_data: object):
        self.headers = ['session_time','name_session_csv','name_total_csv','filename_short', 'time_of_collection','latitude','longitude','altitude','climb','speed','lat_error_est','lon_error_est','alt_error_est',
                    'filename','filename_ext','path_from_fp','path_to_saved']
        self.cfg = cfg
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

        self.path, self.filename = os.path.split(self.path_to_saved)
        self.filename_short = self.filename.split('.')[0]
        self.filename_ext = self.filename.split('.')[1]
        self.path_from_fp = os.path.join(*self.path_to_saved.split(os.path.sep)[3:])
        # print(f'self.path_from_fp = {self.path_from_fp}')

        new_data = pd.DataFrame([[self.cfg.session_time,self.cfg.name_session_csv,self.cfg.name_total_csv,
        self.filename_short,self.current_time,self.latitude,self.longitude,self.altitude,self.climb,self.speed,
        self.lat_error_est,self.lon_error_est,self.alt_error_est,
        self.filename,self.filename_ext,self.path_from_fp,self.path_to_saved]], columns=self.headers)

        self.save_data(new_data)

    def save_data(self, new_data) -> None:
        if self.cfg.save_to_boot:
            self.save_csv(self.cfg.dir_data_none, new_data)
        if self.cfg.has_1_usb:
            self.save_csv(self.cfg.dir_data_1, new_data)
        if self.cfg.has_2_usb:
            self.save_csv(self.cfg.dir_data_2, new_data)
        if self.cfg.has_3_usb:
            self.save_csv(self.cfg.dir_data_3, new_data)
        if self.cfg.has_4_usb:
            self.save_csv(self.cfg.dir_data_4, new_data)
        if self.cfg.has_5_usb:
            self.save_csv(self.cfg.dir_data_5, new_data)
        if self.cfg.has_6_usb:
            self.save_csv(self.cfg.dir_data_6, new_data)

    def save_csv(self, data_name, new_data) -> None:
        ### Session
        try:
            csv_session = pd.read_csv(os.path.join(data_name, self.cfg.name_session_csv),dtype=str)
        except Exception as e:
            print(f"{bcolors.WARNING}       Initializing new session CSV file: {os.path.join(data_name, self.cfg.name_session_csv)}{bcolors.ENDC}")
            # Create empty csv
            with open(os.path.join(data_name, self.cfg.name_session_csv), 'w', newline='') as csvfile:
                csvwriter = csv.writer(csvfile)
                csvwriter.writerow(self.headers)
        ### Total
        try: 
            # Try read csv 
            csv_total = pd.read_csv(os.path.join(data_name, self.cfg.name_total_csv),dtype=str)
        except Exception as e:
            print(f"{bcolors.WARNING}       Initializing new FieldPrism_Data.csv file: {os.path.join(data_name, self.cfg.name_total_csv)}{bcolors.ENDC}")
            # Create empty csv
            with open(os.path.join(data_name, self.cfg.name_total_csv), 'w', newline='') as csvfile:
                csvwriter = csv.writer(csvfile)
                csvwriter.writerow(self.headers)
        
        new_data.to_csv(os.path.join(data_name, self.cfg.name_session_csv), mode='a', header=False, index=False)
        new_data.to_csv(os.path.join(data_name, self.cfg.name_total_csv), mode='a', header=False, index=False)
        print(f'{bcolors.OKGREEN}\n       Added 1 row to session CSV: {os.path.join(data_name, self.cfg.name_session_csv)}{bcolors.ENDC}')
        print(f'{bcolors.OKGREEN}       Added 1 row to total CSV:   {os.path.join(data_name, self.cfg.name_total_csv)}{bcolors.ENDC}\n')

class fragile(object):
    class Break(Exception):
      """Break out of the with statement"""

    def __init__(self, value):
        self.value = value

    def __enter__(self):
        return self.value.__enter__()

    def __exit__(self, etype, value, traceback):
        error = self.value.__exit__(etype, value, traceback)
        if etype == self.Break:
            return True
        return error

def print_options():
    print("main: 1")
    print("align_camera: 3")
    print("Exit: 6")

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

class PreviewWindow():
    def __init__(self, window, image):
        self.window = window
        self.image = image
        self.width = 426
        self.height = 240
        # self.interval = 20 # Interval in ms to get the latest frame

        # Create canvas for image
        self.canvas = Canvas(window, width=self.width, height=self.height)
        # self.canvas.grid(row=0, column=0)
        self.canvas.pack()

        # First image
        blue,green,red = cv2.split(self.image)
        image = cv2.merge((red,green,blue))
        img = Image.fromarray(image)
        # imgtk = ImageTk.PhotoImage(image=img)
        self.canvas.image = ImageTk.PhotoImage(image=img)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.canvas.image)
        print('init preview')

        # Update image on canvas
        # self.update_image()

    # def change_image(self,image):
    #     self.image = image

    def update_image(self,image):
        # Get the latest frame and convert image format
        # try:
        #     self.image = cv2.cvtColor(self.image.read()[1], cv2.COLOR_BGR2RGB) # to RGB
        # except:
        #     pass
        self.image = image
        blue,green,red = cv2.split(self.image)
        imgtk = cv2.merge((red,green,blue))
        imgtk = Image.fromarray(imgtk)
        imgtk = ImageTk.PhotoImage(image=imgtk)
        # self.image = Image.fromarray(self.image) # to PIL format
        # self.image = ImageTk.PhotoImage(self.image) # to ImageTk format

        # Update image
        self.canvas.image = imgtk
        self.canvas.itemconfig(self.canvas.image, image=image)
        print('update preview')

        # Repeat every 'interval' ms
        # self.window.after(self.interval, self.update_image)

class SaveWindow():
    def __init__(self, window, image):
        self.window = window
        self.image = image
        self.width = 507
        self.height = 380
        # self.interval = 20 # Interval in ms to get the latest frame

        # Create canvas for image
        self.canvas = Canvas(window, width=self.width, height=self.height)
        # self.canvas.grid(row=1, column=0)
        self.canvas.pack()

        # First image
        blue,green,red = cv2.split(self.image)
        image = cv2.merge((red,green,blue))
        img = Image.fromarray(image)
        self.canvas.image = ImageTk.PhotoImage(image=img)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.canvas.image)
        print('init save')

        # Update image on canvas
        # self.update_image()

    def update_image(self,image):
        # Get the latest frame and convert image format
        # try:
        #     self.image = cv2.cvtColor(self.image.read()[1], cv2.COLOR_BGR2RGB) # to RGB
        # except:
        #     pass
        self.image = image
        blue,green,red = cv2.split(self.image)
        imgtk = cv2.merge((red,green,blue))
        imgtk = Image.fromarray(imgtk)
        imgtk = ImageTk.PhotoImage(image=imgtk)
        # self.image = Image.fromarray(self.image) # to PIL format
        # self.image = ImageTk.PhotoImage(self.image) # to ImageTk format

        # Update image
        self.canvas.image = imgtk
        self.canvas.itemconfig(self.canvas.image, image=image)
        # self.canvas.create_image(0, 0, anchor=tk.NW, image=imgtk)

        # Repeat every 'interval' ms
        # self.window.after(self.interval, self.update_image)
        print('update save')

def createPipeline():
    # cfg_user = load_cfg()

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

    return pipeline


def run(pipeline, root):
    # Make sure the destination path is present before starting to store the examples
    img_preview = cv2.imread('img/preview_window.jpg')
    img_saved = cv2.imread('img/saved_image_window.jpg')

    frame_preview = tk.Frame(master=root, height=240, bg="white")
    frame_preview.pack(fill=tk.X)
    # frame_preview.grid(row=0, column=0)

    frame_saved = tk.Frame(master=root, height=380, bg="black")
    frame_saved.pack(fill=tk.X)
    # frame_saved.grid(row=1, column=0)

    Window_Preview = PreviewWindow(frame_preview,img_preview)
    Window_Saved = SaveWindow(frame_saved,img_saved)
    # # Connect to device and start pipeline
    with fragile(dai.Device(pipeline)) as device:
        print('Connected cameras: ', device.getConnectedCameras())
        # Print out usb speed
        print('Usb speed: ', device.getUsbSpeed().name)

        
        
        cfg_user = load_cfg()

        # frame_preview = tk.Frame(master=root, height=240, bg="white")
        # frame_preview.pack(fill=tk.X)

        # frame_saved = tk.Frame(master=root, height=380, bg="black")
        # frame_saved.pack(fill=tk.X)

        # frame_controls = tk.Frame(master=root, height=200, bg="gray")
        # frame_controls.pack(fill=tk.X)



        cfg_user = load_cfg()
        # FS = FieldStation(root,pipeline)
        # Window_Preview = PreviewWindow(frame_preview,img_preview)
        # Window_Saved = SaveWindow(frame_saved,img_saved)

        cfg = SetupFP()
        if cfg.storage_present == False:
            print(f"{bcolors.HEADER}Stopping...{bcolors.ENDC}")
            print_options()
            raise fragile.Break
        else:
            # Get data queues
            ispQueue = device.getOutputQueue('isp', maxSize=1, blocking=False)
            videoQueue = device.getOutputQueue('video', maxSize=1, blocking=False)

            TAKE_PHOTO = False
            while True:
                vidFrames = videoQueue.tryGetAll()
                for vidFrame in vidFrames:
                    vframe = vidFrame.getCvFrame()
                    vframe = cv2.rotate(vframe, cv2.ROTATE_180)
                    # cv2.imshow('preview', vframe)
                    # PreviewWindow(FS.frame_preview,vframe)
                    # Window_Preview.change_image(vframe)
                    Window_Preview.update_image(vframe)

                ispFrames = ispQueue.get()
                isp = ispFrames.getCvFrame()

                if TAKE_PHOTO:
                    print(f"       Capturing Image")
                    ispFrames = ispQueue.get()
                    save_frame = ispFrames.getCvFrame()
                    save_frame = cv2.rotate(save_frame, cv2.ROTATE_180)
                    # Save
                    path_to_saved = route_save_image(cfg,save_frame)
                    # cv2.imshow('Saved Image', cv2.pyrDown(cv2.pyrDown(cv2.pyrDown(cv2.imread(path_to_saved)))))
                    # FS.saved_window = PreviewWindow(FS.saved_window,cv2.pyrDown(cv2.pyrDown(cv2.pyrDown(cv2.imread(path_to_saved)))))
                    # saved_window = SaveWindow(FS.frame_saved, cv2.pyrDown(cv2.pyrDown(cv2.pyrDown(cv2.imread(path_to_saved)))))
                    # SaveWindow(FS.frame_saved, cv2.pyrDown(cv2.pyrDown(cv2.pyrDown(cv2.imread(path_to_saved)))))
                    # Window_Saved.change_image(cv2.pyrDown(cv2.pyrDown(cv2.pyrDown(cv2.imread(path_to_saved)))))
                    Window_Saved.update_image(cv2.pyrDown(cv2.pyrDown(cv2.pyrDown(cv2.imread(path_to_saved)))))

                    print(f"       GPS Activated")
                    GPS_data = get_gps(cfg_user['fieldprism']['gps']['speed'])
                    Image = ImageData(cfg, path_to_saved, GPS_data)
                    TAKE_PHOTO = False
                    print(f"{bcolors.OKGREEN}Ready{bcolors.ENDC}")

                key = cv2.waitKey(50)
                if keyboard.is_pressed('6'):
                    print(f"{bcolors.HEADER}Stopping...{bcolors.ENDC}")
                    print_options()
                    break
                elif keyboard.is_pressed('1'):
                    TAKE_PHOTO = True
                    print(f"       Camera Activated")

class FieldStation():
    # cfg_user: object = field(init=False)

    def __init__(self, root, pipeline):
        self.cfg_user = load_cfg()
        # self.img_preview = cv2.imread('img/preview_window.jpg')
        # self.img_saved = cv2.imread('img/saved_image_window.jpg')

        # mainframe = ttk.Frame(root, padding="3 3 12 12")
        # mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        # root.columnconfigure(0, weight=1)
        # root.rowconfigure(0, weight=1)
        self.frame_preview = tk.Frame(master=root, height=240, bg="white")
        self.frame_preview.pack(fill=tk.X)

        self.frame_saved = tk.Frame(master=root, height=380, bg="black")
        self.frame_saved.pack(fill=tk.X)

        self.frame_controls = tk.Frame(master=root, height=200, bg="gray")
        self.frame_controls.pack(fill=tk.X)

        # cap = cv2.VideoCapture(0)
        # self.preview_window = PreviewWindow(self.frame_preview,self.img_preview)
        # self.saved_window = SaveWindow(self.frame_saved,self.img_saved)

if __name__ == "__main__":
    pipeline = createPipeline()
    root = Tk()
    root.title("FieldPrism - Field Station")
    root.minsize(width=507, height=450)

    # FieldStation(root)

    


    # def callback(*args):
    #     global currentStream
    #     currentStream = root.getvar(args[0])
    #     cv2.destroyAllWindows()


    thread = Thread(target=run, args=(pipeline,root,))
    thread.setDaemon(True)
    thread.start()

    root.mainloop()