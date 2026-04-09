# SPDX-License-Identifier: MIT
#
# SPDX-FileCopyrightText: Copyright (c) 2019-2023 Lars Melchior and contributors

set(CPM_DOWNLOAD_VERSION 0.40.1)
set(CPM_HASH_SUM "117cbf2711572f113bab262933eb5187b08cfc06dce0714a1ee94f2183ddc3ec")

if(CPM_SOURCE_CACHE)
  set(CPM_DOWNLOAD_LOCATION "${CPM_SOURCE_CACHE}/cpm/CPM_${CPM_DOWNLOAD_VERSION}.cmake")
elseif(DEFINED ENV{CPM_SOURCE_CACHE})
  set(CPM_DOWNLOAD_LOCATION "$ENV{CPM_SOURCE_CACHE}/cpm/CPM_${CPM_DOWNLOAD_VERSION}.cmake")
else()
  set(CPM_DOWNLOAD_LOCATION "${CMAKE_BINARY_DIR}/cmake/CPM_${CPM_DOWNLOAD_VERSION}.cmake")
endif()

# Expand relative path. This is important if the provided path contains a tilde (~)
get_filename_component(CPM_DOWNLOAD_LOCATION ${CPM_DOWNLOAD_LOCATION} ABSOLUTE)
get_filename_component(CPM_DOWNLOAD_DIRECTORY "${CPM_DOWNLOAD_LOCATION}" DIRECTORY)

# Reconfigure can fail if a previous build used a different CPM source cache.
# In that case, stale internal cache entries make CPM.cmake return early before
# defining CPMAddPackage for the current cache location.
if(DEFINED CPM_DIRECTORY AND NOT CPM_DIRECTORY STREQUAL CPM_DOWNLOAD_DIRECTORY)
  unset(CPM_DIRECTORY CACHE)
  unset(CPM_FILE CACHE)
  unset(CPM_PACKAGES CACHE)
  unset(CPM_VERSION CACHE)
endif()

if(NOT EXISTS "${CPM_DOWNLOAD_LOCATION}")
  file(DOWNLOAD
       https://github.com/cpm-cmake/CPM.cmake/releases/download/v${CPM_DOWNLOAD_VERSION}/CPM.cmake
       ${CPM_DOWNLOAD_LOCATION} EXPECTED_HASH SHA256=${CPM_HASH_SUM}
  )
endif()

include(${CPM_DOWNLOAD_LOCATION})
