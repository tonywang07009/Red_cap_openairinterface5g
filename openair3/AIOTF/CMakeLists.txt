add_library(aiotf_inventory STATIC aiotf_inventory.c)
target_include_directories(aiotf_inventory PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})

add_executable(test_aiotf_inventory tests/test_aiotf_inventory.c)
target_link_libraries(test_aiotf_inventory PRIVATE aiotf_inventory)

add_executable(oai-aiotf aiotf_service.c)
target_link_libraries(oai-aiotf PRIVATE aiotf_inventory)

if(ENABLE_TESTS)
  add_dependencies(tests test_aiotf_inventory oai-aiotf)
  add_test(NAME test_aiotf_inventory COMMAND test_aiotf_inventory)
  add_test(NAME test_aiotf_service COMMAND oai-aiotf --self-test)
endif()
