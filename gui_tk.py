import cv2
import depthai as dai
import tkinter as tk
from threading import Thread


def createPipeline():
    pipeline = dai.Pipeline()

    # Define sources
    camRgb = pipeline.createColorCamera()
    monoLeft = pipeline.create(dai.node.MonoCamera)
    monoRight = pipeline.create(dai.node.MonoCamera)

    # Properties
    camRgb.setPreviewSize(640, 400)
    camRgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
    camRgb.setBoardSocket(dai.CameraBoardSocket.RGB)
    monoLeft.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
    monoLeft.setBoardSocket(dai.CameraBoardSocket.LEFT)
    monoRight.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
    monoRight.setBoardSocket(dai.CameraBoardSocket.RIGHT)

    # Define outputs
    xoutRgb = pipeline.create(dai.node.XLinkOut)
    xoutLeft = pipeline.create(dai.node.XLinkOut)
    xoutRight = pipeline.create(dai.node.XLinkOut)
    xoutRgb.setStreamName("rgb")
    xoutLeft.setStreamName("left")
    xoutRight.setStreamName("right")

    streams = ("rgb", "left", "right")

    # Linking
    camRgb.preview.link(xoutRgb.input)
    monoLeft.out.link(xoutLeft.input)
    monoRight.out.link(xoutRight.input)

    return pipeline, streams


def run(pipeline):
    # Connect to device and start pipeline
    with dai.Device(pipeline) as device:
        queues = [device.getOutputQueue(s, 8, False) for s in streamNames]

        while True:
            for queue in queues:
                name = queue.getName()
                if name != currentStream:  # Display only the "selected" stream
                    continue
                image = queue.get()
                frame = image.getFrame() if name != "rgb" else image.getCvFrame()
                cv2.imshow(name, frame)

            if cv2.waitKey(1) == ord("q"):
                break


pipeline, streamNames = createPipeline()

tkWindow = tk.Tk()
tkWindow.geometry("400x150")
tkWindow.title("Switch streams example")


def callback(*args):
    global currentStream
    currentStream = tkWindow.getvar(args[0])
    cv2.destroyAllWindows()


currentStream = streamNames[0]

currentStreamVar = tk.StringVar(tkWindow)
currentStreamVar.set(currentStream)  # default value
currentStreamVar.trace_add("write", callback)

dropdown = tk.OptionMenu(tkWindow, currentStreamVar, *streamNames)
dropdown.pack()


thread = Thread(target=run, args=(pipeline,))
thread.setDaemon(True)
thread.start()

tkWindow.mainloop()