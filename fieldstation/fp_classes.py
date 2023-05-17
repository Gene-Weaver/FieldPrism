#!/usr/bin/env python3
import os, stat, csv, cv2, psutil, subprocess
from pathlib import Path
from dataclasses import dataclass, field
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from PIL import Image, ImageTk
import pandas as pd
import tkinter as tk
from tkinter import ttk, Canvas
from utils_general import bcolors,  get_datetime
import seaborn as sns

import folium
import pandas as pd
import numpy as np
from pyproj import Proj, Transformer
from scipy.spatial import distance, ConvexHull
from shapely.geometry import MultiPoint
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
    name_total_csv: str = 'FP_Data.csv'

    dir_data_none: str = ''
    dir_data_1: str = ''
    dir_data_2: str = ''
    dir_data_3: str = ''
    dir_data_4: str = ''
    dir_data_5: str = ''
    dir_data_6: str = ''

    dir_qr_none: str = ''
    dir_qr_1: str = ''
    dir_qr_2: str = ''
    dir_qr_3: str = ''
    dir_qr_4: str = ''
    dir_qr_5: str = ''
    dir_qr_6: str = ''

    device_count: int = 0

    def __post_init__(self) -> None:
        self.usb_base_path = '/media/'# OR '/media/pi/' # os.path.join('media','pi')
        self.dir_images_unprocessed = os.path.join('FieldPrism','Images_Unprocessed')

        self.session_time = get_datetime()
        self.dir_data = os.path.join('FieldPrism','Data')
        self.dir_data_session = os.path.join('FieldPrism','Data')
        self.name_session_csv = ''.join(['FP_Data__',self.session_time,'.csv'])
        self.name_session = ''.join(['FP_Data__',self.session_time])
        self.dir_data_session_qr = os.path.join('FieldPrism','QR',self.name_session)

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
                    name_qr = ''.join(['self.dir_qr_',str(drive_num)])
                    exec("%s = %s" % (name_has, True))
                    exec("%s = %s" % (name_is, "os.path.join(self.usb_base_path, drive_name, self.dir_images_unprocessed)"))
                    exec("%s = %s" % (name_data, "os.path.join(self.usb_base_path, drive_name, self.dir_data_session)"))
                    exec("%s = %s" % (name_qr, "os.path.join(self.usb_base_path, drive_name, self.dir_data_session_qr)"))
                    # print(f'self.usb_1 {self.usb_1}')
                    # print(f'self.has_1_usb {self.has_1_usb}')
        if self.usb_1 != '':             
            print(f"{bcolors.OKGREEN}              Path to USB Images {str(drive_num)} [{drive_name}]: {self.usb_1}{bcolors.ENDC}")
            print(f"{bcolors.OKGREEN}              Path to USB Data {str(drive_num)} [{drive_name}]: {self.dir_data_1}{bcolors.ENDC}")
            print(f"{bcolors.OKGREEN}              Path to USB QR {str(drive_num)} [{drive_name}]: {self.dir_qr_1}{bcolors.ENDC}")
        if self.usb_2 != '':             
            print(f"{bcolors.OKGREEN}              Path to USB Images {str(drive_num)} [{drive_name}]: {self.usb_2}{bcolors.ENDC}")
            print(f"{bcolors.OKGREEN}              Path to USB Data {str(drive_num)} [{drive_name}]: {self.dir_data_2}{bcolors.ENDC}")
            print(f"{bcolors.OKGREEN}              Path to USB QR {str(drive_num)} [{drive_name}]: {self.dir_qr_2}{bcolors.ENDC}")
        if self.usb_3 != '':             
            print(f"{bcolors.OKGREEN}              Path to USB Images {str(drive_num)} [{drive_name}]: {self.usb_3}{bcolors.ENDC}")
            print(f"{bcolors.OKGREEN}              Path to USB Data {str(drive_num)} [{drive_name}]: {self.dir_data_3}{bcolors.ENDC}")
            print(f"{bcolors.OKGREEN}              Path to USB QR {str(drive_num)} [{drive_name}]: {self.dir_qr_3}{bcolors.ENDC}")
        if self.usb_4 != '':             
            print(f"{bcolors.OKGREEN}              Path to USB Images {str(drive_num)} [{drive_name}]: {self.usb_4}{bcolors.ENDC}")
            print(f"{bcolors.OKGREEN}              Path to USB Data {str(drive_num)} [{drive_name}]: {self.dir_data_4}{bcolors.ENDC}")
            print(f"{bcolors.OKGREEN}              Path to USB QR {str(drive_num)} [{drive_name}]: {self.dir_qr_4}{bcolors.ENDC}")
        if self.usb_5 != '':             
            print(f"{bcolors.OKGREEN}              Path to USB Images {str(drive_num)} [{drive_name}]: {self.usb_5}{bcolors.ENDC}")
            print(f"{bcolors.OKGREEN}              Path to USB Data {str(drive_num)} [{drive_name}]: {self.dir_data_5}{bcolors.ENDC}")
            print(f"{bcolors.OKGREEN}              Path to USB QR {str(drive_num)} [{drive_name}]: {self.dir_qr_5}{bcolors.ENDC}")
        if self.usb_6 != '':             
            print(f"{bcolors.OKGREEN}              Path to USB Images {str(drive_num)} [{drive_name}]: {self.usb_6}{bcolors.ENDC}")
            print(f"{bcolors.OKGREEN}              Path to USB Data {str(drive_num)} [{drive_name}]: {self.dir_data_6}{bcolors.ENDC}")
            print(f"{bcolors.OKGREEN}              Path to USB QR {str(drive_num)} [{drive_name}]: {self.dir_qr_6}{bcolors.ENDC}")

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
                print(f"{bcolors.OKGREEN}       Creating (or verifying): {self.dir_qr_1}{bcolors.ENDC}")
                Path(self.usb_1).mkdir(parents=True, exist_ok=True)
                Path(self.dir_data_1).mkdir(parents=True, exist_ok=True)
                Path(self.dir_qr_1).mkdir(parents=True, exist_ok=True)
                self.storage_present = True
            if self.has_2_usb:
                print(f"{bcolors.OKGREEN}       Creating (or verifying): {self.usb_2}{bcolors.ENDC}")
                print(f"{bcolors.OKGREEN}       Creating (or verifying): {self.dir_data_2}{bcolors.ENDC}")
                print(f"{bcolors.OKGREEN}       Creating (or verifying): {self.dir_qr_2}{bcolors.ENDC}")
                Path(self.usb_2).mkdir(parents=True, exist_ok=True)
                Path(self.dir_data_2).mkdir(parents=True, exist_ok=True)
                Path(self.dir_qr_2).mkdir(parents=True, exist_ok=True)
                self.storage_present = True
            if self.has_3_usb:
                print(f"{bcolors.OKGREEN}       Creating (or verifying): {self.usb_3}{bcolors.ENDC}")
                print(f"{bcolors.OKGREEN}       Creating (or verifying): {self.dir_data_3}{bcolors.ENDC}")
                print(f"{bcolors.OKGREEN}       Creating (or verifying): {self.dir_qr_3}{bcolors.ENDC}")
                Path(self.usb_3).mkdir(parents=True, exist_ok=True)
                Path(self.dir_data_3).mkdir(parents=True, exist_ok=True)
                Path(self.dir_qr_3).mkdir(parents=True, exist_ok=True)
                self.storage_present = True
            if self.has_4_usb:
                print(f"{bcolors.OKGREEN}       Creating (or verifying): {self.usb_4}{bcolors.ENDC}")
                print(f"{bcolors.OKGREEN}       Creating (or verifying): {self.dir_data_4}{bcolors.ENDC}")
                print(f"{bcolors.OKGREEN}       Creating (or verifying): {self.dir_qr_4}{bcolors.ENDC}")
                Path(self.usb_4).mkdir(parents=True, exist_ok=True)
                Path(self.dir_data_4).mkdir(parents=True, exist_ok=True)
                Path(self.dir_qr_4).mkdir(parents=True, exist_ok=True)
                self.storage_present = True
            if self.has_5_usb:
                print(f"{bcolors.OKGREEN}       Creating (or verifying): {self.usb_5}{bcolors.ENDC}")
                print(f"{bcolors.OKGREEN}       Creating (or verifying): {self.dir_data_5}{bcolors.ENDC}")
                print(f"{bcolors.OKGREEN}       Creating (or verifying): {self.dir_qr_5}{bcolors.ENDC}")
                Path(self.usb_5).mkdir(parents=True, exist_ok=True)
                Path(self.dir_data_5).mkdir(parents=True, exist_ok=True)
                Path(self.dir_qr_5).mkdir(parents=True, exist_ok=True)
                self.storage_present = True
            if self.has_6_usb:
                print(f"{bcolors.OKGREEN}       Creating (or verifying): {self.usb_6}{bcolors.ENDC}")
                print(f"{bcolors.OKGREEN}       Creating (or verifying): {self.dir_data_6}{bcolors.ENDC}")
                print(f"{bcolors.OKGREEN}       Creating (or verifying): {self.dir_qr_6}{bcolors.ENDC}")
                Path(self.usb_6).mkdir(parents=True, exist_ok=True)
                Path(self.dir_data_6).mkdir(parents=True, exist_ok=True)
                Path(self.dir_qr_6).mkdir(parents=True, exist_ok=True)
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

    sharpness_actual: int = -888
    sharpness_min_cutoff: int = -888
    is_sharp: str = ''

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

        self.sharpness_actual = sharpness_actual
        self.sharpness_min_cutoff = sharpness_min_cutoff
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
        self.sharpness_actual, self.sharpness_min_cutoff, self.is_sharp,
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
            print(f"{bcolors.WARNING}       Initializing new FP_Data.csv file: {os.path.join(data_name, self.cfg.name_total_csv)}{bcolors.ENDC}")
            # Create empty csv
            with open(os.path.join(data_name, self.cfg.name_total_csv), 'w', newline='') as csvfile:
                csvwriter = csv.writer(csvfile)
                csvwriter.writerow(self.headers)
        
        new_data.to_csv(os.path.join(data_name, self.cfg.name_session_csv), mode='a', header=False, index=False)
        new_data.to_csv(os.path.join(data_name, self.cfg.name_total_csv), mode='a', header=False, index=False)
        print(f'{bcolors.OKGREEN}\n       Added 1 row to session CSV: {os.path.join(data_name, self.cfg.name_session_csv)}{bcolors.ENDC}')
        print(f'{bcolors.OKGREEN}       Added 1 row to total CSV:   {os.path.join(data_name, self.cfg.name_total_csv)}{bcolors.ENDC}\n')

