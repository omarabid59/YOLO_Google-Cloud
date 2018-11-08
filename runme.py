import sys
sys.path.append('/home/omar_abid4_gmail_com/')
sys.path.append('/home/omar_abid4_gmail_com/facenet_data/src/')
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
        if len(self.queue) < 5:
            self.queue.append(image_np)
        else:
            self.queue.popleft() # Remove the top most element.
            
            
            
objCounting = objectcounting()
thread_image = CustomImageThread()
thread_image.start()
image_data = thread_image.image_data
START_PREDICTOR = True
thread_data = ThreadData()


detector_thresh = 0.8
recognition_thresh = 0.5

DETECTOR_IMG_SCALE = 1.0
TRACKER = 'Legacy'
thread_frm = FaceNetRecog(thread_image.image_data,
                     nnModels + 'faceRecognition/ssd_face_detector/face_label_map.pbtxt',
                  nnModels + 'faceRecognition/repClassifiers/facenet-classifier.pkl',
                  nnModels + 'faceRecognition/faceNet/20180408-102900/20180408-102900.pb',
                             detector_thresh=detector_thresh,
                             recognition_thresh=recognition_thresh,
                             detection_tracker=TRACKER,
                             DETECTOR_IMG_SCALE = DETECTOR_IMG_SCALE)
thread_data.addThreadElement(thread_frm,'f','FRM')


GSM_IMG_SCALE = 1.0;
thread_gsm_1 = DarknetYOLO("YOLO COCO",image_data,
                        THRESHOLD_Y9K,
                         TRACKER_TYPE='Legacy',
                        YOLO_DIR= nnModels + "yolov3/coco/608/",
                          IMG_SCALE=GSM_IMG_SCALE)
thread_data.addThreadElement(thread_gsm_1,'u','GSM-COCO',always_on=False, ignore_thread=False)


thread_gsm_2 = DarknetYOLO("YOLO 9K",image_data,
                        THRESHOLD_YOLO_COCO,
                         TRACKER_TYPE='Legacy',
                        YOLO_DIR=nnModels+"yolov3/y9k/",
                          IMG_SCALE=GSM_IMG_SCALE)
