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

/*
 * rrc_messages_types.h
 *
 *  Created on: Oct 24, 2013
 *      Author: winckel and Navid Nikaein
 */

#ifndef RRC_MESSAGES_TYPES_H_
#define RRC_MESSAGES_TYPES_H_
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>
#include "common/utils/mem/oai_memory.h"
#include "openair1/PHY/defs_common.h"
#include "as_message.h"
#include "rrc_types.h"
#include "s1ap_messages_types.h"
#include "f1ap_messages_types.h"
#include "LTE_SystemInformationBlockType2.h"
#include "LTE_SL-OffsetIndicator-r12.h"
#include "LTE_SubframeBitmapSL-r12.h"
#include "LTE_DRX-Config.h"
#include "LTE_SL-CP-Len-r12.h"
#include "LTE_SL-PeriodComm-r12.h"
#include "LTE_SL-DiscResourcePool-r12.h"
#include "NR_RACH-ConfigCommon.h"
#include "NR_ServingCellConfigCommon.h"
#include "NR_ServingCellConfig.h"
#include "NR_SIB1.h"
#include "NR_SIB19-r17.h"
#include "NR_CellGroupConfig.h"
#include "NR_BCCH-BCH-Message.h"
#include "NR_ReestablishmentCause.h"
#include "NR_UE-NR-Capability.h"

/* Experimental A-IoT CBRA RRC/MAC contract. Keep this in the existing
 * cross-layer message header until the experiment has a stable ASN.1 owner. */
#define NR_AIOT_CBRA_CONFIG_MAGIC 0x43425241U
#define NR_AIOT_CBRA_CONFIG_WIRE_VERSION 1U
#define NR_AIOT_CBRA_CONFIG_WIRE_BYTES 60U
#define NR_AIOT_CBRA_CONFIG_STATUS_NONE 0U
#define NR_AIOT_CBRA_CONFIG_STATUS_ACCEPTED 1U
#define NR_AIOT_CBRA_CONFIG_STATUS_REJECTED 2U
#define NR_AIOT_CBRA_CONFIG_FLAG_ENABLED 0x01U
#define NR_AIOT_CBRA_CONFIG_FLAG_ACK 0x02U
#define NR_AIOT_CBRA_CONFIG_FLAG_REJECT 0x04U
#define NR_AIOT_CBRA_CONFIG_MIN_N 1U
#define NR_AIOT_CBRA_CONFIG_MAX_N (1U << 15)
#define NR_AIOT_CBRA_CONFIG_MAX_PRBS 275U
#define NR_AIOT_CBRA_CONFIG_CW_FREQUENCY_HZ 3630360000ULL

typedef struct nr_aiot_cbra_config_s {
  bool enabled;
  uint8_t status;
  uint32_t version;
  uint32_t round;
  uint64_t activation_slot;
  uint64_t expiry_slot;
  uint32_t reader_handle;
  uint16_t prb_start;
  uint16_t prb_count;
  uint8_t r2d_m;
  uint8_t x;
  uint8_t tbit;
  uint8_t sfs_bitmap;
  uint8_t n_code;
  uint8_t k;
  uint16_t on_duration_slots;
  uint16_t msg2_window_slots;
  uint64_t cw_frequency_hz;
} nr_aiot_cbra_config_t;

typedef struct nr_aiot_cbra_state_s {
  bool active_valid;
  bool pending_valid;
  nr_aiot_cbra_config_t active;
  nr_aiot_cbra_config_t pending;
  uint16_t access_counter;
  uint16_t selected_access_occasion;
  uint8_t selected_frequency_factor;
  uint8_t selected_time_resource;
  uint16_t access_m;
  uint16_t random_id;
  uint32_t random_state;
  uint8_t msg2_remaining;
  bool msg1_sent;
  bool waiting_msg2;
  bool succeeded;
  bool failed;
} nr_aiot_cbra_state_t;

static inline uint16_t nr_aiot_cbra_config_crc16(const uint8_t *data, size_t len)
{
  uint16_t crc = 0;
  for (size_t i = 0; i < len; ++i) {
    crc ^= (uint16_t)data[i] << 8;
    for (unsigned int bit = 0; bit < 8; ++bit)
      crc = (crc & 0x8000U) ? (uint16_t)((crc << 1) ^ 0x1021U) : (uint16_t)(crc << 1);
  }
  return crc;
}

static inline void nr_aiot_cbra_put_u16(uint8_t *dst, uint16_t value)
{
  dst[0] = (uint8_t)(value >> 8);
  dst[1] = (uint8_t)value;
}

static inline void nr_aiot_cbra_put_u32(uint8_t *dst, uint32_t value)
{
  dst[0] = (uint8_t)(value >> 24);
  dst[1] = (uint8_t)(value >> 16);
  dst[2] = (uint8_t)(value >> 8);
  dst[3] = (uint8_t)value;
}

static inline void nr_aiot_cbra_put_u64(uint8_t *dst, uint64_t value)
{
  for (unsigned int i = 0; i < 8; ++i)
    dst[i] = (uint8_t)(value >> (56U - 8U * i));
}

static inline uint16_t nr_aiot_cbra_get_u16(const uint8_t *src)
{
  return (uint16_t)(((uint16_t)src[0] << 8) | src[1]);
}

static inline uint32_t nr_aiot_cbra_get_u32(const uint8_t *src)
{
  return ((uint32_t)src[0] << 24) | ((uint32_t)src[1] << 16) | ((uint32_t)src[2] << 8) | src[3];
}

static inline uint64_t nr_aiot_cbra_get_u64(const uint8_t *src)
{
  uint64_t value = 0;
  for (unsigned int i = 0; i < 8; ++i)
    value = (value << 8) | src[i];
  return value;
}

static inline void nr_aiot_cbra_config_defaults(nr_aiot_cbra_config_t *config)
{
  memset(config, 0, sizeof(*config));
  config->version = 1;
  config->round = 1;
  config->expiry_slot = UINT64_MAX;
  config->reader_handle = 1;
  config->prb_count = 3;
  config->n_code = 1; /* 2^1 access occasions. */
  config->r2d_m = 2;
  config->x = 2;
  config->tbit = 2; /* tau/2; permits factors 1,2,4,8 for the n=2^5,m=8 case. */
  config->sfs_bitmap = 0xf0;
  config->on_duration_slots = 20;
  config->msg2_window_slots = 4;
  config->cw_frequency_hz = NR_AIOT_CBRA_CONFIG_CW_FREQUENCY_HZ;
}

