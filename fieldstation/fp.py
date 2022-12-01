#!/usr/bin/env python3
import time, os, cv2, keyboard
import depthai as dai
from threading import Thread
import tkinter as tk
from tkinter import Tk
from utils import bcolors, load_cfg, print_options, rotate_image_options
from utils_gps import gps_activate, get_gps
from utils_gui import init_ready, change_ready_ind
from fp_align_camera  import align_camera
from fp_classes import PreviewWindow, SaveWindow, Fragile, SetupFP, ImageData

'''
### GUI and Usage ###
* Critical features are visualized in the GUI.
* All QC / diagnostic messages are output in the terminal

* Preview window is center crop of the live camera feed, updates ~3fps

* Saved image window will show the image you just captured. It shows the file that
  was written to the storage device. If you don't see a photo in the window, then
  nothing was saved.  

* Since the live camera feed is slow, count to 3 before taking a photo after you 
  make final adjustments to the specimen.

### Storage ###
* FieldPrism can write all data (images and CSV files) to up to 6 USB storage devices.
* On each FieldPrism startup, we recommend running the Mount USB commands
* Errors and unexpected behavior will occur if you do not run th Mount USB commands 
  after each time that a USB drive is moved/added/removed 

### Mount USB Commands ###
* Can be run in three ways
    1. double click the USB + icon on the desktop
        * If successful, the mounted drives that are visible on the desktop should 
          flash around, disappear, reappear
    2. in the terminal...
        * cd into the FieldPrism folder:   cd FieldPrism/fieldstation
        * run:    python mount_usb_drives.py
        * verify that the terminal output makes sense
    3. in the terminal...
        * cd into the FieldPrism folder:   cd FieldPrism/fieldstation
        * run:    sh ./mount_usb_drives.sh
        * verify that the terminal output makes sense

### USB Speed ##
* In the GUI, if USB Speed is not 'HIGH', then the USB cable connecting the camera to
  the Raspberry Pi is not capbable of high-speed data transfer. Replace it.

### GPS ###
* See https://cdn-learn.adafruit.com/downloads/pdf/adafruit-ultimate-gps.pdf
* The GPS will routinely timeout if not in use.
* Press the '2' key to wake it up without saving data or taking a photo
* Time is reported in UTC time (aka. Greenwich Mean Time)

'''


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

'''
Creates the pipeline that the OAK camera requires
    THE_12_MP allows us to use the full sensor of the OAK-1 camera
    'isp' will save the still
    'video' shows the check camera focus window
'''
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

