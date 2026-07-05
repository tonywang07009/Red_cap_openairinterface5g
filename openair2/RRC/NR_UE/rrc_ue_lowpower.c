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
 */

#include "rrc_ue_lowpower.h"

void nr_rrc_apply_sib1_edrx(NR_UE_RRC_SI_INFO *si_info, const NR_SIB1_v1700_IEs_t *sib1_v1700)
{
  si_info->edrx_allowed_idle_r17 = sib1_v1700 && sib1_v1700->eDRX_AllowedIdle_r17;
  si_info->edrx_allowed_inactive_r17 = sib1_v1700 && sib1_v1700->eDRX_AllowedInactive_r17;
}

bool nr_rrc_edrx_allowed_for_state(const NR_UE_RRC_SI_INFO *si_info, Rrc_State_NR_t state)
{
  switch (state) {
    case RRC_STATE_IDLE_NR:
      return si_info->edrx_allowed_idle_r17;
    case RRC_STATE_INACTIVE_NR:
      return si_info->edrx_allowed_inactive_r17;
    default:
      return false;
  }
}
