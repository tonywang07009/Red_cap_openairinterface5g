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

#include "nr_mac_sdt_fsm.h"

#include <stddef.h>

/**
 * @brief Append one accepted transition to a caller-provided transition array.
 *
 * @param transition Accepted transition record to append.
 * @param[out] transitions Destination array.
 * @param max_transitions Capacity of @p transitions.
 * @param[in,out] num_transitions Current number of stored transitions.
 */
static void append_transition(const nr_redcap_sdt_transition_t *transition,
                              nr_redcap_sdt_transition_t *transitions,
                              size_t max_transitions,
                              size_t *num_transitions)
{
  if (transition == NULL || transitions == NULL || num_transitions == NULL || !transition->accepted || *num_transitions >= max_transitions)
    return;

  transitions[*num_transitions] = *transition;
  (*num_transitions)++;
}

static void init_transition_record(const nr_redcap_sdt_fsm_t *fsm,
                                   nr_redcap_sdt_event_t event,
                                   nr_redcap_sdt_transition_t *transition)
{
  if (transition == NULL)
    return;

  transition->event = event;
  transition->from = fsm->state;
  transition->to = fsm->state;
  transition->selected_path = fsm->selected_path;
  transition->redcap_rrc_state = fsm->redcap_rrc_state;
  transition->pending_payload_bytes = fsm->pending_payload_bytes;
  transition->accepted = false;
}

static nr_redcap_rrc_state_t sdt_state_to_rrc_state(nr_redcap_sdt_state_t state)
{
  switch (state) {
    case NR_REDCAP_SDT_STATE_INACTIVE:
      return NR_REDCAP_RRC_INACTIVE;
    case NR_REDCAP_SDT_STATE_IDLE:
      return NR_REDCAP_RRC_IDLE;
    case NR_REDCAP_SDT_STATE_TRIGGER:
    case NR_REDCAP_SDT_STATE_MSGA_PATH:
    case NR_REDCAP_SDT_STATE_MSG3_PATH:
    case NR_REDCAP_SDT_STATE_ACTIVE:
    default:
      return NR_REDCAP_RRC_CONNECTED;
  }
}

static bool move_to_state(nr_redcap_sdt_fsm_t *fsm,
                          nr_redcap_sdt_state_t next_state,
                          nr_redcap_sdt_transition_t *transition)
{
  if (transition != NULL) {
    transition->from = fsm->state;
    transition->to = next_state;
  }
  fsm->state = next_state;
  fsm->redcap_rrc_state = sdt_state_to_rrc_state(next_state);
  if (transition != NULL) {
    transition->selected_path = fsm->selected_path;
    transition->redcap_rrc_state = fsm->redcap_rrc_state;
    transition->pending_payload_bytes = fsm->pending_payload_bytes;
    transition->accepted = true;
  }
  return true;
}

void nr_redcap_sdt_fsm_init(nr_redcap_sdt_fsm_t *fsm, bool inactive_allowed, uint16_t msga_payload_threshold_bytes)
{
  if (fsm == NULL)
    return;

  fsm->state = NR_REDCAP_SDT_STATE_IDLE;
  fsm->selected_path = NR_REDCAP_SDT_PATH_NONE;
  fsm->redcap_rrc_state = NR_REDCAP_RRC_IDLE;
  fsm->pending_payload_bytes = 0;
  fsm->config.inactive_allowed = inactive_allowed;
  fsm->config.msga_payload_threshold_bytes = msga_payload_threshold_bytes;
}

bool nr_redcap_sdt_fsm_step(nr_redcap_sdt_fsm_t *fsm,
                            nr_redcap_sdt_event_t event,
                            uint16_t payload_bytes,
                            nr_redcap_sdt_transition_t *transition)
{
  if (fsm == NULL)
    return false;

  init_transition_record(fsm, event, transition);

  switch (event) {
    case NR_REDCAP_SDT_EVENT_UL_DATA_ARRIVAL:
      if ((fsm->state != NR_REDCAP_SDT_STATE_IDLE && fsm->state != NR_REDCAP_SDT_STATE_INACTIVE) || payload_bytes == 0)
        return false;
      if (fsm->state == NR_REDCAP_SDT_STATE_INACTIVE && !fsm->config.inactive_allowed)
        return false;
      fsm->pending_payload_bytes = payload_bytes;
      fsm->selected_path = NR_REDCAP_SDT_PATH_NONE;
      return move_to_state(fsm, NR_REDCAP_SDT_STATE_TRIGGER, transition);

    case NR_REDCAP_SDT_EVENT_SELECT_PATH:
      if (fsm->state != NR_REDCAP_SDT_STATE_TRIGGER)
        return false;
      fsm->selected_path = fsm->pending_payload_bytes < fsm->config.msga_payload_threshold_bytes
                               ? NR_REDCAP_SDT_PATH_MSGA
                               : NR_REDCAP_SDT_PATH_MSG3;
      return move_to_state(fsm,
                           fsm->selected_path == NR_REDCAP_SDT_PATH_MSGA ? NR_REDCAP_SDT_STATE_MSGA_PATH
                                                                         : NR_REDCAP_SDT_STATE_MSG3_PATH,
                           transition);

    case NR_REDCAP_SDT_EVENT_UL_GRANT_READY:
      if (fsm->state != NR_REDCAP_SDT_STATE_MSGA_PATH && fsm->state != NR_REDCAP_SDT_STATE_MSG3_PATH)
        return false;
      return move_to_state(fsm, NR_REDCAP_SDT_STATE_ACTIVE, transition);

    case NR_REDCAP_SDT_EVENT_UL_BURST_COMPLETE:
      if (fsm->state != NR_REDCAP_SDT_STATE_ACTIVE)
        return false;
      fsm->pending_payload_bytes = 0;
      return move_to_state(fsm,
                           fsm->config.inactive_allowed ? NR_REDCAP_SDT_STATE_INACTIVE : NR_REDCAP_SDT_STATE_IDLE,
                           transition);

    case NR_REDCAP_SDT_EVENT_RESET:
      fsm->pending_payload_bytes = 0;
      fsm->selected_path = NR_REDCAP_SDT_PATH_NONE;
      return move_to_state(fsm, NR_REDCAP_SDT_STATE_IDLE, transition);

    default:
      return false;
  }
}

