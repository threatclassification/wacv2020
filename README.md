# Requirements
This assumes you are running ubuntu 16.04 and already have darknet/yolo installed.  The regular version of darknet/yolo can either be downloaded by following the instrucitons [here](https://pjreddie.com/darknet/yolo/), or from the threatclassification repo [here](https://github.com/threatclassification/darknet-yolov3).  For the ROS integrated yolo, our local repo is [here](https://github.com/threatclassification/darknet-yolov3-ros).

# Installation of threat detection module
	
	mkdir -p ~/threat_detection/azure/rifle && cd ~/threat_detection
	
	git init && git remote add gh git@github.com:threatclassification/threat_detection.git && git pull gh master

# Datasets
## Download our dataset
[Download here](https://github.com/threatclassification/threat_detection/tree/master/scripts)

## Creating a new dataset
To download new images for making a new dataset follow instructions [here](https://github.com/threatclassification/threat_detection/tree/master/download_images)

To label new class, follow instructions [here](https://github.com/threatclassification/threat_detection/tree/master/YOLOtools)


# Downloading pose caffemodels

	cd ~/threat_detection && . /pose_detection/pose_models/getModels.sh 


# Using virtual environments for python

	sudo pip install virtualenv virtualenvwrapper
	sudo rm -rf ~/.cache/pip

	echo 'export WORKON_HOME=$HOME/.virtualenvs' >> ~/.bashrc
	echo 'source /usr/local/bin/virtualenvwrapper.sh' >> ~/.bashrc
	
	mkvirtualenv cvn


	cd ~ && git clone git@github.com:opencv/opencv.git && cd opencv && git checkout 3.0.0

	mkdir -p ~/opencv/opencv/build
	cd ~/opencv/opencv/build
	cmake -D CMAKE_BUILD_TYPE=RELEASE -D CMAKE_INSTALL_PREFIX=/usr/local -D INSTALL_C_EXAMPLES=OFF -D INSTALL_PYTHON_EXAMPLES=ON -D OPENCV_EXTRA_MODULES_PATH=~/opencv_contrib/modules -D BUILD_EXAMPLES=ON ..