static inline bool nr_aiot_cbra_config_validate(const nr_aiot_cbra_config_t *config, const char **reason)
{
  static const uint8_t allowed_sfs[8] = {0xff, 0xfe, 0xfc, 0xf8, 0xf0, 0xe0, 0xc0, 0x80};
  if (reason != NULL)
    *reason = NULL;
  if (config == NULL) {
    if (reason != NULL) *reason = "null_config";
    return false;
  }
  if (config->status > NR_AIOT_CBRA_CONFIG_STATUS_REJECTED) {
    if (reason != NULL) *reason = "invalid_status";
    return false;
  }
  if (!config->enabled)
    return true;
  if (config->version == 0 || config->round == 0 || config->expiry_slot <= config->activation_slot) {
    if (reason != NULL) *reason = "invalid_lifecycle";
    return false;
  }
  if (config->reader_handle == 0 || config->prb_count == 0 || config->prb_count > NR_AIOT_CBRA_CONFIG_MAX_PRBS
      || (uint32_t)config->prb_start + config->prb_count > NR_AIOT_CBRA_CONFIG_MAX_PRBS) {
    if (reason != NULL) *reason = "invalid_resources";
    return false;
  }
  if (config->r2d_m != 2 && config->r2d_m != 6 && config->r2d_m != 12 && config->r2d_m != 24) {
    if (reason != NULL) *reason = "invalid_r2d_density";
    return false;
  }
  if (config->x == 0 || config->x > 2 || config->tbit >= 8 || config->sfs_bitmap == 0
      || (config->sfs_bitmap & (uint8_t)~allowed_sfs[config->tbit]) != 0) {
    if (reason != NULL) *reason = "invalid_d2r_scheduling";
    return false;
  }
  if (config->n_code > 15 || config->k > 1 || config->on_duration_slots == 0 || config->msg2_window_slots == 0
      || config->cw_frequency_hz != NR_AIOT_CBRA_CONFIG_CW_FREQUENCY_HZ) {
    if (reason != NULL) *reason = "invalid_access_parameters";
    return false;
  }
  return true;
}

static inline size_t nr_aiot_cbra_config_encode(const nr_aiot_cbra_config_t *config,
                                                uint8_t wire[NR_AIOT_CBRA_CONFIG_WIRE_BYTES])
{
  if (!nr_aiot_cbra_config_validate(config, NULL) || wire == NULL)
    return 0;
  memset(wire, 0, NR_AIOT_CBRA_CONFIG_WIRE_BYTES);
  nr_aiot_cbra_put_u32(wire + 0, NR_AIOT_CBRA_CONFIG_MAGIC);
  wire[4] = NR_AIOT_CBRA_CONFIG_WIRE_VERSION;
  wire[5] = NR_AIOT_CBRA_CONFIG_WIRE_BYTES;
  wire[6] = (config->enabled ? NR_AIOT_CBRA_CONFIG_FLAG_ENABLED : 0)
            | (config->status == NR_AIOT_CBRA_CONFIG_STATUS_ACCEPTED ? NR_AIOT_CBRA_CONFIG_FLAG_ACK : 0)
            | (config->status == NR_AIOT_CBRA_CONFIG_STATUS_REJECTED ? NR_AIOT_CBRA_CONFIG_FLAG_REJECT : 0);
  nr_aiot_cbra_put_u32(wire + 8, config->version);
  nr_aiot_cbra_put_u32(wire + 12, config->round);
  nr_aiot_cbra_put_u64(wire + 16, config->activation_slot);
  nr_aiot_cbra_put_u64(wire + 24, config->expiry_slot);
  nr_aiot_cbra_put_u32(wire + 32, config->reader_handle);
  nr_aiot_cbra_put_u16(wire + 36, config->prb_start);
  nr_aiot_cbra_put_u16(wire + 38, config->prb_count);
  wire[40] = config->r2d_m;
  wire[41] = config->x;
  wire[42] = config->tbit;
  wire[43] = config->sfs_bitmap;
  wire[44] = config->n_code;
  wire[45] = config->k;
  nr_aiot_cbra_put_u16(wire + 46, config->on_duration_slots);
  nr_aiot_cbra_put_u16(wire + 48, config->msg2_window_slots);
  nr_aiot_cbra_put_u64(wire + 50, config->cw_frequency_hz);
  nr_aiot_cbra_put_u16(wire + 58, nr_aiot_cbra_config_crc16(wire, 58));
  return NR_AIOT_CBRA_CONFIG_WIRE_BYTES;
}

static inline bool nr_aiot_cbra_config_decode(const uint8_t *wire,
                                              size_t length,
                                              nr_aiot_cbra_config_t *config,
                                              const char **reason)
{
  nr_aiot_cbra_config_t decoded;
  if (reason != NULL)
    *reason = NULL;
  if (wire == NULL || config == NULL || length != NR_AIOT_CBRA_CONFIG_WIRE_BYTES) {
    if (reason != NULL) *reason = "invalid_wire_length";
    return false;
  }
  if (nr_aiot_cbra_get_u32(wire) != NR_AIOT_CBRA_CONFIG_MAGIC || wire[4] != NR_AIOT_CBRA_CONFIG_WIRE_VERSION
      || wire[5] != NR_AIOT_CBRA_CONFIG_WIRE_BYTES || nr_aiot_cbra_get_u16(wire + 58) != nr_aiot_cbra_config_crc16(wire, 58)) {
    if (reason != NULL) *reason = "invalid_wire_crc";
    return false;
  }
  nr_aiot_cbra_config_defaults(&decoded);
  decoded.enabled = (wire[6] & NR_AIOT_CBRA_CONFIG_FLAG_ENABLED) != 0;
  decoded.status = (wire[6] & NR_AIOT_CBRA_CONFIG_FLAG_REJECT) ? NR_AIOT_CBRA_CONFIG_STATUS_REJECTED
                : (wire[6] & NR_AIOT_CBRA_CONFIG_FLAG_ACK) ? NR_AIOT_CBRA_CONFIG_STATUS_ACCEPTED
                : NR_AIOT_CBRA_CONFIG_STATUS_NONE;
  decoded.version = nr_aiot_cbra_get_u32(wire + 8);
  decoded.round = nr_aiot_cbra_get_u32(wire + 12);
  decoded.activation_slot = nr_aiot_cbra_get_u64(wire + 16);
  decoded.expiry_slot = nr_aiot_cbra_get_u64(wire + 24);
  decoded.reader_handle = nr_aiot_cbra_get_u32(wire + 32);
  decoded.prb_start = nr_aiot_cbra_get_u16(wire + 36);
  decoded.prb_count = nr_aiot_cbra_get_u16(wire + 38);
  decoded.r2d_m = wire[40];
  decoded.x = wire[41];
  decoded.tbit = wire[42];
  decoded.sfs_bitmap = wire[43];
  decoded.n_code = wire[44];
  decoded.k = wire[45];
  decoded.on_duration_slots = nr_aiot_cbra_get_u16(wire + 46);
  decoded.msg2_window_slots = nr_aiot_cbra_get_u16(wire + 48);
  decoded.cw_frequency_hz = nr_aiot_cbra_get_u64(wire + 50);
  if (!nr_aiot_cbra_config_validate(&decoded, reason))
    return false;
  *config = decoded;
  return true;
}

