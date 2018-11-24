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

context = zmq.Context()

thread_image = ZeroMQImageInput(context);
thread_image.start()

thread_yolo = DarknetYOLO(thread_image.image_data,
                        YOLO_DIR="/home/omar_abid4_gmail_com/nnModels/yolov3/coco/608/",
                          score_thresh=0.5,
                         fps = 0.08)
thread_yolo.start()

thread_zeromqdatahandler = ZeroMQDataHandler(context,thread_yolo)
thread_zeromqdatahandler.start()