message(STATUS "Add test nas_lib_test")

add_executable(nas_lib_test nas_lib_test.c)

add_dependencies(tests nas_lib_test)
add_test(NAME nas_lib_test COMMAND nas_lib_test)

target_link_libraries(nas_lib_test PRIVATE
    nr_nas
)

target_include_directories(nas_lib_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}
)

add_executable(test_nr_nas_lowpower
    test_nr_nas_lowpower.c
    ../../nr_nas_lowpower.c)
add_dependencies(tests test_nr_nas_lowpower)
add_test(NAME test_nr_nas_lowpower COMMAND test_nr_nas_lowpower)
target_include_directories(test_nr_nas_lowpower PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}/../..
    ${CMAKE_CURRENT_SOURCE_DIR}/..
    ${CMAKE_CURRENT_SOURCE_DIR}/../5GMM/MSG
    ${CMAKE_CURRENT_SOURCE_DIR}/../5GMM/IES
)
