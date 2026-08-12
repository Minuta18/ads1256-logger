add_library(ads_reader SHARED
        src/ads_reader.c
)

target_include_directories(ads_reader PUBLIC
        include
)

set_target_properties(ads_reader PROPERTIES POSITION_INDEPENDENT_CODE ON)