size_t nr_redcap_sdt_start_ul_burst(nr_redcap_sdt_fsm_t *fsm,
                                    uint16_t payload_bytes,
                                    nr_redcap_sdt_transition_t *transitions,
                                    size_t max_transitions)
{
  if (fsm == NULL || payload_bytes == 0)
    return 0;

  size_t num_transitions = 0;
  nr_redcap_sdt_transition_t transition = {0};

  if (fsm->state == NR_REDCAP_SDT_STATE_IDLE || fsm->state == NR_REDCAP_SDT_STATE_INACTIVE) {
    if (!nr_redcap_sdt_fsm_step(fsm, NR_REDCAP_SDT_EVENT_UL_DATA_ARRIVAL, payload_bytes, &transition))
      return num_transitions;
    append_transition(&transition, transitions, max_transitions, &num_transitions);
  }

  if (fsm->state == NR_REDCAP_SDT_STATE_TRIGGER) {
    if (!nr_redcap_sdt_fsm_step(fsm, NR_REDCAP_SDT_EVENT_SELECT_PATH, 0, &transition))
      return num_transitions;
    append_transition(&transition, transitions, max_transitions, &num_transitions);
  }

  if (fsm->state == NR_REDCAP_SDT_STATE_MSGA_PATH || fsm->state == NR_REDCAP_SDT_STATE_MSG3_PATH) {
    if (!nr_redcap_sdt_fsm_step(fsm, NR_REDCAP_SDT_EVENT_UL_GRANT_READY, 0, &transition))
      return num_transitions;
    append_transition(&transition, transitions, max_transitions, &num_transitions);
  }

  return num_transitions;
}

bool nr_redcap_sdt_complete_ul_burst(nr_redcap_sdt_fsm_t *fsm,
                                     bool has_pending_ul_bytes,
                                     nr_redcap_sdt_transition_t *transition)
{
  if (fsm == NULL || has_pending_ul_bytes || fsm->state != NR_REDCAP_SDT_STATE_ACTIVE)
    return false;

  return nr_redcap_sdt_fsm_step(fsm, NR_REDCAP_SDT_EVENT_UL_BURST_COMPLETE, 0, transition);
}

const char *nr_redcap_sdt_state_to_string(nr_redcap_sdt_state_t state)
{
  switch (state) {
    case NR_REDCAP_SDT_STATE_IDLE:
      return "idle";
    case NR_REDCAP_SDT_STATE_TRIGGER:
      return "sdt-trigger";
    case NR_REDCAP_SDT_STATE_MSGA_PATH:
      return "msga-path";
    case NR_REDCAP_SDT_STATE_MSG3_PATH:
      return "msg3-path";
    case NR_REDCAP_SDT_STATE_ACTIVE:
      return "sdt-active";
    case NR_REDCAP_SDT_STATE_INACTIVE:
      return "inactive";
    default:
      return "unknown";
  }
}

const char *nr_redcap_sdt_path_to_string(nr_redcap_sdt_path_t path)
{
  switch (path) {
    case NR_REDCAP_SDT_PATH_NONE:
      return "none";
    case NR_REDCAP_SDT_PATH_MSGA:
      return "msga";
    case NR_REDCAP_SDT_PATH_MSG3:
      return "msg3";
    default:
      return "unknown";
  }
}

const char *nr_redcap_sdt_event_to_string(nr_redcap_sdt_event_t event)
{
  switch (event) {
    case NR_REDCAP_SDT_EVENT_UL_DATA_ARRIVAL:
      return "ul-data-arrival";
    case NR_REDCAP_SDT_EVENT_SELECT_PATH:
      return "select-path";
    case NR_REDCAP_SDT_EVENT_UL_GRANT_READY:
      return "ul-grant-ready";
    case NR_REDCAP_SDT_EVENT_UL_BURST_COMPLETE:
      return "ul-burst-complete";
    case NR_REDCAP_SDT_EVENT_RESET:
      return "reset";
    default:
      return "unknown";
  }
}

int nr_redcap_sdt_transition_fprintf(FILE *stream, const nr_redcap_sdt_transition_t *transition)
{
  if (stream == NULL || transition == NULL)
    return -1;

  return fprintf(stream,
                 "event=%s accepted=%s from=%s to=%s path=%s rrc=%s pending_payload_bytes=%u\n",
                 nr_redcap_sdt_event_to_string(transition->event),
                 transition->accepted ? "true" : "false",
                 nr_redcap_sdt_state_to_string(transition->from),
                 nr_redcap_sdt_state_to_string(transition->to),
                 nr_redcap_sdt_path_to_string(transition->selected_path),
                 nr_redcap_rrc_state_to_string(transition->redcap_rrc_state),
                 transition->pending_payload_bytes);
}
