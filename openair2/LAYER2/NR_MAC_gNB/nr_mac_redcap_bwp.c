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

#include "nr_mac_redcap_bwp.h"

#include "assertions.h"

#define NR_REDCAP_SCS_KHZ15_VALUE 0
#define NR_REDCAP_SCS_KHZ30_VALUE 1

/**
 * @brief Compute ASN.1 locationAndBandwidth for a RedCap initial BWP.
 *
 * RedCap initial BWPs in this project are encoded against the full FR1 carrier
 * grid represented by the standard 275-PRB RIV domain.
 *
 * @param[in] nprb BWP size in PRBs.
 * @param[in] rb_start BWP start PRB.
 *
 * @return Encoded locationAndBandwidth value.
 */
static int nr_redcap_location_and_bw(int nprb, int rb_start)
{
  const int bwp_size = 275;
  AssertFatal(nprb > 0 && (nprb + rb_start <= bwp_size),
              "Illegal NPRB/RBstart configuration (%d,%d) for RedCap initial BWP size %d\n",
              nprb,
              rb_start,
              bwp_size);

  if (nprb <= 1 + (bwp_size >> 1))
    return bwp_size * (nprb - 1) + rb_start;

  return bwp_size * (bwp_size + 1 - nprb) + (bwp_size - 1 - rb_start);
}

int nr_redcap_fr1_max_prbs_from_scs(long scs)
{
  switch (scs) {
    case NR_REDCAP_SCS_KHZ15_VALUE:
      return 106;
    case NR_REDCAP_SCS_KHZ30_VALUE:
      return 51;
    default:
      return -1;
  }
}

bool nr_redcap_initial_bwp_requested(int start, int size, int scs)
{
  return start >= 0 || size >= 0 || scs >= 0;
}

void nr_redcap_configure_initial_bwp(nr_redcap_bwp_config_t *cfg,
                                     const char *direction,
                                     int start,
                                     int size,
                                     int scs,
                                     int common_param_a,
                                     int common_param_b,
                                     int param_a,
                                     int param_b,
                                     int full_bw)
{
  AssertFatal(cfg != NULL, "RedCap %s initial BWP destination must not be NULL\n", direction);
  AssertFatal(start >= 0 && size > 0 && scs >= 0,
              "RedCap %s initial BWP requires start/size/scs to be configured together\n",
              direction);

  const int max_prbs = nr_redcap_fr1_max_prbs_from_scs(scs);
  AssertFatal(max_prbs > 0,
              "RedCap %s initial BWP only supports FR1 SCS 15/30 kHz in the current implementation (configured scs=%d)\n",
              direction,
              scs);
  AssertFatal(size <= max_prbs,
              "RedCap %s initial BWP size %d exceeds the FR1 20 MHz limit for scs=%d (max %d PRBs)\n",
              direction,
              size,
              scs,
              max_prbs);
  AssertFatal(start >= 0 && start + size <= full_bw,
              "RedCap %s initial BWP start=%d size=%d exceeds the configured common carrier bandwidth %d\n",
              direction,
              start,
              size,
              full_bw);

  *cfg = (nr_redcap_bwp_config_t){
      .configured = true,
      .scs = scs,
      .bwp_start = start,
      .bwp_size = size,
      .location_and_bw = nr_redcap_location_and_bw(size, start),
      .controlResourceSetZero = param_a >= 0 ? param_a : common_param_a,
      .searchSpaceZero = param_b >= 0 ? param_b : common_param_b,
      .pucch_ResourceCommonRedCap_r17 = param_a >= 0 ? param_a : common_param_a,
  };
}

void nr_redcap_validate_coreset0_dl_bwp(nr_redcap_coreset0_mode_t mode,
                                        const nr_redcap_bwp_config_t *dl_bwp,
                                        int carrier_bw)
{
  if (dl_bwp == NULL || !dl_bwp->configured || mode != NR_REDCAP_CORESET0_MODE_CASE_B)
    return;

  AssertFatal(nr_redcap_is_edge_aligned_bwp(dl_bwp->bwp_start, dl_bwp->bwp_size, carrier_bw),
              "RedCap CORESET#0 Case B requires an edge-aligned initial DL BWP, but start=%d size=%d carrier_bw=%d\n",
              dl_bwp->bwp_start,
              dl_bwp->bwp_size,
              carrier_bw);
}
