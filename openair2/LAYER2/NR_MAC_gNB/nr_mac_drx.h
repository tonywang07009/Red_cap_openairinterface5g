/*
 * Licensed to the OpenAirInterface (OAI) Software Alliance under one or more
 * contributor license agreements. See the NOTICE file distributed with this
 * work for additional information regarding copyright ownership.
 */

#ifndef __LAYER2_NR_MAC_GNB_NR_MAC_DRX_H__
#define __LAYER2_NR_MAC_GNB_NR_MAC_DRX_H__

#include <stdbool.h>
#include <stdint.h>

#define NR_GNB_DRX_SFN_MODULUS 1024U
#define NR_GNB_DRX_MAX_HARQ_PROCESSES 16U

typedef struct {
  uint64_t rtt_until_slot;
  uint64_t retransmission_until_slot;
} nr_gnb_drx_harq_timer_t;

typedef struct {
  uint32_t policy_version;
  uint32_t long_cycle_ms;
  uint32_t on_duration_ms;
  uint32_t inactivity_ms;
  uint32_t start_offset_ms;
  bool drx_command_enabled;
} nr_gnb_drx_profile_t;

typedef struct {
  bool configured;
  bool clock_initialized;
  bool pending_config_valid;
  bool previous_config_valid;
  bool rrc_completion_pending;
  bool drx_command_requested;
  bool drx_command_pending;
  uint32_t latest_policy_version;
  uint32_t last_mod_slot;
  uint64_t absolute_slot;
  uint64_t active_until_slot;
  uint32_t long_cycle_slots;
  uint32_t on_duration_slots;
  uint32_t inactivity_slots;
  uint32_t start_offset_slots;
  nr_gnb_drx_profile_t applied;
  nr_gnb_drx_profile_t previous;
  nr_gnb_drx_profile_t pending;
  nr_gnb_drx_harq_timer_t dl_harq[NR_GNB_DRX_MAX_HARQ_PROCESSES];
  nr_gnb_drx_harq_timer_t ul_harq[NR_GNB_DRX_MAX_HARQ_PROCESSES];
} nr_gnb_drx_state_t;

bool nr_gnb_drx_profile_is_valid(const nr_gnb_drx_profile_t *profile);
bool nr_gnb_drx_stage_profile(nr_gnb_drx_state_t *state, const nr_gnb_drx_profile_t *profile);
bool nr_gnb_drx_commit_profile(nr_gnb_drx_state_t *state,
                               uint16_t frame,
                               uint16_t slot,
                               uint16_t slots_per_frame);
void nr_gnb_drx_cancel_pending(nr_gnb_drx_state_t *state);
bool nr_gnb_drx_complete_reconfiguration(nr_gnb_drx_state_t *state);
bool nr_gnb_drx_fail_reconfiguration(nr_gnb_drx_state_t *state, uint16_t slots_per_frame);
bool nr_gnb_drx_is_active(nr_gnb_drx_state_t *state,
                          uint16_t frame,
                          uint16_t slot,
                          uint16_t slots_per_frame,
                          bool scheduling_request_pending);
void nr_gnb_drx_note_new_transmission(nr_gnb_drx_state_t *state,
                                      uint16_t frame,
                                      uint16_t slot,
                                      uint16_t slots_per_frame);
void nr_gnb_drx_note_dl_ack(nr_gnb_drx_state_t *state);
void nr_gnb_drx_note_dl_harq_result(nr_gnb_drx_state_t *state,
                                    uint8_t harq_pid,
                                    bool acknowledged,
                                    uint16_t frame,
                                    uint16_t slot,
                                    uint16_t slots_per_frame);
void nr_gnb_drx_note_ul_harq_transmission(nr_gnb_drx_state_t *state,
                                          uint8_t harq_pid,
                                          uint16_t frame,
                                          uint16_t slot,
                                          uint16_t slots_per_frame);
void nr_gnb_drx_clear_harq(nr_gnb_drx_state_t *state, bool downlink, uint8_t harq_pid);
bool nr_gnb_drx_request_command(nr_gnb_drx_state_t *state);
bool nr_gnb_drx_command_ready(const nr_gnb_drx_state_t *state,
                              bool scheduling_request_pending,
                              bool retransmission_pending,
                              bool queues_empty);
bool nr_gnb_drx_take_command(nr_gnb_drx_state_t *state,
                             bool scheduling_request_pending,
                             bool retransmission_pending,
                             bool queues_empty);

#endif
