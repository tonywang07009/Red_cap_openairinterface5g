cmake_minimum_required(VERSION 3.16)

project(tl_expected_gate_c_stub LANGUAGES CXX)

add_library(tl::expected INTERFACE IMPORTED GLOBAL)

set_target_properties(tl::expected PROPERTIES
    INTERFACE_INCLUDE_DIRECTORIES ${CMAKE_CURRENT_SOURCE_DIR}/include
)
