add_executable(test_nr_redcap_coreset0 test_nr_redcap_coreset0.cpp)
target_link_libraries(test_nr_redcap_coreset0 PRIVATE GTest::gtest)
add_dependencies(tests test_nr_redcap_coreset0)
add_test(NAME test_nr_redcap_coreset0 COMMAND ./test_nr_redcap_coreset0)

add_executable(test_nr_redcap_sdt_fsm test_nr_redcap_sdt_fsm.cpp ../nr_mac_sdt_fsm.c)
target_link_libraries(test_nr_redcap_sdt_fsm PRIVATE GTest::gtest)
add_dependencies(tests test_nr_redcap_sdt_fsm)
add_test(NAME test_nr_redcap_sdt_fsm COMMAND ./test_nr_redcap_sdt_fsm)
