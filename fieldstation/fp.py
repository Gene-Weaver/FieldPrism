#!/usr/bin/env python3
import time, os, cv2, keyboard, inspect, sys
import depthai as dai
from threading import Thread
import tkinter as tk
from tkinter import Tk
import pandas as pd
from gps3.agps3threaded import AGPS3mechanism
from utils_general import bcolors, load_cfg, print_options, rotate_image_options
from utils_gps import gps_activate, test_gps
from utils_gui import init_ready, change_ready_ind, config_gui
from utils_sound import *
from fp_align_camera  import align_camera
from fp_classes import PreviewWindow, SaveWindow, Fragile, SetupFP, ImageData, GPSTest
import numpy as np

currentdir = os.path.dirname(os.path.dirname(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
sys.path.append(currentdir)
# from fieldprism.utils_processing import (get_cfg_from_full_path, make_images_in_dir_vertical, get_scale_ratio, write_yaml, 
                            # make_file_names_valid, remove_overlapping_predictions, increment_path)
# from fieldprism.utils_processing import bcolors, File_Structure
from fieldprism.component_detector import check_QR_codes
from fieldprism.utils_barcodes import read_QR_codes
# from fieldprism.utils_rename import rename_files_from_QR_codes
# from fieldprism.utils_data import Data_Vault, Data_FS, Data_Naming, build_empty_csv, write_datarow_to_file, get_weights
'''
 ______ _      _     _ _____ _        _   _             
 |  ___(_)    | |   | /  ___| |      | | (_)            
 | |_   _  ___| | __| \ `--.| |_ __ _| |_ _  ___  _ __  
 |  _| | |/ _ \ |/ _` |`--. \ __/ _` | __| |/ _ \| '_ \ 
 | |   | |  __/ | (_| /\__/ / || (_| | |_| | (_) | | | |
 \_|   |_|\___|_|\__,_\____/ \__\__,_|\__|_|\___/|_| |_|

  By: William Weaver
  University of Michigan, 2022
  Department of Ecology and Evolutionary Biology

Thanks for using FieldPrism (FP) and FieldStation (FS)! Here are a few tips:

----- GUI and Usage ------------------------------------
     - Critical features are visualized in the GUI.
     - All QC / diagnostic messages are output in the terminal

     - Preview window is center crop of the live camera feed, updates ~3fps

     - Saved image window will show the image you just captured. It shows the file that
       was written to the storage device. If you don't see a photo in the window, then
       nothing was saved.  

     - Since the live camera feed is slow, count to 3 before taking a photo after you 
       make final adjustments to the specimen / subject.

     - Insufficient power delivery can cause several, strange issues. If you see
       an "Input/Output" error (in the terminal), then you need to supply more power.
     - The R Pi cannot deliver enough power for all components simultaneously. I recommend
       running the camera on a separate power bank, or at least using a power bank that 
       is rated to charge multiple devices at the same time (at least 2 USB-A ports)

----- Storage ------------------------------------
     - FieldPrism can write all data (images and CSV files) to up to 6 USB storage devices.
       (This is hard coded, not dynamic)
     - On each FieldPrism startup, you *MUST* run the Mount USB command
     - If you remove or add a USB drive, you *MUST* run the Mount USB command
     - Errors and unexpected behavior will occur if you do not run the Mount USB command 
       after each time that a USB drive is moved/added/removed 
     - If you get an "Input/Output" error (in the terminal) it is caused by 
       insufficient power delivery
     - You can save images to the boot SD card, but it is strongly not recommended

----- Mount USB Commands ------------------------------------
     - Can be run in three ways
     1. (Recommended) double click the Mount USB + icon on the desktop
        * If successful, the mounted drives that are visible on the desktop should 
          flash around, disappear, reappear
        * Insepct the terminal output and look for errors
     2. In the terminal...
        * cd into the FieldPrism folder:   cd FieldPrism/fieldstation
        * run:    python mount_usb_drives.py
        * verify that the terminal output makes sense
     3. In the terminal...
        * cd into the FieldPrism folder:   cd FieldPrism/fieldstation
        * run:    sh ./mount_usb_drives.sh
        * verify that the terminal output makes sense

----- USB Speed ------------------------------------
     - In the GUI, if USB Speed is not 'HIGH', then the USB cable connecting the camera to
       the Raspberry Pi is not capbable of high-speed data transfer. Replace it.

----- GPS ------------------------------------
     - See https://cdn-learn.adafruit.com/downloads/pdf/adafruit-ultimate-gps.pdf
     - The GPS will routinely timeout if not in use
     - Press the '2' key to wake it up without saving data or taking a photo
     - Time is reported in UTC time (aka. Greenwich Mean Time)  
     - GPS Speed: You can change the way FS gets a GPS point, but the default should
       work most of the time
           * 'fast' takes ~0.3sec. to get a fix 
           * 'cautious' takes ~1.5sec.
       Cautious adds a tiny delay to allow GPS lock and waits for 10 successful pings
       Fast has no delay and only waits for 3 successful pings

----- Time ------------------------------------
     - If there is no GPS signal, then the time will be based on the R Pi clock, which
       is likely to be wrong since it needs the internet to update. 

----- Time ------------------------------------
     - All data is saved to two files:
           1. A session CSV, new each time you launch FS
           2. A cummulative CSV, all data rows
     - Session CSVs are a backup

----- Mapping Keys ------------------------------------
     - If you use a mini keyboard other than the one we validated, you should verify 
       that the default key values of your keyboard. Connect it to any PC / MAC, see
       what each key press returns, map your keys in the config file below
     - Feel free to change the values to suite you

----- Camera Rotation ------------------------------------
     - Take a photo. If it looks strange in the Saved Image Window then adjust the 
       rotation options below
     - Setting both rotations parameters to True will rotate image 270 degrees CW
'''
'''
Detect if image was blurry
'''
def startup(dir_root, device, agps_thread, label_total_status, label_session_status, label_ndevice_status, label_usbspeed_status, label_camera_status, label_gps_status, label_gps_lat_status, label_gps_lon_status, label_local_time_status, label_gps_time_status):
    print('Connected cameras: ', device.getConnectedCameras())
    print('Usb speed: ', device.getUsbSpeed().name)
    
    # Load configs
    
    cfg_user = load_cfg() # from FieldStation.yaml
    cfg = SetupFP()
    sharpness_min_cutoff = cfg_user['fieldstation']['sharpness']
    '''
    Start the sound
    '''
    Sound = Sounds(dir_root, cfg_user)

    # Update USB Speed
    if device.getUsbSpeed().name == 'HIGH':
        label_usbspeed_status.config(text = str(device.getUsbSpeed().name), fg='green2')
    else:
        label_usbspeed_status.config(text = str(device.getUsbSpeed().name), fg='red')

    # Update device count 
    if cfg.device_count > 0:
        label_ndevice_status.config(text = str(cfg.device_count), fg='green2')
    else:
        label_ndevice_status.config(text = str(cfg.device_count), fg='red')

    # Update Total CSV
    label_total_status.config(text = str(cfg.name_total_csv), fg='white')

    # Update Session ID
    label_session_status.config(text = str(cfg.name_session_csv), fg='white')

    label_camera_status.config(text = 'Allow ~30 seconds for GPS fix', fg='cyan')
    n_attempts_on_startup = abs(int(cfg_user['fieldstation']['gps']['n_attempts_on_startup']))
    sec_pause_between_attempts_on_startup = abs(int(cfg_user['fieldstation']['gps']['n_attempts_on_startup']))
    for i in range(0,n_attempts_on_startup):
        print(f"{bcolors.WARNING}       Attempt #{i} to get GPS fix{bcolors.ENDC}")
        GPS_data_test = gps_activate(agps_thread, label_gps_status, label_gps_lat_status, label_gps_lon_status, label_local_time_status, label_gps_time_status, cfg_user,False,False)
        if GPS_data_test.latitude != -999:
            break
        time.sleep(sec_pause_between_attempts_on_startup)
    GPS_data_test = gps_activate(agps_thread, label_gps_status, label_gps_lat_status, label_gps_lon_status, label_local_time_status, label_gps_time_status, cfg_user,True,True)
    label_camera_status.config(text = ' Please Wait ', fg='green2')

    return cfg, cfg_user, Sound, sharpness_min_cutoff

def detect_sharpness(sharpness_min_cutoff, img):
    # Blurry image cutoff
    sharpness_actual = int(cv2.Laplacian(img, cv2.CV_64F).var())
    if sharpness_actual < sharpness_min_cutoff:
        return False, sharpness_actual
    else:
        return True, sharpness_actual
    
def update_level_labels(label, result):
    label.config(text=result)

def update_levels(L1, L2, L3, L4, L5, L6, RESULTS):
    update_level_labels(L1, RESULTS["Level_1"])
    update_level_labels(L2, RESULTS["Level_2"])
    update_level_labels(L3, RESULTS["Level_3"])
    update_level_labels(L4, RESULTS["Level_4"])
    update_level_labels(L5, RESULTS["Level_5"])
    update_level_labels(L6, RESULTS["Level_6"])

# def update_visibility(n_qr_value, L1, L2, L3, L4, L5, L6):
#     # n_qr_value = n_qr.get()
#     levels = [L1, L2, L3, L4, L5, L6]

#     for i, level in enumerate(levels):
#         if i < n_qr_value:
#             level.grid()
#         else:
#             level.grid_remove()

def report_sharpness(live_or_saved, label_focus_live_status, label_focus_saved_status, is_sharp, sharpness_min_cutoff, sharpness_actual):
    if live_or_saved == 'live':
        if is_sharp:
            text_focus_live = ''.join(['(',str(sharpness_min_cutoff),')',' Sharp - ', str(sharpness_actual)])
            label_focus_live_status.config(text = text_focus_live, fg='green2')
        else:
            text_focus_live = ''.join(['(',str(sharpness_min_cutoff),')',' Blurry - ', str(sharpness_actual)])
            label_focus_live_status.config(text = text_focus_live, fg='goldenrod')
    else:
        if is_sharp:
            text_focus_live = ''.join(['(',str(sharpness_min_cutoff),')',' Sharp - ', str(sharpness_actual)])
            label_focus_saved_status.config(text = text_focus_live, fg='green2')
        else:
            text_focus_live = ''.join(['(',str(sharpness_min_cutoff),')',' Blurry - ', str(sharpness_actual)])
            label_focus_saved_status.config(text = text_focus_live, fg='red')

def report_camera_activated(cfg_user, label_camera_status, images_this_session, Sound):
    print(f"       Camera Activated")
    # Play sound
    if cfg_user['fieldstation']['sound']['play_sound']:
        sound_taking_photo(Sound)
    # Print status
    print(f"       Capturing Image")
    label_camera_status.config(text = 'Capturing Image...', fg='goldenrod')
    images_this_session += 1
    return images_this_session

def report_camera_complete(cfg_user, Image, images_this_session, label_csv_status, label_camera_status, label_fname_status, label_nimage_status, Sound):
    label_csv_status.config(text = 'Added 1 Row to CSV', fg='green2')
    label_camera_status.config(text = 'Ready!', fg='green2')
    label_fname_status.config(text = Image.filename)
    label_nimage_status.config(text = str(images_this_session))
    print(f"{bcolors.OKGREEN}Ready{bcolors.ENDC}")
    if cfg_user['fieldstation']['sound']['play_sound']:
        sound_photo_complete(Sound)

'''
Save image to storage device
'''
def save_image(save_frame, name_time, save_dir):
    path_to_saved = "".join([name_time,'.jpg'])
    path_to_saved = os.path.join(save_dir,path_to_saved)

    cv2.imwrite(path_to_saved, save_frame)

    print(f"{bcolors.OKGREEN}       Image Saved: {path_to_saved}{bcolors.ENDC}")    
    return path_to_saved

'''
Route the photo to each attached storage device. 
'''
def route_save_image(Setup, cfg_user, save_frame, is_sharp):
    name_time = str(int(time.time() * 1000))
    if not is_sharp:
        if cfg_user['fieldstation']['add_flag_to_blurry_images']:
            name_time = ''.join([name_time, '__B'])

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
    return path_to_saved, name_time

def route_save_image_qr(Setup, cfg_user, save_frame, is_sharp, name_time):
    if not is_sharp:
        if cfg_user['fieldstation']['add_flag_to_blurry_images']:
            name_time = ''.join([name_time, '__B'])

    if Setup.save_to_boot:
        path_to_saved = save_image(save_frame, name_time, Setup.dir_qr_none)
    if Setup.has_1_usb:
        path_to_saved = save_image(save_frame, name_time, Setup.dir_qr_1)
    if Setup.has_2_usb:
        path_to_saved = save_image(save_frame, name_time, Setup.dir_qr_2)
    if Setup.has_3_usb:
        path_to_saved = save_image(save_frame, name_time, Setup.dir_qr_3)
    if Setup.has_4_usb:
        path_to_saved = save_image(save_frame, name_time, Setup.dir_qr_4)
    if Setup.has_5_usb:
        path_to_saved = save_image(save_frame, name_time, Setup.dir_qr_5)
    if Setup.has_6_usb:
        path_to_saved = save_image(save_frame, name_time, Setup.dir_qr_6)
    return path_to_saved

def route_save_image_qr_crop(Setup, cfg_user, save_frame, is_sharp, name_time):
    path_to_saved = None  # Initialize the variable
    counter = 1  # Counter for appending "__n" to name_time

    for frame in save_frame:
        # print(f"before: {name_time}")
        # Append "__n" to name_time
        name_time_with_counter = f"{name_time}__{counter}"
        # print(f"after: {name_time_with_counter}")
        
        if Setup.save_to_boot:
            path_to_saved = save_image(frame, name_time_with_counter, Setup.dir_qr_none)
        if Setup.has_1_usb:
            path_to_saved = save_image(frame, name_time_with_counter, Setup.dir_qr_1)
        if Setup.has_2_usb:
            path_to_saved = save_image(frame, name_time_with_counter, Setup.dir_qr_2)
        if Setup.has_3_usb:
            path_to_saved = save_image(frame, name_time_with_counter, Setup.dir_qr_3)
        if Setup.has_4_usb:
            path_to_saved = save_image(frame, name_time_with_counter, Setup.dir_qr_4)
        if Setup.has_5_usb:
            path_to_saved = save_image(frame, name_time_with_counter, Setup.dir_qr_5)
        if Setup.has_6_usb:
            path_to_saved = save_image(frame, name_time_with_counter, Setup.dir_qr_6)

        counter += 1  # Increment the counter for the next iteration

    # print(f"counter = {counter}")
    return path_to_saved

'''
Button callbacks
'''
def command_exit(cfg_user, Sound, agps_thread, root):
    if cfg_user['fieldstation']['sound']['play_sound']:
        sound_exit(Sound)
    print(f"{bcolors.HEADER}Stopping...{bcolors.ENDC}")
    print_options()
    agps_thread.stop()
    cv2.destroyAllWindows()
    root.destroy()

def command_gps(cfg_user, agps_thread, label_gps_status, label_gps_lat_status, label_gps_lon_status, label_local_time_status, label_gps_time_status, Sound):
    print(f"       Testing GPS")
    GPS_data_test = gps_activate(agps_thread, label_gps_status, label_gps_lat_status, label_gps_lon_status, label_local_time_status, label_gps_time_status, cfg_user,True,True)
    if cfg_user['fieldstation']['sound']['play_sound']:
        if GPS_data_test.latitude == -999:
            sound_gps_fail(Sound)
        else:
            sound_gps_success(Sound)

def run_gps_acc_test(label_camera_status, cfg, cfg_user, gps_acc, agps_thread, label_gps_status, label_gps_lat_status, label_gps_lon_status, label_local_time_status, label_gps_time_status, Sound):
    label_camera_status.config(text = 'Testing GPS Accuracy', fg='goldenrod')

    print(f"       Running GPS Accuracy Test")
    selection = gps_acc.get()
    if selection == "min5":
        gps_val = False
    elif selection == "min15":
        print(f"{bcolors.BOLD}            Using unstable enhanced QR reader{bcolors.ENDC}")
        gps_val = True



    if not gps_val:
        print(f"           5 Min Test")
        label_camera_status.config(text = f'Waking GPS - 0%', fg='goldenrod')
        # Loop 60 times
        n_times = 100
        for nnn in range(n_times):
            percent = round(np.multiply(np.divide(nnn+1,n_times),100))
            label_camera_status.config(text = f'Waking GPS - {percent}%', fg='goldenrod')
            ___ = gps_activate(agps_thread, label_gps_status, label_gps_lat_status, label_gps_lon_status, label_local_time_status, label_gps_time_status, cfg_user,True,True)

        # Initialize CSV file
        data = []

        # Loop 60 times
        n_times = 6
        for nnn in range(n_times):
            percent = round(np.multiply(np.divide(nnn+1,n_times),100))
            label_camera_status.config(text = f'5 Min GPS Test - {percent}%', fg='goldenrod')
            GPS_data = gps_activate(agps_thread, label_gps_status, label_gps_lat_status, label_gps_lon_status, label_local_time_status, label_gps_time_status, cfg_user,True,True)
            if GPS_data.latitude == -999:
                sound_gps_fail(Sound)
            else:
                sound_gps_success(Sound)

            current_time = GPS_data.current_time
            latitude = GPS_data.latitude
            longitude = GPS_data.longitude
            altitude = GPS_data.altitude
            climb = GPS_data.climb
            speed = GPS_data.speed
            lat_error_est = GPS_data.lat_error_est
            lon_error_est = GPS_data.lon_error_est
            alt_error_est = GPS_data.alt_error_est

            # Append data to DataFrame
            data.append([current_time, latitude, longitude, altitude, climb, speed, lat_error_est, lon_error_est, alt_error_est])
            
            time.sleep(4.8)
        GPS_all = pd.DataFrame(data, columns=["current_time", "latitude", "longitude", "altitude", "climb", "speed", "lat_error_est", "lon_error_est", "alt_error_est"])
        GPSTest(cfg, GPS_all)
    else:
        print(f"           15 Min Test")
        label_camera_status.config(text = f'Waking GPS - 0%', fg='goldenrod')
        # Loop 60 times
        n_times = 100
        for nnn in range(n_times):
            percent = round(np.multiply(np.divide(nnn+1,n_times),100))
            label_camera_status.config(text = f'Waking GPS - {percent}%', fg='goldenrod')
            ___ = gps_activate(agps_thread, label_gps_status, label_gps_lat_status, label_gps_lon_status, label_local_time_status, label_gps_time_status, cfg_user,True,True)
            time.sleep(0.1)

        # Initialize CSV file
        data = []

        # Loop 180 times
        n_times = 180
        for _ in range(n_times):
            percent = round(np.multiply(np.divide(nnn+1,n_times),100))
            label_camera_status.config(text = f'15 Min GPS Test - {percent}%', fg='goldenrod')
            GPS_data = gps_activate(agps_thread, label_gps_status, label_gps_lat_status, label_gps_lon_status, label_local_time_status, label_gps_time_status, cfg_user,True,True)
            if GPS_data.latitude == -999:
                sound_gps_fail(Sound)
            else:
                sound_gps_success(Sound)

            current_time = GPS_data.current_time
            latitude = GPS_data.latitude
            longitude = GPS_data.longitude
            altitude = GPS_data.altitude
            climb = GPS_data.climb
            speed = GPS_data.speed
            lat_error_est = GPS_data.lat_error_est
            lon_error_est = GPS_data.lon_error_est
            alt_error_est = GPS_data.alt_error_est

            # Append data to DataFrame
            data.append([current_time, latitude, longitude, altitude, climb, speed, lat_error_est, lon_error_est, alt_error_est])

            time.sleep(4.8)
        GPS_all = pd.DataFrame(data, columns=["current_time", "latitude", "longitude", "altitude", "climb", "speed", "lat_error_est", "lon_error_est", "alt_error_est"])
        GPSTest(cfg, GPS_all)


def button_photo():
    global TAKE_PHOTO
    TAKE_PHOTO = True

def button_gps():
    global TAKE_GPS
    TAKE_GPS = True

def button_gps_test():
    global TEST_GPS
    TEST_GPS = True

def button_exit():
    global TAKE_EXIT
    TAKE_EXIT = True
    
'''
Creates the pipeline that the OAK camera requires
    THE_12_MP allows us to use the full sensor of the OAK-1 camera
    'isp' will save the still
    'video' shows the check camera focus window
'''
def createPipeline():
    # Create pipeline
    pipeline = dai.Pipeline()

    # Define sources and outputs
    camRgb = pipeline.create(dai.node.ColorCamera)
    camRgb.setBoardSocket(dai.CameraBoardSocket.RGB)
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

'''
Main code that runs the GUI, is called from start_gui()
'''
def run(pipeline, root):
    software_version = '2023-05 v-2-0'
    dir_root = os.path.dirname(os.path.dirname(__file__))
    '''
    Make sure the destination path is present before starting to store the examples
    '''
    img_preview = cv2.imread(os.path.join(dir_root,'img','preview_window.jpg'))
    img_saved = cv2.imread(os.path.join(dir_root,'img','saved_image_window.jpg'))

    '''Start the GPS'''
    agps_thread = AGPS3mechanism()  # Instantiate AGPS3 Mechanisms
    agps_thread.stream_data()  # From localhost (), or other hosts, by example, (host='gps.ddns.net')
    agps_thread.run_thread()  # Throttle time to sleep after an empty lookup, default '()' 0.2 two tenths of a second

    # Initialize globals for buttons
    global TAKE_PHOTO
    TAKE_PHOTO = False
    global TAKE_GPS
    TAKE_GPS = False
    global TAKE_EXIT
    TAKE_EXIT = False
    global TEST_GPS
    TEST_GPS = False

    '''
    Setup the GUI
    '''
    [root, frame_preview, frame_saved, label_camera_status, label_focus_live_status, 
    label_focus_saved_status, label_fname_status, label_gps_status, label_gps_lat_status, 
    label_gps_lon_status, label_gps_time_status, label_local_time_status, label_total_status, 
    label_session_status, label_csv_status, label_nimage_status, label_ndevice_status, 
    label_usbspeed_status, label_version_status, label_nqr_status,
    L1, L2, L3, L4, L5, L6, use_enhanced, gps_acc, frame_qr_data] = config_gui(root, software_version)

    # -------------- Buttons
    # frame
    root.configure(bg="black")
    frame_button = tk.Frame(master=root, height = 60, bg="black")
    frame_button.grid(row=4, column=0, columnspan= 2, sticky="nsew")
    
    frame_button.rowconfigure(0, minsize=60)
    frame_button.columnconfigure([0, 1, 2, 3, 4, 5], minsize=200)

    b_photo = tk.Button(master=frame_button, command=lambda: button_photo(), text = "PHOTO", font=("Arial", 20), bg="green4", fg="black", activebackground="green2")
    b_gps = tk.Button(master=frame_button, command=lambda: button_gps(), text = "GPS", font=("Arial", 20), bg="royal blue", fg="black", activebackground="deep sky blue")
    b_exit = tk.Button(master=frame_button, command=lambda: button_exit(), text = "QUIT", font=("Arial", 20), bg="maroon", fg="white", activebackground="red")
    b_gps_acc_test = tk.Button(master=frame_qr_data, command=lambda: button_gps_test(), text = "Test", font=("Arial", 20), bg="royal blue", fg="black", activebackground="deep sky blue")

    b_exit.grid(row=0, column=0, sticky="nsew")
    b_gps.grid(row=0, column=3, sticky="nsew")
    b_photo.grid(row=0, column=4, sticky="nsew")
    b_gps_acc_test.grid(row=19, column=0, sticky="nsew")

    '''
    Initialize the two camera windows in the GUI
    '''
    Window_Preview = PreviewWindow(frame_preview,img_preview)
    Window_Saved = SaveWindow(frame_saved,img_saved)
    
    '''
    Connect to camera and start pipeline
        Fragile class allows the whole pipeline and GUI to terminate on exit keypress
    '''
    with Fragile(dai.Device(pipeline)) as device:
        # Test GPS, takes 34 seconds to wake, try to get signal 
        cfg, cfg_user, Sound, sharpness_min_cutoff = startup(dir_root, device, agps_thread, label_total_status,
                                                            label_session_status, label_ndevice_status, label_usbspeed_status,
                                                            label_camera_status, label_gps_status, label_gps_lat_status, label_gps_lon_status, 
                                                            label_local_time_status, label_gps_time_status)     

        '''
        If USB storage is not present, quit
        '''
        if cfg.storage_present == False:
            print(f"{bcolors.HEADER}Stopping...{bcolors.ENDC}")
            print_options()
            if cfg_user['fieldstation']['sound']['play_sound']:
                sound_storage_error(Sound)
            raise Fragile.Break
        else:
            # Get data queues from camera
            ispQueue = device.getOutputQueue('isp', maxSize=1, blocking=False)
            videoQueue = device.getOutputQueue('video', maxSize=1, blocking=False)

            # Initialize "Ready" animated text for the GUI
            ind_ready, direction = init_ready()

            images_this_session = 0
            if cfg_user['fieldstation']['sound']['play_sound']:
                sound_start(Sound)
            # Data collection / imaging loop, exit on keypress, using Fragile class
            while True:
                # Update "Ready" each loop
                text_ready, ind_ready, direction = change_ready_ind(ind_ready,direction)
                label_camera_status.config(text = text_ready, fg='green2')
                
                # Get latest frame from camera video feed (center crop)
                vidFrames = videoQueue.tryGetAll()
                for vidFrame in vidFrames:
                    vframe = vidFrame.getCvFrame()
                    vframe = rotate_image_options(vframe,cfg_user)
                    # cv2.imshow('preview', vframe)
                    # PreviewWindow(FS.frame_preview,vframe)
                    # Window_Preview.change_image(vframe)
                    Window_Preview.update_image(vframe)
                    is_sharp, sharpness_actual = detect_sharpness(sharpness_min_cutoff, vframe)
                    report_sharpness('live', label_focus_live_status, label_focus_saved_status, is_sharp, sharpness_min_cutoff, sharpness_actual)

                # Get latest frame from camera full sensor
                ispFrames = ispQueue.get()
                isp = ispFrames.getCvFrame()

                # If keypress for photo on last loop, then save a still now
                # update_visibility(int(label_nqr_status.cget("text")), L1, L2, L3, L4, L5, L6)
                if TAKE_PHOTO:
                    # Print status
                    label_camera_status.config(text = 'Camera Activated...', fg='goldenrod')
                    label_csv_status.config(text = 'Collecting Data', fg='goldenrod')
                    
                    images_this_session = report_camera_activated(cfg_user, label_camera_status, images_this_session, Sound)

                    # Get latest frame
                    ispFrames = ispQueue.get()
                    save_frame = ispFrames.getCvFrame()

                    # Get pixel dimensions
                    height = save_frame.shape[0]
                    width = save_frame.shape[1]

                    # Rotate Camera
                    # Can rotate 270 by setting both to True
                    save_frame = rotate_image_options(save_frame,cfg_user)

                    # Check focus
                    is_sharp, sharpness_actual = detect_sharpness(sharpness_min_cutoff, save_frame)
                    report_sharpness('saved', label_focus_live_status, label_focus_saved_status, is_sharp, sharpness_min_cutoff, sharpness_actual)

                    # Save image
                    path_to_saved, name_time = route_save_image(cfg, cfg_user, save_frame, is_sharp)

                    # Update the image in the GUI by reading the image that was just written to storage
                    Window_Saved.update_image(cv2.pyrDown(cv2.pyrDown(cv2.pyrDown(cv2.imread(path_to_saved)))))

                    # Activate GPS, update GUI, and return GPS data
                    GPS_data = gps_activate(agps_thread, label_gps_status, label_gps_lat_status, label_gps_lon_status, label_local_time_status, label_gps_time_status, cfg_user,True,True)

                    # Check for valid QR code
                    n_qr = int(label_nqr_status.cget("text"))
                    label_camera_status.config(text = 'Detecting QR Codes and Markers', fg='magenta')
                    qr_found, img_out_qr, cropped_QRs = check_QR_codes(path_to_saved, cfg.dir_data_session_qr, cfg.name_session, label_nqr_status)
                    path_to_saved_qr_whole = route_save_image_qr(cfg, cfg_user, img_out_qr, is_sharp, name_time)
                    path_to_saved_qr = route_save_image_qr_crop(cfg, cfg_user, cropped_QRs, is_sharp, name_time)

                    # Update the image in the GUI by reading the image that was just written to storage
                    try:
                        Window_Saved.update_image(cv2.pyrDown(cv2.pyrDown(cv2.pyrDown(cv2.imread(path_to_saved_qr_whole)))))
                    except:
                        Window_Saved.update_image(cv2.pyrDown(cv2.pyrDown(cv2.pyrDown(cv2.imread(path_to_saved)))))

                    label_camera_status.config(text = 'Reading QR Codes', fg='magenta')
                    RESULTS = read_QR_codes(n_qr, cropped_QRs, use_enhanced)
                    update_levels(L1, L2, L3, L4, L5, L6, RESULTS)

                    # Write data to CSV file
                    Image = ImageData(cfg, path_to_saved, GPS_data, height, width, sharpness_actual, sharpness_min_cutoff, is_sharp)

                    # Print status
                    report_camera_complete(cfg_user, Image, images_this_session, label_csv_status, label_camera_status, label_fname_status, label_nimage_status, Sound)

                    # Reset TAKE_PHOTO
                    TAKE_PHOTO = False

                # Key Press Options
                _key = cv2.waitKey(50)
                if (keyboard.is_pressed(cfg_user['fieldstation']['keymap']['exit']) or TAKE_EXIT):
                    command_exit(cfg_user, Sound, agps_thread, root)
                    break

                elif keyboard.is_pressed(cfg_user['fieldstation']['keymap']['photo']):
                    # Take photo
                    TAKE_PHOTO = True

                elif (keyboard.is_pressed(cfg_user['fieldstation']['keymap']['test_gps']) or TAKE_GPS):
                    TAKE_GPS = False
                    command_gps(cfg_user, agps_thread, label_gps_status, label_gps_lat_status, label_gps_lon_status, label_local_time_status, label_gps_time_status, Sound)

                elif TEST_GPS:
                    TEST_GPS = False
                    run_gps_acc_test(label_camera_status, cfg, cfg_user, gps_acc, agps_thread, label_gps_status, label_gps_lat_status, label_gps_lon_status, label_local_time_status, label_gps_time_status, Sound)

'''
Initialize the tkinter GUI
    Threading is required to run the GUI and camera simultaneously
'''
def start_gui():
    pipeline = createPipeline()
    root = Tk()
    root.title("FieldPrism - Field Station")
    root.minsize(width=507, height=450)

    Thread(target=run, args=(pipeline,root,), daemon=True).start()

    root.mainloop()

'''
Routing options
    May be deprecated
'''
def route():
    cfg_user = load_cfg()
    if cfg_user['fieldstation']['open_GUI_directly']:
        start_gui()
    else:
        print_options()
        while True:
            key = cv2.waitKey(1)
            if keyboard.is_pressed('6'):
                print(f"{bcolors.HEADER}Exiting FieldPrism{bcolors.ENDC}")
                cv2.destroyAllWindows()
                break
            elif keyboard.is_pressed('1'):
                print("Starting FieldPrism Data Collection")
                start_gui()
            elif keyboard.is_pressed('2'):
                print("Test/Wake GPS")
                test_gps()
            elif keyboard.is_pressed('3'):
                print("Aligning Camera")
                align_camera()

if __name__ == "__main__":
    route()
