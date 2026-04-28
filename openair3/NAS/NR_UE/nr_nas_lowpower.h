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

#ifndef NR_NAS_LOWPOWER_H
#define NR_NAS_LOWPOWER_H

#include <stdbool.h>

#include "nr_nas_msg.h"

void nr_nas_psm_init(nr_ue_nas_t *nas);
void nr_nas_psm_update_timers(nr_ue_nas_t *nas, int t3324, int t3512);
void nr_nas_psm_mark_active_time_expired(nr_ue_nas_t *nas);
bool nr_nas_psm_low_power_ready(const nr_ue_nas_t *nas);

#endif
