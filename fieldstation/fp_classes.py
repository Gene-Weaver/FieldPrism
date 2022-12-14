#!/usr/bin/env python3
import os, stat, csv, cv2, psutil
from pathlib import Path
from dataclasses import dataclass, field
import matplotlib.pyplot as plt
from PIL import Image, ImageTk
import pandas as pd
import tkinter as tk
from tkinter import ttk, Canvas
from utils import bcolors,  get_datetime

'''
Main setup class.
    Begins with checking the environment, USB mounting points
'''
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

    device_count: int = 0

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
        self.verify_mount_usb_locations()     
        print(f"")  

        # USB save to all
        self.device_count = 0
        list_drives = ["/dev/sda1", "/dev/sdb1", "/dev/sdc1", "/dev/sdd1", "/dev/sde1", "/dev/sdf1"]
        # list_data = [self.dir_data_1, self.dir_data_2, self.dir_data_3, self.dir_data_4, self.dir_data_5, self.dir_data_6]
        # list_usb = [self.usb_1, self.usb_2, self.usb_3, self.usb_4, self.usb_5, self.usb_6]
        for num, p in enumerate(list_drives):
            if self.isblockdevice(p):
                # if p == "/dev/sda1":
                drive_num = num+1
                path_to_drive = "".join(['/media/USB',str(drive_num),'/'])
                drive_name = "".join(['USB',str(drive_num)])
                if os.path.ismount(path_to_drive):
                    print(f"{bcolors.OKGREEN}       Storage Drive Exists({p}): [{self.isblockdevice(p)}] and is mounted to ({path_to_drive}): [{os.path.ismount(path_to_drive)}]{bcolors.ENDC}")
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

        self.device_count = sum([self.save_to_boot, self.has_1_usb, self.has_2_usb, self.has_3_usb, self.has_4_usb, self.has_5_usb, self.has_6_usb])
        print(f"{bcolors.HEADER}Number of storage drives: {self.device_count}{bcolors.ENDC}")

        if self.device_count == 0:
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

    def isblockdevice(self,path) -> None:
        return os.path.exists(path) and stat.S_ISBLK(os.stat(path).st_mode)

    def verify_mount_usb_locations(self) -> None:
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

'''
Data class for image data. Stores all image metadata including GPS.
'''
@dataclass
class ImageData:
    # Path data
    path_to_saved: str = ''
    path_from_fp: str = ''
    path: str = ''
    filename: str = ''
    filename_short: str = ''
    filename_ext: str = ''

    # Image size
    image_height: int = -888
    image_width: int = -888

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

    def __init__(self, cfg, path_to_saved: str, GPS_data: object, image_height: int, image_width: int, sharpness_actual: int, sharpness_min_cutoff: int, is_sharp: bool):
        self.headers = ['session_time','name_session_csv','name_total_csv','filename_short', 'time_of_collection','latitude','longitude','altitude','climb','speed','lat_error_est','lon_error_est','alt_error_est',
                    'sharpness_actual', 'sharpness_min_cutoff', 'is_sharp',
                    'filename','filename_ext','path_from_fp','path_to_saved','image_height','image_width']
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

        self.blur_actual = sharpness_actual
        self.blur_cutoff = sharpness_min_cutoff
        self.is_sharp = str(is_sharp)

        self.image_height = image_height
        self.image_width = image_width

        self.path, self.filename = os.path.split(self.path_to_saved)
        self.filename_short = self.filename.split('.')[0]
        self.filename_ext = self.filename.split('.')[1]
        self.path_from_fp = os.path.join(*self.path_to_saved.split(os.path.sep)[3:])

        new_data = pd.DataFrame([[self.cfg.session_time,self.cfg.name_session_csv,self.cfg.name_total_csv,
        self.filename_short,self.current_time,self.latitude,self.longitude,self.altitude,self.climb,self.speed,
        self.lat_error_est,self.lon_error_est,self.alt_error_est,
        self.blur_actual, self.blur_cutoff,
        self.filename,self.filename_ext,self.path_from_fp,self.path_to_saved,
        self.image_height, self.image_width]], columns=self.headers)

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

class Fragile(object):
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

class PreviewWindow():
    def __init__(self, window, image):
        self.window = window
        self.image = image
        self.width = 426
        self.height = 240

        # Create canvas for image
        self.canvas = Canvas(window, width=self.width, height=self.height)
        self.canvas.pack()

        # First image
        blue,green,red = cv2.split(self.image)
        image = cv2.merge((red,green,blue))
        img = Image.fromarray(image)
        self.canvas.image = ImageTk.PhotoImage(image=img)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.canvas.image)

    def update_image(self,image):
        self.image = image
        blue,green,red = cv2.split(self.image)
        imgtk = cv2.merge((red,green,blue))
        imgtk = Image.fromarray(imgtk)
        imgtk = ImageTk.PhotoImage(image=imgtk)

        # Update image
        self.canvas.image = imgtk
        self.canvas.create_image(0, 0, anchor=tk.NW, image=imgtk)

class SaveWindow():
    def __init__(self, window, image):
        self.window = window
        self.image = image
        self.width = 507
        self.height = 380

        # Create canvas for image
        self.canvas = Canvas(window, width=self.width, height=self.height)
        self.canvas.pack()

        # First image
        blue,green,red = cv2.split(self.image)
        image = cv2.merge((red,green,blue))
        img = Image.fromarray(image)
        self.canvas.image = ImageTk.PhotoImage(image=img)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.canvas.image)

    def update_image(self,image):
        self.image = image
        blue,green,red = cv2.split(self.image)
        imgtk = cv2.merge((red,green,blue))
        imgtk = Image.fromarray(imgtk)
        imgtk = ImageTk.PhotoImage(image=imgtk)

        # Update image
        self.canvas.image = imgtk
        self.canvas.create_image(0, 0, anchor=tk.NW, image=imgtk)

class Redirect():
    def __init__(self, widget, autoscroll=True):
        self.widget = widget
        self.autoscroll = autoscroll

    def write(self, text):
        self.widget.insert('end', text)
        if self.autoscroll:
            self.widget.see("end")  # autoscroll

    def flush(self):
       pass