import sys
sys.path.append('/home/omar_abid4_gmail_com/')
sys.path.append('/home/omar_abid4_gmail_com/facenet/src/')
webserver_files = '/home/omar_abid4_gmail_com/cloud_ml_webrtc/webserver/'
nnModels = '/home/omar_abid4_gmail_com/nnModels/'
import logging
import tornado.escape
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket
import os.path
import uuid
from PIL import Image
import time

#from io import StringIO
from io import BytesIO
import uuid
import numpy
import json
from tornado.options import define, options
import tornado.httpserver
import numpy as np
import ssl
from tornado.ioloop import PeriodicCallback
import base64
port = 8888
import threading

import aipodMain.utilities.constants as constants

import warnings
warnings.filterwarnings('ignore')
# Input Source Thread
from aipodMain.threads.ImageInput.AbstractImageInputThread import AbstractImageInputThread

# Predictor Threads
from aipodMain.threads.Predictor.PredictorImage import PredictorImage
from aipodMain.threads.Predictor.VisualizerPredictor import VisualizerPredictor
from aipodMain.threads.Predictor.SubsetImgPredictor2 import SubsetImgPredictor
from aipodMain.threads.Predictor.DarkNet.PredictorDarknet import DarknetYOLO
from aipodMain.utilities.ThreadData import ThreadData
from aipodMain.threads.Predictor.FaceRecognition.Pipeline.Wrapper import FaceDetectionRecognition as FaceNetRecog
# GUI
from aipodMain.GUI.draw_face_frame import draw_face_frame
from aipodMain.GUI.draw_lidar_frame import draw_lidar_frame
from aipodMain.GUI.draw_label_frame import draw_label_frame
from aipodMain.GUI.draw_image_frame import draw_image_frame
from aipodMain.GUI.MAIN_GUI import nn_draw
# Controller
from aipodMain.GUI.CONTROLLER import CONTROLLER

# Helper Functions
from aipodMain.utilities.ai_helper.objectcounting import objectcounting
from aipodMain.utilities.ai_helper import helper as ai_helper
import time
import cv2
from PIL import Image

print("Finished Loading Imports")


# TRACKER
MIN_HITS = 1 
MAX_AGE = 4

# MODEL SCORE THRESHOLD VALUES
THRESHOLD_Y9K = 0.5
THRESHOLD_YOLO_COCO  = 0.4
THRESHOLD_COCO = 0.4
THRESHOLD_INCEPTION = 0.4
THRESHOLD_WEAPONS_ONLY = 0.6
THRESHOLD_WEAPONS_ONLY_SUB = 0.1
THRESHOLD_WEAPON_PARTS = 0.4
THRESHOLD_WEAPON_PARTS_SUB = 0.4
# Label List
DISP_LABEL_LIST = [
    # Weapons
    'gun-barrel','machine-guns','trigger','handguns', 'rifle',
    # Coco Module
    'person', 'backpack', 'bottle', 'knife', 
    'cell phone', 'scissors', 'Weapon',
    # Faster R-CNN Module
    'Person','Rifle', 'Handgun', 'Shotgun', 'Digital clock', 'Alarm clock', 'Syringe',
      "Bottle", "Knife", "Backpack",
      "Mobile phone"]
# Exclude All Of These Classes
ENABLE_EXCLUDE_LABEL_LIST = True
EXCLUDE_LABEL_LIST = [
    # Faster R-CNN
    'Clothing', 'Face', 'Hair', 'Head', 'Arm', 'Hand', 'Beard', 'bed','sofa',
    # COCO
    "mouse" ,
    # Weapons
    'NA',
    # YOLO 9K
    'Weapon','y9k-Rifle','y9k-Handgun','y9k-Shotgun', 'worker','creation','craftsman','living thing',
    'instrumentality', 'artifact', 'organism', 'person-9k', 'matter', 'expert' ,'whole', 'entertainer', 'nutriment',
    'backpack-9k', 'African','Mexican','Arabian'
]


from collections import deque
import numpy as np
import time

