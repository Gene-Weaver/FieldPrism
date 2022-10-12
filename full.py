#!/usr/bin/env python3

import time
from pathlib import Path
import cv2
import depthai as dai
import keyboard

def main():
    # Create pipeline
    pipeline = dai.Pipeline()

    # Define sources and outputs
    camRgb = pipeline.create(dai.node.ColorCamera)
    camRgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_4_K)
    camRgb.setIspScale(2,6) # 1080P -> 720P
    stillEncoder = pipeline.create(dai.node.VideoEncoder)

    controlIn = pipeline.create(dai.node.XLinkIn)
    configIn = pipeline.create(dai.node.XLinkIn)
    ispOut = pipeline.create(dai.node.XLinkOut)
    videoOut = pipeline.create(dai.node.XLinkOut)
    stillMjpegOut = pipeline.create(dai.node.XLinkOut)

    controlIn.setStreamName('control')
    configIn.setStreamName('config')
    ispOut.setStreamName('isp')
    videoOut.setStreamName('video')
    stillMjpegOut.setStreamName('still')

    # Properties
    # camRgb.setVideoSize(3140, 2160)
    camRgb.setVideoSize(1280, 720)
    stillEncoder.setDefaultProfilePreset(1, dai.VideoEncoderProperties.Profile.MJPEG)

    # Linking
    camRgb.isp.link(ispOut.input)
    camRgb.still.link(stillEncoder.input)
    camRgb.video.link(videoOut.input)
    controlIn.out.link(camRgb.inputControl)
    configIn.out.link(camRgb.inputConfig)
    stillEncoder.bitstream.link(stillMjpegOut.input)

    # Connect to device and start pipeline
    with dai.Device(pipeline) as device:
        # Get data queues
        controlQueue = device.getInputQueue('control')
        configQueue = device.getInputQueue('config')
        ispQueue = device.getOutputQueue('isp')
        videoQueue = device.getOutputQueue('video')
        stillQueue = device.getOutputQueue('still')

        # Output queue will be used to get the rgb frames from the output defined above
        # qRgb = device.getOutputQueue(name="rgb", maxSize=30, blocking=False)
        # qStill = device.getOutputQueue(name="still", maxSize=30, blocking=True)
        # qControl = device.getInputQueue(name="control")

        # Make sure the destination path is present before starting to store the examples
        dirName = "rgb_data"
        Path(dirName).mkdir(parents=True, exist_ok=True)

        while True:
            vidFrames = videoQueue.tryGetAll()
            for vidFrame in vidFrames:
                frame = vidFrame.getCvFrame()
                frame = cv2.pyrDown(frame)
                frame = cv2.pyrDown(frame)
                cv2.imshow('video', frame)

            ispFrames = ispQueue.tryGetAll()
            for ispFrame in ispFrames:
                time.sleep(0.1)
                pass
                # cv2.imshow('isp', ispFrame.getCvFrame())


            stillFrames = stillQueue.tryGetAll()
            for stillFrame in stillFrames:
                print("STILL STILL STILL")
                # Decode JPEG
                frame = cv2.imdecode(stillFrame.getData(), cv2.IMREAD_UNCHANGED)
                # Display
                cv2.imshow('still', frame)
                # time.sleep(2)

            # Update screen (1ms pooling rate)
            key = cv2.waitKey(1)
            if keyboard.is_pressed('6'):
                break
            elif keyboard.is_pressed('1'):
                ctrl = dai.CameraControl()
                ctrl.setCaptureStill(True)
                controlQueue.send(ctrl)
                print("Sent 'still' event to the camera!")
                time.sleep(3)
                
            
            # key = cv2.waitKey(1)
            # if keyboard.is_pressed('6'):
            #     break
            # elif keyboard.is_pressed('1'):
            #     ctrl = dai.CameraControl()
            #     ctrl.setCaptureStill(True)
            #     controlQueue.send(ctrl)
            #     print("Sent 'still' event to the camera!")

if __name__ == '__main__':
    main()