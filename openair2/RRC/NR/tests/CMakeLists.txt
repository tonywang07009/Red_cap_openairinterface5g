
add_executable(rrc_bearers_test rrc_bearers_test.c ../rrc_gNB_radio_bearers.c ${OPENAIR2_DIR}/LAYER2/nr_pdcp/asn1_utils.c)
add_dependencies(tests rrc_bearers_test)
add_test(NAME rrc_bearers_test COMMAND rrc_bearers_test)
target_include_directories(rrc_bearers_test PRIVATE ./common/utils/ds common/utils/LOG)
target_link_libraries(rrc_bearers_test PRIVATE ds alg asn1_e1ap asn1_lte_rrc_hdrs asn1_nr_rrc_hdrs LOG T)
target_compile_definitions(rrc_bearers_test PRIVATE ENABLE_TESTS)

add_executable(test_nr_rrc_redcap
  test_nr_rrc_redcap.cpp
  ${OPENAIR2_DIR}/RRC/NR_UE/rrc_ue_redcap.c)
add_dependencies(tests test_nr_rrc_redcap)
add_test(NAME test_nr_rrc_redcap COMMAND ./test_nr_rrc_redcap)
target_include_directories(test_nr_rrc_redcap PRIVATE ${CMAKE_SOURCE_DIR})
target_link_libraries(test_nr_rrc_redcap PRIVATE GTest::gtest minimal_lib asn1_nr_rrc)

add_executable(test_nr_rrc_lowpower
  test_nr_rrc_lowpower.cpp
  ${OPENAIR2_DIR}/RRC/NR_UE/rrc_ue_lowpower.c)
add_dependencies(tests test_nr_rrc_lowpower)
add_test(NAME test_nr_rrc_lowpower COMMAND ./test_nr_rrc_lowpower)
target_include_directories(test_nr_rrc_lowpower PRIVATE ${CMAKE_SOURCE_DIR} ${CMAKE_SOURCE_DIR}/common/utils/threadPool)
target_link_libraries(test_nr_rrc_lowpower PRIVATE GTest::gtest minimal_lib asn1_nr_rrc)