static inline unsigned int nr_aiot_cbra_access_m(const nr_aiot_cbra_config_t *config)
{
  unsigned int n_sfs = 0;
  for (uint8_t bitmap = config->sfs_bitmap; bitmap != 0; bitmap >>= 1)
    n_sfs += bitmap & 1U;
  return n_sfs * config->x;
}

static inline void nr_aiot_cbra_state_init(nr_aiot_cbra_state_t *state)
{
  memset(state, 0, sizeof(*state));
  state->random_state = 0x6d2b79f5U;
}

static inline void nr_aiot_cbra_state_clear_exchange(nr_aiot_cbra_state_t *state)
{
  state->access_counter = 0;
  state->selected_access_occasion = 0;
  state->selected_frequency_factor = 0;
  state->selected_time_resource = 0;
  state->access_m = 0;
  state->random_id = 0;
  state->msg2_remaining = 0;
  state->msg1_sent = false;
  state->waiting_msg2 = false;
  state->succeeded = false;
  state->failed = false;
}

static inline bool nr_aiot_cbra_state_stage(nr_aiot_cbra_state_t *state,
                                            const nr_aiot_cbra_config_t *config,
                                            const char **reason)
{
  if (reason != NULL) *reason = NULL;
  if (state == NULL || !nr_aiot_cbra_config_validate(config, reason) || config->status != NR_AIOT_CBRA_CONFIG_STATUS_NONE) {
    if (reason != NULL && *reason == NULL) *reason = "invalid_stage_config";
    return false;
  }
  if (!config->enabled) {
    state->pending_valid = false;
    state->active_valid = false;
    nr_aiot_cbra_state_clear_exchange(state);
    return true;
  }
  if ((state->active_valid && config->version < state->active.version)
      || (state->pending_valid && config->version < state->pending.version)) {
    if (reason != NULL) *reason = "stale_config";
    return false;
  }
  if ((state->pending_valid && config->version == state->pending.version)
      || (state->active_valid && config->version == state->active.version))
    return true;
  state->pending = *config;
  state->pending_valid = true;
  return true;
}

static inline bool nr_aiot_cbra_state_activate(nr_aiot_cbra_state_t *state, uint64_t slot)
{
  if (state == NULL)
    return false;
  if (state->active_valid && slot >= state->active.expiry_slot) {
    state->active_valid = false;
    nr_aiot_cbra_state_clear_exchange(state);
  }
  if (state->pending_valid && slot >= state->pending.activation_slot && slot < state->pending.expiry_slot) {
    state->active = state->pending;
    state->active_valid = true;
    state->pending_valid = false;
    nr_aiot_cbra_state_clear_exchange(state);
  }
  if (state->pending_valid && slot >= state->pending.expiry_slot)
    state->pending_valid = false;
  return state->active_valid && slot < state->active.expiry_slot;
}

static inline bool nr_aiot_cbra_state_start_msg1(nr_aiot_cbra_state_t *state)
{
  if (state == NULL || !state->active_valid || state->selected_access_occasion == 0 || state->msg1_sent)
    return false;
  state->random_state ^= state->random_state << 13;
  state->random_state ^= state->random_state >> 17;
  state->random_state ^= state->random_state << 5;
  state->random_id = (uint16_t)(state->random_state >> 8);
  if (state->random_id == 0)
    state->random_id = 1;
  state->msg1_sent = true;
  state->waiting_msg2 = true;
  state->msg2_remaining = state->active.k ? 4 : 1;
  return true;
}

static inline bool nr_aiot_cbra_state_select_access_occasion(nr_aiot_cbra_state_t *state, uint16_t ordinal)
{
  if (state == NULL || !state->active_valid || ordinal == 0 || ordinal > state->access_m)
    return false;
  const unsigned int frequency_ordinal = (ordinal - 1U) / state->active.x;
  const unsigned int time_ordinal = (ordinal - 1U) % state->active.x;
  unsigned int enabled_frequency = 0;
  for (unsigned int bit = 0; bit < 8; ++bit) {
    if ((state->active.sfs_bitmap & (uint8_t)(0x80U >> bit)) == 0)
      continue;
    if (enabled_frequency == frequency_ordinal) {
      state->selected_access_occasion = ordinal;
      state->selected_frequency_factor = (uint8_t)(1U << bit);
      state->selected_time_resource = (uint8_t)(time_ordinal + 1U);
      return true;
    }
    ++enabled_frequency;
  }
  return false;
}

static inline bool nr_aiot_cbra_state_on_paging(nr_aiot_cbra_state_t *state, uint16_t random_i)
{
  if (state == NULL || !state->active_valid)
    return false;
  const unsigned int n = 1U << state->active.n_code;
  const uint16_t access_m = (uint16_t)nr_aiot_cbra_access_m(&state->active);
  if (random_i >= n || access_m == 0)
    return false;
  nr_aiot_cbra_state_clear_exchange(state);
  state->access_m = access_m;
  state->access_counter = random_i;
  if (state->access_counter < state->access_m) {
    return nr_aiot_cbra_state_select_access_occasion(state, (uint16_t)(state->access_counter + 1U))
           && nr_aiot_cbra_state_start_msg1(state);
  }
  return true;
}

