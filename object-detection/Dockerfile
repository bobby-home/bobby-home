FROM debian:bullseye AS base
FROM debian:bullseye-slim AS base-slim

###
# Tensorflow
###
FROM base as tfbuild
RUN apt update && apt install -y curl wget git unzip gcc g++ make cmake

RUN wget -O tensorflow.zip https://github.com/tensorflow/tensorflow/archive/v2.6.0.zip && \
    unzip tensorflow.zip && \
    mv tensorflow-2.6.0 tensorflow && \
    cd tensorflow && \
    bash ./tensorflow/lite/tools/make/download_dependencies.sh

RUN bash ./tensorflow/tensorflow/lite/tools/make/build_rpi_lib.sh && \
   cp ./tensorflow/tensorflow/lite/tools/make/gen/rpi_armv7l/lib/libtensorflow-lite.a /usr/local/lib

###
# FlatBuffers
###
RUN cd ./tensorflow/tensorflow/lite/tools/make/downloads/flatbuffers && \
    mkdir build && cd build && cmake .. -DFLATBUFFERS_BUILD_TESTS=OFF && make -j4 && make install && ldconfig

###
# MQTT
###
from base as mqtt
RUN apt update && apt install -y build-essential git cmake wget unzip \
    libssl-dev doxygen graphviz

RUN wget -O paho.mqtt.c.zip https://github.com/eclipse/paho.mqtt.c/archive/refs/tags/v1.3.9.zip && \
    unzip paho.mqtt.c.zip && mv paho.mqtt.c-1.3.9 paho.mqtt.c

RUN cd ./paho.mqtt.c && \
    cmake -Bbuild -H. -DPAHO_ENABLE_TESTING=OFF -DBUILD_SHARED_LIBS=OFF -DPAHO_BUILD_STATIC=ON -DPAHO_WITH_SSL=OFF && \
    cmake --build build/ --target install && ldconfig

RUN wget -O paho.mqtt.cpp.zip https://github.com/eclipse/paho.mqtt.cpp/archive/refs/tags/v1.2.0.zip && \
   unzip paho.mqtt.cpp.zip && mv paho.mqtt.cpp-1.2.0 paho.mqtt.cpp

RUN cd ./paho.mqtt.cpp && \
    cmake -Bbuild -H. -DPAHO_ENABLE_TESTING=OFF -DBUILD_SHARED_LIBS=OFF -DPAHO_BUILD_STATIC=ON -DPAHO_WITH_SSL=OFF && \
    cmake --build build/ --target install && ldconfig

###
# OpenCV
###
FROM base as opencv
RUN apt update && apt install -y build-essential cmake git pkg-config \
	libjpeg-dev libpng-dev \
	libavcodec-dev libavformat-dev \
	libswscale-dev libdc1394-22-dev \
	libv4l-dev v4l-utils \
	libtbb2 libtbb-dev \
    wget unzip

RUN wget -O opencv.zip https://github.com/opencv/opencv/archive/refs/tags/4.5.5.zip && \
    unzip opencv.zip && mv opencv-4.5.5 opencv && cd opencv && \
    mkdir build

