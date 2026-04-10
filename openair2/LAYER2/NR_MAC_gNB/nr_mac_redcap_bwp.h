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

#ifndef __LAYER2_NR_MAC_GNB_NR_MAC_REDCAP_BWP_H__
#define __LAYER2_NR_MAC_GNB_NR_MAC_REDCAP_BWP_H__

#include <stdbool.h>
#include "nr_mac_redcap.h"

typedef struct nr_redcap_bwp_config {
  bool configured;
  int scs;
  int bwp_start;
  int bwp_size;
  int location_and_bw;
  int controlResourceSetZero;
  int searchSpaceZero;
  int pucch_ResourceCommonRedCap_r17;
} nr_redcap_bwp_config_t;

/**
 * @brief Return the FR1 RedCap maximum PRB count for a given SCS.
 *
 * The current implementation supports the FR1 RedCap 20 MHz operating points
 * used by the project runtime assets: 106 PRBs for 15 kHz and 51 PRBs for
 * 30 kHz.
 *
 * @param[in] scs Subcarrier spacing encoded with NR ASN.1 values.
 *
 * @return Maximum PRB count for the supported SCS, or -1 for unsupported SCS.
 */
int nr_redcap_fr1_max_prbs_from_scs(long scs);

/**
 * @brief Check whether any RedCap initial BWP field was explicitly configured.
 *
 * @param[in] start Requested BWP start PRB.
 * @param[in] size Requested BWP size in PRBs.
 * @param[in] scs Requested BWP SCS.
 *
 * @retval true At least one field is configured and the caller must validate the triplet.
 * @retval false No RedCap initial BWP was requested.
 */
bool nr_redcap_initial_bwp_requested(int start, int size, int scs);

/**
 * @brief Validate and populate a RedCap initial BWP configuration.
 *
 * This helper centralizes the config-side validation used by the RedCap gNB
 * YAML path before the values are copied into the SIB1 build path.
 *
 * @param[out] cfg Destination RedCap BWP configuration.
 * @param[in] direction Log string indicating DL or UL.
 * @param[in] start Requested BWP start PRB.
 * @param[in] size Requested BWP size in PRBs.
 * @param[in] scs Requested BWP SCS.
 * @param[in] common_param_a Fallback value from the common BWP.
 * @param[in] common_param_b Secondary fallback value from the common BWP.
 * @param[in] param_a Explicit RedCap override for the first optional parameter.
 * @param[in] param_b Explicit RedCap override for the second optional parameter.
 * @param[in] full_bw Full carrier bandwidth in PRBs.
 */
void nr_redcap_configure_initial_bwp(nr_redcap_bwp_config_t *cfg,
                                     const char *direction,
                                     int start,
                                     int size,
                                     int scs,
                                     int common_param_a,
                                     int common_param_b,
                                     int param_a,
                                     int param_b,
                                     int full_bw);

/**
 * @brief Validate the RedCap initial DL BWP against the configured CORESET#0 mode.
 *
 * Case B requires the RedCap-specific initial DL BWP to be edge-aligned. The
 * parser invokes this helper so invalid YAML is rejected before the SIB1 build
 * stage.
 *
 * @param[in] mode Configured RedCap CORESET#0 mode.
 * @param[in] dl_bwp Parsed RedCap initial DL BWP.
 * @param[in] carrier_bw Full carrier bandwidth in PRBs.
 */
void nr_redcap_validate_coreset0_dl_bwp(nr_redcap_coreset0_mode_t mode,
                                        const nr_redcap_bwp_config_t *dl_bwp,
                                        int carrier_bw);

#endif
