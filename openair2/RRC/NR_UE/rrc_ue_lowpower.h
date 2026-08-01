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

#ifndef RRC_UE_LOWPOWER_H
#define RRC_UE_LOWPOWER_H

#include <stdbool.h>

#include "rrc_defs.h"
#include "NR_SIB1-v1700-IEs.h"

void nr_rrc_apply_sib1_edrx(NR_UE_RRC_SI_INFO *si_info, const NR_SIB1_v1700_IEs_t *sib1_v1700);
bool nr_rrc_edrx_allowed_for_state(const NR_UE_RRC_SI_INFO *si_info, Rrc_State_NR_t state);

#endif
