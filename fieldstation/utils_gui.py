#!/usr/bin/env python3
import tkinter as tk

'''
Configure the GUI
'''
def config_gui(root, software_version):
    root.rowconfigure([0, 1, 2, 3, 4], minsize=30)
    root.columnconfigure([0, 1, 2], minsize=100)

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
    
    # # -------------- Buttons
    # # frame
    # frame_button = tk.Frame(master=root, height = 60, bg="black")
    # frame_button.grid(row=4, column=0, columnspan= 2, sticky="nsew")
    
    # frame_button.rowconfigure(0, minsize=60)
    # frame_button.columnconfigure([0, 1, 2, 3, 4, 5], minsize=200)

    # b_photo = tk.Button(master=frame_button, command=lambda: button_photo(), text = "PHOTO", font=("Arial", 20), bg="green4", fg="black", activebackground="green2")
    # b_gps = tk.Button(master=frame_button, command=lambda: button_gps(), text = "GPS", font=("Arial", 20), bg="royal blue", fg="black", activebackground="deep sky blue")
    # b_exit = tk.Button(master=frame_button, command=lambda: button_exit(), text = "QUIT", font=("Arial", 20), bg="maroon", fg="white", activebackground="red")

    # b_exit.grid(row=0, column=0, sticky="nsew")
    # b_gps.grid(row=0, column=3, sticky="nsew")
    # b_photo.grid(row=0, column=4, sticky="nsew")

    # -------------- Info header
    label_top_info = tk.Label(master=root, text="Info", bg="black", fg="white", font=("Arial", 20))
    label_top_info.grid(row=0, column=1, sticky="nsew")

    # -------------- Frame that will contain all status info below
    # -------------- frame_info will contain each label in a 18 row x 2 column layout 
    frame_info = tk.Frame(master=root, width = 250, bg="black")
    frame_info.grid(row=1, column=1, rowspan=3, sticky="nsew")

    frame_info.rowconfigure([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21], minsize=30)
    frame_info.columnconfigure(0, minsize=250)

    # -------------- Camera status
    frame_info_camera = tk.Frame(master=frame_info, height=60, width = 250, bg="black")
    frame_info_camera.grid(row=0, column=0, sticky="nsew")
    frame_info_camera.rowconfigure(0, minsize=60)
    frame_info_camera.columnconfigure([0, 1], minsize=250)

    label_camera = tk.Label(master=frame_info_camera, text="Camera Status: ", bg="black", fg="White", font=("Calibri ", 16))
    label_camera.grid(row=0, column=0, sticky="e")
    label_camera_status = tk.Label(master=frame_info_camera, text=" Please Wait ", bg="black", fg="green2", font=("Calibri", 16))
    label_camera_status.grid(row=0, column=1, sticky="w")

        # -------------- Camera Focus Live
    frame_info_focus_live = tk.Frame(master=frame_info, height=60, width = 250, bg="black")
    frame_info_focus_live.grid(row=1, column=0, sticky="nsew")
    frame_info_focus_live.rowconfigure(0, minsize=30)
    frame_info_focus_live.columnconfigure([0, 1], minsize=250)

    label_focus_live = tk.Label(master=frame_info_focus_live, text="Live Camera Focus: ", bg="black", fg="White", font=("Calibri ", 16))
    label_focus_live.grid(row=0, column=0, sticky="e")
    label_focus_live_status = tk.Label(master=frame_info_focus_live, text="  ", bg="black", fg="green2", font=("Calibri", 16))
    label_focus_live_status.grid(row=0, column=1, sticky="w")

    # -------------- Camera Focus Saved
    frame_info_focus_saved = tk.Frame(master=frame_info, height=60, width = 250, bg="black")
    frame_info_focus_saved.grid(row=2, column=0, sticky="nsew")
    frame_info_focus_saved.rowconfigure(0, minsize=30)
    frame_info_focus_saved.columnconfigure([0, 1], minsize=250)

    label_focus_saved = tk.Label(master=frame_info_focus_saved, text="Saved Image Focus: ", bg="black", fg="White", font=("Calibri ", 16))
    label_focus_saved.grid(row=0, column=0, sticky="e")
    label_focus_saved_status = tk.Label(master=frame_info_focus_saved, text="  ", bg="black", fg="green2", font=("Calibri", 16))
    label_focus_saved_status.grid(row=0, column=1, sticky="w")

    # -------------- File name
    frame_info_fname = tk.Frame(master=frame_info, height=60, width = 250, bg="black")
    frame_info_fname.grid(row=4, column=0, sticky="nsew")
    frame_info_fname.rowconfigure(0, minsize=30)
    frame_info_fname.columnconfigure([0, 1], minsize=250)

    label_fname = tk.Label(master=frame_info_fname, text="Image File Name: ", bg="black", fg="White", font=("Calibri ", 16))
    label_fname.grid(row=0, column=0, sticky="e")
    label_fname_status = tk.Label(master=frame_info_fname, text="", bg="black", fg="green2", font=("Calibri ", 16))
    label_fname_status.grid(row=0, column=1, sticky="w")

    # -------------- GPS Status
    frame_info_gps = tk.Frame(master=frame_info, height=60, width = 250, bg="black")
    frame_info_gps.grid(row=6, column=0, sticky="nsew")
    frame_info_gps.rowconfigure(0, minsize=30)
    frame_info_gps.columnconfigure([0, 1], minsize=250)

    label_gps = tk.Label(master=frame_info_gps, text="GPS Status: ", bg="black", fg="White", font=("Calibri ", 16))
    label_gps.grid(row=0, column=0, sticky="e")
    label_gps_status = tk.Label(master=frame_info_gps, text="", bg="black", fg="green2", font=("Calibri ", 16))
    label_gps_status.grid(row=0, column=1, sticky="w")

    # -------------- GPS Lat
    frame_info_gps_lat = tk.Frame(master=frame_info, height=60, width = 250, bg="black")
    frame_info_gps_lat.grid(row=7, column=0, sticky="nsew")
    frame_info_gps_lat.rowconfigure(0, minsize=30)
    frame_info_gps_lat.columnconfigure([0, 1], minsize=250)

    label_gps_lat = tk.Label(master=frame_info_gps_lat, text="Latitude: ", bg="black", fg="White", font=("Calibri ", 16))
    label_gps_lat.grid(row=0, column=0, sticky="e")
    label_gps_lat_status = tk.Label(master=frame_info_gps_lat, text="", bg="black", fg="green2", font=("Calibri ", 16))
    label_gps_lat_status.grid(row=0, column=1, sticky="w")

    # -------------- GPS Long
    frame_info_gps_lon = tk.Frame(master=frame_info, height=60, width = 250, bg="black")
    frame_info_gps_lon.grid(row=8, column=0, sticky="nsew")
    frame_info_gps_lon.rowconfigure(0, minsize=30)
    frame_info_gps_lon.columnconfigure([0, 1], minsize=250)

    label_gps_lon = tk.Label(master=frame_info_gps_lon, text="Longitude: ", bg="black", fg="White", font=("Calibri ", 16))
    label_gps_lon.grid(row=0, column=0, sticky="e")
    label_gps_lon_status = tk.Label(master=frame_info_gps_lon, text="", bg="black", fg="green2", font=("Calibri ", 16))
    label_gps_lon_status.grid(row=0, column=1, sticky="w")

    # -------------- GPS Time (UTC)
    frame_info_gps_time = tk.Frame(master=frame_info, height=60, width = 250, bg="black")
    frame_info_gps_time.grid(row=9, column=0, sticky="nsew")
    frame_info_gps_time.rowconfigure(0, minsize=30)
    frame_info_gps_time.columnconfigure([0, 1], minsize=250)

    label_gps_time = tk.Label(master=frame_info_gps_time, text="GPS Time (UTC): ", bg="black", fg="White", font=("Calibri ", 16))
    label_gps_time.grid(row=0, column=0, sticky="e")
    label_gps_time_status = tk.Label(master=frame_info_gps_time, text="", bg="black", fg="white", font=("Calibri ", 16))
    label_gps_time_status.grid(row=0, column=1, sticky="w")

    # -------------- R Pi Local Time
    frame_info_local_time = tk.Frame(master=frame_info, height=60, width = 250, bg="black")
    frame_info_local_time.grid(row=10, column=0, sticky="nsew")
    frame_info_local_time.rowconfigure(0, minsize=30)
    frame_info_local_time.columnconfigure([0, 1], minsize=250)

    label_local_time = tk.Label(master=frame_info_local_time, text="Local Time (R Pi): ", bg="black", fg="White", font=("Calibri ", 16))
    label_local_time.grid(row=0, column=0, sticky="e")
    label_local_time_status = tk.Label(master=frame_info_local_time, text="", bg="black", fg="white", font=("Calibri ", 16))
    label_local_time_status.grid(row=0, column=1, sticky="w")

    # -------------- CSV Total
    frame_info_total = tk.Frame(master=frame_info, height=60, width = 250, bg="black")
    frame_info_total.grid(row=12, column=0, sticky="nsew")
    frame_info_total.rowconfigure(0, minsize=30)
    frame_info_total.columnconfigure([0, 1], minsize=250)

    label_total = tk.Label(master=frame_info_total, text="CSV Total: ", bg="black", fg="White", font=("Calibri ", 16))
    label_total.grid(row=0, column=0, sticky="e")
    label_total_status = tk.Label(master=frame_info_total, text="", bg="black", fg="white", font=("Calibri ", 16))
    label_total_status.grid(row=0, column=1, sticky="w")
    
    # -------------- CSV Session
    frame_info_session = tk.Frame(master=frame_info, height=60, width = 250, bg="black")
    frame_info_session.grid(row=13, column=0, sticky="nsew")
    frame_info_session.rowconfigure(0, minsize=30)
    frame_info_session.columnconfigure([0, 1], minsize=250)

    label_session = tk.Label(master=frame_info_session, text="CSV Session: ", bg="black", fg="White", font=("Calibri ", 16))
    label_session.grid(row=0, column=0, sticky="e")
    label_session_status = tk.Label(master=frame_info_session, text="", bg="black", fg="white", font=("Calibri ", 16))
    label_session_status.grid(row=0, column=1, sticky="w")

    # -------------- CSV
    frame_info_csv = tk.Frame(master=frame_info, height=60, width = 250, bg="black")
    frame_info_csv.grid(row=14, column=0, sticky="nsew")
    frame_info_csv.rowconfigure(0, minsize=30)
    frame_info_csv.columnconfigure([0, 1], minsize=250)

    label_csv = tk.Label(master=frame_info_csv, text="CSV Data: ", bg="black", fg="White", font=("Calibri ", 16))
    label_csv.grid(row=0, column=0, sticky="e")
    label_csv_status = tk.Label(master=frame_info_csv, text="Waiting", bg="black", fg="white", font=("Calibri ", 16))
    label_csv_status.grid(row=0, column=1, sticky="w")

    # -------------- Session Image Count
    frame_info_nimage = tk.Frame(master=frame_info, height=60, width = 250, bg="black")
    frame_info_nimage.grid(row=16, column=0, sticky="nsew")
    frame_info_nimage.rowconfigure(0, minsize=30)
    frame_info_nimage.columnconfigure([0, 1], minsize=250)

    label_nimage = tk.Label(master=frame_info_nimage, text="Session Image Count: ", bg="black", fg="White", font=("Calibri ", 16))
    label_nimage.grid(row=0, column=0, sticky="e")
    label_nimage_status = tk.Label(master=frame_info_nimage, text="0", bg="black", fg="white", font=("Calibri ", 16))
    label_nimage_status.grid(row=0, column=1, sticky="w")


    # -------------- Number of storage devices
    frame_info_ndevice = tk.Frame(master=frame_info, height=60, width = 250, bg="black")
    frame_info_ndevice.grid(row=18, column=0, sticky="nsew")
    frame_info_ndevice.rowconfigure(0, minsize=30)
    frame_info_ndevice.columnconfigure([0, 1], minsize=250)

    label_ndevice = tk.Label(master=frame_info_ndevice, text="Storage Devices: ", bg="black", fg="White", font=("Calibri ", 16))
    label_ndevice.grid(row=0, column=0, sticky="e")
    label_ndevice_status = tk.Label(master=frame_info_ndevice, text="", bg="black", fg="white", font=("Calibri ", 16))
    label_ndevice_status.grid(row=0, column=1, sticky="w")

    # -------------- USB Speed
    frame_info_usbspeed = tk.Frame(master=frame_info, height=60, width = 250, bg="black")
    frame_info_usbspeed.grid(row=19, column=0, sticky="nsew")
    frame_info_usbspeed.rowconfigure(0, minsize=30)
    frame_info_usbspeed.columnconfigure([0, 1], minsize=250)

    label_usbspeed = tk.Label(master=frame_info_usbspeed, text="Camera USB Speed: ", bg="black", fg="White", font=("Calibri ", 16))
    label_usbspeed.grid(row=0, column=0, sticky="e")
    label_usbspeed_status = tk.Label(master=frame_info_usbspeed, text="", bg="black", fg="white", font=("Calibri ", 16))
    label_usbspeed_status.grid(row=0, column=1, sticky="w")

    # -------------- FP version
    frame_info_version = tk.Frame(master=frame_info, height=60, width = 250, bg="black")
    frame_info_version.grid(row=21, column=0, sticky="nsew")
    frame_info_version.rowconfigure(0, minsize=30)
    frame_info_version.columnconfigure([0, 1], minsize=250)

    label_version = tk.Label(master=frame_info_version, text="FieldStation Version:", bg="black", fg="White", font=("Calibri ", 8))
    label_version.grid(row=0, column=0, sticky="e")
    label_version_status = tk.Label(master=frame_info_version, text=software_version, bg="black", fg="white", font=("Calibri ", 8))
    label_version_status.grid(row=0, column=1, sticky="w")



    # -------------- QR header
    label_top_qr = tk.Label(master=root, text="   QR Codes", bg="black", fg="white", font=("Arial", 20))
    label_top_qr.grid(row=0, column=2, sticky="w")

    frame_qr = tk.Frame(master=root, width = 100, bg="black")
    frame_qr.grid(row=1, column=2, rowspan=3, sticky="nsew")

    frame_qr.rowconfigure([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, ], minsize=30)
    frame_qr.columnconfigure(0, minsize=50)

    # -------------- n_qr parameter
    frame_qr_data = tk.Frame(master=frame_qr, height=60, width=250, bg="black")
    frame_qr_data.grid(row=2, column=0, sticky="nsew")  # Assuming this is row 17, adjust according to your actual layout
    frame_qr_data.rowconfigure([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, ], minsize=30)
    frame_qr_data.columnconfigure([0, 1], minsize=50)

    n_qr = tk.IntVar(value=50)

    label_nqr = tk.Label(master=frame_qr_data, text="BBox Confidence", bg="black", fg="White", font=("Calibri ", 16))
    label_nqr.grid(row=0, column=0, sticky="nsew")

    frame_buttons = tk.Frame(master=frame_qr_data, bg="black")
    frame_buttons.grid(row=1, column=0, sticky="nsew")
    frame_buttons.columnconfigure([0, 1, 2], weight=1)

    def increase_nqr():
        current_value = n_qr.get()
        if current_value < 95:  # Adjust as needed for the maximum value
            n_qr.set(current_value + 5)
        label_nqr_status.config(text=str(n_qr.get()))

    def decrease_nqr():
        current_value = n_qr.get()
        if current_value > 5:  # Adjust as needed for the minimum value
            n_qr.set(current_value - 5)
        label_nqr_status.config(text=str(n_qr.get()))

    
    b_nqr_increase = tk.Button(master=frame_buttons, command=increase_nqr, text="+", font=("Arial", 20), bg="green4", fg="black", activebackground="green2")
    b_nqr_increase.grid(row=0, column=2, sticky="nsew")

    label_nqr_status = tk.Label(master=frame_buttons, text=str(n_qr.get()), bg="black", fg="white", font=("Calibri ", 16))
    label_nqr_status.grid(row=0, column=1, sticky="ew")

    b_nqr_decrease = tk.Button(master=frame_buttons, command=decrease_nqr, text="-", font=("Arial", 20), bg="maroon", fg="white", activebackground="red")
    b_nqr_decrease.grid(row=0, column=0, sticky="nsew")

    frame_qr_data.columnconfigure(1, weight=1)
    
    # -------------- Level 1
    rv_start = 4
    label_nqr = tk.Label(master=frame_qr_data, text="QR Code Values", bg="black", fg="White", font=("Calibri ", 16))
    label_nqr.grid(row=rv_start, column=0, sticky="nsew")

    rv_start += 1
    frame_L1 = tk.Frame(master=frame_qr_data, height=60, width = 100, bg="black")
    frame_L1.grid(row=rv_start, column=0, sticky="nsew")
    frame_L1.rowconfigure(0, minsize=30)
    frame_L1.columnconfigure([0, 1], minsize=50)

    L1 = tk.Label(master=frame_L1, text="Level 1: ", bg="black", fg="White", font=("Calibri ", 16))
    L1.grid(row=0, column=0, sticky="e")
    L1 = tk.Label(master=frame_L1, text="none", bg="black", fg="white", font=("Calibri ", 16))
    L1.grid(row=0, column=1, sticky="w")

    # -------------- Level 2
    rv_start += 1
    frame_L2 = tk.Frame(master=frame_qr_data, height=60, width = 100, bg="black")
    frame_L2.grid(row=rv_start, column=0, sticky="nsew")
    frame_L2.rowconfigure(0, minsize=30)
    frame_L2.columnconfigure([0, 1], minsize=50)

    L2 = tk.Label(master=frame_L2, text="Level 2: ", bg="black", fg="White", font=("Calibri ", 16))
    L2.grid(row=0, column=0, sticky="e")
    L2 = tk.Label(master=frame_L2, text="none", bg="black", fg="white", font=("Calibri ", 16))
    L2.grid(row=0, column=1, sticky="w")

    # -------------- Level 3
    rv_start += 1
    frame_L3 = tk.Frame(master=frame_qr_data, height=60, width = 100, bg="black")
    frame_L3.grid(row=rv_start, column=0, sticky="nsew")
    frame_L3.rowconfigure(0, minsize=30)
    frame_L3.columnconfigure([0, 1], minsize=50)

    L3 = tk.Label(master=frame_L3, text="Level 3: ", bg="black", fg="White", font=("Calibri ", 16))
    L3.grid(row=0, column=0, sticky="e")
    L3 = tk.Label(master=frame_L3, text="none", bg="black", fg="white", font=("Calibri ", 16))
    L3.grid(row=0, column=1, sticky="w")

    # -------------- Level 4
    rv_start += 1
    frame_L4 = tk.Frame(master=frame_qr_data, height=60, width = 100, bg="black")
    frame_L4.grid(row=rv_start, column=0, sticky="nsew")
    frame_L4.rowconfigure(0, minsize=30)
    frame_L4.columnconfigure([0, 1], minsize=50)

    L4 = tk.Label(master=frame_L4, text="Level 4: ", bg="black", fg="White", font=("Calibri ", 16))
    L4.grid(row=0, column=0, sticky="e")
    L4 = tk.Label(master=frame_L4, text="none", bg="black", fg="white", font=("Calibri ", 16))
    L4.grid(row=0, column=1, sticky="w")

    # -------------- Level 5
    rv_start += 1
    frame_L5 = tk.Frame(master=frame_qr_data, height=60, width = 100, bg="black")
    frame_L5.grid(row=rv_start, column=0, sticky="nsew")
    frame_L5.rowconfigure(0, minsize=30)
    frame_L5.columnconfigure([0, 1], minsize=50)

    L5 = tk.Label(master=frame_L5, text="Level 5: ", bg="black", fg="White", font=("Calibri ", 16))
    L5.grid(row=0, column=0, sticky="e")
    L5 = tk.Label(master=frame_L5, text="none", bg="black", fg="white", font=("Calibri ", 16))
    L5.grid(row=0, column=1, sticky="w")

    # -------------- Level 6
    rv_start += 1
    frame_L6 = tk.Frame(master=frame_qr_data, height=60, width = 100, bg="black")
    frame_L6.grid(row=rv_start, column=0, sticky="nsew")
    frame_L6.rowconfigure(0, minsize=30)
    frame_L6.columnconfigure([0, 1], minsize=50)

    L6 = tk.Label(master=frame_L6, text="Level 6: ", bg="black", fg="White", font=("Calibri ", 16))
    L6.grid(row=0, column=0, sticky="e")
    L6 = tk.Label(master=frame_L6, text="none", bg="black", fg="white", font=("Calibri ", 16))
    L6.grid(row=0, column=1, sticky="w")

    # Callback function for radio buttons
    radio_var = tk.StringVar(value="standard")
    use_enhanced = False

    def radio_selected():
        global use_enhanced
        selection = radio_var.get()
        if selection == "standard":
            use_enhanced = False
        elif selection == "enhance":
            use_enhanced = True

    rv_start += 2
    frame_mode_L = tk.Frame(master=frame_qr_data, height=60, width=100, bg="black")
    frame_mode_L.grid(row=rv_start, column=0, sticky="nsew")
    frame_mode_L.rowconfigure(0, minsize=30)
    frame_mode_L.columnconfigure([0], minsize=50)
    mode_L = tk.Label(master=frame_mode_L, text="QR Reader Type", bg="black", fg="white", font=("Calibri ", 16))
    mode_L.grid(row=0, column=0, sticky="w")

    rv_start += 1
    frame_mode = tk.Frame(master=frame_qr_data, height=60, width=100, bg="black")
    frame_mode.grid(row=rv_start, column=0, rowspan=2, sticky="nsew")
    frame_mode.rowconfigure(0, minsize=30)
    frame_mode.columnconfigure([0], minsize=50)

    # Create the radio buttons
    standard_radio = tk.Radiobutton(frame_mode, text="Standard", variable=radio_var, value="standard", command=radio_selected,
                                    bg="black", fg="white", font=("Calibri ", 16), highlightthickness=0,
                                    selectcolor="red")
    standard_radio.grid(row=0, column=0, sticky="w")
    enhance_radio = tk.Radiobutton(frame_mode, text="Enhanced", variable=radio_var, value="enhance", command=radio_selected,
                                bg="black", fg="white", font=("Calibri ", 16), highlightthickness=0,
                                selectcolor="red")
    enhance_radio.grid(row=1, column=0, sticky="w")

    return root, frame_preview, frame_saved, label_camera_status, label_focus_live_status, label_focus_saved_status, label_fname_status, label_gps_status, label_gps_lat_status, label_gps_lon_status, label_gps_time_status, label_local_time_status, label_total_status, label_session_status, label_csv_status, label_nimage_status, label_ndevice_status, label_usbspeed_status, label_version_status, label_nqr_status, L1, L2, L3, L4, L5, L6, radio_var

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
    sys.stdout = Redirect(text_terminal)
'''

'''
Function to animate "Ready" in the GUI
Updates each time the camera sends a photo to the "check focus" window
'''


def change_ready_ind(n,direction):
    to_out = '>'
    to_in = '<'
    if n == 10:
        direction='down'
        pick = to_in
        n -= 1
    elif n == 0:
        direction='up'
        pick = to_out
        n += 1
    else:
        if direction == 'up':
            pick = to_out
            n += 1
        else:
            pick = to_in
            n -= 1
    m = 10-n
    right = ''.join([char*m for char in pick])
    left = ''.join([char*n for char in pick])

    text_ready = ''.join([left,' Ready ',right])

    return text_ready, n, direction

def init_ready():
    ind_ready = 0
    direction ='up'
    return ind_ready, direction