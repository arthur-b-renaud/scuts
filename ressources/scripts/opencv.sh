#!/usr/bin/env bash
OPENCV_VERSION='3.4.3'

#OpenCV
apt-get install -y qt5-default libvtk6-dev
apt-get install -y zlib1g-dev libjpeg-dev libwebp-dev libpng-dev libtiff5-dev libopenexr-dev libgdal-dev
apt-get install -y libdc1394-22-dev libavcodec-dev libavformat-dev libswscale-dev libtheora-dev libvorbis-dev libxvidcore-dev libx264-dev yasm libopencore-amrnb-dev libopencore-amrwb-dev libv4l-dev libxine2-dev
apt-get install -y libtbb-dev libeigen3-dev
apt-get install -y python-dev python-tk python-numpy python3-dev python3-tk python3-numpy
apt-get install -y ant default-jdk
apt-get install -y doxygen

apt-get -y install git gfortran
apt-get -y install libtiff5-dev
apt-get -y install libxine2-dev libv4l-dev
apt-get -y install qt5-default libgtk2.0-dev libtbb-dev
apt-get -y install libatlas-base-dev
apt-get -y install libfaac-dev libmp3lame-dev libtheora-dev
apt-get -y install libvorbis-dev libxvidcore-dev
apt-get -y install libopencore-amrnb-dev libopencore-amrwb-dev
apt-get -y install x264 v4l-utils
apt-get -y install libprotobuf-dev protobuf-compiler
apt-get -y install libgoogle-glog-dev libgflags-dev
apt-get -y install libgphoto2-dev libeigen3-dev libhdf5-dev doxygen
apt-get -y install python-dev python-pip python3-dev python3-pip

pip2 install -U pip numpy
pip3 install -U pip numpy

mkdir "/usr/local/Cellar"
cd "/usr/local/Cellar"
git clone https://github.com/opencv/opencv.git
cd opencv
git checkout 3.4.3
cd ..

git clone https://github.com/opencv/opencv_contrib.git
cd opencv_contrib
git checkout 3.4.3
cd ..

cd "/usr/local/Cellar"
cd opencv
mkdir build
cd build

cmake -D CMAKE_BUILD_TYPE=RELEASE \
      -D CMAKE_INSTALL_PREFIX=/usr/local \
      -D INSTALL_C_EXAMPLES=ON \
      -D INSTALL_PYTHON_EXAMPLES=ON \
      -D WITH_TBB=ON \
      -D WITH_V4L=ON \
      -D WITH_QT=ON \
      -D OPENCV_ENABLE_NONFREE=ON \
      -D WITH_OPENGL=ON \
      -D OPENCV_EXTRA_MODULES_PATH=../../opencv_contrib/modules \
      -D BUILD_EXAMPLES=ON ..
	  
make
make install
ldconfig

echo "Final tests with Python 2 and Python 3"
python -c "import cv2; print(cv2.__version__); img = cv2.imread('')"
python3 -c "import cv2; print(cv2.__version__); img = cv2.imread('')"

make clean

# Then for having cv2 in a virtualenv
ln -s "/usr/local/lib/python3.5/dist-packages/cv2.cpython-35m-x86_64-linux-gnu.so" "/home/renaud/.local/share/virtualenvs/scuts-9KAUpLJp/lib/python3.6/site-packages/cv2/cv2.so"