'''
Main code that runs the GUI, is called from start_gui()
'''
def run(pipeline, root):
    software_version = '2022-12 v-1-0'
    dir_root = os.path.dirname(os.path.dirname(__file__))
    '''
    Make sure the destination path is present before starting to store the examples
    '''
    img_preview = cv2.imread(os.path.join(dir_root,'img/preview_window.jpg'))
    img_saved = cv2.imread(os.path.join(dir_root,'img/saved_image_window.jpg'))

    '''
    Setup the GUI
    '''
    root.rowconfigure([0, 1, 2, 3], minsize=30)
    root.columnconfigure([0, 1], minsize=100)

    # -------------- Camera Preview Window (Check Camera Focus)
    label_preview = tk.Label(master=root, text="Preview (Check Camera Focus)", bg="black", fg="white", font=("Arial", 20))
    label_preview.grid(row=0, column=0, sticky="nsew")
    frame_preview = tk.Frame(master=root, height=240, bg="black")
    frame_preview.grid(row=1, column=0, sticky="nsew")

    # -------------- Camera Window, shows saved image
    label_saved = tk.Label(master=root, text="Saved Image", bg="black", fg="white", font=("Arial", 20))
    label_saved.grid(row=2, column=0, sticky="nsew")
    frame_saved = tk.Frame(master=root, height=380, bg="black")
    frame_saved.grid(row=3, column=0, sticky="nsew")

    # -------------- Info header
    label_top_info = tk.Label(master=root, text="Info", bg="black", fg="white", font=("Arial", 20))
    label_top_info.grid(row=0, column=1, sticky="nsew")

    # -------------- Frame that will contain all status info below
    # -------------- frame_info will contain each label in a 18 row x 2 column layout 
    frame_info = tk.Frame(master=root, width = 250, bg="black")
    frame_info.grid(row=1, column=1, rowspan=3, sticky="nsew")

    frame_info.rowconfigure([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19], minsize=30)
    frame_info.columnconfigure(0, minsize=250)

    # -------------- Camera status
    frame_info_camera = tk.Frame(master=frame_info, height=60, width = 250, bg="black")
    frame_info_camera.grid(row=0, column=0, sticky="nsew")
    frame_info_camera.rowconfigure(0, minsize=60)
    frame_info_camera.columnconfigure([0, 1], minsize=250)

    label_camera = tk.Label(master=frame_info_camera, text="Camera Status: ", bg="black", fg="White", font=("Calibri ", 16))
    label_camera.grid(row=0, column=0, sticky="e")
    label_camera_status = tk.Label(master=frame_info_camera, text=" Please Wait ", bg="black", fg="green", font=("Calibri", 16))
    label_camera_status.grid(row=0, column=1, sticky="w")

    # -------------- File name
    frame_info_fname = tk.Frame(master=frame_info, height=60, width = 250, bg="black")
    frame_info_fname.grid(row=1, column=0, sticky="nsew")
    frame_info_fname.rowconfigure(0, minsize=30)
    frame_info_fname.columnconfigure([0, 1], minsize=250)

    label_fname = tk.Label(master=frame_info_fname, text="Image File Name: ", bg="black", fg="White", font=("Calibri ", 16))
    label_fname.grid(row=0, column=0, sticky="e")
    label_fname_status = tk.Label(master=frame_info_fname, text="", bg="black", fg="green", font=("Calibri ", 16))
    label_fname_status.grid(row=0, column=1, sticky="w")

    # -------------- GPS Status
    frame_info_gps = tk.Frame(master=frame_info, height=60, width = 250, bg="black")
    frame_info_gps.grid(row=3, column=0, sticky="nsew")
    frame_info_gps.rowconfigure(0, minsize=30)
    frame_info_gps.columnconfigure([0, 1], minsize=250)

    label_gps = tk.Label(master=frame_info_gps, text="GPS Status: ", bg="black", fg="White", font=("Calibri ", 16))
    label_gps.grid(row=0, column=0, sticky="e")
    label_gps_status = tk.Label(master=frame_info_gps, text="", bg="black", fg="green", font=("Calibri ", 16))
    label_gps_status.grid(row=0, column=1, sticky="w")

    # -------------- GPS Lat
    frame_info_gps_lat = tk.Frame(master=frame_info, height=60, width = 250, bg="black")
    frame_info_gps_lat.grid(row=4, column=0, sticky="nsew")
    frame_info_gps_lat.rowconfigure(0, minsize=30)
    frame_info_gps_lat.columnconfigure([0, 1], minsize=250)

    label_gps_lat = tk.Label(master=frame_info_gps_lat, text="Latitude: ", bg="black", fg="White", font=("Calibri ", 16))
    label_gps_lat.grid(row=0, column=0, sticky="e")
    label_gps_lat_status = tk.Label(master=frame_info_gps_lat, text="", bg="black", fg="green", font=("Calibri ", 16))
    label_gps_lat_status.grid(row=0, column=1, sticky="w")

    # -------------- GPS Long
    frame_info_gps_lon = tk.Frame(master=frame_info, height=60, width = 250, bg="black")
    frame_info_gps_lon.grid(row=5, column=0, sticky="nsew")
    frame_info_gps_lon.rowconfigure(0, minsize=30)
    frame_info_gps_lon.columnconfigure([0, 1], minsize=250)

    label_gps_lon = tk.Label(master=frame_info_gps_lon, text="Longitude: ", bg="black", fg="White", font=("Calibri ", 16))
    label_gps_lon.grid(row=0, column=0, sticky="e")
    label_gps_lon_status = tk.Label(master=frame_info_gps_lon, text="", bg="black", fg="green", font=("Calibri ", 16))
    label_gps_lon_status.grid(row=0, column=1, sticky="w")

    # -------------- GPS Time (UTC)
    frame_info_gps_time = tk.Frame(master=frame_info, height=60, width = 250, bg="black")
    frame_info_gps_time.grid(row=6, column=0, sticky="nsew")
    frame_info_gps_time.rowconfigure(0, minsize=30)
    frame_info_gps_time.columnconfigure([0, 1], minsize=250)

    label_gps_time = tk.Label(master=frame_info_gps_time, text="GPS Time (UTC): ", bg="black", fg="White", font=("Calibri ", 16))
    label_gps_time.grid(row=0, column=0, sticky="e")
    label_gps_time_status = tk.Label(master=frame_info_gps_time, text="", bg="black", fg="white", font=("Calibri ", 16))
    label_gps_time_status.grid(row=0, column=1, sticky="w")

    # -------------- R Pi Local Time
    frame_info_local_time = tk.Frame(master=frame_info, height=60, width = 250, bg="black")
    frame_info_local_time.grid(row=7, column=0, sticky="nsew")
    frame_info_local_time.rowconfigure(0, minsize=30)
    frame_info_local_time.columnconfigure([0, 1], minsize=250)

    label_local_time = tk.Label(master=frame_info_local_time, text="Local Time (R Pi): ", bg="black", fg="White", font=("Calibri ", 16))
    label_local_time.grid(row=0, column=0, sticky="e")
    label_local_time_status = tk.Label(master=frame_info_local_time, text="", bg="black", fg="white", font=("Calibri ", 16))
    label_local_time_status.grid(row=0, column=1, sticky="w")

    # -------------- CSV Total
    frame_info_total = tk.Frame(master=frame_info, height=60, width = 250, bg="black")
    frame_info_total.grid(row=10, column=0, sticky="nsew")
    frame_info_total.rowconfigure(0, minsize=30)
    frame_info_total.columnconfigure([0, 1], minsize=250)

    label_total = tk.Label(master=frame_info_total, text="CSV Total: ", bg="black", fg="White", font=("Calibri ", 16))
    label_total.grid(row=0, column=0, sticky="e")
    label_total_status = tk.Label(master=frame_info_total, text="", bg="black", fg="white", font=("Calibri ", 16))
    label_total_status.grid(row=0, column=1, sticky="w")
    
    # -------------- CSV Session
    frame_info_session = tk.Frame(master=frame_info, height=60, width = 250, bg="black")
    frame_info_session.grid(row=11, column=0, sticky="nsew")
    frame_info_session.rowconfigure(0, minsize=30)
    frame_info_session.columnconfigure([0, 1], minsize=250)

    label_session = tk.Label(master=frame_info_session, text="CSV Session: ", bg="black", fg="White", font=("Calibri ", 16))
    label_session.grid(row=0, column=0, sticky="e")
    label_session_status = tk.Label(master=frame_info_session, text="", bg="black", fg="white", font=("Calibri ", 16))
    label_session_status.grid(row=0, column=1, sticky="w")

    # -------------- CSV
    frame_info_csv = tk.Frame(master=frame_info, height=60, width = 250, bg="black")
    frame_info_csv.grid(row=12, column=0, sticky="nsew")
    frame_info_csv.rowconfigure(0, minsize=30)
    frame_info_csv.columnconfigure([0, 1], minsize=250)

    label_csv = tk.Label(master=frame_info_csv, text="CSV Data: ", bg="black", fg="White", font=("Calibri ", 16))
    label_csv.grid(row=0, column=0, sticky="e")
    label_csv_status = tk.Label(master=frame_info_csv, text="Waiting", bg="black", fg="white", font=("Calibri ", 16))
    label_csv_status.grid(row=0, column=1, sticky="w")

    # -------------- CSV
    frame_info_nimage = tk.Frame(master=frame_info, height=60, width = 250, bg="black")
    frame_info_nimage.grid(row=14, column=0, sticky="nsew")
    frame_info_nimage.rowconfigure(0, minsize=30)
    frame_info_nimage.columnconfigure([0, 1], minsize=250)

    label_nimage = tk.Label(master=frame_info_nimage, text="Session Image Count: ", bg="black", fg="White", font=("Calibri ", 16))
    label_nimage.grid(row=0, column=0, sticky="e")
    label_nimage_status = tk.Label(master=frame_info_nimage, text="0", bg="black", fg="white", font=("Calibri ", 16))
    label_nimage_status.grid(row=0, column=1, sticky="w")

    # -------------- Number of storage devices
    frame_info_ndevice = tk.Frame(master=frame_info, height=60, width = 250, bg="black")
    frame_info_ndevice.grid(row=16, column=0, sticky="nsew")
    frame_info_ndevice.rowconfigure(0, minsize=30)
    frame_info_ndevice.columnconfigure([0, 1], minsize=250)

    label_ndevice = tk.Label(master=frame_info_ndevice, text="Storage Devices: ", bg="black", fg="White", font=("Calibri ", 16))
    label_ndevice.grid(row=0, column=0, sticky="e")
    label_ndevice_status = tk.Label(master=frame_info_ndevice, text="", bg="black", fg="white", font=("Calibri ", 16))
    label_ndevice_status.grid(row=0, column=1, sticky="w")

    # -------------- USB Speed
    frame_info_usbspeed = tk.Frame(master=frame_info, height=60, width = 250, bg="black")
    frame_info_usbspeed.grid(row=17, column=0, sticky="nsew")
    frame_info_usbspeed.rowconfigure(0, minsize=30)
    frame_info_usbspeed.columnconfigure([0, 1], minsize=250)

    label_usbspeed = tk.Label(master=frame_info_usbspeed, text="Camera USB Speed: ", bg="black", fg="White", font=("Calibri ", 16))
    label_usbspeed.grid(row=0, column=0, sticky="e")
    label_usbspeed_status = tk.Label(master=frame_info_usbspeed, text="", bg="black", fg="white", font=("Calibri ", 16))
    label_usbspeed_status.grid(row=0, column=1, sticky="w")

    # -------------- USB Speed
    frame_info_version = tk.Frame(master=frame_info, height=60, width = 250, bg="black")
    frame_info_version.grid(row=19, column=0, sticky="nsew")
    frame_info_version.rowconfigure(0, minsize=30)
    frame_info_version.columnconfigure([0, 1], minsize=250)

    label_version = tk.Label(master=frame_info_version, text="FieldStation Version:", bg="black", fg="White", font=("Calibri ", 8))
    label_version.grid(row=0, column=0, sticky="e")
    label_version_status = tk.Label(master=frame_info_version, text=software_version, bg="black", fg="white", font=("Calibri ", 8))
    label_version_status.grid(row=0, column=1, sticky="w")

    '''
    # Terminal out, but causes error
    # empty1 = tk.Label(master=root, text="Terminal Output", bg="black", fg="white")
    empty1.grid(row=0, column=1, sticky="nsew")
    
    frame_terminal = tk.Frame(root, height=350, width=400, bg="black")
    frame_terminal.grid(row=1, column= 1, rowspan=3, sticky="nsew")

    text_terminal = tk.Text(frame_terminal, bg="black", fg="white")
    text_terminal.pack(side='left', fill='both')

    scrollbar = tk.Scrollbar(frame_terminal)
    scrollbar.pack(side='right', fill='y')

    text_terminal['yscrollcommand'] = scrollbar.set
    scrollbar['command'] = text_terminal.yview

    old_stdout = sys.stdout    
    sys.stdout = Redirect(text_terminal)'''

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
        print('Connected cameras: ', device.getConnectedCameras())
        print('Usb speed: ', device.getUsbSpeed().name)
        
        # Load configs
        cfg_user = load_cfg() # from FieldPrism.yaml
        cfg = SetupFP()

        # Update USB Speed
        if device.getUsbSpeed().name == 'HIGH':
            label_usbspeed_status.config(text = str(device.getUsbSpeed().name), fg='green')
        else:
            label_usbspeed_status.config(text = str(device.getUsbSpeed().name), fg='red')

        # Update device count 
        if cfg.device_count > 0:
            label_ndevice_status.config(text = str(cfg.device_count), fg='green')
        else:
            label_ndevice_status.config(text = str(cfg.device_count), fg='red')

        # Update Total CSV
        label_total_status.config(text = str(cfg.name_total_csv), fg='white')

        # Update Session ID
        label_session_status.config(text = str(cfg.name_session_csv), fg='white')

        # Test GPS, takes 34 seconds to wake, try to get signal 
        label_camera_status.config(text = 'Allow ~30 seconds for GPS fix', fg='cyan')
        for i in range(0,5):
            print(f"{bcolors.WARNING}       Attempt #{i} to get GPS fix{bcolors.ENDC}")
            GPS_data_test = gps_activate(label_gps_status, label_gps_lat_status, label_gps_lon_status, label_local_time_status, label_gps_time_status, cfg_user,False,False)
            if GPS_data_test.latitude != -999:
                break
            time.sleep(4)
        GPS_data_test = gps_activate(label_gps_status, label_gps_lat_status, label_gps_lon_status, label_local_time_status, label_gps_time_status, cfg_user,True,True)
        label_camera_status.config(text = ' Please Wait ', fg='green')

        if cfg.storage_present == False:
            print(f"{bcolors.HEADER}Stopping...{bcolors.ENDC}")
            print_options()
            raise Fragile.Break
        else:
            # Get data queues from camera
            ispQueue = device.getOutputQueue('isp', maxSize=1, blocking=False)
            videoQueue = device.getOutputQueue('video', maxSize=1, blocking=False)

            # Initialize "Ready" animated text for the GUI
            ind_ready, direction = init_ready()

            # Initialize TAKE_PHOTO
            TAKE_PHOTO = False
            images_this_session = 0

            # Data collection / imaging loop, exit on keypress, using Fragile class
            while True:
                # Update "Ready" each loop
                text_ready, ind_ready, direction = change_ready_ind(ind_ready,direction)
                label_camera_status.config(text = text_ready, fg='green')

                # Get latest frame from camera video feed (center crop)
                vidFrames = videoQueue.tryGetAll()
                for vidFrame in vidFrames:
                    vframe = vidFrame.getCvFrame()
                    vframe = rotate_image_options(vframe,cfg_user)
                    # cv2.imshow('preview', vframe)
                    # PreviewWindow(FS.frame_preview,vframe)
                    # Window_Preview.change_image(vframe)
                    Window_Preview.update_image(vframe)
                
                # Get latest frame from camera full sensor
                ispFrames = ispQueue.get()
                isp = ispFrames.getCvFrame()

                # If keypress for photo on last loop, then save a still now
                if TAKE_PHOTO:
                    # Print status
                    print(f"       Capturing Image")
                    label_camera_status.config(text = 'Capturing Image...', fg='orange')
                    images_this_session += 1


                    # Get latest frame
                    ispFrames = ispQueue.get()
                    save_frame = ispFrames.getCvFrame()

                    # Get pixel dimensions
                    height = save_frame.shape[0]
                    width = save_frame.shape[1]

                    # Rotate Camera
                    # Can rotate 270 by setting both to True
                    save_frame = rotate_image_options(save_frame,cfg_user)

                    # Save image
                    path_to_saved = route_save_image(cfg,save_frame)

                    # Update the image in the GUI by reading the image that was just written to storage
                    Window_Saved.update_image(cv2.pyrDown(cv2.pyrDown(cv2.pyrDown(cv2.imread(path_to_saved)))))

                    # Activate GPS, update GUI, and return GPS data
                    GPS_data = gps_activate(label_gps_status, label_gps_lat_status, label_gps_lon_status, label_local_time_status, label_gps_time_status, cfg_user,True,True)

                    # Write data to CSV file
                    Image = ImageData(cfg, path_to_saved, GPS_data, height, width)

                    # Print status
                    label_csv_status.config(text = 'Added 1 Row to CSV', fg='green')
                    label_camera_status.config(text = 'Ready!', fg='green')
                    label_fname_status.config(text = Image.filename)
                    label_nimage_status.config(text = str(images_this_session))
                    print(f"{bcolors.OKGREEN}Ready{bcolors.ENDC}")

                    # Reset TAKE_PHOTO
                    TAKE_PHOTO = False

                # Key Press Options
                _key = cv2.waitKey(50)
                if keyboard.is_pressed(cfg_user['fieldstation']['keymap']['exit']):
                    print(f"{bcolors.HEADER}Stopping...{bcolors.ENDC}")
                    print_options()
                    cv2.destroyAllWindows()
                    root.destroy()
                    break

                elif keyboard.is_pressed(cfg_user['fieldstation']['keymap']['photo']):
                    # Take photo
                    TAKE_PHOTO = True
                    
                    # Print status
                    label_camera_status.config(text = 'Camera Activated...', fg='orange')
                    label_csv_status.config(text = 'Collecting Data', fg='orange')
                    print(f"       Camera Activated")

                elif keyboard.is_pressed(cfg_user['fieldstation']['keymap']['test_gps']):
                    print(f"       Testing GPS")
                    GPS_data_test = gps_activate(label_gps_status, label_gps_lat_status, label_gps_lon_status, label_local_time_status, label_gps_time_status, cfg_user,True,True)
                    
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
            get_gps('cautious')
        elif keyboard.is_pressed('3'):
            print("Aligning Camera")
            align_camera()

if __name__ == "__main__":
    # route()
    start_gui()