static inline bool nr_aiot_cbra_state_on_access_trigger(nr_aiot_cbra_state_t *state)
{
  if (state == NULL || !state->active_valid)
    return false;
  if (state->waiting_msg2) {
    if (state->msg2_remaining > 0)
      --state->msg2_remaining;
    if (state->msg2_remaining == 0) {
      state->waiting_msg2 = false;
      state->failed = true;
    }
    return false;
  }
  if (state->msg1_sent || state->access_counter < state->access_m)
    return false;
  state->access_counter = (uint16_t)(state->access_counter - state->access_m);
  if (state->access_counter < state->access_m) {
    return nr_aiot_cbra_state_select_access_occasion(state, (uint16_t)(state->access_counter + 1U))
           && nr_aiot_cbra_state_start_msg1(state);
  }
  return true;
}

static inline bool nr_aiot_cbra_state_on_msg2(nr_aiot_cbra_state_t *state, uint16_t random_id)
{
  if (state == NULL || !state->waiting_msg2 || random_id != state->random_id)
    return false;
  state->waiting_msg2 = false;
  state->succeeded = true;
  state->msg2_remaining = 0;
  return true;
}

static inline bool nr_aiot_cbra_state_on_msg1(nr_aiot_cbra_state_t *state,
                                              uint16_t random_id,
                                              uint16_t access_occasion)
{
  if (state == NULL || !state->active_valid || random_id == 0 || access_occasion == 0
      || state->waiting_msg2 || state->failed)
    return false;
  state->random_id = random_id;
  state->selected_access_occasion = access_occasion;
  state->msg1_sent = true;
  state->waiting_msg2 = true;
  state->msg2_remaining = state->active.k ? 4 : 1;
  return true;
}

static inline bool nr_aiot_cbra_exchange_fits(const nr_aiot_cbra_config_t *config, uint32_t required_slots)
{
  return config != NULL && required_slots <= config->on_duration_slots;
}

/* Experimental model-tick bound used until the PHY-to-MAC absolute timing
 * owner is selected: trigger slot + response offset + Msg2 window + close. */
static inline uint32_t nr_aiot_cbra_complete_exchange_slots(const nr_aiot_cbra_config_t *config,
                                                             uint32_t response_offset_slots)
{
  if (config == NULL || response_offset_slots > UINT32_MAX - (uint32_t)config->msg2_window_slots - 2U)
    return UINT32_MAX;
  return response_offset_slots + (uint32_t)config->msg2_window_slots + 2U;
}

//-------------------------------------------------------------------------------------------//
// Messages for RRC logging
#if defined(DISABLE_ITTI_XER_PRINT)
  #include "LTE_BCCH-DL-SCH-Message.h"
  #include "LTE_DL-CCCH-Message.h"
  #include "LTE_DL-DCCH-Message.h"
  #include "LTE_UE-EUTRA-Capability.h"
  #include "LTE_UL-CCCH-Message.h"
  #include "LTE_UL-DCCH-Message.h"

  typedef LTE_BCCH_DL_SCH_Message_t   RrcDlBcchMessage;
  typedef LTE_DL_CCCH_Message_t       RrcDlCcchMessage;
  typedef LTE_DL_DCCH_Message_t       RrcDlDcchMessage;
  typedef LTE_UE_EUTRA_Capability_t   RrcUeEutraCapability;
  typedef LTE_UL_CCCH_Message_t       RrcUlCcchMessage;
  typedef LTE_UL_DCCH_Message_t       RrcUlDcchMessage;
#endif

//-------------------------------------------------------------------------------------------//
// Defines to access message fields.
#define RRC_STATE_IND(mSGpTR)           (mSGpTR)->ittiMsg.rrc_state_ind

#define RRC_CONFIGURATION_REQ(mSGpTR)   (mSGpTR)->ittiMsg.rrc_configuration_req

#define NBIOTRRC_CONFIGURATION_REQ(mSGpTR)   (mSGpTR)->ittiMsg.nbiotrrc_configuration_req

#define NAS_KENB_REFRESH_REQ(mSGpTR)    (mSGpTR)->ittiMsg.nas_kenb_refresh_req
#define NAS_CELL_SELECTION_REQ(mSGpTR)  (mSGpTR)->ittiMsg.nas_cell_selection_req
#define NAS_CONN_ESTABLI_REQ(mSGpTR)    (mSGpTR)->ittiMsg.nas_conn_establi_req
#define NAS_UPLINK_DATA_REQ(mSGpTR)     (mSGpTR)->ittiMsg.nas_ul_data_req
#define NAS_DETACH_REQ(mSGpTR)          (mSGpTR)->ittiMsg.nas_detach_req
#define NAS_DEREGISTRATION_REQ(mSGpTR)  (mSGpTR)->ittiMsg.nas_deregistration_req
#define NAS_5GMM_IND(mSGpTR)            (mSGpTR)->ittiMsg.nas_5gmm_ind

#define NAS_RAB_ESTABLI_RSP(mSGpTR)     (mSGpTR)->ittiMsg.nas_rab_est_rsp

#define NAS_CELL_SELECTION_CNF(mSGpTR)  (mSGpTR)->ittiMsg.nas_cell_selection_cnf
#define NAS_CELL_SELECTION_IND(mSGpTR)  (mSGpTR)->ittiMsg.nas_cell_selection_ind
#define NAS_PAGING_IND(mSGpTR)          (mSGpTR)->ittiMsg.nas_paging_ind
#define NAS_CONN_ESTABLI_CNF(mSGpTR)    (mSGpTR)->ittiMsg.nas_conn_establi_cnf
#define NAS_CONN_RELEASE_IND(mSGpTR)    (mSGpTR)->ittiMsg.nas_conn_release_ind
#define NR_NAS_CONN_ESTABLISH_IND(mSGpTR) (mSGpTR)->ittiMsg.nr_nas_conn_establish_ind
#define NR_NAS_CONN_RELEASE_IND(mSGpTR) (mSGpTR)->ittiMsg.nr_nas_conn_release_ind
#define NAS_UPLINK_DATA_CNF(mSGpTR)     (mSGpTR)->ittiMsg.nas_ul_data_cnf
#define NAS_DOWNLINK_DATA_IND(mSGpTR)   (mSGpTR)->ittiMsg.nas_dl_data_ind

#define RRC_SUBFRAME_PROCESS(mSGpTR)    (mSGpTR)->ittiMsg.rrc_subframe_process
#define NRRRC_FRAME_PROCESS(mSGpTR)     (mSGpTR)->ittiMsg.nr_rrc_frame_process