class CustomImageThread(AbstractImageInputThread):
    def __init__(self, IMAGE_WIDTH = 640 ,IMAGE_HEIGHT = 480):
        name = 'Custom Image Thread'
        super().__init__(name, IMAGE_WIDTH ,IMAGE_HEIGHT)
        empty_image = np.zeros(shape=(20,20,3))
        self.queue = deque([empty_image])
        self.image_data.image_np = empty_image
        self.image_data.isInit = True

    def updateImg(self, threadName):
        while not self.done:
            last_image = self.image_data.image_np
            try:
                last_image = self.queue.popleft()[:,:,::-1]
            except:
                pass
            self.image_data.image_np = last_image
            time.sleep(0.05)
            
    def appendElement(self, image_np):
        '''
        Adds an image for processing to the queue.
        '''
        if len(self.queue) < 10:
            self.queue.append(image_np)
        else:
            self.queue.popleft() # Remove the top most element.
            
objCounting = objectcounting()
thread_image = CustomImageThread()
thread_image.start()
image_data = thread_image.image_data
START_PREDICTOR = True
thread_data = ThreadData()


thread_gsm_1 = DarknetYOLO("YOLO COCO",image_data,
                        THRESHOLD_YOLO_COCO,
                         TRACKER_TYPE='Legacy',
                        YOLO_DIR= nnModels + "yolov3/coco/608/",
                          IMG_SCALE=0.5)
thread_data.addThreadElement(thread_gsm_1,'u','GSM-COCO',always_on=False, ignore_thread=False)

thread_vis = VisualizerPredictor("Visualization Thread VISUALIZATION",   
                                 nnModels + 'faceRecognition/ssd_face_detector/ssd_inference_graph.pb',
                                     image_data, MOBILE_VIS_LAYERS = True)


thread_data.start_all()
print("Done")


# Neural Network
nnDraw = nn_draw(thread_vis.output_data,640,480,update_interval=5)
t1 = threading.Thread(target=nnDraw.updateWithThread).start()


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", MainHandler),
            (r"/test", TestHandler),
            (r"/webcam", WebcamHandler),
            (r"/cnn_data", CNNHandler),
            (r"/mlresults", MLResultHandler)
            ]

        settings = dict(
            cookie_secret="asdsafl.rleknknfkjqweonrkbknoijsdfckjnk 234jn",
            template_path=os.path.join(os.path.dirname(webserver_files), "templates"),
            static_path=os.path.join(os.path.dirname(webserver_files), "static"),
            xsrf_cookies=False,
            autoescape=None,
            debug=True
            )
        tornado.web.Application.__init__(self, handlers, **settings)
    def startTornado(self):
        print("Starting Tornaado")
        http_server = tornado.httpserver.HTTPServer(app, ssl_options=ssl_ctx)
        http_server.listen(port)
        #tornado.ioloop.IOLoop.current().start()
    def stopTornado(self):
        print("Stopping")
        tornado.ioloop.IOLoop.current().stop()

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("facedetect.html")
        
class TestHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("dashboard.html")
        
class WebcamHandler(tornado.websocket.WebSocketHandler):
    '''
    When data is received, append it to our thread image queue.
    '''
    def open(self):
        print('new webcam connection')
        logging.info('new webcam connection')
        #self.set_nodelay(True)
        data = {}
        data['name'] = 'empty_message'
        self.callback = PeriodicCallback(self.update, 500)
        self.callback.start()
        self.empty_message = json.dumps(data)
        self.t1 = time.time()

    def on_message(self, message):
        image = Image.open(BytesIO(message))
        cv_image = numpy.array(image)
        thread_image.appendElement(cv_image)
        # Send Empty data back
        self.write_message(self.empty_message)
        self.t1 = time.time()  


    def on_close(self):
        logging.info('connection webcam closed')
        print("Connection webcam closed")
        self.callback.stop()
    def update(self):
        # If we haven't heard back, send a wakeup message.
        elapsedTime = time.time() - self.t1
        if elapsedTime > 5:
            self.write_message(self.empty_message)
        
        
