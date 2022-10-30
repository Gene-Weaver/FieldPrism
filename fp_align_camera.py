#!/usr/bin/env python3
import keyboard, cv2
import depthai as dai
from utils import print_options, load_cfg
'''
Align Camera:
    Due to bandwidth constraints, higher resolutions cannot be streamed in real-time.
    Since we need to capture full-resolution images, the stream in fp.py is full-res,
    but it can only update ~3fps.

    Take in the 12MP signal. 
    Crop to 4k
    Show downsampled image.
    The photo will be wider than the preview, 12MP hxw ratio is more square (4:3), preview is 16x9.
'''
def align_camera():
    print_options()
    cfg_user = load_cfg()
    # Create pipeline
    pipeline = dai.Pipeline()
    # Define source and output
    camRgb = pipeline.create(dai.node.ColorCamera)
    camRgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_4_K)
    xoutRgb = pipeline.create(dai.node.XLinkOut)
    camRgb.setIspScale(2,17)
    xoutRgb.setStreamName("preview")
    camRgb.setPreviewSize(426,240)
    camRgb.setInterleaved(False)
    camRgb.setColorOrder(dai.ColorCameraProperties.ColorOrder.RGB)
    # Linking
    camRgb.preview.link(xoutRgb.input)
    # Connect to device and start pipeline
    with dai.Device(pipeline) as device:
        qRgb = device.getOutputQueue('preview', maxSize=1, blocking=False)
        while True: 
            inRgb = qRgb.get()
            frame = inRgb.getCvFrame()

            if cfg_user['fieldprism']['rotate_camera_180']:
                frame = cv2.rotate(frame, cv2.ROTATE_180)
            if cfg_user['fieldprism']['rotate_camera_90_clockwise']:
                frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)

            cv2.imshow("Preview: Press Exit Key to Close Window", frame)
            key = cv2.waitKey(50)
            if keyboard.is_pressed(cfg_user['fieldprism']['keymap']['exit']):
                print_options()
                cv2.destroyAllWindows()
                break

if __name__ == '__main__':
    align_camera()