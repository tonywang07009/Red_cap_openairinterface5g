/*
 * Licensed to the OpenAirInterface (OAI) Software Alliance under one or more
 * contributor license agreements. See the NOTICE file distributed with this
 * work for additional information regarding copyright ownership.
 */

#include "nr_mac_drx.h"

#include <stddef.h>

static bool approved_profile(uint32_t cycle_ms, uint32_t on_duration_ms)
{
  static const struct {
    uint32_t cycle_ms;
    uint32_t on_duration_ms;
  } profiles[] = {
      {320, 10}, {640, 10}, {1280, 20}, {2560, 20}, {5120, 40}, {10240, 40},
  };

  for (size_t i = 0; i < sizeof(profiles) / sizeof(profiles[0]); ++i) {
    if (profiles[i].cycle_ms == cycle_ms && profiles[i].on_duration_ms == on_duration_ms)
      return true;
  }
  return false;
}

static bool update_clock(nr_gnb_drx_state_t *state, uint16_t frame, uint16_t slot, uint16_t slots_per_frame)
{
  if (state == NULL || slots_per_frame == 0 || frame >= NR_GNB_DRX_SFN_MODULUS || slot >= slots_per_frame)
    return false;

  const uint32_t period_slots = NR_GNB_DRX_SFN_MODULUS * slots_per_frame;
  const uint32_t current_mod_slot = (uint32_t)frame * slots_per_frame + slot;
  if (!state->clock_initialized) {
    state->clock_initialized = true;
    state->last_mod_slot = current_mod_slot;
    state->absolute_slot = current_mod_slot;
    return true;
  }

  const uint32_t delta = (current_mod_slot + period_slots - state->last_mod_slot) % period_slots;
  state->absolute_slot += delta;
  state->last_mod_slot = current_mod_slot;
  return true;
}

bool nr_gnb_drx_profile_is_valid(const nr_gnb_drx_profile_t *profile)
{
  if (profile == NULL || profile->inactivity_ms != 20)
    return false;
  if (!approved_profile(profile->long_cycle_ms, profile->on_duration_ms))
    return false;
  return profile->start_offset_ms < profile->long_cycle_ms;
}

bool nr_gnb_drx_stage_profile(nr_gnb_drx_state_t *state, const nr_gnb_drx_profile_t *profile)
{
  if (state == NULL || !nr_gnb_drx_profile_is_valid(profile))
    return false;
  if (state->rrc_completion_pending)
    return false;
  if ((state->configured || state->pending_config_valid) && profile->policy_version <= state->latest_policy_version)
    return false;

  state->pending = *profile;
  state->pending_config_valid = true;
  state->rrc_completion_pending = true;
  state->latest_policy_version = profile->policy_version;
  return true;
}

bool nr_gnb_drx_commit_profile(nr_gnb_drx_state_t *state,
                               uint16_t frame,
                               uint16_t slot,
                               uint16_t slots_per_frame)
{
  if (state == NULL || !state->pending_config_valid || slots_per_frame == 0 || slots_per_frame % 10 != 0)
    return false;
  if (!update_clock(state, frame, slot, slots_per_frame))
    return false;

  const uint32_t slots_per_ms = slots_per_frame / 10;
  if (state->configured) {
    state->previous = state->applied;
    state->previous_config_valid = true;
  }
  state->applied = state->pending;
  state->long_cycle_slots = state->applied.long_cycle_ms * slots_per_ms;
  state->on_duration_slots = state->applied.on_duration_ms * slots_per_ms;
  state->inactivity_slots = state->applied.inactivity_ms * slots_per_ms;
  state->start_offset_slots = state->applied.start_offset_ms * slots_per_ms;
  state->configured = true;
  state->pending_config_valid = false;
  state->drx_command_requested = false;
  state->drx_command_pending = false;
  state->active_until_slot = 0;
  return true;
}

void nr_gnb_drx_cancel_pending(nr_gnb_drx_state_t *state)
{
  if (state == NULL)
    return;
  state->pending_config_valid = false;
  state->rrc_completion_pending = false;
}

