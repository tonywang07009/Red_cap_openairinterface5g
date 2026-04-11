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

#ifndef __LAYER2_NR_MAC_GNB_NR_MAC_SDT_FSM_H__
#define __LAYER2_NR_MAC_GNB_NR_MAC_SDT_FSM_H__

#include <stdbool.h>
#include <stddef.h>
#include <stdio.h>
#include <stdint.h>

#include "nr_mac_redcap.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
  NR_REDCAP_SDT_STATE_IDLE = 0,
  NR_REDCAP_SDT_STATE_TRIGGER,
  NR_REDCAP_SDT_STATE_MSGA_PATH,
  NR_REDCAP_SDT_STATE_MSG3_PATH,
  NR_REDCAP_SDT_STATE_ACTIVE,
  NR_REDCAP_SDT_STATE_INACTIVE,
} nr_redcap_sdt_state_t;

typedef enum {
  NR_REDCAP_SDT_PATH_NONE = 0,
  NR_REDCAP_SDT_PATH_MSGA,
  NR_REDCAP_SDT_PATH_MSG3,
} nr_redcap_sdt_path_t;

typedef enum {
  NR_REDCAP_SDT_EVENT_UL_DATA_ARRIVAL = 0,
  NR_REDCAP_SDT_EVENT_SELECT_PATH,
  NR_REDCAP_SDT_EVENT_UL_GRANT_READY,
  NR_REDCAP_SDT_EVENT_UL_BURST_COMPLETE,
  NR_REDCAP_SDT_EVENT_RESET,
} nr_redcap_sdt_event_t;

typedef struct {
  bool inactive_allowed;
  uint16_t msga_payload_threshold_bytes;
} nr_redcap_sdt_config_t;

typedef struct {
  nr_redcap_sdt_event_t event;
  nr_redcap_sdt_state_t from;
  nr_redcap_sdt_state_t to;
  nr_redcap_sdt_path_t selected_path;
  nr_redcap_rrc_state_t redcap_rrc_state;
  uint16_t pending_payload_bytes;
  bool accepted;
} nr_redcap_sdt_transition_t;

typedef struct {
  nr_redcap_sdt_state_t state;
  nr_redcap_sdt_path_t selected_path;
  nr_redcap_rrc_state_t redcap_rrc_state;
  uint16_t pending_payload_bytes;
  nr_redcap_sdt_config_t config;
} nr_redcap_sdt_fsm_t;

#define NR_REDCAP_SDT_MSGA_PAYLOAD_THRESHOLD_BYTES 256

void nr_redcap_sdt_fsm_init(nr_redcap_sdt_fsm_t *fsm, bool inactive_allowed, uint16_t msga_payload_threshold_bytes);
bool nr_redcap_sdt_fsm_step(nr_redcap_sdt_fsm_t *fsm,
                            nr_redcap_sdt_event_t event,
                            uint16_t payload_bytes,
                            nr_redcap_sdt_transition_t *transition);
/**
 * @brief Expand a scheduler-observed UL grant into the SDT FSM burst-start sequence.
 *
 * The MAC scheduler only observes the moment when pending UL data is converted
 * into a PUSCH grant. This helper derives the corresponding local FSM
 * transitions in order: [UL_DATA_ARRIVAL] -> [SELECT_PATH] -> [UL_GRANT_READY].
 *
 * @param[in,out] fsm SDT FSM instance.
 * @param payload_bytes Pending UL payload bytes that triggered the new grant.
 * @param[out] transitions Caller-provided array receiving accepted transitions in order.
 * @param max_transitions Capacity of @p transitions.
 *
 * @return Number of accepted transitions stored in @p transitions.
 */
size_t nr_redcap_sdt_start_ul_burst(nr_redcap_sdt_fsm_t *fsm,
                                    uint16_t payload_bytes,
                                    nr_redcap_sdt_transition_t *transitions,
                                    size_t max_transitions);
/**
 * @brief Close an active SDT burst when the scheduler sees no more pending UL data.
 *
 * @param[in,out] fsm SDT FSM instance.
 * @param has_pending_ul_bytes True when the UE still has pending UL data after processing.
 * @param[out] transition Transition record for the accepted completion event.
 *
 * @retval true The FSM moved from [SDT_ACTIVE] to [INACTIVE] or [IDLE].
 * @retval false The burst remains active or the FSM was not in a completable state.
 */
bool nr_redcap_sdt_complete_ul_burst(nr_redcap_sdt_fsm_t *fsm,
                                     bool has_pending_ul_bytes,
                                     nr_redcap_sdt_transition_t *transition);
const char *nr_redcap_sdt_state_to_string(nr_redcap_sdt_state_t state);
const char *nr_redcap_sdt_path_to_string(nr_redcap_sdt_path_t path);
/**
 * @brief Return a stable string label for an SDT FSM event.
 *
 * @param event SDT FSM event identifier.
 * @return Human-readable string label for @p event.
 */
const char *nr_redcap_sdt_event_to_string(nr_redcap_sdt_event_t event);
/**
 * @brief Write a single SDT FSM transition record to a stream.
 *
 * @param stream Output stream receiving the formatted transition line.
 * @param transition Transition record produced by nr_redcap_sdt_fsm_step().
 * @return Number of characters written, or a negative value on error.
 */
int nr_redcap_sdt_transition_fprintf(FILE *stream, const nr_redcap_sdt_transition_t *transition);

#ifdef __cplusplus
}
#endif

#endif
