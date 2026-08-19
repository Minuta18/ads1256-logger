cmake_minimum_required(VERSION 3.16)
project(ads_reader)

find_package(PkgConfig REQUIRED)
pkg_check_modules(GPIOD REQUIRED libgpiod)

add_library(ads_reader SHARED
        src/ads1256.c
        src/spidev.c
        src/ads_reader.c
)

target_include_directories(ads_reader PUBLIC
        include
)

target_include_directories(ads_reader PRIVATE ${GPIOD_INCLUDE_DIRS})
target_link_libraries(ads_reader PRIVATE ${GPIOD_LIBRARIES})

set_target_properties(ads_reader PROPERTIES POSITION_INDEPENDENT_CODE ON)