@dataclass
class GPSTest:
    # Path data
    has_points: bool = False
    CEP: float = 0.0
    RMS: float = 0.0
    plot_path: str = ''
    cfg: object = field(init=False)
    df_summary: object = field(init=False)
    map_gps: object = field(init=False)
    gps_plot: object = field(init=False)
    Window_Saved: object = field(init=False)
    results_df: object = field(init=False)

    
    def __init__(self, cfg, df, label_rms, label_cep, Window_Saved):
        self.cfg = cfg
        self.label_rms = label_rms
        self.label_cep = label_cep
        self.Window_Saved = Window_Saved
        self.save_data(df, "__GPS_Accuracy_Data")

        self.process_gps(df)

        self.save_data(self.results_df, "__GPS_Accuracy_Summary")

        if self.has_points:
            self.save_data_map("__GPS_Accuracy_Map")

        self.show_error()

    def show_error(self):
        if (self.CEP == 0.0) or (self.RMS == 0.0):
            self.label_rms.config(text = f'RMS: no signal', fg='red')
            self.label_cep.config(text = f'CEP: no signal', fg='red')
        else:
            self.label_rms.config(text = f'RMS: {round(self.RMS,1)} m.', fg='green2')
            self.label_cep.config(text = f'CEP: {round(self.CEP,1)} m.', fg='green2')

    def get_plot_path(self):
        return self.plot_path

    def save_data(self, df, suffix) -> None:
        if self.cfg.save_to_boot:
            self.save_csv(self.cfg.dir_data_none, df, suffix)
        if self.cfg.has_1_usb:
            self.save_csv(self.cfg.dir_data_1, df, suffix)
        if self.cfg.has_2_usb:
            self.save_csv(self.cfg.dir_data_2, df, suffix)
        if self.cfg.has_3_usb:
            self.save_csv(self.cfg.dir_data_3, df, suffix)
        if self.cfg.has_4_usb:
            self.save_csv(self.cfg.dir_data_4, df, suffix)
        if self.cfg.has_5_usb:
            self.save_csv(self.cfg.dir_data_5, df, suffix)
        if self.cfg.has_6_usb:
            self.save_csv(self.cfg.dir_data_6, df, suffix)
    
    def save_data_map(self, suffix) -> None:
        if self.cfg.save_to_boot:
            self.save_map(self.cfg.dir_data_none, suffix)
        if self.cfg.has_1_usb:
            self.save_map(self.cfg.dir_data_1, suffix)
        if self.cfg.has_2_usb:
            self.save_map(self.cfg.dir_data_2, suffix)
        if self.cfg.has_3_usb:
            self.save_map(self.cfg.dir_data_3, suffix)
        if self.cfg.has_4_usb:
            self.save_map(self.cfg.dir_data_4, suffix)
        if self.cfg.has_5_usb:
            self.save_map(self.cfg.dir_data_5, suffix)
        if self.cfg.has_6_usb:
            self.save_map(self.cfg.dir_data_6, suffix)

    def save_csv(self, data_name, df, suffix) -> None:
        # Save DataFrame to CSV
        filename_parts = self.cfg.name_session_csv.split('.')
        filename_parts[0] += suffix
        gps_savename = '.'.join(filename_parts)

        df.to_csv(os.path.join(data_name, gps_savename), mode='a', header=True, index=False)
        print(f'{bcolors.OKGREEN}\n       Added {len(df)} row(s) to session CSV: {os.path.join(data_name, gps_savename)}{bcolors.ENDC}')

    def save_map(self, data_name, suffix) -> None:
        # Save DataFrame to CSV
        filename_parts = self.cfg.name_session_csv.split('.')
        filename_parts[0] += suffix
        base_map = filename_parts[0]
        base_plot = ''.join([filename_parts[0],'_Plot'])
        gps_map_savename = '.'.join([base_map, 'html'])
        gps_plot_savename = ''.join([base_plot, '.jpg'])
        counter = 1
        counterP = 1

        full_map_path = os.path.join(data_name, gps_map_savename)
        full_plot_path = os.path.join(data_name, gps_plot_savename)

        # Check if the map file already exists, if it does, increment the counter and append it to the filename
        while os.path.isfile(full_map_path):
            counter += 1
            gps_map_savename = '.'.join([f"{base_map}_{counter}", 'html'])
            full_map_path = os.path.join(data_name, gps_map_savename)

        self.map_gps.save(full_map_path)

        # Check if the plot file already exists, if it does, increment the counter and append it to the filename
        while os.path.isfile(full_plot_path):
            counterP += 1
            gps_plot_savename = ''.join([f"{base_plot}_{counter}", '.jpg'])
            full_plot_path = os.path.join(data_name, gps_plot_savename)

        self.plot_path = full_plot_path
        cv2.imwrite(full_plot_path, self.gps_plot)
        # Save the map to an HTML file
        print(f'{bcolors.OKGREEN}\n       Saved GPS map to: {full_map_path}{bcolors.ENDC}')
        print(f'{bcolors.OKGREEN}\n       Saved GPS plot to: {full_plot_path}{bcolors.ENDC}')


        # Open the HTML file in the Chromium browser
        try:
            subprocess.Popen(['chromium-browser', '--no-sandbox', 'file://' + full_map_path])
        except Exception as e:
            print(f"Failed to open browser: {e}")


    def process_gps(self, df):
        # Initialize the results dataframe
        results = []

        self.coordinates_df = df[['latitude', 'longitude']].query('latitude != -999 and longitude != -999')

        # Convert the coordinates DataFrame to a list of lists
        coordinates = self.coordinates_df.values.tolist()

        # Calculate the center latitude and longitude
        if len(coordinates) == 0:
            results.append([0,0,0,0,0,0,0,0])
            self.results_df = pd.DataFrame(results, columns=["SD_Spread_X", "SD_Spread_Y", "RMS", "Spread_X", "Spread_Y", "CEP", "Area", "N",])
        else:
            center_lat = sum(float(coord[0]) for coord in coordinates) / len(coordinates)
            center_lon = sum(float(coord[1]) for coord in coordinates) / len(coordinates)

            # Find the UTM zone and hemisphere
            zone_number = int((180 + center_lon) / 6) + 1
            hemisphere = 'north' if center_lat >= 0 else 'south'

            # Create a transformer for converting latitude and longitude to UTM
            transformer = Transformer.from_crs(
                f'+proj=longlat +datum=WGS84 +no_defs',
                f'+proj=utm +zone={zone_number} +{hemisphere} +datum=WGS84 +units=m +no_defs',
                always_xy=True
            )

            # Convert the coordinates to UTM
            utm_coords = [transformer.transform(coord[1], coord[0]) for coord in coordinates]

            # Calculate the 1 SD spread and RMS error for each cluster
            rms_errors = []
            ceps = []
            min_bounding_polygons = []

            cluster_coords = utm_coords
            std_dev_x = np.std([coord[0] for coord in cluster_coords])
            std_dev_y = np.std([coord[1] for coord in cluster_coords])
            rms_error = np.sqrt((std_dev_x**2 + std_dev_y**2) / 2)
            rms_errors.append(rms_error)
            print(f"Cluster - 1 SD spread (meters): X: {std_dev_x}, Y: {std_dev_y}")
            print(f"Cluster - RMS error (meters): {rms_error}")

            spread_x = max(coord[0] for coord in cluster_coords) - min(coord[0] for coord in cluster_coords)
            spread_y = max(coord[1] for coord in cluster_coords) - min(coord[1] for coord in cluster_coords)
            print(f"Cluster - Spread (meters): X: {spread_x}, Y: {spread_y}")
            
            center = np.mean(cluster_coords, axis=0)
            distances = [distance.euclidean(coord, center) for coord in cluster_coords]
            cep = np.percentile(distances, 50)
            ceps.append(cep)
            print(f"Cluster - CEP: {cep}") 

            points = MultiPoint(cluster_coords)
            min_rotated_rect = points.minimum_rotated_rectangle
            min_bounding_polygons.append(min_rotated_rect)
            print(f"Cluster - Area: {min_rotated_rect.area}") 

            print(f"N = {len(cluster_coords)}")

            # Create a map centered at the average of the coordinates
            self.map_gps = folium.Map(location=[center_lat, center_lon], zoom_start=22, tiles='CartoDB Positron')
            ### These are nice to have, but open very slowly on the RPi...
            # self.map_gps = folium.Map(location=[center_lat, center_lon], zoom_start=22, tiles='Stamen Terrain')
            # folium.TileLayer('cartodbdark_matter').add_to(self.map_gps)
            # folium.TileLayer('CartoDB Positron').add_to(self.map_gps)
            # Add a layer control widget to the map
            # folium.LayerControl().add_to(self.map_gps)

            # Add the points to the map with different colors for each cluster
            for coord in coordinates:
                folium.Circle(location=[float(coord[0]), float(coord[1])], radius=1, color="green", fill=False, fill_opacity=0.1).add_to(self.map_gps)

            # Calculate center of coordinates
            center = np.mean(coordinates, axis=0)

            # Use the center for each marker
            for i, (rms, cep, min_bounding_polygon) in enumerate(zip(rms_errors, ceps, min_bounding_polygons)):
                folium.Marker(location=[float(center[0]), float(center[1])], icon=None, popup=f"RMS: {round(rms, 1)} meters\nCEP: {round(cep, 1)} meters\nArea: {round(min_bounding_polygon.area, 1)} sq meters").add_to(self.map_gps)
            
            results.append([std_dev_x,std_dev_y,rms_error,spread_x,spread_y,cep,min_rotated_rect.area,len(cluster_coords)])

            self.results_df = pd.DataFrame(results, columns=["SD_Spread_X", "SD_Spread_Y", "RMS", "Spread_X", "Spread_Y", "CEP", "Area", "N",])
            self.has_points = True
            self.CEP = cep
            self.RMS = rms_error

            # Creating the x,y plot with the center translated to the origin
            cluster_coords_array = np.array(cluster_coords)
            center = np.mean(cluster_coords_array, axis=0)
            translated_coords = cluster_coords_array - center

            # Create a DataFrame with the translated coordinates
            df_coor = pd.DataFrame(translated_coords, columns=['x', 'y'])

            # Create a figure and an axis in matplotlib
            fig, ax = plt.subplots()

            # Create heatmap using seaborn's kdeplot
            c_cmap = sns.cubehelix_palette(start=2, rot=0, dark=0.20, light=.90, reverse=False, as_cmap=True)

            # Create heatmap using seaborn's kdeplot
            sns.kdeplot(data=df_coor, x='x', y='y', ax=ax, cmap=c_cmap, shade=True)


            # Add the points to the plot
            ax.scatter(df_coor['x'], df_coor['y'], color="lime")

            # Add RMS circle
            circle_rms = Circle((0, 0), rms_error, fill=False, color='magenta', linestyle='dashed')
            ax.add_patch(circle_rms)

            # Add CEP circle
            circle_cep = Circle((0, 0), cep, fill=False, color='cyan')
            ax.add_patch(circle_cep)

            # Setting equal aspect so the circles look like circles
            ax.set_aspect('equal')

            # Set axis labels and title
            ax.set_xlabel("West-East (meters)")
            ax.set_ylabel("North-South (meters)")
            ax.set_title("GPS Report")

            # Show legends
            ax.legend([circle_rms, circle_cep], ['RMS', 'CEP'])

            # Convert the Matplotlib figure to an OpenCV image
            canvas = FigureCanvas(fig)
            canvas.draw()
            gps_plot = np.frombuffer(canvas.tostring_rgb(), dtype='uint8')
            gps_plot = gps_plot.reshape(canvas.get_width_height()[::-1] + (3,))

            # Convert RGB to BGR
            self.gps_plot = cv2.cvtColor(gps_plot, cv2.COLOR_RGB2BGR)



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