RUN cd ./opencv/build && \
cmake -D CMAKE_BUILD_TYPE=RELEASE \
-D BUILD_SHARED_LIBS=OFF \
-D BUILD_PROTOBUF=OFF \
-D WITH_PROTOBUF=OFF \
-D BUILD_JAVA=OFF \
-D WITH_ADE=OFF \
-D BUILD_opencv_flann=OFF \
-D BUILD_opencv_java_bindings_generator=OFF \
-D BUILD_opencv_js_bindings_generator=OFF \
-D WITH_FFMPEG=OFF \
-D WITH_IMGCODEC_PFM=OFF \
-D WITH_IMGCODEC_PXM=OFF \
-D WITH_IMGCODEC_SUNRASTER=OFF \
-D WITH_QUIRC=OFF \
-D CMAKE_INSTALL_PREFIX=/usr/local \
-D ENABLE_NEON=ON \
-D ENABLE_VFPV3=ON \
-D BUILD_ZLIB=ON \
-D BUILD_OPENMP=OFF \
-D BUILD_TIFF=OFF \
-D BUILD_OPENJPEG=OFF \
-D BUILD_JASPER=OFF \
-D BUILD_OPENEXR=OFF \
-D BUILD_WEBP=OFF \
-D BUILD_IPP_IW=OFF \
-D BUILD_ITT=OFF \
-D WITH_OPENMP=OFF \
-D WITH_OPENCL=OFF \
-D WITH_AVFOUNDATION=OFF \
-D WITH_CAP_IOS=OFF \
-D WITH_CAROTENE=OFF \
-D WITH_CPUFEATURES=OFF \
-D WITH_EIGEN=OFF \
-D WITH_GSTREAMER=OFF \
-D WITH_GTK=OFF \
-D WITH_IPP=OFF \
-D WITH_HALIDE=OFF \
-D WITH_VULKAN=OFF \
-D WITH_INF_ENGINE=OFF \
-D WITH_NGRAPH=OFF \
-D WITH_JASPER=OFF \
-D WITH_OPENJPEG=OFF \
-D WITH_WEBP=OFF \
-D WITH_OPENEXR=OFF \
-D WITH_TIFF=OFF \
-D WITH_OPENVX=OFF \
-D WITH_GDCM=OFF \
-D WITH_TBB=OFF \
-D WITH_HPX=OFF \
-D WITH_EIGEN=OFF \
-D WITH_V4L=ON \
-D WITH_LIBV4L=ON \
-D WITH_VTK=OFF \
-D WITH_QT=OFF \
-D BUILD_opencv_python3=OFF \
-D BUILD_opencv_java=OFF \
-D BUILD_opencv_gapi=OFF \
-D BUILD_opencv_objc=OFF \
-D BUILD_opencv_js=OFF \
-D BUILD_opencv_ts=OFF \
-D BUILD_opencv_dnn=OFF \
-D BUILD_opencv_calib3d=OFF \
-D BUILD_opencv_objdetect=OFF \
-D BUILD_opencv_stitching=OFF \
-D BUILD_opencv_ml=OFF \
-D BUILD_opencv_world=OFF \
-D BUILD_EXAMPLES=OFF \
-D OPENCV_ENABLE_NONFREE=OFF \
-D OPENCV_GENERATE_PKGCONFIG=ON \
-D INSTALL_C_EXAMPLES=OFF \
-D INSTALL_PYTHON_EXAMPLES=OFF .. && \
cmake --build . --target install

###
# Object Detection
###
FROM base as build
COPY --from=mqtt /usr/local/include /usr/local/include
COPY --from=mqtt /usr/local/lib /usr/local/lib
COPY --from=mqtt /usr/local/include /usr/local/include
COPY --from=opencv /usr/local/lib /usr/local/lib
COPY --from=opencv /usr/local/include /usr/local/include
RUN mkdir /root/tensorflow
COPY --from=tfbuild ./tensorflow/ /root/tensorflow
COPY --from=tfbuild /usr/local/lib /usr/local/lib

RUN apt update && apt-get install -y build-essential cmake make g++ gcc uuid-dev git pkg-config \
    libjpeg-dev libpng-dev libdc1394-22-dev
COPY . /opt/
RUN cd opt && mkdir build && cd build && cmake .. && make -j4

###
# Final image
###
FROM base-slim
RUN apt update && apt install -y libjpeg-dev libpng-dev netcat
COPY --from=build /opt/build/object-detection /opt
COPY ./detect.tflite ./coco_labels.txt ./entrypoint.sh /opt
RUN chmod +x /opt/entrypoint.sh

ENTRYPOINT ["/opt/entrypoint.sh"]
CMD ["/opt/object-detection", "/opt/coco_labels.txt", "/opt/detect.tflite"]
