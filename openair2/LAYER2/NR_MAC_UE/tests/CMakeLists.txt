add_executable(test_nr_ue_power_procedures
  test_nr_ue_power_procedures.cpp)
target_link_libraries(test_nr_ue_power_procedures PRIVATE nr_ue_power_procedures GTest::gtest minimal_lib)
add_dependencies(tests test_nr_ue_power_procedures)
add_test(NAME test_nr_ue_power_procedures
  COMMAND ./test_nr_ue_power_procedures)

add_executable(test_nr_ue_ra_procedures test_nr_ue_ra_procedures.cpp)
target_link_libraries(test_nr_ue_ra_procedures PRIVATE nr_ue_ra_procedures nr_ue_power_procedures GTest::gtest minimal_lib)
add_dependencies(tests test_nr_ue_ra_procedures)
add_test(NAME test_nr_ue_ra_procedures
  COMMAND ./test_nr_ue_ra_procedures)

add_executable(test_nr_ue_redcap_bwp
  test_nr_ue_redcap_bwp.cpp
  ../nr_ue_redcap_bwp.c)
target_link_libraries(test_nr_ue_redcap_bwp PRIVATE GTest::gtest minimal_lib asn1_nr_rrc)
add_dependencies(tests test_nr_ue_redcap_bwp)
add_test(NAME test_nr_ue_redcap_bwp
  COMMAND ./test_nr_ue_redcap_bwp)
