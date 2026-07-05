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
#include <stdint.h>

typedef enum {
  NR_REDCAP_CORESET0_MODE_CASE_A = 0,
  NR_REDCAP_CORESET0_MODE_CASE_B = 1,
} nr_redcap_coreset0_mode_t;

typedef enum {
  NR_REDCAP_RRC_IDLE = 0,
  NR_REDCAP_RRC_INACTIVE = 1,
  NR_REDCAP_RRC_CONNECTED = 2,
} nr_redcap_rrc_state_t;

#define NR_REDCAP_HD_FDD_MIN_RXTXTIME 6
#define NR_REDCAP_UL_PRB_CAP_DISABLED 0

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
 * @brief Clamp the effective scheduler DL/UL switching gap for RedCap HD-FDD.
 *
 * The current project plan uses [6 slots] as the local HD-FDD Type A
 * scheduling assumption for RedCap. When the cell explicitly allows
 * [halfDuplexRedCapAllowed-r17], the gNB shall not schedule with a smaller
 * [minRXTXTIME] than this project-level assumption.
 *
 * @param half_duplex_redcap_allowed True when the RedCap SIB1/config path allows HD-FDD UEs.
 * @param configured_min_rxtxtime Scheduler minRXTXTIME requested by configuration.
 *
 * @return Effective minRXTXTIME after applying the RedCap HD-FDD floor.
 */
static inline int nr_redcap_effective_min_rxtxtime(bool half_duplex_redcap_allowed, int configured_min_rxtxtime)
{
  if (!half_duplex_redcap_allowed)
    return configured_min_rxtxtime;

  return configured_min_rxtxtime >= NR_REDCAP_HD_FDD_MIN_RXTXTIME ? configured_min_rxtxtime : NR_REDCAP_HD_FDD_MIN_RXTXTIME;
}

/**
 * @brief Sanitize a runtime UL PRB cap received for a specific UE.
 *
 * A value of [0] disables the runtime cap. Any non-zero cap smaller than the
 * scheduler minimum grant is rounded up so the scheduler can still allocate a
 * valid PUSCH grant.
 *
 * @param requested_cap Requested runtime UL PRB cap.
 * @param min_grant_prb Minimum valid UL grant size for the cell.
 *
 * @return Effective stored UL PRB cap, or [0] when disabled.
 */
static inline uint16_t nr_redcap_sanitize_ul_prb_cap(uint16_t requested_cap, uint16_t min_grant_prb)
{
  if (requested_cap == NR_REDCAP_UL_PRB_CAP_DISABLED)
    return NR_REDCAP_UL_PRB_CAP_DISABLED;

  return requested_cap < min_grant_prb ? min_grant_prb : requested_cap;
}

/**
 * @brief Clamp a requested UL RB allocation with an optional RedCap runtime cap.
 *
 * @param requested_rb Requested RB allocation before RedCap runtime control.
 * @param configured_cap Stored runtime cap for the UE. [0] disables the cap.
 * @param min_grant_prb Minimum valid UL grant size for the cell.
 *
 * @return Effective RB allocation upper bound after RedCap runtime control.
 */
static inline uint16_t nr_redcap_effective_ul_prb_cap(uint16_t requested_rb, uint16_t configured_cap, uint16_t min_grant_prb)
{
  const uint16_t effective_cap = nr_redcap_sanitize_ul_prb_cap(configured_cap, min_grant_prb);
  if (effective_cap == NR_REDCAP_UL_PRB_CAP_DISABLED || requested_rb <= effective_cap)
    return requested_rb;

  return effective_cap;
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
