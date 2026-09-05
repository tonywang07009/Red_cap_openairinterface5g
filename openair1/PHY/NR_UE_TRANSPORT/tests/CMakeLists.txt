add_executable(test_nr_ue_aiot_r2d_resources
  test_nr_ue_aiot_r2d_resources.c
  ../nr_ue_rf_helpers.c
  ../../CODING/crc_byte.c)
# Discard unrelated RF helpers so this pure admission test needs no softmodem globals.
target_compile_options(test_nr_ue_aiot_r2d_resources PRIVATE -ffunction-sections -fdata-sections)
target_link_options(test_nr_ue_aiot_r2d_resources PRIVATE -Wl,--no-export-dynamic -Wl,--gc-sections)
target_link_libraries(test_nr_ue_aiot_r2d_resources PRIVATE asn1_nr_rrc_hdrs asn1_lte_rrc_hdrs T_headers)
target_include_directories(test_nr_ue_aiot_r2d_resources PRIVATE
  ${CMAKE_SOURCE_DIR}/common/utils/barrier
  ${CMAKE_SOURCE_DIR}/common/utils/actor
  ${CMAKE_SOURCE_DIR}/common/utils/threadPool)
add_dependencies(tests test_nr_ue_aiot_r2d_resources)
add_test(NAME test_nr_ue_aiot_r2d_resources COMMAND test_nr_ue_aiot_r2d_resources)