#define RLC_SDU_INDICATION(mSGpTR)      (mSGpTR)->ittiMsg.rlc_sdu_indication
#define NRDuDlReq(mSGpTR)      (mSGpTR)->ittiMsg.nr_du_dl_req

#define NAS_PDU_SESSION_REQ(mSGpTR) (mSGpTR)->ittiMsg.nas_pdu_session_req

#define NR_RRC_RLC_MAXRTX(mSGpTR) (mSGpTR)->ittiMsg.nr_rlc_maxrtx_indication

typedef struct RrcStateInd_s {
  Rrc_State_t state;
  Rrc_Sub_State_t sub_state;
} RrcStateInd;

typedef struct RadioResourceConfig_s {
  long                    prach_root;
  long                    prach_config_index;
  BOOLEAN_t               prach_high_speed;
  long                    prach_zero_correlation;
  long                    prach_freq_offset;
  long                    pucch_delta_shift;
  long                    pucch_nRB_CQI;
  long                    pucch_nCS_AN;
  long                    pucch_n1_AN;
  long                    pdsch_referenceSignalPower;
  long                    pdsch_p_b;
  long                    pusch_n_SB;
  long                    pusch_hoppingMode;
  long                    pusch_hoppingOffset;
  BOOLEAN_t               pusch_enable64QAM;
  BOOLEAN_t               pusch_groupHoppingEnabled;
  long                    pusch_groupAssignment;
  BOOLEAN_t               pusch_sequenceHoppingEnabled;
  long                    pusch_nDMRS1;
  long                    phich_duration;
  long                    phich_resource;
  BOOLEAN_t               srs_enable;
  long                    srs_BandwidthConfig;
  long                    srs_SubframeConfig;
  BOOLEAN_t               srs_ackNackST;
  BOOLEAN_t               srs_MaxUpPts;
  long                    pusch_p0_Nominal;
  long                    pusch_alpha;
  long                    pucch_p0_Nominal;
  long                    msg3_delta_Preamble;
  long                    ul_CyclicPrefixLength;
  e_LTE_DeltaFList_PUCCH__deltaF_PUCCH_Format1                    pucch_deltaF_Format1;
  e_LTE_DeltaFList_PUCCH__deltaF_PUCCH_Format1b                   pucch_deltaF_Format1b;
  e_LTE_DeltaFList_PUCCH__deltaF_PUCCH_Format2                    pucch_deltaF_Format2;
  e_LTE_DeltaFList_PUCCH__deltaF_PUCCH_Format2a                   pucch_deltaF_Format2a;
  e_LTE_DeltaFList_PUCCH__deltaF_PUCCH_Format2b                   pucch_deltaF_Format2b;
  long                    rach_numberOfRA_Preambles;
  BOOLEAN_t               rach_preamblesGroupAConfig;
  long                    rach_sizeOfRA_PreamblesGroupA;
  long                    rach_messageSizeGroupA;
  e_LTE_RACH_ConfigCommon__preambleInfo__preamblesGroupAConfig__messagePowerOffsetGroupB                    rach_messagePowerOffsetGroupB;
  long                    rach_powerRampingStep;
  long                    rach_preambleInitialReceivedTargetPower;
  long                    rach_preambleTransMax;
  long                    rach_raResponseWindowSize;
  long                    rach_macContentionResolutionTimer;
  long                    rach_maxHARQ_Msg3Tx;
  long                    bcch_modificationPeriodCoeff;
  long                    pcch_defaultPagingCycle;
  long                    pcch_nB;
  LTE_DRX_Config_PR                                   drx_Config_present;
  long                                                drx_onDurationTimer;
  long                                                drx_InactivityTimer;
  long                                                drx_RetransmissionTimer;
  LTE_DRX_Config__setup__longDRX_CycleStartOffset_PR  drx_longDrx_CycleStartOffset_present;
  long                                                drx_longDrx_CycleStartOffset;
  long                                                drx_shortDrx_Cycle;
  long                                                drx_shortDrx_ShortCycleTimer;
  long                    ue_TimersAndConstants_t300;
  long                    ue_TimersAndConstants_t301;
  long                    ue_TimersAndConstants_t310;
  long                    ue_TimersAndConstants_t311;
  long                    ue_TimersAndConstants_n310;
  long                    ue_TimersAndConstants_n311;
  long                    ue_TransmissionMode;
  long                    ue_multiple_max;
  //SIB2 BR Options
  long       preambleTransMax_CE_r13;
  BOOLEAN_t     prach_ConfigCommon_v1310;
  BOOLEAN_t            *mpdcch_startSF_CSS_RA_r13;
  long        mpdcch_startSF_CSS_RA_r13_val;
  long       *prach_HoppingOffset_r13;
  BOOLEAN_t     mbms_dedicated_serving_cell;
} RadioResourceConfig;

