# INTRODUCTION
This repository demonstrates how one can do Object Detection in real time using GPUs that are available on Google Cloud for free using Google's 1 year credits. The resulting object detection results can be visualized in a web browser as shown below.

![alt text](https://github.com/omarabid59/cloud_ml_webrtc/blob/master/demo.gif "Demo of Object Detection on the Cloud!")

## Why should I use this?
Object detection is a difficult and computationally expensive problem and not everyone has access to GPUs to do real time object detection. Furthermore, there are alternatives. For example, Tensorflow offers lightweight mobilenet models (see [here](https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/detection_model_zoo.md)), but they come at the cost of reduced accuracy. Object detection is also available on iOS/Android, but they face the same issues mentioned earlier.

Doing object detection on the cloud eliminates these problems. What's more is that since you can choose which GPU you want to use, you can run much "heavy" deep neural networks while still achieving close to real time accuracy?

I've tested inference/testing on the following models, all with a latency of less than 500 ms. The latency will depend on the location of the Google Cloud Server and where you are located (more on this later).
- [ssd inception v2 coco](http://download.tensorflow.org/models/object_detection/ssd_inception_v2_coco_2018_01_28.tar.gz)
- [YOLO COCO](https://pjreddie.com/darknet/yolo/)
- [YOLO 9000](https://pjreddie.com/darknet/yolo/)
# DEPENDENCIES
- Install the depenencies by running ``pip3 install -r requirements.txt`` in this git repository
- We use a YOLO python GPU binding. See the [original repository for more details](https://github.com/madhawav/YOLO3-4-Py)
- For sending real time video streams over the browser, we use an ``asyncio`` implementation of ``WebRTC`` called [aiortc](https://github.com/jlaine/aiortc). Aiortc must be installed according to their instruction and working before this repository will be usable. Here are a summary of the steps I have compiled:
    - Uninstall any currently installed version of ffmpeg:
        - ``sudo apt remove ffmpeg``
    - Install FFMPEG 3
        - ``sudo add-apt-repository ppa:jonathonf/ffmpeg-3``
        - ``sudo apt update``
        - ``sudo apt install ffmpeg``
        - ``export LD_LIBRARY_PATH="/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH"``
        - ``sudo apt install libavdevice-dev libavfilter-dev libopus-dev libvpx-dev pkg-config``
    - ``pip3 install aiohttp aiortc opencv-python``

Additionally you need to install the Tensorflow Object Detection API see [here for instructions](https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/installation.md). I will remove this dependency in a future release.
