import warnings
warnings.filterwarnings('ignore')

from PredictorDarknet import DarknetYOLO
import time
import cv2
from PIL import Image

from ZeroMQ import ZeroMQDataHandler
from ZeroMQ import ZeroMQImageInput

import zmq
print("Finished Loading Imports")

import os
ROOT = os.path.dirname(os.path.realpath(__file__))

context = zmq.Context()

thread_image = ZeroMQImageInput(context);
thread_image.start()

thread_yolo = DarknetYOLO(thread_image.image_data,
                        YOLO_DIR=ROOT + "/model/",
                          score_thresh=0.5,
                         fps = 0.08)
thread_yolo.start()

thread_zeromqdatahandler = ZeroMQDataHandler(context,thread_yolo)
thread_zeromqdatahandler.start()
