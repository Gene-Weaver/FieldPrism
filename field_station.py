'''
Run the FieldPrism field station. 
Requires:
    - Raspberry Pi 4 8GB
    - Luxonis OAK-1 camera
'''

import time, os, cv2
from pathlib import Path
import depthai as dai
from glob import glob
from subprocess import check_output, CalledProcessError

def get_usb_devices():
    sdb_devices = map(os.path.realpath, glob('/sys/block/sd*'))
    usb_devices = (dev for dev in sdb_devices
        if 'usb' in dev.split('/')[5])
    return dict((os.path.basename(dev), dev) for dev in usb_devices)

def get_mount_points(devices=None):
    devices = devices or get_usb_devices() # if devices are None: get_usb_devices
    print(devices)
    print("######################################")
    output = check_output(['mount']).splitlines()
    print(output)
    print("######################################")
    is_usb = lambda path: any(dev in path for dev in devices)
    print(is_usb)
    print("######################################")
    usb_info = (line for line in output if is_usb(line.split()[0]))
    print(usb_info)
    print("######################################")
    return [(info.split()[0], info.split()[2]) for info in usb_info]

if __name__ == '__main__':
    print(get_mount_points())

# # Create pipeline
# pipeline = dai.Pipeline()

# camRgb = pipeline.create(dai.node.ColorCamera)
# camRgb.setBoardSocket(dai.CameraBoardSocket.RGB)
# camRgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_4_K)

# xoutRgb = pipeline.create(dai.node.XLinkOut)
# xoutRgb.setStreamName("rgb")
# camRgb.video.link(xoutRgb.input)

# xin = pipeline.create(dai.node.XLinkIn)
# xin.setStreamName("control")
# xin.out.link(camRgb.inputControl)

# # Properties
# videoEnc = pipeline.create(dai.node.VideoEncoder)
# videoEnc.setDefaultProfilePreset(1, dai.VideoEncoderProperties.Profile.MJPEG)
# camRgb.still.link(videoEnc.input)

# # Linking
# xoutStill = pipeline.create(dai.node.XLinkOut)
# xoutStill.setStreamName("still")
# videoEnc.bitstream.link(xoutStill.input)

# # Connect to device and start pipeline
# with dai.Device(pipeline) as device:

#     # Output queue will be used to get the rgb frames from the output defined above
#     qRgb = device.getOutputQueue(name="rgb", maxSize=30, blocking=False)
#     qStill = device.getOutputQueue(name="still", maxSize=30, blocking=True)
#     qControl = device.getInputQueue(name="control")

#     # Make sure the destination path is present before starting to store the examples
#     dirName = "rgb_data"
#     Path(dirName).mkdir(parents=True, exist_ok=True)

#     while True:
#         inRgb = qRgb.tryGet()  # Non-blocking call, will return a new data that has arrived or None otherwise
#         if inRgb is not None:
#             frame = inRgb.getCvFrame()
#             # 4k / 4
#             frame = cv2.pyrDown(frame)
#             frame = cv2.pyrDown(frame)
#             cv2.imshow("rgb", frame)

#         if qStill.has():
#             fName = f"{dirName}/{int(time.time() * 1000)}.jpg"
#             with open(fName, "wb") as f:
#                 f.write(qStill.get().getData())
#                 print('Image saved to', fName)
        
#         key = cv2.waitKey(1)
#         if key == ord('q'):
#             break
#         elif key == ord('c'):
#             ctrl = dai.CameraControl()
#             ctrl.setCaptureStill(True)
#             qControl.send(ctrl)
#             print("Sent 'still' event to the camera!")