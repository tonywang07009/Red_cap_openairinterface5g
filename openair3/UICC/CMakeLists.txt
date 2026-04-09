add_library(lib_uicc OBJECT usim_interface.c)
target_include_directories(lib_uicc PRIVATE .)
target_link_libraries(lib_uicc PRIVATE log_headers)

add_library(lib_nr_redcap_config OBJECT nr_redcap_config.c)
target_include_directories(lib_nr_redcap_config PRIVATE .)
target_link_libraries(lib_nr_redcap_config PRIVATE log_headers)
