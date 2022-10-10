'''
Run the FieldPrism field station. 
Requires:
    - Raspberry Pi 4 8GB
    - Luxonis OAK-1 camera
'''

from re import T
import time, os, cv2
from pathlib import Path
import depthai as dai
from glob import glob

# Create pipeline
pipeline = dai.Pipeline()

camRgb = pipeline.create(dai.node.ColorCamera)
camRgb.setBoardSocket(dai.CameraBoardSocket.RGB)
camRgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_4_K)

xoutRgb = pipeline.create(dai.node.XLinkOut)
xoutRgb.setStreamName("rgb")
camRgb.video.link(xoutRgb.input)

xin = pipeline.create(dai.node.XLinkIn)
xin.setStreamName("control")
xin.out.link(camRgb.inputControl)

# Properties
videoEnc = pipeline.create(dai.node.VideoEncoder)
videoEnc.setDefaultProfilePreset(1, dai.VideoEncoderProperties.Profile.MJPEG)
camRgb.still.link(videoEnc.input)

# Linking
xoutStill = pipeline.create(dai.node.XLinkOut)
xoutStill.setStreamName("still")
videoEnc.bitstream.link(xoutStill.input)

# Connect to device and start pipeline
with dai.Device(pipeline) as device:

    # Output queue will be used to get the rgb frames from the output defined above
    qRgb = device.getOutputQueue(name="rgb", maxSize=30, blocking=False)
    qStill = device.getOutputQueue(name="still", maxSize=30, blocking=True)
    qControl = device.getInputQueue(name="control")

    # Make sure the destination path is present before starting to store the examples
    dir_name = "rgb_data"
    USB_PATH = 'media/pi/'
    has_1_USB = False
    has_2_USB = False
    USB_DRIVE_1 = ''
    USB_DRIVE_2 = ''
    if len(os.listdir(USB_PATH)) == 1:
        USB_DRIVE_1 = os.path.join(USB_PATH,os.listdir(USB_PATH)[0],dir_name)
        has_1_USB = True
    elif len(os.listdir(USB_PATH)) == 2:
        USB_DRIVE_1 = os.path.join(USB_PATH,os.listdir(USB_PATH)[0],dir_name)
        USB_DRIVE_2 = os.path.join(USB_PATH,os.listdir(USB_PATH)[1],dir_name)
        has_1_USB = True
        has_2_USB = True
    print(f"path to USB_DRIVE_1: {USB_DRIVE_1}")
    print(f"path to USB_DRIVE_2: {USB_DRIVE_2}")

    
    if not has_1_USB and not has_2_USB:
        USB_DRIVE_0 = dir_name
        Path(USB_DRIVE_0).mkdir(parents=True, exist_ok=True)
    elif has_1_USB and not has_2_USB:
        Path(USB_DRIVE_1).mkdir(parents=True, exist_ok=True)
    elif has_1_USB and has_2_USB:
        Path(USB_DRIVE_1).mkdir(parents=True, exist_ok=True)
        Path(USB_DRIVE_2).mkdir(parents=True, exist_ok=True)
        
    while True:
        inRgb = qRgb.tryGet()  # Non-blocking call, will return a new data that has arrived or None otherwise
        if inRgb is not None:
            frame = inRgb.getCvFrame()
            # 4k / 4
            frame = cv2.pyrDown(frame)
            frame = cv2.pyrDown(frame)
            cv2.imshow("rgb", frame)

        if qStill.has():
            if not has_1_USB and not has_2_USB:
                fName = f"{USB_DRIVE_0}/{int(time.time() * 1000)}.jpg"
                with open(fName, "wb") as f:
                    f.write(qStill.get().getData())
                    print('Image saved to', fName)
            elif has_1_USB and not has_2_USB:
                fName = f"{USB_DRIVE_1}/{int(time.time() * 1000)}.jpg"
                with open(fName, "wb") as f:
                    f.write(qStill.get().getData())
                    print('Image saved to', fName)
            elif has_1_USB and has_2_USB:
                fName1 = f"{USB_DRIVE_1}/{int(time.time() * 1000)}.jpg"
                fName2 = f"{USB_DRIVE_2}/{int(time.time() * 1000)}.jpg"
                with open(fName1, "wb") as f:
                    f.write(qStill.get().getData())
                    print('Image saved to', fName1)
                with open(fName2, "wb") as f:
                    f.write(qStill.get().getData())
                    print('Image saved to', fName2)   
        
        key = cv2.waitKey(1)
        if key == ord('q'):
            break
        elif key == ord('c'):
            ctrl = dai.CameraControl()
            ctrl.setCaptureStill(True)
            qControl.send(ctrl)
            print("Sent 'still' event to the camera!")