bool nr_gnb_drx_complete_reconfiguration(nr_gnb_drx_state_t *state)
{
  if (state == NULL || !state->rrc_completion_pending || state->pending_config_valid)
    return false;
  state->rrc_completion_pending = false;
  return true;
}

bool nr_gnb_drx_fail_reconfiguration(nr_gnb_drx_state_t *state, uint16_t slots_per_frame)
{
  if (state == NULL || !state->rrc_completion_pending || slots_per_frame == 0 || slots_per_frame % 10 != 0)
    return false;

  if (state->pending_config_valid) {
    state->pending_config_valid = false;
  } else if (state->previous_config_valid) {
    const uint32_t slots_per_ms = slots_per_frame / 10;
    state->applied = state->previous;
    state->long_cycle_slots = state->applied.long_cycle_ms * slots_per_ms;
    state->on_duration_slots = state->applied.on_duration_ms * slots_per_ms;
    state->inactivity_slots = state->applied.inactivity_ms * slots_per_ms;
    state->start_offset_slots = state->applied.start_offset_ms * slots_per_ms;
    state->previous_config_valid = false;
  } else {
    return false;
  }

  state->rrc_completion_pending = false;
  state->drx_command_requested = false;
  state->drx_command_pending = false;
  state->active_until_slot = 0;
  return true;
}

bool nr_gnb_drx_is_active(nr_gnb_drx_state_t *state,
                          uint16_t frame,
                          uint16_t slot,
                          uint16_t slots_per_frame,
                          bool scheduling_request_pending,
                          bool retransmission_pending)
{
  if (state == NULL)
    return true;
  if (!update_clock(state, frame, slot, slots_per_frame))
    return false;
  if (!state->configured)
    return true;
  if (scheduling_request_pending || retransmission_pending || state->absolute_slot < state->active_until_slot)
    return true;

  const uint64_t cycle_position =
      (state->absolute_slot + state->long_cycle_slots - state->start_offset_slots) % state->long_cycle_slots;
  return cycle_position < state->on_duration_slots;
}

void nr_gnb_drx_note_new_transmission(nr_gnb_drx_state_t *state,
                                      uint16_t frame,
                                      uint16_t slot,
                                      uint16_t slots_per_frame)
{
  if (state == NULL || !state->configured || !update_clock(state, frame, slot, slots_per_frame))
    return;
  state->active_until_slot = state->absolute_slot + 1 + state->inactivity_slots;
}

void nr_gnb_drx_note_dl_ack(nr_gnb_drx_state_t *state)
{
  if (state == NULL || !state->configured || state->rrc_completion_pending || !state->applied.drx_command_enabled
      || !state->drx_command_requested)
    return;
  if (state->absolute_slot < state->active_until_slot) {
    state->drx_command_requested = false;
    state->drx_command_pending = true;
  }
}

bool nr_gnb_drx_request_command(nr_gnb_drx_state_t *state)
{
  if (state == NULL || !state->configured || state->rrc_completion_pending || !state->applied.drx_command_enabled
      || state->drx_command_requested || state->drx_command_pending)
    return false;
  state->drx_command_requested = true;
  return true;
}

bool nr_gnb_drx_command_ready(const nr_gnb_drx_state_t *state,
                              bool scheduling_request_pending,
                              bool retransmission_pending,
                              bool queues_empty)
{
  return state != NULL && state->configured && !state->rrc_completion_pending && state->applied.drx_command_enabled
         && state->drx_command_pending
         && !scheduling_request_pending && !retransmission_pending && queues_empty
         && state->absolute_slot < state->active_until_slot;
}

bool nr_gnb_drx_take_command(nr_gnb_drx_state_t *state,
                             bool scheduling_request_pending,
                             bool retransmission_pending,
                             bool queues_empty)
{
  if (!nr_gnb_drx_command_ready(state, scheduling_request_pending, retransmission_pending, queues_empty))
    return false;
  state->drx_command_pending = false;
  state->active_until_slot = state->absolute_slot;
  return true;
}
