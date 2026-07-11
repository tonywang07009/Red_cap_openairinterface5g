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

uint64_t nr_ue_drx_unwrap_slot(nr_drx_config_t *drx, uint32_t slots_per_frame, frame_t frame, slot_t slot)
{
  const uint64_t raw_slot = nr_ue_drx_absolute_slot(slots_per_frame, frame, slot);
  if (!drx->clock_initialized) {
    drx->clock_initialized = true;
    drx->last_absolute_slot = raw_slot;
    return raw_slot;
  }

  const uint64_t sfn_span = (uint64_t)MAX_FRAME_NUMBER * slots_per_frame;
  const uint64_t last_raw_slot = drx->last_absolute_slot % sfn_span;
  const uint64_t forward = (raw_slot + sfn_span - last_raw_slot) % sfn_span;
  uint64_t absolute_slot;
  if (forward <= sfn_span / 2) {
    absolute_slot = drx->last_absolute_slot + forward;
  } else {
    const uint64_t backward = sfn_span - forward;
    absolute_slot = backward <= drx->last_absolute_slot ? drx->last_absolute_slot - backward : raw_slot;
  }

  if (absolute_slot > drx->last_absolute_slot)
    drx->last_absolute_slot = absolute_slot;
  return absolute_slot;
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

static uint64_t nr_ue_drx_first_cycle_start(const nr_drx_config_t *drx, uint64_t from_slot, uint64_t cycle)
{
  if (!cycle)
    return from_slot;
  const uint64_t offset = (drx->long_cycle_offset_slots + drx->slot_offset) % cycle;
  const uint64_t phase = (from_slot + cycle - offset) % cycle;
  return from_slot + (cycle - phase) % cycle;
}

static void nr_ue_drx_update_short_cycle(nr_drx_config_t *drx, uint64_t absolute_slot)
{
  if (!drx->short_cycle_configured) {
    drx->short_cycle_active = false;
    drx->short_cycle_pending = false;
    return;
  }

  if (drx->short_cycle_pending && absolute_slot >= drx->short_cycle_pending_start_slot) {
    if (drx->short_cycle_active && drx->short_cycle_pending_start_slot < drx->short_cycle_until_slot) {
      if (drx->short_cycle_pending_until_slot > drx->short_cycle_until_slot)
        drx->short_cycle_until_slot = drx->short_cycle_pending_until_slot;
    } else if (absolute_slot < drx->short_cycle_pending_until_slot) {
      drx->short_cycle_active = true;
      drx->short_cycle_until_slot = drx->short_cycle_pending_until_slot;
      drx->monitor_cycle_from_slot =
          nr_ue_drx_first_cycle_start(drx, drx->short_cycle_pending_start_slot, drx->short_cycle_slots);
    } else {
      drx->short_cycle_active = false;
      drx->short_cycle_until_slot = 0;
      drx->monitor_cycle_from_slot =
          nr_ue_drx_first_cycle_start(drx, drx->short_cycle_pending_until_slot, drx->long_cycle_slots);
    }
    drx->short_cycle_pending = false;
  }

  if (drx->short_cycle_active && absolute_slot >= drx->short_cycle_until_slot) {
    const uint64_t transition_slot = drx->short_cycle_until_slot;
    drx->short_cycle_active = false;
    drx->short_cycle_until_slot = 0;
    drx->monitor_cycle_from_slot = nr_ue_drx_first_cycle_start(drx, transition_slot, drx->long_cycle_slots);
  }
}

static bool nr_ue_drx_harq_is_active(const nr_drx_harq_timer_t *timer, uint64_t absolute_slot)
{
  return timer->rtt_until_slot < timer->retransmission_until_slot && absolute_slot >= timer->rtt_until_slot
         && absolute_slot < timer->retransmission_until_slot;
}

bool nr_ue_drx_is_active_slot(nr_drx_config_t *drx, uint64_t absolute_slot, bool pending_sr)
{
  if (!drx->configured)
    return true;

  nr_ue_drx_update_short_cycle(drx, absolute_slot);

  if (pending_sr)
    return true;
  if (drx->active_until_slot > absolute_slot)
    return true;

  for (int i = 0; i < NR_MAX_HARQ_PROCESSES; i++) {
    if (nr_ue_drx_harq_is_active(&drx->dl_harq[i], absolute_slot)
        || nr_ue_drx_harq_is_active(&drx->ul_harq[i], absolute_slot))
      return true;
  }

  const uint64_t cycle = drx->short_cycle_active ? drx->short_cycle_slots : drx->long_cycle_slots;
  if (!cycle || !drx->on_duration_slots)
    return true;
  if (absolute_slot < drx->monitor_cycle_from_slot)
    return false;

  const uint64_t start_offset = (drx->long_cycle_offset_slots + drx->slot_offset) % cycle;
  const uint64_t cycle_slot = (absolute_slot + cycle - start_offset) % cycle;
  return cycle_slot < drx->on_duration_slots;
}

bool nr_ue_drx_is_active(NR_UE_MAC_INST_t *mac, frame_t frame, slot_t slot)
{
  NR_UE_SCHEDULING_INFO *sched_info = &mac->scheduling_info;
  nr_drx_config_t *drx = &sched_info->drx_config;
  const uint32_t slots_per_frame = mac->frame_structure.numb_slots_frame;
  if (!slots_per_frame)
    return true;

  const uint64_t absolute_slot = nr_ue_drx_unwrap_slot(drx, slots_per_frame, frame, slot);
  const bool active = mac->ra.contention_resolution_timer.active || mac->ra.response_window_timer.active
                      || nr_ue_drx_is_active_slot(drx, absolute_slot, nr_ue_drx_has_pending_sr(sched_info));
  if (drx->configured)
    __atomic_add_fetch(&sched_info->drx_slot_counts, 1ULL | ((uint64_t)active << 32), __ATOMIC_RELAXED);
  return active;
}

void nr_ue_drx_get_metrics(NR_UE_SCHEDULING_INFO *sched_info,
                           bool reset,
                           uint32_t *observed_slots,
                           uint32_t *active_slots)
{
  const uint64_t counts = reset ? __atomic_exchange_n(&sched_info->drx_slot_counts, 0, __ATOMIC_RELAXED)
                                : __atomic_load_n(&sched_info->drx_slot_counts, __ATOMIC_RELAXED);
  *observed_slots = (uint32_t)counts;
  *active_slots = (uint32_t)(counts >> 32);
}

static void nr_ue_drx_schedule_short_cycle(nr_drx_config_t *drx)
{
  if (!drx->short_cycle_configured || !drx->short_cycle_slots || !drx->short_cycle_timer) {
    drx->short_cycle_pending = false;
    return;
  }

  drx->short_cycle_pending = true;
  drx->short_cycle_pending_start_slot = drx->active_until_slot;
  drx->short_cycle_pending_until_slot =
      drx->short_cycle_pending_start_slot + (uint64_t)drx->short_cycle_timer * drx->short_cycle_slots;
}

static uint64_t nr_ue_drx_event_slot(NR_UE_MAC_INST_t *mac, frame_t frame, slot_t slot)
{
  const uint32_t slots_per_frame = mac->frame_structure.numb_slots_frame;
  return nr_ue_drx_unwrap_slot(&mac->scheduling_info.drx_config, slots_per_frame, frame, slot);
}

static void nr_ue_drx_on_assignment(NR_UE_MAC_INST_t *mac,
                                    frame_t frame,
                                    slot_t slot,
                                    uint8_t harq_pid,
                                    bool new_transmission,
                                    bool downlink)
{
  nr_drx_config_t *drx = &mac->scheduling_info.drx_config;
  if (!drx->configured || !mac->frame_structure.numb_slots_frame || harq_pid >= NR_MAX_HARQ_PROCESSES)
    return;

  const uint64_t absolute_slot = nr_ue_drx_event_slot(mac, frame, slot);
  nr_ue_drx_update_short_cycle(drx, absolute_slot);
  nr_drx_harq_timer_t *harq = downlink ? &drx->dl_harq[harq_pid] : &drx->ul_harq[harq_pid];
  *harq = (nr_drx_harq_timer_t){0};
  if (!new_transmission)
    return;

  drx->active_until_slot = absolute_slot + 1 + drx->inactivity_slots;
  nr_ue_drx_schedule_short_cycle(drx);
}

void nr_ue_drx_on_dl_assignment(NR_UE_MAC_INST_t *mac,
                                frame_t frame,
                                slot_t slot,
                                uint8_t harq_pid,
                                bool new_transmission)
{
  nr_ue_drx_on_assignment(mac, frame, slot, harq_pid, new_transmission, true);
}

void nr_ue_drx_on_ul_assignment(NR_UE_MAC_INST_t *mac,
                                frame_t frame,
                                slot_t slot,
                                uint8_t harq_pid,
                                bool new_transmission)
{
  nr_ue_drx_on_assignment(mac, frame, slot, harq_pid, new_transmission, false);
}

void nr_ue_drx_on_dl_harq_feedback(NR_UE_MAC_INST_t *mac,
                                   frame_t frame,
                                   slot_t slot,
                                   uint8_t harq_pid,
                                   bool acknowledged)
{
  nr_drx_config_t *drx = &mac->scheduling_info.drx_config;
  if (!drx->configured || !mac->frame_structure.numb_slots_frame || harq_pid >= NR_MAX_HARQ_PROCESSES)
    return;

  const uint64_t absolute_slot = nr_ue_drx_event_slot(mac, frame, slot);
  nr_drx_harq_timer_t *harq = &drx->dl_harq[harq_pid];
  *harq = (nr_drx_harq_timer_t){0};
  if (acknowledged)
    return;

  harq->rtt_until_slot = absolute_slot + 1 + drx->harq_rtt_dl_slots;
  harq->retransmission_until_slot = harq->rtt_until_slot + drx->retransmission_dl_slots;
}

void nr_ue_drx_on_ul_harq_transmission(NR_UE_MAC_INST_t *mac, frame_t frame, slot_t slot, uint8_t harq_pid)
{
  nr_drx_config_t *drx = &mac->scheduling_info.drx_config;
  if (!drx->configured || !mac->frame_structure.numb_slots_frame || harq_pid >= NR_MAX_HARQ_PROCESSES)
    return;

  const uint64_t absolute_slot = nr_ue_drx_event_slot(mac, frame, slot);
  nr_drx_harq_timer_t *harq = &drx->ul_harq[harq_pid];
  harq->rtt_until_slot = absolute_slot + 1 + drx->harq_rtt_ul_slots;
  harq->retransmission_until_slot = harq->rtt_until_slot + drx->retransmission_ul_slots;
}

void nr_ue_drx_on_command(NR_UE_MAC_INST_t *mac, frame_t frame, slot_t slot, bool long_cycle_command)
{
  nr_drx_config_t *drx = &mac->scheduling_info.drx_config;
  if (!drx->configured || !mac->frame_structure.numb_slots_frame)
    return;

  const uint64_t absolute_slot = nr_ue_drx_event_slot(mac, frame, slot);
  nr_ue_drx_update_short_cycle(drx, absolute_slot);
  drx->active_until_slot = 0;
  drx->short_cycle_pending = false;
  const uint64_t transition_slot = absolute_slot + 1;

  if (!long_cycle_command && drx->short_cycle_configured && drx->short_cycle_slots && drx->short_cycle_timer) {
    drx->short_cycle_active = true;
    drx->short_cycle_until_slot = transition_slot + (uint64_t)drx->short_cycle_timer * drx->short_cycle_slots;
    drx->monitor_cycle_from_slot = nr_ue_drx_first_cycle_start(drx, transition_slot, drx->short_cycle_slots);
  } else {
    drx->short_cycle_active = false;
    drx->short_cycle_until_slot = 0;
    drx->monitor_cycle_from_slot = nr_ue_drx_first_cycle_start(drx, transition_slot, drx->long_cycle_slots);
  }
}
