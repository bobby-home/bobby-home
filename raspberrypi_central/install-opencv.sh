sudo apt-get update && sudo apt-get upgrade

sudo apt-get -y install python-pip build-essential cmake pkg-config
sudo apt-get -y install libjpeg-dev libtiff5-dev libjasper-dev libpng-dev

sudo apt-get -y install libavcodec-dev libavformat-dev libswscale-dev libv4l-dev
sudo apt-get -y install libxvidcore-dev libx264-dev

sudo apt-get -y install libfontconfig1-dev libcairo2-dev
sudo apt-get -y install libgdk-pixbuf2.0-dev libpango1.0-dev
sudo apt-get -y install libgtk2.0-dev libgtk-3-dev

sudo apt-get -y install libatlas-base-dev gfortran

sudo apt-get -y install libhdf5-dev libhdf5-serial-dev libhdf5-103
sudo apt-get -y install libqtgui4 libqtwebkit4 libqt4-test python3-pyqt5

sudo apt-get -y install python3-dev

cd ~
wget -O opencv.zip https://github.com/opencv/opencv/archive/4.1.1.zip
wget -O opencv_contrib.zip https://github.com/opencv/opencv_contrib/archive/4.1.1.zip
unzip opencv.zip
unzip opencv_contrib.zip
mv opencv-4.1.1 opencv
mv opencv_contrib-4.1.1 opencv_contrib

rm opencv.zip && rm opencv_contrib.zip

# virtual env
sudo pip install virtualenv virtualenvwrapper
echo "export WORKON_HOME=$HOME/.virtualenvs" >> ~/.profile
echo "export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3" >> ~/.profile
echo "source /usr/local/bin/virtualenvwrapper.sh" >> ~/.profile
source ~/.profile

mkvirtualenv cv -p python3
workon cv
pip install numpy

cd ~/opencv
mkdir build
cd build
# Note: The Raspberry Pi Zero W hardware is not compatible with NEON or VFPv3.
# Remove ENABLE_NEON and ENABLE_VFPV3 if you're building for rpi zero.
    # -D ENABLE_NEON=ON \
    # -D ENABLE_VFPV3=ON \
cmake -D CMAKE_BUILD_TYPE=RELEASE \
    -D CMAKE_INSTALL_PREFIX=/usr/local \
    -D OPENCV_EXTRA_MODULES_PATH=~/opencv_contrib/modules \
    -D BUILD_TESTS=OFF \
    -D INSTALL_PYTHON_EXAMPLES=OFF \
    -D OPENCV_ENABLE_NONFREE=ON \
    -D CMAKE_SHARED_LINKER_FLAGS=-latomic \
    -D BUILD_EXAMPLES=OFF ..

# (cv) pi@raspberrypi:~/.virtualenvs/cv/lib/python3.7/site-packages $ ln -s /usr/local/lib/python3.7/site-packages/cv2/python-3.7/cv2.cpython-37m-arm-linux-gnueabihf.so cv2.so
