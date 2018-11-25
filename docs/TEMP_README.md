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
	- ``wget https://github.com/pjreddie/darknet/blob/master/cfg/yolov3.cfg``
	- ``wget https://pjreddie.com/media/files/yolov3.weights``
	- ``wget https://raw.githubusercontent.com/pjreddie/darknet/master/data/coco.names``

# Install Tensorflow's Object Detection Application
	-
