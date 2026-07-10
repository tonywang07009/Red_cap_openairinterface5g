add_executable(test_nr_redcap_coreset0 test_nr_redcap_coreset0.cpp)
target_link_libraries(test_nr_redcap_coreset0 PRIVATE GTest::gtest)
add_dependencies(tests test_nr_redcap_coreset0)
add_test(NAME test_nr_redcap_coreset0 COMMAND ./test_nr_redcap_coreset0)

add_executable(test_nr_redcap_bwp test_nr_redcap_bwp.cpp ../nr_mac_redcap_bwp.c ../../../../common/utils/minimal_stub.c)
target_link_libraries(test_nr_redcap_bwp PRIVATE GTest::gtest asn1_nr_rrc)
add_dependencies(tests test_nr_redcap_bwp)
add_test(NAME test_nr_redcap_bwp COMMAND ./test_nr_redcap_bwp)

add_executable(test_nr_redcap_sdt_fsm test_nr_redcap_sdt_fsm.cpp ../nr_mac_sdt_fsm.c)
target_link_libraries(test_nr_redcap_sdt_fsm PRIVATE GTest::gtest)
add_dependencies(tests test_nr_redcap_sdt_fsm)
add_test(NAME test_nr_redcap_sdt_fsm COMMAND ./test_nr_redcap_sdt_fsm)

add_executable(test_nr_redcap_rc_ctrl test_nr_redcap_rc_ctrl.cpp ../../../E2AP/RAN_FUNCTION/O-RAN/ran_func_rc_redcap.c)
target_link_libraries(test_nr_redcap_rc_ctrl PRIVATE GTest::gtest)
add_dependencies(tests test_nr_redcap_rc_ctrl)
add_test(NAME test_nr_redcap_rc_ctrl COMMAND ./test_nr_redcap_rc_ctrl)

add_executable(test_nr_gnb_drx test_nr_gnb_drx.cpp ../nr_mac_drx.c)
target_link_libraries(test_nr_gnb_drx PRIVATE GTest::gtest)
add_dependencies(tests test_nr_gnb_drx)
add_test(NAME test_nr_gnb_drx COMMAND ./test_nr_gnb_drx)
