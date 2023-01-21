# FieldStation User Manual

Below you will find a guide to use the FieldStation GUI and some tips for using it in the field.

## Installation
- Install our Raspberry Pi OS image onto a Raspberry Pi 4
  - We validated FieldStation using the 8GB version of the Raspberry Pi 4, but the 4GB should also work.
- Download Pi Imager and our Raspberry Pi OS image

## GUI and Usage 
- Critical features are visualized in the graphical user interface (GUI).
- All quality control/diagnostic messages are output in the terminal.
- The preview window is a center-cropped version of the live camera feed, which updates at a rate of approximately 3 frames per second.
- The saved image window will display the image that you just captured, and it shows the file that was written to the storage device. If you do not see a photo in the window, then nothing was saved.
- Since the live camera feed may be slow, it is recommended to count to three before taking a photo after making final adjustments to the specimen or subject.
- Insufficient power delivery can cause a number of strange issues. If you see an "Input/Output" error (in the terminal), then you need to supply more power.
- The Raspberry Pi (R Pi) may not be able to deliver enough power for all components simultaneously. It is recommended to run the camera on a separate power bank, or at least use a power bank that is rated to charge multiple devices at the same time (with at least 2 USB-A ports).

## Storage
- FieldStation can write all data (images and CSV files) to up to 6 USB storage devices. This is hard-coded and not dynamic.
- On each FieldStation startup, it is *MUST* run the Mount USB command.
- If you remove or add a USB drive, you *MUST* run the Mount USB command.
- Errors and unexpected behavior may occur if the Mount USB command is not run each time a USB drive is moved, added, or removed.
- If you get an "Input/Output" error (in the terminal), it is caused by insufficient power delivery.
- It is strongly not recommended to save images to the boot SD card.

## Mount USB Commands
- The Mount USB command can be run in three ways:
  1. (Recommended) Double-click the Mount USB + icon on the desktop. If successful, the mounted drives that are visible on the desktop should flash around, disappear, and reappear. Inspect the terminal output and look for errors.
  2. In the terminal, navigate to the FieldPrism folder by typing "cd FieldPrism/fieldstation" and then run "python mount_usb_drives.py". Verify that the terminal output makes sense.
  3. In the terminal, navigate to the FieldPrism folder by typing "cd FieldPrism/fieldstation" and then run "sh ./mount_usb_drives.sh". Verify that the terminal output makes sense.

## USB Speed
- In the GUI, if the USB speed is not displayed as "HIGH", then the USB cable connecting the camera to the Raspberry Pi is not capable of high-speed data transfer. In this case, it is recommended to replace the cable.

## GPS
- For more information about the GPS used in FieldStation, see the user manual at https://cdn-learn.adafruit.com/downloads/pdf/adafruit-ultimate-gps.pdf
- The GPS will routinely time out if not in use. Press the '2' key to wake it up without saving data or taking a photo.
- Time is reported in Coordinated Universal Time (UTC), also known as Greenwich Mean Time (GMT).
- GPS Speed: You can change the way FS gets a GPS point, but the default setting should work most of the time. The options are:
  * 'fast' which takes approximately 0.3 seconds to get a fix 
  * 'cautious' which takes approximately 1.5 seconds.
  The cautious setting adds a small delay to allow GPS lock and waits for 10 successful pings. The fast setting has no delay and only waits for 3 successful pings.

## Time
- If there is no GPS signal, then the time will be based on the Raspberry Pi clock, which is likely to be incorrect since it needs an internet connection to update.

## Data Saving
- All data is saved to two files:
    1. A session CSV, which is created anew each time you launch FS
    2. A cumulative CSV, which contains all data rows.
- Session CSVs are a backup.

## Mapping Keys 
- If you use a mini keyboard other than the one that has been validated, you should verify the default key values of your keyboard by connecting it to any PC or MAC, and see what each key press returns. Map your keys in the config file accordingly.
- You are free to change the values to suit your preferences.

## Camera Rotation
- Take a photo. If the image looks strange in the Saved Image Window, then adjust the rotation options below.
- Setting both rotation parameters to True will rotate the image 270 degrees clockwise.

## Sharpness
- The sharpness of the image can be calculated using cv2.Laplacian(img, cv2.CV_64F).var()
- This will add '__B' at the end of the jpg file name.
