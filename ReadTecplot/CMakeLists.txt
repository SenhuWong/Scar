cmake_minimum_required(VERSION 3.10.0)

project(TecReader)
set(HDF5_DIR ~/thirdParty/HDF_Group/HDF5/1.8.21/share/cmake/hdf5)
find_package(HDF5 REQUIRED)
message("HDF5 INCLUDE DIR IS ${HDF5_INCLUDE_DIRS}")

message("HDF5 LIBRARIES ARE ${HDF5_LIBRARIES}")
message(${HDF5_LIBRARIES})
set(CMAKE_EXPORT_COMPILE_COMMANDS on)

set(SRC main.cpp)

add_executable(myAPP ${SRC})

target_include_directories(myAPP PUBLIC ${HDF5_INCLUDE_DIRS})
target_link_libraries(myAPP ${HDF5_LIBRARIES})