// eNB: ENB_APP -> RRC messages
typedef struct RrcConfigurationReq_s {
  uint32_t                cell_identity;
  uint16_t                tac;
  uint16_t                mcc[PLMN_LIST_MAX_SIZE];
  uint16_t                mnc[PLMN_LIST_MAX_SIZE];
  uint8_t                 mnc_digit_length[PLMN_LIST_MAX_SIZE];
  uint8_t                 num_plmn;
  int                     enable_measurement_reports;
  int                     enable_x2;
  uint32_t                rrc_inactivity_timer_thres; // for testing, maybe change later
  paging_drx_t            default_drx;
  int16_t                 nb_cc;
  frame_type_t            frame_type[MAX_NUM_CCs];
  uint8_t                 tdd_config[MAX_NUM_CCs];
  uint8_t                 tdd_config_s[MAX_NUM_CCs];
  lte_prefix_type_t       prefix_type[MAX_NUM_CCs];
  uint8_t                 pbch_repetition[MAX_NUM_CCs];
  int16_t                 eutra_band[MAX_NUM_CCs];
  uint32_t                downlink_frequency[MAX_NUM_CCs];
  int32_t                 uplink_frequency_offset[MAX_NUM_CCs];
  int16_t                 Nid_cell[MAX_NUM_CCs];// for testing, change later
  int16_t                 N_RB_DL[MAX_NUM_CCs];// for testing, change later
  int                     nb_antenna_ports[MAX_NUM_CCs];
  int                     eMBMS_configured;
  int                     eMBMS_M2_configured;
  int                     eMTC_configured;
  int                     SL_configured;

  RadioResourceConfig     radioresourceconfig[MAX_NUM_CCs];
  RadioResourceConfig     radioresourceconfig_BR[MAX_NUM_CCs];


  //MIB
  long        schedulingInfoSIB1_BR_r13[MAX_NUM_CCs];
  //SIB1 BR options
  uint16_t     *hyperSFN_r13                           [MAX_NUM_CCs];
  long       *eDRX_Allowed_r13                       [MAX_NUM_CCs];
  BOOLEAN_t     cellSelectionInfoCE_r13                [MAX_NUM_CCs];
  long        q_RxLevMinCE_r13                       [MAX_NUM_CCs];
  long       *q_QualMinRSRQ_CE_r13                   [MAX_NUM_CCs];
  BOOLEAN_t     bandwidthReducedAccessRelatedInfo_r13  [MAX_NUM_CCs];
  long            si_Narrowband_r13         [MAX_NUM_CCs][32];
  long            si_TBS_r13                [MAX_NUM_CCs][32];
  int             scheduling_info_br_size   [MAX_NUM_CCs];
  long        si_WindowLength_BR_r13                       [MAX_NUM_CCs];
  long        si_RepetitionPattern_r13                     [MAX_NUM_CCs];
  BOOLEAN_t     *fdd_DownlinkOrTddSubframeBitmapBR_r13       [MAX_NUM_CCs];
  uint64_t      fdd_DownlinkOrTddSubframeBitmapBR_val_r13    [MAX_NUM_CCs];
  uint16_t      *fdd_UplinkSubframeBitmapBR_r13              [MAX_NUM_CCs];
  long        startSymbolBR_r13                            [MAX_NUM_CCs];
  long        si_HoppingConfigCommon_r13                   [MAX_NUM_CCs];
  long       *si_ValidityTime_r13                          [MAX_NUM_CCs];
  long            systemInfoValueTagSi_r13      [MAX_NUM_CCs][10];
  int             system_info_value_tag_SI_size [MAX_NUM_CCs];
  BOOLEAN_t     freqHoppingParametersDL_r13                   [MAX_NUM_CCs];
  long       *mpdcch_pdsch_HoppingNB_r13                    [MAX_NUM_CCs];
  BOOLEAN_t     interval_DLHoppingConfigCommonModeA_r13       [MAX_NUM_CCs];
  long        interval_DLHoppingConfigCommonModeA_r13_val   [MAX_NUM_CCs];
  BOOLEAN_t     interval_DLHoppingConfigCommonModeB_r13       [MAX_NUM_CCs];
  long        interval_DLHoppingConfigCommonModeB_r13_val   [MAX_NUM_CCs];
  long       *mpdcch_pdsch_HoppingOffset_r13                [MAX_NUM_CCs];
  long firstPreamble_r13                 [MAX_NUM_CCs][4];
  long lastPreamble_r13                  [MAX_NUM_CCs][4];
  long ra_ResponseWindowSize_r13         [MAX_NUM_CCs][4];
  long mac_ContentionResolutionTimer_r13 [MAX_NUM_CCs][4];
  long rar_HoppingConfig_r13             [MAX_NUM_CCs][4];
  int  rach_CE_LevelInfoList_r13_size    [MAX_NUM_CCs];
  //  long pcch_defaultPagingCycle_br;
  long rsrp_range           [MAX_NUM_CCs][3];
  int rsrp_range_list_size  [MAX_NUM_CCs];
  long prach_config_index                        [MAX_NUM_CCs][4];
  long prach_freq_offset                         [MAX_NUM_CCs][4];
  long *prach_StartingSubframe_r13               [MAX_NUM_CCs][4];
  long *maxNumPreambleAttemptCE_r13              [MAX_NUM_CCs][4];
  long numRepetitionPerPreambleAttempt_r13       [MAX_NUM_CCs][4];
  long mpdcch_NumRepetition_RA_r13               [MAX_NUM_CCs][4];
  long prach_HoppingConfig_r13                   [MAX_NUM_CCs][4];
  int  prach_parameters_list_size                [MAX_NUM_CCs];
  long max_available_narrow_band                 [MAX_NUM_CCs][4][2];
  int  max_available_narrow_band_size            [MAX_NUM_CCs][4];
  long pucch_info_value       [MAX_NUM_CCs][4];
  int  pucch_info_value_size  [MAX_NUM_CCs];
  bool  pcch_config_v1310               [MAX_NUM_CCs];
  long  paging_narrowbands_r13          [MAX_NUM_CCs];
  long  mpdcch_numrepetition_paging_r13 [MAX_NUM_CCs];
  long  *nb_v1310                        [MAX_NUM_CCs];
  long  *pucch_NumRepetitionCE_Msg4_Level0_r13  [MAX_NUM_CCs];
  long  *pucch_NumRepetitionCE_Msg4_Level1_r13  [MAX_NUM_CCs];
  long  *pucch_NumRepetitionCE_Msg4_Level2_r13  [MAX_NUM_CCs];
  long  *pucch_NumRepetitionCE_Msg4_Level3_r13  [MAX_NUM_CCs];
  bool  sib2_freq_hoppingParameters_r13_exists             [MAX_NUM_CCs];
  long  *sib2_mpdcch_pdsch_hoppingNB_r13                   [MAX_NUM_CCs];
  long  *sib2_interval_DLHoppingConfigCommonModeA_r13      [MAX_NUM_CCs];
  long  sib2_interval_DLHoppingConfigCommonModeA_r13_val  [MAX_NUM_CCs];
  long  *sib2_interval_DLHoppingConfigCommonModeB_r13      [MAX_NUM_CCs];
  long  sib2_interval_DLHoppingConfigCommonModeB_r13_val  [MAX_NUM_CCs];
  long  *sib2_interval_ULHoppingConfigCommonModeA_r13      [MAX_NUM_CCs];
  long  sib2_interval_ULHoppingConfigCommonModeA_r13_val  [MAX_NUM_CCs];
  long  *sib2_interval_ULHoppingConfigCommonModeB_r13      [MAX_NUM_CCs];
  long  sib2_interval_ULHoppingConfigCommonModeB_r13_val  [MAX_NUM_CCs];
  long  *sib2_mpdcch_pdsch_hoppingOffset_r13               [MAX_NUM_CCs];
  long  *pdsch_maxNumRepetitionCEmodeA_r13                 [MAX_NUM_CCs];
  long  *pdsch_maxNumRepetitionCEmodeB_r13                 [MAX_NUM_CCs];
  long  *pusch_maxNumRepetitionCEmodeA_r13                 [MAX_NUM_CCs];
  long  *pusch_maxNumRepetitionCEmodeB_r13                 [MAX_NUM_CCs];
  long  *pusch_repetitionLevelCEmodeA_r13				   [MAX_NUM_CCs];
  long  *pusch_HoppingOffset_v1310                         [MAX_NUM_CCs];

  //SIB18
  e_LTE_SL_CP_Len_r12            rxPool_sc_CP_Len[MAX_NUM_CCs];
  e_LTE_SL_PeriodComm_r12        rxPool_sc_Period[MAX_NUM_CCs];
  e_LTE_SL_CP_Len_r12            rxPool_data_CP_Len[MAX_NUM_CCs];
  long                           rxPool_ResourceConfig_prb_Num[MAX_NUM_CCs];
  long                           rxPool_ResourceConfig_prb_Start[MAX_NUM_CCs];
  long                           rxPool_ResourceConfig_prb_End[MAX_NUM_CCs];
  LTE_SL_OffsetIndicator_r12_PR  rxPool_ResourceConfig_offsetIndicator_present[MAX_NUM_CCs];
  long                           rxPool_ResourceConfig_offsetIndicator_choice[MAX_NUM_CCs];
  LTE_SubframeBitmapSL_r12_PR    rxPool_ResourceConfig_subframeBitmap_present[MAX_NUM_CCs];
  char                          *rxPool_ResourceConfig_subframeBitmap_choice_bs_buf[MAX_NUM_CCs];
  long                           rxPool_ResourceConfig_subframeBitmap_choice_bs_size[MAX_NUM_CCs];
  long                           rxPool_ResourceConfig_subframeBitmap_choice_bs_bits_unused[MAX_NUM_CCs];

  //SIB19
  //for discRxPool
  LTE_SL_CP_Len_r12_t            discRxPool_cp_Len[MAX_NUM_CCs];
  e_LTE_SL_DiscResourcePool_r12__discPeriod_r12               discRxPool_discPeriod[MAX_NUM_CCs];
  long                           discRxPool_numRetx[MAX_NUM_CCs];
  long                           discRxPool_numRepetition[MAX_NUM_CCs];
  long                           discRxPool_ResourceConfig_prb_Num[MAX_NUM_CCs];
  long                           discRxPool_ResourceConfig_prb_Start[MAX_NUM_CCs];
  long                           discRxPool_ResourceConfig_prb_End[MAX_NUM_CCs];
  LTE_SL_OffsetIndicator_r12_PR  discRxPool_ResourceConfig_offsetIndicator_present[MAX_NUM_CCs];
  long                           discRxPool_ResourceConfig_offsetIndicator_choice[MAX_NUM_CCs];
  LTE_SubframeBitmapSL_r12_PR    discRxPool_ResourceConfig_subframeBitmap_present[MAX_NUM_CCs];
  char                          *discRxPool_ResourceConfig_subframeBitmap_choice_bs_buf[MAX_NUM_CCs];
  long                           discRxPool_ResourceConfig_subframeBitmap_choice_bs_size[MAX_NUM_CCs];
  long                           discRxPool_ResourceConfig_subframeBitmap_choice_bs_bits_unused[MAX_NUM_CCs];
  //for discRxPoolPS
  LTE_SL_CP_Len_r12_t            discRxPoolPS_cp_Len[MAX_NUM_CCs];
  e_LTE_SL_DiscResourcePool_r12__discPeriod_r12                   discRxPoolPS_discPeriod[MAX_NUM_CCs];
  long                           discRxPoolPS_numRetx[MAX_NUM_CCs];
  long                           discRxPoolPS_numRepetition[MAX_NUM_CCs];
  long                           discRxPoolPS_ResourceConfig_prb_Num[MAX_NUM_CCs];
  long                           discRxPoolPS_ResourceConfig_prb_Start[MAX_NUM_CCs];
  long                           discRxPoolPS_ResourceConfig_prb_End[MAX_NUM_CCs];
  LTE_SL_OffsetIndicator_r12_PR  discRxPoolPS_ResourceConfig_offsetIndicator_present[MAX_NUM_CCs];
  long                           discRxPoolPS_ResourceConfig_offsetIndicator_choice[MAX_NUM_CCs];
  LTE_SubframeBitmapSL_r12_PR    discRxPoolPS_ResourceConfig_subframeBitmap_present[MAX_NUM_CCs];
  char                          *discRxPoolPS_ResourceConfig_subframeBitmap_choice_bs_buf[MAX_NUM_CCs];
  long                           discRxPoolPS_ResourceConfig_subframeBitmap_choice_bs_size[MAX_NUM_CCs];
  long                           discRxPoolPS_ResourceConfig_subframeBitmap_choice_bs_bits_unused[MAX_NUM_CCs];
  //Nr secondary cell group SSB central frequency (for ENDC NSA)
  int                            nr_scg_ssb_freq;
} RrcConfigurationReq;

