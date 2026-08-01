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

#ifndef __LAYER2_NR_MAC_UE_NR_UE_REDCAP_BWP_H__
#define __LAYER2_NR_MAC_UE_NR_UE_REDCAP_BWP_H__

#include <stdbool.h>

#include "NR_ServingCellConfigCommonSIB.h"

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Select the SIB1 downlink initial BWP to be used by the UE.
 *
 * For a Rel-17 RedCap UE, TS 38.331 allows the network to signal a dedicated
 * `initialDownlinkBWP-RedCap-r17`. When that IE is present, the UE shall use it
 * instead of the common `initialDownlinkBWP`.
 *
 * @param scc SIB1 servingCellConfigCommon container.
 * @param is_redcap_ue True when the local UE capability indicates RedCap.
 * @return Pointer to the selected initial downlink BWP. Never NULL when @p scc is valid.
 */
NR_BWP_DownlinkCommon_t *nr_ue_get_sib1_initial_dl_bwp(const NR_ServingCellConfigCommonSIB_t *scc, bool is_redcap_ue);

/**
 * @brief Select the SIB1 uplink initial BWP to be used by the UE.
 *
 * For a Rel-17 RedCap UE, TS 38.331 allows the network to signal a dedicated
 * `initialUplinkBWP-RedCap-r17`. When that IE is present, the UE shall use it
 * instead of the common `initialUplinkBWP`.
 *
 * @param scc SIB1 servingCellConfigCommon container.
 * @param is_redcap_ue True when the local UE capability indicates RedCap.
 * @return Pointer to the selected initial uplink BWP, or NULL when uplinkConfigCommon is absent.
 */
NR_BWP_UplinkCommon_t *nr_ue_get_sib1_initial_ul_bwp(const NR_ServingCellConfigCommonSIB_t *scc, bool is_redcap_ue);

#ifdef __cplusplus
}
#endif

#endif
