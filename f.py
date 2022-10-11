import time, os, cv2
from pathlib import Path
import depthai as dai

# Start defining a pipeline
pipeline = dai.Pipeline()

# Define a source - color camera
camRgb = pipeline.createColorCamera()
camRgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_4_K)

# Create RGB output
xoutRgb = pipeline.createXLinkOut()
xoutRgb.setStreamName("rgb")
camRgb.video.link(xoutRgb.input)

# Create encoder to produce JPEG images
videoEnc = pipeline.createVideoEncoder()
videoEnc.setDefaultProfilePreset(camRgb.getVideoSize(), camRgb.getFps(), dai.VideoEncoderProperties.Profile.MJPEG)
camRgb.video.link(videoEnc.input)

# Create JPEG output
xoutJpeg = pipeline.createXLinkOut()
xoutJpeg.setStreamName("jpeg")
videoEnc.bitstream.link(xoutJpeg.input)


# Pipeline defined, now the device is connected to
with dai.Device(pipeline) as device:
    # Start pipeline
    device.startPipeline()

    # Output queue will be used to get the rgb frames from the output defined above
    qRgb = device.getOutputQueue(name="rgb", maxSize=30, blocking=False)
    qJpeg = device.getOutputQueue(name="jpeg", maxSize=30, blocking=True)

    # Make sure the destination path is present before starting to store the examples
    dir_name = os.path.join('FieldPrism','Unprocessed_Images')
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
        inRgb = qRgb.tryGet()  # non-blocking call, will return a new data that has arrived or None otherwise

        if inRgb is not None:
            frame = inRgb.getCvFrame()
            # 4k / 4
            frame2 = cv2.pyrDown(frame)
            frame2 = cv2.pyrDown(frame2)
            cv2.imshow("rgb", cv2.rotate(frame2, cv2.ROTATE_180))

        if cv2.waitKey(1) == ord('c'):
            save_frame = cv2.rotate(frame, cv2.ROTATE_180)
            name_time = str(int(time.time() * 1000))

            if not has_1_USB and not has_2_USB:
                fname0 = "".join([name_time,'.jpg'])
                fname0 = os.path.join(USB_DRIVE_0,fname0)
                print(f"Capturing image ==> {fname0}")
                cv2.imwrite(fname0, save_frame)
                print('Image saved to', fname0)
            elif has_1_USB and not has_2_USB:
                fname1 = "".join([name_time,'.jpg'])
                fname1 = os.path.join(USB_DRIVE_1,fname1)
                print(f"Capturing image ==> {fname1}")
                cv2.imwrite(fname1, save_frame)
                print('Image saved to', fname1)
            elif has_1_USB and has_2_USB:
                fname1 = "".join([name_time,'.jpg'])
                fname1 = os.path.join(USB_DRIVE_1,fname1)
                fname2 = "".join([name_time,'.jpg'])
                fname2 = os.path.join(USB_DRIVE_2,fname2)
                print(f"Capturing image. Saving redundant ==> {fname1}   \n&\n   {fname2}")
                cv2.imwrite(fname1, save_frame)
                print('Image saved to', fname1)  
                cv2.imwrite(fname2, save_frame)
                print('Image saved to', fname2)  


            # for encFrame in qJpeg.tryGetAll():
            #     with open(f"06_data/{int(time.time() * 10000)}.jpg", "wb") as f:
            #         f.write(bytearray(encFrame.getData()))

        if cv2.waitKey(1) == ord('q'):
            break