#define MAX_NUM_NBIOT_CELEVELS    3

typedef struct NbIoTRrcConfigurationReq_s {
  uint32_t                cell_identity;
  uint16_t                tac;
  uint16_t                mcc;
  uint16_t                mnc;
  uint8_t                 mnc_digit_length;
  frame_type_t            frame_type;
  uint8_t                 tdd_config;
  uint8_t                 tdd_config_s;
  lte_prefix_type_t       prefix_type;
  lte_prefix_type_t       prefix_type_UL;
  int16_t                 eutra_band;
  uint32_t                downlink_frequency;
  int32_t                 uplink_frequency_offset;
  int16_t                 Nid_cell;// for testing, change later
  int16_t                 N_RB_DL;// for testing, change later
  //RACH
  long                    rach_raResponseWindowSize_NB;
  long                    rach_macContentionResolutionTimer_NB;
  long                    rach_powerRampingStep_NB;
  long                    rach_preambleInitialReceivedTargetPower_NB;
  long                    rach_preambleTransMax_CE_NB;
  //BCCH
  long                    bcch_modificationPeriodCoeff_NB;
  //PCCH
  long                    pcch_defaultPagingCycle_NB;
  long                    pcch_nB_NB;
  long                    pcch_npdcch_NumRepetitionPaging_NB;
  //NPRACH
  long                    nprach_CP_Length;
  long                    nprach_rsrp_range;
  long                    nprach_Periodicity[MAX_NUM_NBIOT_CELEVELS];
  long                    nprach_StartTime[MAX_NUM_NBIOT_CELEVELS];
  long                    nprach_SubcarrierOffset[MAX_NUM_NBIOT_CELEVELS];
  long                    nprach_NumSubcarriers[MAX_NUM_NBIOT_CELEVELS];
  long                    numRepetitionsPerPreambleAttempt_NB[MAX_NUM_NBIOT_CELEVELS];
  long                    nprach_SubcarrierMSG3_RangeStart;
  long                    maxNumPreambleAttemptCE_NB;
  long                    npdcch_NumRepetitions_RA[MAX_NUM_NBIOT_CELEVELS];
  long                    npdcch_StartSF_CSS_RA[MAX_NUM_NBIOT_CELEVELS];
  long                    npdcch_Offset_RA[MAX_NUM_NBIOT_CELEVELS];
  //NPDSCH
  long                    npdsch_nrs_Power;
  //NPUSCH
  long                    npusch_ack_nack_numRepetitions_NB;
  long                    npusch_srs_SubframeConfig_NB;
  long                    npusch_threeTone_CyclicShift_r13;
  long                    npusch_sixTone_CyclicShift_r13;
  BOOLEAN_t               npusch_groupHoppingEnabled;
  long                    npusch_groupAssignmentNPUSCH_r13;

  //DL_GapConfig
  long                    dl_GapThreshold_NB;
  long                    dl_GapPeriodicity_NB;
  long                    dl_GapDurationCoeff_NB;
  //Uplink power control Common
  long                    npusch_p0_NominalNPUSCH;
  long                    npusch_alpha;
  long                    deltaPreambleMsg3;
  //UE timers and constants
  long                    ue_TimersAndConstants_t300_NB;
  long                    ue_TimersAndConstants_t301_NB;
  long                    ue_TimersAndConstants_t310_NB;
  long                    ue_TimersAndConstants_t311_NB;
  long                    ue_TimersAndConstants_n310_NB;
  long                    ue_TimersAndConstants_n311_NB;
} NbIoTRrcConfigurationReq;