class CNNHandler(tornado.websocket.WebSocketHandler):
    '''
    When data is received, append it to our thread image queue.
    '''
    def open(self):
        print('new ccn connection')
        logging.info('new CNN connection')
        self.image_np = np.ones(shape=(6,6,3))
        self.next_message = True
        self.t1 = time.time()
        self.callback = PeriodicCallback(self.update, 200)
        self.callback.start()

    def on_message(self, message):
        self.next_message = True
    def update(self):
        elapsedTime = time.time() - self.t1
        if self.next_message or (elapsedTime > 2):
            image_np = nnDraw.showNeuralNetVisualization()*255.0
            image_np = image_np.astype('uint8')
            data = Image.fromarray(image_np)
            fp = BytesIO()
            data.save(fp, 'JPEG')
            data = base64.b64encode(fp.getvalue())
            data = "data:image/png;base64," + data.decode('utf-8')
            self.write_message(json.dumps({
                "img": data,
                "desc": "img_description",
            }))
            self.next_message = False
            self.t1 = time.time()
        


    def on_close(self):
        logging.info('connection CNN closed')
        self.callback.stop()
        print("Connection CNN closed")

class MLResultHandler (tornado.websocket.WebSocketHandler):
    '''
    When data is received, append it to our thread image queue.
    '''
    def open(self):
        logging.info('new ml result connection')
        self.callback = PeriodicCallback(self.update, 500)
        self.callback.start()
        self.previous_data = []
        self.image_height = 0
        self.image_width = 0
    def on_message(self, message):
        if self.image_height == 0:
            data = json.loads(message)
            try:
                self.image_height = int(data['image_properties']['height'])
                self.image_width = int(data['image_properties']['width'])
                print("received" + " height: " + str(self.image_height) + " width: " + str(self.image_width))
            except:
                print("nope")

    def create_thread_data(self,thread_data):
        all_data = []

        for thread_ in thread_data.thread_list:
            h = self.image_height; w = self.image_width;
            data = {}
            data['type'] = 'thread_data'
            data['name'] = thread_.name
            if 'Face' in thread_.name:
                continue
            data['bbs'] = self.fix_bb_coords(thread_.output_data.bbs.copy(),
                                        h,w)
            data['scores'] = thread_.output_data.scores.tolist()
            class_names = []
            for c in thread_.output_data.classes:
                class_names.append(thread_.output_data.category_index.get(c)['name'])
            data['classes'] = class_names
            data['unique_labels'] = objCounting.countFromList(class_names)
            all_data.append(data)
        return all_data
    def create_face_and_model_data(self,output_data):
        data = {}
        data['type'] = 'face_data'
        data['db_image'] = 'omar'
        
    def update(self):
        # First we need to concatenate the output data
        all_data = self.create_thread_data(thread_data)

        # Add the face data. TODO: Pass in the face data!
        #data = json.dumps(self.create_face_and_model_data(thread_frm.output_data))
        #all_data.append(data)
        # Prevent sending duplicate data.
        if all_data != self.previous_data:
            self.write_message(json.dumps(all_data))
        self.previous_data = all_data

    def fix_bb_coords(self,bbs,h,w):
        for indx, bb in enumerate(bbs):
            bbs[indx][0] = int(bbs[indx][0]*h)
            bbs[indx][1] = int(bbs[indx][1]*w)
            bbs[indx][2] = int(bbs[indx][2]*h)
            bbs[indx][3] = int(bbs[indx][3]*w)  
            
            bbs[indx][0] = max(min(bbs[indx][0],h),0)
            bbs[indx][2] = max(min(bbs[indx][2],h),0)
            bbs[indx][1] = max(min(bbs[indx][1],w),0)
            bbs[indx][3] = max(min(bbs[indx][3],w),0)
                
        return bbs.tolist()

  


    def on_close(self):
        logging.info('connection ml closed')
        self.callback.stop()

thread_gsm_1.continue_predictor()


app = Application()
ssl_ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
ssl_ctx.load_cert_chain(webserver_files + "ssl/domain.crt",
                       webserver_files + "ssl/domain.key")


http_server = tornado.httpserver.HTTPServer(app, ssl_options=ssl_ctx)
http_server.listen(port)
tornado.ioloop.IOLoop.current().start()