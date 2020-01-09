# INTRODUCTION

**NOTE. This repository is no longer actively being maintained by me. However, if others would like to make changes, please put up a Pull request and I'll do my best to merge the changes ASAP. Happy coding! :)**

This repository demonstrates how one can do Object Detection in real time using GPUs that are available on Google Cloud for free using Google's 1 year credits. We use a [You Only Look Once](https://pjreddie.com/darknet/yolo/) archictecture for object detection that can be visualized in a web browser as shown below.

![alt text](https://github.com/omarabid59/cloud_ml_webrtc/blob/master/docs/demo.gif "Demo of Object Detection on the Cloud!")

## Why should I use this?
Object detection is a difficult and computationally expensive problem and not everyone has access to GPUs to do real time object detection. Furthermore, there are alternatives. For example, Tensorflow offers lightweight mobilenet models (see [here](https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/detection_model_zoo.md)), but they come at the cost of reduced accuracy. Object detection is also available on iOS/Android, but they face the same issues mentioned earlier.

An interesting solution has also been presented on [WebRTCHacks](https://webrtchacks.com/webrtc-cv-tensorflow/). I've tested it myself and it works well. However, that solution sends Webcam video as a series of encoded jpg images resulting in significant bandwidth usage and latency that is not present in this solution.

Doing object detection on the cloud eliminates these problems. What's more is that since you can choose which GPU you want to use, you can run much "heavy" deep neural networks while still achieving close to real time accuracy.

Inference/testing on the following models has been verified, all with a latency of less than 100 ms. The latency will depend on the location of the Google Cloud Server and where you are located (more on this later).
- [ssd inception v2 coco](http://download.tensorflow.org/models/object_detection/ssd_inception_v2_coco_2018_01_28.tar.gz)
- [YOLO COCO](https://pjreddie.com/darknet/yolo/)
- [YOLO 9000](https://pjreddie.com/darknet/yolo/)

# DEPENDENCIES
- We use a YOLO python GPU binding. See the [original repository for more details](https://github.com/madhawav/YOLO3-4-Py)
- For sending real time video streams over the browser, we use an ``asyncio`` implementation of ``WebRTC`` called [aiortc](https://github.com/jlaine/aiortc). Aiortc must be installed according to their instruction and working before this repository will be usable. Here are a summary of the steps I have compiled:



# Installation
## Install depenencies
1. Create an instance of the Virtual Machine by running the following in the Google Cloud Shell. Replace ``YOUR_PROJECT_NAME`` with the name of your project the VM should be deployed in.  
	- ``gcloud beta compute --project=YOUR_PROJECT_NAME instances create instance-1 --zone=us-east1-b --machine-type=n1-standard-2 --subnet=default --network-tier=PREMIUM --maintenance-policy=TERMINATE --service-account=740303654106-compute@developer.gserviceaccount.com --scopes=https://www.googleapis.com/auth/devstorage.read_only,https://www.googleapis.com/auth/logging.write,https://www.googleapis.com/auth/monitoring.write,https://www.googleapis.com/auth/servicecontrol,https://www.googleapis.com/auth/service.management.readonly,https://www.googleapis.com/auth/trace.append --accelerator=type=nvidia-tesla-p100,count=1 --tags=http-server,https-server --image=c2-deeplearning-tf-1-12-cu100-20181120 --image-project=ml-images --boot-disk-size=60GB --boot-disk-type=pd-standard --boot-disk-device-name=instance-1``

2. Open up an SSH terminal of the newly created instance as shown below. Also note down the **external IP**. You will need it for later.
![alt text](https://github.com/omarabid59/YOLO_Google-Cloud/blob/master/docs/step_1.png)


3. You will get a prompt asking to install NVIDIA drivers. Enter `y`.
![alt text](https://github.com/omarabid59/YOLO_Google-Cloud/blob/master/docs/step_2.png)
4. Install ffmpeg and additional packages.
	- ``sudo apt install ffmpeg``
	- ``sudo apt install libavdevice-dev libavfilter-dev libopus-dev libvpx-dev pkg-config``
5. Once the installation is complete, clone the git repository and install the dependencies. Grab a cup of coffee. This will take a few minutes.
	- ``cd ~``
	- ``git clone https://github.com/omarabid59/YOLO_Google-Cloud.git``
	- ``cd ~/YOLO_Google-Cloud``
	- ``pip3 install -r requirements.txt``

## Download YOLO model.
1. Next, download the YOLO model cfg file and weights file by running the following commands:
	- ``mkdir -p ~/YOLO_Google-Cloud/mlserver/model``
	- ``cd ~/YOLO_Google-Cloud/mlserver/model``
	- ``wget https://raw.githubusercontent.com/pjreddie/darknet/master/cfg/yolov3.cfg``
	- ``wget https://pjreddie.com/media/files/yolov3.weights``
	- ``wget https://raw.githubusercontent.com/pjreddie/darknet/master/data/coco.names``

# Quick Start
1. First run the Machine Learning Server.
	- ``nohup python3 ~/YOLO_Google-Cloud/mlserver/mlserverclient.py &``
2. Next, run the http server. If you see the command output below, it means you are good to go!
	- ``cd ~/YOLO_Google-Cloud/webserver/ && python3 httpserver.py``
![alt text](https://github.com/omarabid59/YOLO_Google-Cloud/blob/master/docs/step_3.png)
3. Now, go to your browser and type in the following. Where ``YOUR_IP_ADDRESS`` is the one you obtained in step 2.
	- ``https://YOUR_IP_ADDRESS:8889``
That's it!

# IMPORTANT NOTE.
**REMEMBER TO SHUT OFF THE GOOGLE CLOUD VM IMMEDIATELY AFTER YOU ARE FINISHED EXPERIMENTING TO AVOID USING UP YOUR GOOGLE CREDITS AND BEING CHARGED (If you exceed your credits)**