thread_data.addThreadElement(thread_gsm_2,'y','GSM-COCO',always_on=False, ignore_thread=False)



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
            try:
                self.write_message(json.dumps({
                    "img": data,
                    "desc": "img_description",
                }))
            except:
                print("CNN Message send failed")
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
   
    
    class ModuleData:
        def __init__(self):
            self.weapons_only = False
            self.weapon_parts = False
            self.model_9k = False
            self.model_coco = False
            self.show_all_classes = False
            self.model_frm = False
            self.prev_weapons_only = False
            self.prev_weapon_parts = False
            self.prev_model_9k = False
            self.prev_model_coco = False
            self.prev_show_all_classes = False
            self.prev_model_frm = False
        def str2bool(self,data):
            data = str(data)
            if data == 'True':
                return True
            else:
                return False
        def updateModules(self):
            if self.prev_model_coco != self.model_coco:
                if self.model_coco:
                    thread_gsm_1.continue_predictor()
                else: 
                    thread_gsm_1.pause_predictor()
                self.prev_model_coco = self.model_coco
                print("COCO: " + str(self.model_coco))
            if self.prev_model_9k != self.model_9k:
                if self.model_9k:
                    thread_gsm_2.continue_predictor()
                else: 
                    thread_gsm_2.pause_predictor()
                self.prev_model_9k = self.model_9k
                print("Y9K: " + str(self.model_9k))
            if self.prev_model_frm != self.model_frm:
                if self.model_frm:
                    thread_frm.continue_predictor()
                else: 
                    thread_frm.pause_predictor()
                self.prev_model_frm = self.model_frm
                print("FRM: " + str(self.model_frm))
            
    def open(self):
        logging.info('new ml result connection')
        self.callback = PeriodicCallback(self.update, 50)
        self.callback.start()
        self.previous_data = []
        self.image_height = 0
        self.image_width = 0
        self.moduleData = self.ModuleData()
    def on_message(self, message):
        if self.image_height == 0:
            data = json.loads(message)
            try:
                self.image_height = int(data['image_properties']['height'])
                self.image_width = int(data['image_properties']['width'])
                print("received" + " height: " + str(self.image_height) + " width: " + str(self.image_width))
            except:
                print("nope")
        try:
            data = json.loads(message)
            self.moduleData.weapons_only = self.moduleData.str2bool(data['module_settings']['weapons_only'])
            self.moduleData.weapon_parts = self.moduleData.str2bool(data['module_settings']['weapon_parts'])
            self.moduleData.model_9k = self.moduleData.str2bool(data['module_settings']['model_9k'])
            self.moduleData.model_coco = self.moduleData.str2bool(data['module_settings']['model_coco'])
            self.moduleData.show_all_classes = self.moduleData.str2bool(data['module_settings']['show_all_classes'])
            self.moduleData.model_frm = self.moduleData.str2bool(data['module_settings']['model_frm'])
            self.moduleData.updateModules()
        except:
            print("Failed receiving module data.")

    def create_thread_data(self,thread_data):
        all_data = []
        current_3d_model = "default"
        for thread_ in thread_data.thread_list:
            h = self.image_height; w = self.image_width;
            data = {}
            data['type'] = 'thread_data'
            data['name'] = thread_.name
            if 'thread_frm' in thread_.name:
                data,face_data = self.create_face_data(thread_)
                all_data.append(data)
                all_data.append(face_data)
                continue
            data['bbs'] = self.fix_bb_coords(thread_.output_data.bbs.copy(),
                                        h,w)
            data['scores'] = thread_.output_data.scores.tolist()
            class_names = []
            for c in thread_.output_data.classes:
                class_names.append(thread_.output_data.category_index.get(c)['name'])
            data['classes'] = class_names
            
            if thread_.pause:
                data['bbs'] = [];
                data['scores'] = [];
                data['classes'] = [];
                class_names = [];
            # Remove classes we don't care about.
            if not self.moduleData.show_all_classes:
                indices = []
                bbs = data['bbs']
                scores = data['scores']
                classes = data['classes']
                data['bbs'] = []
                data['scores'] = []
                data['classes'] = []
                for c,s,bb in zip(classes,scores,bbs):
                    if c in DISP_LABEL_LIST:
                        data['scores'].append(s)
                        data['classes'].append(c)
                        data['bbs'].append(bb)

            unique_labels = objCounting.countFromList(data['classes'])
            data['unique_labels'] = unique_labels
            all_data.append(data)
            # Remove the "Count in front"
            labels = [" ".join(str(x) for x in label.split(' ')[1:]) for label in unique_labels]
            # Check the existence of specific labels for displaying a 3D model
            if 'machgun-grip' in labels \
                or 'machine-guns' in labels \
                or 'machgun-barrel' in labels \
                or 'machgun-magazine' in labels \
                or 'rifle-barrel' in labels \
                or 'rifle-cartridge' in labels \
                or 'buttstock' in labels \
                or 'rifle' in labels:
                current_3d_model = 'machine_gun'
            elif 'gun-barrel' in labels \
                 or 'trigger' in labels \
                 or 'handguns' in labels \
                 or 'grip' in labels:
                current_3d_model = 'handgun'

            elif 'cell phone' in labels:
                current_3d_model = 'mobile'
        all_data.append({
            "type":"model_display", "name":current_3d_model
        })

        return all_data
    def create_face_data(self,thread_):
        # Make sure this is the face thread.
        h = self.image_height; w = self.image_width;
        data = {}
        face_data = {}
        face_data["type"] = "face_display"
        data['type'] = 'thread_data'
        data['name'] = thread_.name
        output_data = thread_.output_data
        recog_trk_ids = list(output_data.recognition_data.output_data.tracker_ids)
        persons = list(output_data.recognition_data.output_data.persons)
        scores = list(output_data.recognition_data.output_data.scores)
        bbs = list(output_data.detection_data.bbs)
        detect_trk_ids = list(output_data.detection_data.tracker_ids)
        output_persons = []
        for bb, detector_trk_id in zip(bbs,
                                       detect_trk_ids):
            try:
                indx = recog_trk_ids.index(detector_trk_id)
                output_persons.append(persons[indx])
            except:
                output_persons.append(output_data.recognition_data.EMPTY_ELEMENT)

        data['bbs'] = self.fix_bb_coords(np.asarray(bbs.copy()),
                                h,w)
        data['scores'] = scores
        output_persons = [x.split(':')[-1] for x in output_persons]
        data['classes'] = output_persons
        persons = list(set(output_persons))
        if len(persons) > 0:
            if 'Alex' in persons:
                 current_face_model = 'lex'
            elif 'Brent-Pass' in persons:
                 current_face_model = 'brent'
            elif 'Carl-freer' in persons:
                 current_face_model = 'carl'
            elif 'Haris' in persons:
                 current_face_model = 'haris'
            elif 'Jan' in persons:
                 current_face_model = 'jan'
            elif 'Lucie-parker' in persons:
                 current_face_model = 'lucie'
            elif 'omar' in persons:
                 current_face_model = 'omar'
            elif 'phanikumar' in persons:
                 current_face_model = 'phani'
            else:
                 current_face_model = 'mask'
            face_data['name'] = current_face_model
        else:
            face_data['name'] = 'mask'
        return data,face_data
        
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

        
        
app = Application()
ssl_ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
ssl_ctx.load_cert_chain(webserver_files + "ssl/domain.crt",
                       webserver_files + "ssl/domain.key")


http_server = tornado.httpserver.HTTPServer(app, ssl_options=ssl_ctx)
http_server.listen(port)
tornado.ioloop.IOLoop.current().start()

print("RUNNING SERVER!")