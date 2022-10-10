'''
Run the FieldPrism field station. 
Requires:
    - Raspberry Pi 4 8GB
    - Luxonis OAK-1 camera
'''

import time, os
from pathlib import Path
import cv2
import depthai as dai

# Create pipeline
pipeline = dai.Pipeline()

# Define sources and outputs
camRgb = pipeline.create(dai.node.ColorCamera)
manip = pipeline.create(dai.node.ImageManip)

camOut = pipeline.create(dai.node.XLinkOut)
manipOut = pipeline.create(dai.node.XLinkOut)
manipCfg = pipeline.create(dai.node.XLinkIn)

camOut.setStreamName("preview")
manipOut.setStreamName("manip")
manipCfg.setStreamName("manipCfg")

# Properties
camRgb.setPreviewSize(1920, 1080)
camRgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_4_K)
camRgb.setInterleaved(False)
camRgb.setColorOrder(dai.ColorCameraProperties.ColorOrder.RGB)
manip.setMaxOutputFrameSize(3840 * 2160 * 3)

# Linking
camRgb.preview.link(camOut.input)
camRgb.preview.link(manip.inputImage)
manip.out.link(manipOut.input)
manipCfg.out.link(manip.inputConfig)

# Connect to device and start pipeline
with dai.Device(pipeline) as device:
    print(f"Pipline started")

    # Output queue will be used to get the rgb frames from the output defined above
    qRgb = device.getOutputQueue(name="rgb", maxSize=30, blocking=False)
    qStill = device.getOutputQueue(name="still", maxSize=30, blocking=True)
    qControl = device.getInputQueue(name="control")

    # Create input & output queues
    qPreview = device.getOutputQueue(name="preview", maxSize=30, blocking=False)
    qStill = device.getOutputQueue(name="still", maxSize=30, blocking=True)
    qManipCfg = device.getInputQueue(name="manipCfg")

    key = -1
    # Make sure the destination path is present before starting to store the examples
    dir_name = "rgb_data"
    USB_PATH = '/media/pi/'
    has_1_USB = False
    has_2_USB = False
    USB_DRIVE_1 = ''
    USB_DRIVE_2 = ''
    print(USB_PATH)
    print(os.listdir(USB_PATH))
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

    print(f"Creating save dirs")
    if not has_1_USB and not has_2_USB:
        USB_DRIVE_0 = dir_name
        Path(USB_DRIVE_0).mkdir(parents=True, exist_ok=True)
    elif has_1_USB and not has_2_USB:
        Path(USB_DRIVE_1).mkdir(parents=True, exist_ok=True)
    elif has_1_USB and has_2_USB:
        Path(USB_DRIVE_1).mkdir(parents=True, exist_ok=True)
        Path(USB_DRIVE_2).mkdir(parents=True, exist_ok=True)

    while key != ord('q'):
        inRgb = qStill.tryGet()  # Non-blocking call, will return a new data that has arrived or None otherwise
        if inRgb is not None:
            frame = inRgb.getCvFrame()
            # 4k / 4
            frame = cv2.pyrDown(frame)
            frame = cv2.pyrDown(frame)
            cv2.imshow("rgb", frame)

        if key == ord('c') and inRgb is not None:
            for q in [qPreview, qStill]:
                name_time = str(int(time.time() * 1000))

                pkt = q.get()
                name = q.getName()
                shape = (3, pkt.getHeight(), pkt.getWidth())
                frame = pkt.getCvFrame()

                fname0 = "".join([name_time,'.jpg'])
                fname0 = os.path.join(USB_DRIVE_0,fname0)
                print(f"fname1 ==> {fname0}")
                
                with open(fname0, "wb") as f:
                        f.write(frame.getData())
                        print('Image saved to', fname0)
        key = cv2.waitKey(1)

'''
# Connect to device and start pipeline
with dai.Device(pipeline) as device:
    print(f"Pipline started")

    # Output queue will be used to get the rgb frames from the output defined above
    qRgb = device.getOutputQueue(name="rgb", maxSize=30, blocking=False)
    qStill = device.getOutputQueue(name="still", maxSize=30, blocking=True)
    qControl = device.getInputQueue(name="control")

    # Make sure the destination path is present before starting to store the examples
    dir_name = "rgb_data"
    USB_PATH = '/media/pi/'
    has_1_USB = False
    has_2_USB = False
    USB_DRIVE_1 = ''
    USB_DRIVE_2 = ''
    print(USB_PATH)
    print(os.listdir(USB_PATH))
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

    print(f"Creating save dirs")
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

        print(qStill.has())
        if qStill.has():
            print(f"qStill ==> {qStill.has()}")
            name_time = str(int(time.time() * 1000))
            if not has_1_USB and not has_2_USB:
                fname0 = "".join(name_time,'.jpg')
                fname0 = os.path.join(USB_DRIVE_0,fname0)
                print(f"fname1 ==> {fname0}")
                with open(fname0, "wb") as f:
                    f.write(qStill.get().getData())
                    print('Image saved to', fname0)
            elif has_1_USB and not has_2_USB:
                fname1 = "".join(name_time,'.jpg')
                fname1 = os.path.join(USB_DRIVE_1,fname1)
                print(f"fname1 ==> {fname1}")
                with open(fname1, "wb") as f:
                    f.write(qStill.get().getData())
                    print('Image saved to', fname1)
            elif has_1_USB and has_2_USB:
                fname1 = "".join(name_time,'.jpg')
                fname1 = os.path.join(USB_DRIVE_1,fname1)
                fname2 = "".join(name_time,'.jpg')
                fname2 = os.path.join(USB_DRIVE_2,fname2)
                print(f"fname1 ==> {fname1}")
                print(f"fname2 ==> {fname2}")
                with open(fname1, "wb") as f:
                    f.write(qStill.get().getData())
                    print('Image saved to', fname1)
                with open(fname2, "wb") as f:
                    f.write(qStill.get().getData())
                    print('Image saved to', fname2)   
        # for i in range(0,20):# IMG_COUNT < 20: 
        #     time. sleep(2)
        #     ctrl = dai.CameraControl()
        #     ctrl.setCaptureStill(True)
        #     qControl.send(ctrl)
        #     print(f"Sent 'still' event to the camera! img = {i}")
        key = cv2.waitKey(1)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        elif cv2.waitKey(1) & 0xFF == ord('c'):
            ctrl = dai.CameraControl()
            ctrl.setCaptureStill(True)
            qControl.send(ctrl)
            print(f"Sent 'still' event to the camera!")
'''