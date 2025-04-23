cmake_minimum_required(VERSION 3.14)
project(ffenc_uiuc)

# Use C++11
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find Python and pybind11
find_package(Python3 REQUIRED COMPONENTS Interpreter Development)
find_package(pybind11 REQUIRED)

# Include headers
include_directories(
    ${PROJECT_SOURCE_DIR}/ffmpeg/include
    ${PROJECT_SOURCE_DIR}/ffmpeg/include/libavformat
    ${PROJECT_SOURCE_DIR}/x264/include
)

message(PROJECT_SOURCE_DIR="${PROJECT_SOURCE_DIR}")

message(Python3_INCLUDE_DIRS="${Python3_INCLUDE_DIRS}")

# Add ffenc module
add_library(ffenc MODULE ffenc/ffenc.cc)
set_target_properties(ffenc PROPERTIES PREFIX "" SUFFIX ".pyd")
target_link_libraries(ffenc PRIVATE
    pybind11::module
    avformat avcodec avutil swscale x264
)
target_include_directories(
  ffenc PRIVATE ${Python3_INCLUDE_DIRS}
)
target_link_directories(ffenc PRIVATE
    ${PROJECT_SOURCE_DIR}/ffmpeg/lib
    ${PROJECT_SOURCE_DIR}/x264/lib
)

# Add ffdec module
add_library(ffdec MODULE ffdec/ffdec.cc)
set_target_properties(ffdec PROPERTIES PREFIX "" SUFFIX ".pyd")
target_link_libraries(ffdec PRIVATE
    pybind11::module
    avformat avcodec avutil swscale x264
)
target_include_directories(ffdec PRIVATE ${Python3_INCLUDE_DIRS})
target_link_directories(ffdec PRIVATE
    ${PROJECT_SOURCE_DIR}/ffmpeg/lib
    ${PROJECT_SOURCE_DIR}/x264/lib
)
