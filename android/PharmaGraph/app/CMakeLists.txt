cmake_minimum_required(VERSION 3.22.1)

project("pharma-native")

# Set the path to llama.cpp if available
# set(LLAMA_DIR ${CMAKE_SOURCE_DIR}/../../../llama.cpp)

add_library(${CMAKE_PROJECT_NAME} SHARED
        src/main/cpp/pharma-native.cpp)

# Placeholder for llama.cpp linking
# add_subdirectory(${LLAMA_DIR} llama.cpp)

target_link_libraries(${CMAKE_PROJECT_NAME}
        android
        log
        # llama
)
