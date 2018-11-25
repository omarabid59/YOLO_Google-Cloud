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
