import threading
import base64
import numpy as np
import time
from MODULE_DATA import ModuleData
import cv2
import base64
import zmq

class ImageData:
    def __init__(self):
        self.image_np = ()
        self.isInit = False
        self.width = None
        self.height = None

class ZeroMQImageInput(threading.Thread):
    def __init__(self, context, IMAGE_WIDTH = 640 ,IMAGE_HEIGHT = 480):
        threading.Thread.__init__(self)
        self.name = "ZeroMQ Image Input Thread"
        self.image_data = ImageData()
        self.done = False
        self.IMAGE_WIDTH = IMAGE_WIDTH
        self.IMAGE_HEIGHT = IMAGE_HEIGHT
        self.cap = []  
        self.image_data.image_np = np.zeros(shape=(IMAGE_HEIGHT,IMAGE_WIDTH,3))
        self.currentTime = 0
        self.image_data.isInit = True
        self.footage_socket = context.socket(zmq.SUB)
        self.footage_socket.bind('tcp://*:5555')
        self.footage_socket.setsockopt_string(zmq.SUBSCRIBE, str(''))

    def run(self):
        print("Starting " + self.name)
        self.updateImg(self.name)
        print("Exiting " + self.name)

    def updateImg(self, threadName):
        while not self.done:
            frame = self.footage_socket.recv_string()
            img = base64.b64decode(frame)
            npimg = np.fromstring(img, dtype=np.uint8)
            source = cv2.imdecode(npimg, 1)
            self.image_data.image_np = source

    def getImage(self):
        return self.image_data.image_np

    def stop(self):
        self.done = True
        
class ZeroMQDataHandler(threading.Thread):
    def __init__(self,context, thread_yolo):
        threading.Thread.__init__(self)
        self.name = 'ZeroMQ DataHandler'
        self.done = False
        self.moduleData = ModuleData(thread_yolo)
        self.data_socket_send = context.socket(zmq.PUB)
        self.data_socket_send.connect('tcp://localhost:5557')
        self.data_socket_rcv = context.socket(zmq.SUB)
        self.data_socket_rcv.bind('tcp://*:5556')
        self.data_socket_rcv.setsockopt_string(zmq.SUBSCRIBE, str(''))



    def run(self):
        print("Starting " + self.name)
        self.update(self.name)
        print("Exiting " + self.name)

    def update(self, threadName):
        while not self.done:
            try:
                data = self.data_socket_rcv.recv_string()
                self.moduleData.updateData(data)
                all_data = self.moduleData.create_detection_data()
                self.data_socket_send.send_string(all_data)
                #print(data)
            except Exception as e:
                print("Error occured sending or receiving data on ML client. " + str(e))

    def stop(self):
        self.done = True

   