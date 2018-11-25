import threading
import time
import glob
import numpy as np
from pydarknet import Detector
from pydarknet import Image as darknetImage
import pandas as pd
from data_structures import OutputClassificationData



class DarknetYOLO(threading.Thread):

    def __init__(self, image_data,
                         YOLO_DIR,
                         score_thresh=0.5,
                         fps=0.08):
        print("DIRECTORY: " + YOLO_DIR)
        self.createDataFile(YOLO_DIR)
        YOLO_DATA =  glob.glob(YOLO_DIR + '*.data')[0]
        YOLO_CFG =  glob.glob(YOLO_DIR + '*.cfg')[0]
        YOLO_WEIGHTS =  glob.glob(YOLO_DIR + '*.weights')[0]

        CLASS_NAMES =  glob.glob(YOLO_DIR + '*.names')[0]

        self.createClassNames(YOLO_DIR, CLASS_NAMES)
        ENABLE_BY_DEFAULT = False
        self.done = False
        threading.Thread.__init__(self)

        self.pause = False
        self.name = "YOLO Predictor Thread"


        self.image_data = image_data
        self.net = net = Detector(bytes(YOLO_CFG, encoding="utf-8"), bytes(YOLO_WEIGHTS, encoding="utf-8"), 0,
               bytes(YOLO_DATA, encoding="utf-8"))
        self.results = []

        self.output_data = OutputClassificationData()
        self.output_data.score_thresh = score_thresh
        self.output_data.category_index = self.category_index
        self.frames_per_ms = fps;


    def createDataFile(self, YOLO_DIR):
        FILE_DATA = YOLO_DIR + YOLO_DIR.split('/')[-2] + '.data'
        FILE_NAMES = glob.glob(YOLO_DIR + '*.names')[0]
        NUM_CLASSES = len(pd.read_csv(FILE_NAMES,header=None).index.values)
        f= open(FILE_DATA,"w+")
        f.write('classes= ' + str(NUM_CLASSES) + '\n')
        f.write('names= ' + str(FILE_NAMES) + '\n')
        f.close()

    def createClassNames(self,YOLO_DIR, CLASS_NAMES):
        self.__BEGIN_STRING = ''
        self.CLASS_NAMES = [self.__BEGIN_STRING + str(s)
                            for s in pd.read_csv(CLASS_NAMES,header=None,names=['LabelName']).LabelName.tolist()]

        # Remove all of the odd characters
        for indx,x in enumerate(self.CLASS_NAMES):
            if "'" in x:
                self.CLASS_NAMES[indx] = x.replace("'","")
        return PATH_TO_LABELS



    def getLabelIndex(self,class_):
        class_ = str(class_.decode("utf-8"))
        # Get the remapped label
        label = class_

        indx = self.CLASS_NAMES.index(class_) + 1
        return indx




    def predict_once(self, image_np):
        dark_frame = darknetImage(image_np)
        image_height,image_width,_ = image_np.shape
        results = self.net.detect(dark_frame,self.output_data.score_thresh)
        del dark_frame
        classes = []
        scores = []
        bbs = []
        for class_, score, bounds in results:
            x, y, w, h = bounds

            X = (x - w/2)/image_width
            Y = (y - h/2)/image_height
            X_ = (x + w/2)/image_width
            Y_ = (y + h/2)/image_height
            bbs.append([Y, X,Y_,X_])
            scores.append(score)
            index = self.getLabelIndex(class_)
            classes.append(index)
        scores = np.asarray(scores)
        classes = np.asarray(classes)
        bbs = np.asarray(bbs)

        self.output_data.scores = scores
        self.output_data.classes = classes
        self.output_data.bbs = bbs
        self.output_data.image_data.image_np = image_np

        time.sleep(self.frames_per_ms)

    def predict(self,threadName):
        while not self.done:
            image_np = self.getImage()
            if not self.pause:
                self.predict_once(image_np)
            else:
                self.output_data.bbs = np.asarray([])
                time.sleep(2.0) # Sleep for 2 seconds
    def run(self):
        print("Starting " + self.name)
        self.predict(self.name)
        print("Exiting " + self.name)
    def pause_predictor(self):
        self.pause = True
    def continue_predictor(self):
        self.pause = False
    def stop(self):
        self.done = True
    def getImage(self):
        '''
        Returns the image that we will use for prediction.
        '''
        self.output_data.image_data.original_image_np = self.image_data.image_np
        self.output_data.image_data.image_np = self.image_data.image_np

        return self.output_data.image_data.image_np
