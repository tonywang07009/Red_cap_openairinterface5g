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

#include "nr_ue_redcap_bwp.h"

NR_BWP_DownlinkCommon_t *nr_ue_get_sib1_initial_dl_bwp(const NR_ServingCellConfigCommonSIB_t *scc, bool is_redcap_ue)
{
  if (is_redcap_ue && scc->downlinkConfigCommon.ext1 && scc->downlinkConfigCommon.ext1->initialDownlinkBWP_RedCap_r17)
    return scc->downlinkConfigCommon.ext1->initialDownlinkBWP_RedCap_r17;
  return (NR_BWP_DownlinkCommon_t *)&scc->downlinkConfigCommon.initialDownlinkBWP;
}

NR_BWP_UplinkCommon_t *nr_ue_get_sib1_initial_ul_bwp(const NR_ServingCellConfigCommonSIB_t *scc, bool is_redcap_ue)
{
  if (scc->uplinkConfigCommon == NULL)
    return NULL;
  if (is_redcap_ue && scc->ext2 && scc->ext2->uplinkConfigCommon_v1700
      && scc->ext2->uplinkConfigCommon_v1700->initialUplinkBWP_RedCap_r17)
    return scc->ext2->uplinkConfigCommon_v1700->initialUplinkBWP_RedCap_r17;
  return &scc->uplinkConfigCommon->initialUplinkBWP;
}
