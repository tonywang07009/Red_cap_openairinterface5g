/*
 * Licensed to the OpenAirInterface (OAI) Software Alliance under one or more
 * contributor license agreements.  See the NOTICE file distributed with
 * this work for additional information regarding copyright ownership.
 * The OpenAirInterface Software Alliance licenses this file to You under
 * the OAI Public License, Version 1.1  (the "License"); you may not use this file
 * except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.openairinterface.org/?page_id=698
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *-------------------------------------------------------------------------------
 * For more information about the OpenAirInterface (OAI) Software Alliance:
 *      contact@openairinterface.org
 */

#ifndef __LAYER2_NR_MAC_GNB_NR_MAC_REDCAP_H__
#define __LAYER2_NR_MAC_GNB_NR_MAC_REDCAP_H__

#include <stdbool.h>

typedef enum {
  NR_REDCAP_CORESET0_MODE_CASE_A = 0,
  NR_REDCAP_CORESET0_MODE_CASE_B = 1,
} nr_redcap_coreset0_mode_t;

typedef enum {
  NR_REDCAP_RRC_IDLE = 0,
  NR_REDCAP_RRC_INACTIVE = 1,
  NR_REDCAP_RRC_CONNECTED = 2,
} nr_redcap_rrc_state_t;

/**
 * @brief Check whether the configured RedCap CORESET#0 mode is supported.
 *
 * @param[in] mode Requested CORESET#0 mode from configuration.
 *
 * @retval true The mode is supported by the current implementation.
 * @retval false The mode is outside the supported RedCap CORESET#0 modes.
 */
static inline bool nr_redcap_is_valid_coreset0_mode(int mode)
{
  return mode == NR_REDCAP_CORESET0_MODE_CASE_A || mode == NR_REDCAP_CORESET0_MODE_CASE_B;
}

/**
 * @brief Convert a RedCap CORESET#0 mode to a stable log string.
 *
 * @param[in] mode Requested CORESET#0 mode.
 *
 * @return Human-readable mode name for logs and test assertions.
 */
static inline const char *nr_redcap_coreset0_mode_to_string(nr_redcap_coreset0_mode_t mode)
{
  switch (mode) {
    case NR_REDCAP_CORESET0_MODE_CASE_A:
      return "case-a-full-cell";
    case NR_REDCAP_CORESET0_MODE_CASE_B:
      return "case-b-edge-only";
    default:
      return "unknown";
  }
}

static inline const char *nr_redcap_rrc_state_to_string(nr_redcap_rrc_state_t state)
{
  switch (state) {
    case NR_REDCAP_RRC_IDLE:
      return "idle";
    case NR_REDCAP_RRC_INACTIVE:
      return "inactive";
    case NR_REDCAP_RRC_CONNECTED:
      return "connected";
    default:
      return "unknown";
  }
}

/**
 * @brief Check whether a RedCap BWP touches the lower or upper cell edge.
 *
 * Case B requires the RedCap-specific initial DL BWP to be edge-aligned so that
 * the commonControlResourceSet can be interpreted as an edge-only CORESET#0.
 *
 * @param[in] bwp_start Start PRB of the BWP inside the cell carrier.
 * @param[in] bwp_size Size of the BWP in PRBs.
 * @param[in] carrier_bw Full carrier bandwidth in PRBs.
 *
 * @retval true The BWP is aligned with the lower or upper cell edge.
 * @retval false The BWP is internal to the carrier or invalid.
 */
static inline bool nr_redcap_is_edge_aligned_bwp(int bwp_start, int bwp_size, int carrier_bw)
{
  if (bwp_start < 0 || bwp_size <= 0 || carrier_bw <= 0 || bwp_start + bwp_size > carrier_bw)
    return false;

  return bwp_start == 0 || bwp_start + bwp_size == carrier_bw;
}

#endif
