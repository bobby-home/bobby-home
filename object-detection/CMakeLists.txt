cmake_minimum_required(VERSION 3.11)

project(object-detection)

include(FetchContent)
include(ExternalProject)

if (NOT EXISTS ${CMAKE_BINARY_DIR}/CMakeCache.txt)
    if (NOT CMAKE_BUILD_TYPE)
        set(CMAKE_BUILD_TYPE "Release" CACHE STRING "" FORCE)
        message(STATUS "No previous build - default to Release build")
    endif()
endif()

set (CMAKE_EXPORT_COMPILE_COMMANDS ON)
set (CMAKE_CXX_STANDARD 17)

# remove -pedantic for tensorflow...
add_compile_options(-Wall -Wextra -Wno-unused-parameter -faligned-new)
# should it be 32 bits as I'm targetting the RPI with 32bits OS?
add_definitions(-D_FILE_OFFSET_BITS=64)

if (CMAKE_COMPILER_IS_GNUCXX)
    add_compile_options(-Wno-psabi)
endif()

#option(BUILD_SHARED_LIBS "Build using shared libraries" ON)
set(BUILD_SHARED_LIBS OFF)

IF (NOT ENABLE_COMPILE_FLAGS_FOR_TARGET)
    # On a Pi this will give us armhf or arm64.
    execute_process(COMMAND dpkg-architecture -qDEB_HOST_ARCH
        OUTPUT_VARIABLE ENABLE_COMPILE_FLAGS_FOR_TARGET OUTPUT_STRIP_TRAILING_WHITESPACE)
endif()
message(STATUS "Platform: ${ENABLE_COMPILE_FLAGS_FOR_TARGET}")
if ("${ENABLE_COMPILE_FLAGS_FOR_TARGET}" STREQUAL "arm64")
    # 64-bit binaries can be fully optimised.
    add_definitions(-ftree-vectorize)
elseif ("${ENABLE_COMPILE_FLAGS_FOR_TARGET}" STREQUAL "armv8-neon")
    # Only build with 32-bit Pi 3/4 specific optimisations if requested on the command line.
    add_definitions(-mfpu=neon-fp-armv8 -ftree-vectorize)
endif()

# Source package generation setup.
set(CPACK_GENERATOR "TXZ")
set(CPACK_PACKAGE_FILE_NAME "object-detection-build")
set(CPACK_SOURCE_GENERATOR "TXZ")
set(CPACK_INSTALL_SCRIPTS ${CMAKE_SOURCE_DIR}/package.cmake)
set(CPACK_SOURCE_PACKAGE_FILE_NAME "object-detection-src")
set(CPACK_SOURCE_IGNORE_FILES "/\.git*;/build;")
include(CPack)

set(PKG_CONFIG_ARGN, "--cflags --libs")

find_package(Threads)

# Paho MQTT lib
#find_package(OpenSSL REQUIRED)
find_library(paho-mqttpp3 NAMES libpaho-mqttpp3.a REQUIRED)
find_library(paho-mqtt3a NAMES libpaho-mqtt3a.a REQUIRED)

add_library(pahottpp STATIC IMPORTED)
set_target_properties(pahottpp PROPERTIES IMPORTED_LOCATION ${paho-mqttpp3})

add_library(pahomqtt3a SHARED IMPORTED)
set_property(TARGET pahomqtt3a PROPERTY IMPORTED_LOCATION ${paho-mqtt3a})

# Directories
add_subdirectory(processing)

add_executable(object-detection mqtt-objectdetection.cpp)

include(FindPkgConfig)
#find_package(UUID REQUIRED)
pkg_search_module(UUID REQUIRED uuid)
#target_link_libraries(object-detection ${UUID_LIBRARIES})
include_directories(object-detection ${UUID_INCLUDE_DIRS})

# opencv
find_package(OpenCV REQUIRED)
#target_link_libraries(object-detection ${OpenCV_LIBS})
include_directories(${OpenCV_INCLUDE_DIRS})

# json
FetchContent_Declare(json
    GIT_REPOSITORY https://github.com/nlohmann/json
    GIT_TAG v3.10.5
)

FetchContent_GetProperties(json)
if(NOT json_POPULATED)
    FetchContent_Populate(json)
    add_subdirectory(${json_SOURCE_DIR} ${json_BINARY_DIR} EXCLUDE_FROM_ALL)
endif()

#target_link_libraries(object-detection nlohmann_json::nlohmann_json)

# fmt
FetchContent_Declare(fmt
  GIT_REPOSITORY https://github.com/fmtlib/fmt.git
  GIT_TAG master
)
FetchContent_MakeAvailable(fmt)

#target_link_libraries(object-detection fmt::fmt)

# doc test
# from: https://github.com/doctest/doctest/blob/master/doc/markdown/build-systems.md
find_package(Git)
if(Git_FOUND)
  message("Git found: ${GIT_EXECUTABLE}")
endif()

ExternalProject_Add(
    doctest
    PREFIX ${CMAKE_BINARY_DIR}/doctest
    GIT_REPOSITORY https://github.com/doctest/doctest.git
    TIMEOUT 10
    UPDATE_COMMAND ${GIT_EXECUTABLE} pull
    CONFIGURE_COMMAND ""
    BUILD_COMMAND ""
    INSTALL_COMMAND ""
    LOG_DOWNLOAD ON
)
# Expose required variable (DOCTEST_INCLUDE_DIR) to parent scope
ExternalProject_Get_Property(doctest source_dir)
set(DOCTEST_INCLUDE_DIR ${source_dir}/doctest CACHE INTERNAL "Path to include folder for doctest")
target_include_directories(object-detection PUBLIC ${DOCTEST_INCLUDE_DIR})

# Include tensorflow
include_directories(object-detection ~/tensorflow/tensorflow/lite/tools/make/downloads/flatbuffers/include)
include_directories(object-detection ~/tensorflow)

#target_link_libraries(object-detection processing)
target_link_libraries(object-detection PRIVATE Threads::Threads pahottpp pahomqtt3a ${OpenCV_LIBS}
    fmt::fmt nlohmann_json::nlohmann_json
    processing
    -L~/tensorflow/tensorflow/lite/tools/make/gen/rpi_armv7l/lib
    ${UUID_LIBRARIES}
    )
