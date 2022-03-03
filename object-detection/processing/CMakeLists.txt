cmake_minimum_required(VERSION 3.6)

# Create a library called "processing" which includes source files.
add_library(processing object_detection.cpp)

find_package(Threads)

# add tf things. Bad way, but it works.
include_directories(processing ~/tensorflow/tensorflow/lite/tools/make/downloads/flatbuffers/include)
include_directories(processing ~/tensorflow)

# I added the libtensorflow-lite.a to /lib
# so I don't need this, and more importantly, the next line is working, which was not the case before.
#target_link_libraries(processing ~/tensorflow/tensorflow/lite/tools/make/gen/rpi_armv7l/lib)

# opencv
set(OpenCV_STATIC ON)
find_package(OpenCV REQUIRED)
target_link_libraries(processing PRIVATE ${OpenCV_LIBS} Threads::Threads tensorflow-lite)
include_directories(${OpenCV_INCLUDE_DIRS})


message(STATUS "target_include_directories PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}")
target_include_directories(processing PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})

#install(TARGETS processing LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR} ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR})
