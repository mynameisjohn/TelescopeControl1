cmake_minimum_required(VERSION 2.8)

project(TelescopeControl)
set(CMAKE_CXX_FLAGS "-std=c++14 -Wall")

find_package(SDL2)

file(GLOB SRC ${CMAKE_CURRENT_SOURCE_DIR}/src/*)
file(GLOB INC ${CMAKE_CURRENT_SOURCE_DIR}/include/*)
file(GLOB SCRIPTS ${CMAKE_CURRENT_SOURCE_DIR}/scripts/*)

add_subdirectory(${CMAKE_CURRENT_SOURCE_DIR}/pyl)
add_executable(TelescopeControl ${SRC})
target_include_directories(TelescopeControl PUBLIC 
    ${CMAKE_CURRENT_SOURCE_DIR}/pyl 
    ${PYTHON_INCLUDE_DIR}
    ${SDL2_INCLUDE_DIR})

target_link_libraries(TelescopeControl LINK_PUBLIC PyLiaison ${PYTHON_LIBRARY} ${SDL2_LIBRARY})

