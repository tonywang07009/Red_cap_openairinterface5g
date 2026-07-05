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

#include "nr_ue_drx.h"

uint64_t nr_ue_drx_absolute_slot(uint32_t slots_per_frame, frame_t frame, slot_t slot)
{
  return (uint64_t)frame * slots_per_frame + slot;
}

bool nr_ue_drx_has_pending_sr(const NR_UE_SCHEDULING_INFO *sched_info)
{
  for (int i = 0; i < NR_MAX_SR_ID; i++) {
    const nr_sr_info_t *sr = &sched_info->sr_info[i];
    if (sr->active_SR_ID && sr->pending)
      return true;
  }
  return false;
}

bool nr_ue_drx_is_active_slot(const nr_drx_config_t *drx, uint64_t absolute_slot, bool pending_sr)
{
  if (!drx->configured)
    return true;

  if (pending_sr)
    return true;

  if (drx->active_until_slot > absolute_slot)
    return true;

  if (!drx->long_cycle_slots || !drx->on_duration_slots)
    return true;

  const uint64_t cycle = drx->long_cycle_slots;
  const uint64_t start_offset = (drx->long_cycle_offset_slots + drx->slot_offset) % cycle;
  const uint64_t cycle_slot = (absolute_slot + cycle - start_offset) % cycle;
  return cycle_slot < drx->on_duration_slots;
}

bool nr_ue_drx_is_active(const NR_UE_MAC_INST_t *mac, frame_t frame, slot_t slot)
{
  const NR_UE_SCHEDULING_INFO *sched_info = &mac->scheduling_info;
  const uint32_t slots_per_frame = mac->frame_structure.numb_slots_frame;
  if (!slots_per_frame)
    return true;

  const uint64_t absolute_slot = nr_ue_drx_absolute_slot(slots_per_frame, frame, slot);
  return nr_ue_drx_is_active_slot(&sched_info->drx_config, absolute_slot, nr_ue_drx_has_pending_sr(sched_info));
}

void nr_ue_drx_note_activity(NR_UE_MAC_INST_t *mac, frame_t frame, slot_t slot)
{
  nr_drx_config_t *drx = &mac->scheduling_info.drx_config;
  const uint32_t slots_per_frame = mac->frame_structure.numb_slots_frame;
  if (!drx->configured || !slots_per_frame || !drx->inactivity_slots)
    return;

  const uint64_t absolute_slot = nr_ue_drx_absolute_slot(slots_per_frame, frame, slot);
  drx->active_until_slot = absolute_slot + drx->inactivity_slots;
}