// gNB: GNB_APP -> RRC messages
typedef struct NRRrcConfigurationReq_s {
  uint32_t                tac;
  plmn_id_t plmn[PLMN_LIST_MAX_SIZE];
  uint8_t                 num_plmn;

  bool um_on_default_drb;
  bool                    enable_sdap;
  int                     drbs;
  nr_aiot_cbra_config_t   aiot_cbra_config;
  int                     aiot_cbra_update_tbit;
} gNB_RrcConfigurationReq;

typedef struct NRDuDlReq_s {
  rnti_t rnti;
  uint8_t *buf;
  uint64_t srb_id;
}  NRDuDlReq_t;

// eNB: realtime -> RRC messages
typedef struct rrc_subframe_process_s {
  protocol_ctxt_t ctxt;
  int CC_id;
} RrcSubframeProcess;

typedef struct nrrrc_frame_process_s {
  int hfn;
  int frame;
  int gnb_id;
} NRRrcFrameProcess;

typedef enum NR_Release_Cause_e {
  RRC_CONNECTION_FAILURE,
  RRC_RESUME_FAILURE,
  OTHER,
} NR_Release_Cause_t;

typedef struct nr_nas_conn_release_ind {
  NR_Release_Cause_t cause;
} NRNasConnReleaseInd;

// eNB: RLC -> RRC messages
typedef struct rlc_sdu_indication_s {
  int rnti;
  int is_successful;
  int srb_id;
  int message_id;
} RlcSduIndication;

typedef struct {
  int ue_id;
} RlcMaxRtxIndication;

typedef struct {
  bool is_srb;
  int rb_id;
} nr_mac_rrc_resume_rb_t;

typedef struct {
  NR_ReestablishmentCause_t cause;
} nr_mac_rrc_config_reset_t;
typedef struct {
  NR_CellGroupConfig_t *cellGroupConfig;
  NR_UE_NR_Capability_t *UE_NR_Capability;
  int hfn;
  int frame;
} nr_mac_rrc_config_cg_t;
typedef struct {
  NR_BCCH_BCH_Message_t *bcch;
  bool access_barred;
} nr_mac_rrc_config_mib_t;
typedef struct {
  NR_SIB1_t *sib1;
  bool can_start_ra;
} nr_mac_rrc_config_sib1_t;
typedef struct {
  NR_SIB19_r17_t *sib19;
  int hfn;
  int frame;
  bool can_start_ra;
} nr_mac_rrc_config_other_sib_t;
typedef struct {
  int get_sib;
} nr_mac_rrc_sched_sib_t;
typedef struct {
  nr_aiot_cbra_config_t config;
} nr_mac_rrc_config_aiot_cbra_t;


enum payload_type {
  NR_MAC_RRC_CONFIG_RESET,
  NR_MAC_RRC_CONFIG_CG,
  NR_MAC_RRC_CONFIG_MIB,
  NR_MAC_RRC_CONFIG_SIB1,
  NR_MAC_RRC_CONFIG_OTHER_SIB,
  NR_MAC_RRC_SCHED_SIB,
  NR_MAC_RRC_RESUME_RB,
  NR_MAC_RRC_TRIGGER_RA,
  NR_MAC_RRC_ENTER_INACTIVE,
  NR_MAC_RRC_CONFIG_AIOT_CBRA
};

typedef struct {
  enum payload_type payload_type;
  union {
    nr_mac_rrc_config_reset_t config_reset;
    nr_mac_rrc_config_cg_t config_cg;
    nr_mac_rrc_config_mib_t config_mib;
    nr_mac_rrc_config_sib1_t config_sib1;
    nr_mac_rrc_sched_sib_t sched_sib;
    nr_mac_rrc_config_other_sib_t config_other_sib;
    nr_mac_rrc_resume_rb_t resume_rb;
    nr_mac_rrc_config_aiot_cbra_t config_aiot_cbra;
  } payload;
} nr_mac_rrc_message_t;

#endif /* RRC_MESSAGES_TYPES_H_ */
