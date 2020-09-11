FROM python:3.7.4

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN python -m pip install --upgrade pip

COPY requirements.txt /tmp/
RUN pip install --requirement /tmp/requirements.txt

# WIP: Build OpenCV
RUN apt-get update && apt-get install -y build-essential cmake git pkg-config \
    libjpeg-dev libtiff5-dev libpng-dev \
    libavcodec-dev libavformat-dev libswscale-dev libv4l-dev \
    libgtk2.0-dev libcanberra-gtk-module \
    libatlas-base-dev gfortran


RUN cd ~ && \
    wget -O opencv.zip https://github.com/opencv/opencv/archive/4.1.1.zip && \
    unzip opencv.zip && mv opencv-4.1.1 opencv

RUN cd ~ && \
    wget -O opencv_contrib.zip https://github.com/opencv/opencv_contrib/archive/4.1.1.zip && \
    unzip opencv_contrib.zip && mv opencv_contrib-4.1.1 opencv_contrib 

RUN dpkgArch="$(dpkg --print-architecture)"; \
    cd ~/opencv && \
    mkdir build && \
    cd build && \
    case "${dpkgArch##*-}" in \
        armv7) pythonArch='arm-linux-gnueabihf'; extra="-D ENABLE_NEON=ON; -D ENABLE_VFPV3=ON" ;; \
        amd64) pythonArch='x86_64-linux-gnu' ;; \
        *) echo >&2; echo >&2 "error: current architecture ($dpkgArch) is not supported." ;; \
    esac; \
    cmake -D CMAKE_BUILD_TYPE=RELEASE \
    -D CMAKE_INSTALL_PREFIX=/usr/local \
    -D OPENCV_EXTRA_MODULES_PATH=~/opencv_contrib/modules \
    # Don't enable this for amd64 arch. So in my case, enable it for raspberry pi.
    $extra \
    -D BUILD_TESTS=OFF \
    -D INSTALL_PYTHON_EXAMPLES=OFF \
    -D OPENCV_ENABLE_NONFREE=ON \
    # -DBUILD_opencv_java=OFF \
    -D CMAKE_SHARED_LINKER_FLAGS=-latomic \
    -DPYTHON_EXECUTABLE=$(which python3.7) \
    -D BUILD_EXAMPLES=OFF ..

RUN cd ~/opencv/build && make -j8

RUN ln -s /root/opencv/build/lib/python3/cv2.cpython-37$pythonArch.so \
  /usr/local/lib/python3.7/site-packages/cv2.so
