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
#include <openair3/UICC/usim_interface.h>

#define NR_REDCAP_SECTION "nrue_recap"

#define NR_REDCAP_CFG_PARAMS_DESC { \
      {"enable",                      "Enable RedCap capability injection from YAML\n", 0, .iptr=&cfg->enabled,                         .defintval=0,  TYPE_INT, 0 }, \
      {"band",                        "NR band for supportedBandListNR\n",               0, .iptr=&cfg->band,                            .defintval=78, TYPE_INT, 0 }, \
      {"support_of_redcap_r17",       "Advertise supportOfRedCap-r17\n",                 0, .iptr=&cfg->support_of_redcap_r17,           .defintval=1,  TYPE_INT, 0 }, \
      {"support_of_16drb_redcap_r17", "Advertise supportOf16DRB-RedCap-r17\n",           0, .iptr=&cfg->support_of_16drb_redcap_r17,     .defintval=0,  TYPE_INT, 0 }, \
      {"pdcp_drb_long_sn_redcap_r17", "Advertise longSN_RedCap-r17\n",                   0, .iptr=&cfg->pdcp_drb_long_sn_redcap_r17,     .defintval=0,  TYPE_INT, 0 }, \
      {"rlc_am_drb_long_sn_redcap_r17", "Advertise am-WithLongSN-RedCap-r17\n",          0, .iptr=&cfg->rlc_am_drb_long_sn_redcap_r17,   .defintval=0,  TYPE_INT, 0 }, \
      {"number_of_rx_redcap_r17",     "UE-side RedCap Rx branch count used for SIB1 barring checks\n", 0, .iptr=&cfg->number_of_rx_redcap_r17, .defintval=1, TYPE_INT, 0 }, \
      {"half_duplex_fdd_type_a_redcap_r17", "UE-side half-duplex FDD Type A support used for SIB1 barring checks\n", 0, .iptr=&cfg->half_duplex_fdd_type_a_redcap_r17, .defintval=0, TYPE_INT, 0 }, \
      {"pusch_256qam",                "Advertise UE PUSCH 256QAM support in supportedBandListNR\n", 0, .iptr=&cfg->pusch_256qam, .defintval=0, TYPE_INT, 0 }, \
      {"pdsch_256qam",                "Advertise UE PDSCH 256QAM support for FR1\n", 0, .iptr=&cfg->pdsch_256qam, .defintval=0, TYPE_INT, 0 }, \
  };

bool load_nr_redcap_config(const char *sectionName, nr_redcap_cfg_t *cfg)
{
  AssertFatal(cfg != NULL, "nr_redcap_cfg_t must not be NULL\n");
  *cfg = (nr_redcap_cfg_t){0};
  paramdef_t redcap_params[] = NR_REDCAP_CFG_PARAMS_DESC;
  const char *cfg_section = sectionName ? sectionName : NR_REDCAP_SECTION;
  int ret = config_get(config_get_if(), redcap_params, sizeofArray(redcap_params), cfg_section);
  AssertFatal(ret >= 0, "configuration couldn't be performed for nrue_recap name: %s", cfg_section);
  if (!cfg->enabled)
    return false;

  if (cfg->band <= 0) {
    LOG_W(SIM, "nrue_recap.band=%d is invalid, using default band 78\n", cfg->band);
    cfg->band = 78;
  }
  if (cfg->number_of_rx_redcap_r17 < 1 || cfg->number_of_rx_redcap_r17 > 2) {
    LOG_W(SIM, "nrue_recap.number_of_rx_redcap_r17=%d is invalid, using 1\n", cfg->number_of_rx_redcap_r17);
    cfg->number_of_rx_redcap_r17 = 1;
  }

  LOG_I(SIM,
        "nrue_recap RedCap config: band=n%d RedCap=%d 16DRB=%d PDCP_longSN=%d RLC_AM_longSN=%d Rx=%d halfDuplexFDD-TypeA=%d PUSCH256QAM=%d PDSCH256QAM=%d\n",
        cfg->band,
        cfg->support_of_redcap_r17,
        cfg->support_of_16drb_redcap_r17,
        cfg->pdcp_drb_long_sn_redcap_r17,
        cfg->rlc_am_drb_long_sn_redcap_r17,
        cfg->number_of_rx_redcap_r17,
        cfg->half_duplex_fdd_type_a_redcap_r17,
        cfg->pusch_256qam,
        cfg->pdsch_256qam);
  return true;
}
