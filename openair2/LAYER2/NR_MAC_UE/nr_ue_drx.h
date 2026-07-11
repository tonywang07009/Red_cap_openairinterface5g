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

#ifndef NR_UE_DRX_H
#define NR_UE_DRX_H

#include <stdbool.h>
#include <stdint.h>

#include "mac_defs.h"

uint64_t nr_ue_drx_absolute_slot(uint32_t slots_per_frame, frame_t frame, slot_t slot);
uint64_t nr_ue_drx_unwrap_slot(nr_drx_config_t *drx, uint32_t slots_per_frame, frame_t frame, slot_t slot);
bool nr_ue_drx_has_pending_sr(const NR_UE_SCHEDULING_INFO *sched_info);
bool nr_ue_drx_is_active_slot(nr_drx_config_t *drx, uint64_t absolute_slot, bool pending_sr);
bool nr_ue_drx_is_active(NR_UE_MAC_INST_t *mac, frame_t frame, slot_t slot);
void nr_ue_drx_get_metrics(NR_UE_SCHEDULING_INFO *sched_info,
                           bool reset,
                           uint32_t *observed_slots,
                           uint32_t *active_slots);
void nr_ue_drx_on_dl_assignment(NR_UE_MAC_INST_t *mac,
                                frame_t frame,
                                slot_t slot,
                                uint8_t harq_pid,
                                bool new_transmission);
void nr_ue_drx_on_ul_assignment(NR_UE_MAC_INST_t *mac,
                                frame_t frame,
                                slot_t slot,
                                uint8_t harq_pid,
                                bool new_transmission);
void nr_ue_drx_on_dl_harq_feedback(NR_UE_MAC_INST_t *mac,
                                   frame_t frame,
                                   slot_t slot,
                                   uint8_t harq_pid,
                                   bool acknowledged);
void nr_ue_drx_on_ul_harq_transmission(NR_UE_MAC_INST_t *mac, frame_t frame, slot_t slot, uint8_t harq_pid);
void nr_ue_drx_on_command(NR_UE_MAC_INST_t *mac, frame_t frame, slot_t slot, bool long_cycle_command);

#endif
