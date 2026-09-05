/*
 * Licensed to the OpenAirInterface (OAI) Software Alliance under one or more
 * contributor license agreements.  See the NOTICE file distributed with
 * this work for additional information regarding copyright ownership.
 * The OpenAirInterface Software Alliance licenses this file to You under
 * the OAI Public License, Version 1.0  (the "License"); you may not use this file
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

/*! \file nr_ue_rf_helpers.c
 * \brief      Functional helpers to configure the RF boards at UE side
 * \author     Guido Casati
 * \date       2020
 * \version    0.1
 * \company    Fraunhofer IIS
 * \email:     guido.casati@iis.fraunhofer.de
 */

#include "PHY/defs_nr_UE.h"
#include "nr_transport_proto_ue.h"
#include "executables/softmodem-common.h"
#include "PHY/CODING/coding_defs.h"

extern PHY_VARS_NR_UE ***PHY_vars_UE_g;

#define AIOT_T2_MANCHESTER_CHIPS_PER_BIT 2
#define AIOT_T2_D2R_CHIPS_PER_BIT 4
#define AIOT_T2_INVENTORY_COMMAND 0x01

nr_ue_aiot_r2d_resource_result_t nr_ue_aiot_validate_r2d_resources(unsigned int prb_count,
                                                               unsigned int chips_per_symbol,
                                                               const char **reason)
{
  unsigned int minimum_prbs;

  if (reason != NULL)
    *reason = NULL;

  /* TS 38.291 V19.3.0 table 4.3.3.3-1: minimum R2D PRBs by chip density. */
  switch (chips_per_symbol) {
    case 2:
    case 6:
      minimum_prbs = 1;
      break;
    case 12:
      minimum_prbs = 2;
      break;
    case 24:
      minimum_prbs = 3;
      break;
    default:
      if (reason != NULL)
        *reason = "invalid_r2d_density";
      return NR_UE_AIOT_R2D_INVALID_RESOURCE;
  }

  if (prb_count == 0) {
    if (reason != NULL)
      *reason = "invalid_r2d_prbs";
    return NR_UE_AIOT_R2D_INVALID_RESOURCE;
  }

  if (prb_count < minimum_prbs) {
    if (reason != NULL)
      *reason = "insufficient_r2d_prbs";
    return NR_UE_AIOT_R2D_INSUFFICIENT_PRBS;
  }

  return NR_UE_AIOT_R2D_RESOURCE_OK;
}

nr_ue_aiot_d2r_scheduling_result_t nr_ue_aiot_validate_d2r_scheduling(
    const nr_ue_aiot_d2r_scheduling_t *scheduling,
    unsigned int *n_sfs,
    unsigned int *m,
    const char **reason)
{
  static const uint8_t allowed_sfs_masks[NR_UE_AIOT_D2R_TBIT_COUNT] = {
      0xff,
      0xfe,
      0xfc,
      0xf8,
      0xf0,
      0xe0,
      0xc0,
      0x80,
  };

  if (reason != NULL)
    *reason = NULL;
  if (scheduling == NULL) {
    if (reason != NULL)
      *reason = "invalid_d2r_scheduling";
    return NR_UE_AIOT_D2R_SCHED_INVALID;
  }
  if (scheduling->x < 1 || scheduling->x > 2) {
    if (reason != NULL)
      *reason = "invalid_d2r_x";
    return NR_UE_AIOT_D2R_SCHED_INVALID;
  }
  if (scheduling->tbit >= NR_UE_AIOT_D2R_TBIT_COUNT) {
    if (reason != NULL)
      *reason = "invalid_d2r_tbit";
    return NR_UE_AIOT_D2R_SCHED_INVALID;
  }

  const uint8_t allowed_sfs = allowed_sfs_masks[scheduling->tbit];
  if (scheduling->sfs_bitmap == 0) {
    if (reason != NULL)
      *reason = "empty_sfs_bitmap";
    return NR_UE_AIOT_D2R_SCHED_INVALID;
  }
  if ((scheduling->sfs_bitmap & (uint8_t)~allowed_sfs) != 0) {
    if (reason != NULL)
      *reason = "illegal_sfs_for_tbit";
    return NR_UE_AIOT_D2R_SCHED_ILLEGAL_SFS;
  }

  unsigned int enabled_factors = 0;
  for (uint8_t bits = scheduling->sfs_bitmap; bits != 0; bits >>= 1)
    enabled_factors += bits & 1;
  if (n_sfs != NULL)
    *n_sfs = enabled_factors;
  if (m != NULL)
    *m = enabled_factors * scheduling->x;
  return NR_UE_AIOT_D2R_SCHED_OK;
}

bool nr_ue_aiot_derive_d2r_timing(const nr_ue_aiot_d2r_scheduling_t *scheduling,
                                  unsigned int chips_per_symbol,
                                  nr_ue_aiot_d2r_timing_t *timing,
                                  const char **reason)
{
  if (reason != NULL)
    *reason = NULL;
  if (timing == NULL) {
    if (reason != NULL)
      *reason = "invalid_d2r_timing";
    return false;
  }

  unsigned int n_sfs = 0;
  if (nr_ue_aiot_validate_d2r_scheduling(scheduling, &n_sfs, NULL, reason)
      != NR_UE_AIOT_D2R_SCHED_OK)
    return false;

  static const uint32_t tbit_numerator[NR_UE_AIOT_D2R_TBIT_COUNT] = {2, 1, 1, 1, 1, 1, 1, 1};
  static const uint32_t tbit_denominator[NR_UE_AIOT_D2R_TBIT_COUNT] = {1, 1, 2, 4, 8, 16, 32, 96};
  unsigned int first_factor_index = 0;
  while ((scheduling->sfs_bitmap & (uint8_t)(0x80 >> first_factor_index)) == 0)
    ++first_factor_index;
  const uint32_t factor = 1U << first_factor_index;
  const uint32_t raw_denominator = 2 * factor * tbit_denominator[scheduling->tbit];
  uint32_t numerator = tbit_numerator[scheduling->tbit];
  uint32_t denominator = raw_denominator;
  while (denominator % numerator != 0) {
    const uint32_t remainder = denominator % numerator;
    denominator = numerator;
    numerator = remainder;
  }
  denominator /= numerator;
  numerator = 1;

  nr_ue_aiot_time_ratio_t derived_tchip = {
      .numerator = numerator,
      .denominator = denominator,
  };
  nr_ue_aiot_time_ratio_t derived_toffset;
  if (derived_tchip.numerator == 1 && derived_tchip.denominator <= 4) {
    derived_toffset = (nr_ue_aiot_time_ratio_t){.numerator = 10, .denominator = 1};
  } else if (derived_tchip.numerator == 1
             && (derived_tchip.denominator == 8 || derived_tchip.denominator == 16)) {
    derived_toffset = (nr_ue_aiot_time_ratio_t){.numerator = 5, .denominator = 1};
  } else if (derived_tchip.numerator == 1
             && (derived_tchip.denominator == 32 || derived_tchip.denominator == 64)) {
    derived_toffset = (nr_ue_aiot_time_ratio_t){.numerator = 1, .denominator = 1};
  } else if (derived_tchip.numerator == 1
             && (derived_tchip.denominator == 128 || derived_tchip.denominator == 192)) {
    if (chips_per_symbol == 2)
      derived_toffset = (nr_ue_aiot_time_ratio_t){.numerator = 1, .denominator = 1};
    else if (chips_per_symbol == 6 || chips_per_symbol == 12 || chips_per_symbol == 24)
      derived_toffset = (nr_ue_aiot_time_ratio_t){.numerator = 1, .denominator = 4};
    else {
      if (reason != NULL)
        *reason = "invalid_r2d_density";
      return false;
    }
  } else {
    if (reason != NULL)
      *reason = "unsupported_d2r_timing";
    return false;
  }

  (void)n_sfs;
  timing->tchip_prime = derived_tchip;
  timing->toffset = derived_toffset;
  return true;
}

static size_t aiot_t2_crc_bits(size_t payload_len)
{
  return payload_len * 8 <= 24 ? 6 : 16;
}

static uint32_t aiot_t2_crc(const uint8_t *payload, size_t payload_len)
{
  return aiot_t2_crc_bits(payload_len) == 6 ? crc6((uint8_t *)payload, payload_len * 8) >> 26
                                            : crc16((uint8_t *)payload, payload_len * 8) >> 16;
}

static void aiot_t2_encode_pair(uint8_t bit, c16_t *pair)
{
  pair[0].r = bit ? 0 : 1;
  pair[1].r = bit ? 1 : 0;
}

bool nr_ue_aiot_t2_prepare_r2d(uint32_t tag_id, openair0_timestamp timestamp, aiot_t2_rf_packet_t *packet)
{
  if (packet == NULL || tag_id == 0 || tag_id > 60)
    return false;

  const uint8_t command = AIOT_T2_INVENTORY_COMMAND;
  const size_t payload_bits = 8;
  const size_t crc_bits = aiot_t2_crc_bits(sizeof(command));
  const uint32_t crc = aiot_t2_crc(&command, sizeof(command));
  const size_t frame_bits = payload_bits + crc_bits;
  *packet = (aiot_t2_rf_packet_t){
      .header = {
          .size = frame_bits * AIOT_T2_MANCHESTER_CHIPS_PER_BIT,
          .nbAnt = 1,
          .timestamp = timestamp,
          .option_value = tag_id,
          .option_flag = OPTION_AIOT_T2_R2D,
          .beam_map = 1,
      },
  };
  for (size_t i = 0; i < frame_bits; ++i) {
    const uint8_t bit = i < payload_bits ? (command >> (7 - i)) & 1 : (crc >> (crc_bits - 1 - (i - payload_bits))) & 1;
    aiot_t2_encode_pair(bit, &packet->samples[i * AIOT_T2_MANCHESTER_CHIPS_PER_BIT]);
  }
  return true;
}

bool nr_ue_aiot_t2_prepare_r2d_with_resources(const nr_ue_aiot_r2d_request_t *request,
                                               aiot_t2_rf_packet_t *packet,
                                               const char **reason)
{
  if (reason != NULL)
    *reason = NULL;

  if (request == NULL || packet == NULL) {
    if (reason != NULL)
      *reason = "invalid_r2d_request";
    return false;
  }

  if (nr_ue_aiot_validate_r2d_resources(request->prb_count, request->chips_per_symbol, reason)
      != NR_UE_AIOT_R2D_RESOURCE_OK)
    return false;

  if (request->d2r_scheduling != NULL) {
    nr_ue_aiot_d2r_timing_t timing;
    if (!nr_ue_aiot_derive_d2r_timing(request->d2r_scheduling, request->chips_per_symbol, &timing, reason))
      return false;
  }

  if (request->tag_id == 0 || request->tag_id > 60) {
    if (reason != NULL)
      *reason = "invalid_tag_id";
    return false;
  }

  return nr_ue_aiot_t2_prepare_r2d(request->tag_id, request->timestamp, packet);
}

static bool aiot_t2_decode_pair(const c16_t *pair, uint8_t *bit)
{
  const bool first = pair[0].r != 0 || pair[0].i != 0;
  const bool second = pair[1].r != 0 || pair[1].i != 0;
  if (first == second)
    return false;
  *bit = second;
  return true;
}

nr_ue_aiot_t2_decode_result_t nr_ue_aiot_t2_decode_d2r(const aiot_t2_rf_packet_t *packet,
                                                       uint8_t *payload,
                                                       size_t payload_capacity,
                                                       size_t *payload_len)
{
  if (packet == NULL || payload == NULL || payload_len == NULL || packet->header.nbAnt != 1
      || (packet->header.option_flag & OPTION_AIOT_T2_D2R) == 0 || packet->header.option_value == 0
      || packet->header.option_value > 60 || packet->header.size == 0 || packet->header.size > AIOT_T2_MAX_RF_SAMPLES
      || packet->header.size % AIOT_T2_D2R_CHIPS_PER_BIT != 0)
    return NR_UE_AIOT_T2_INVALID_LENGTH;

  const size_t frame_bits = packet->header.size / AIOT_T2_D2R_CHIPS_PER_BIT;
  const size_t crc_bits = frame_bits <= 30 ? 6 : 16;
  if (frame_bits <= crc_bits || (frame_bits - crc_bits) % 8 != 0)
    return NR_UE_AIOT_T2_INVALID_LENGTH;
  *payload_len = (frame_bits - crc_bits) / 8;
  if (*payload_len == 0 || *payload_len > AIOT_T2_MAX_PAYLOAD_BYTES || *payload_len > payload_capacity)
    return NR_UE_AIOT_T2_INVALID_LENGTH;

  uint8_t frame_bits_decoded[AIOT_T2_MAX_RF_SAMPLES / AIOT_T2_D2R_CHIPS_PER_BIT];
  for (size_t i = 0; i < frame_bits; ++i) {
    uint8_t line_pair[2];
    const c16_t *encoded = &packet->samples[i * AIOT_T2_D2R_CHIPS_PER_BIT];
    if (!aiot_t2_decode_pair(encoded, &line_pair[0]) || !aiot_t2_decode_pair(encoded + 2, &line_pair[1])
        || (line_pair[0] == line_pair[1]))
      return NR_UE_AIOT_T2_INVALID_LINE_CODE;
    frame_bits_decoded[i] = line_pair[1];
  }

  memset(payload, 0, *payload_len);
  const size_t payload_bits = *payload_len * 8;
  for (size_t i = 0; i < payload_bits; ++i)
    payload[i / 8] |= frame_bits_decoded[i] << (7 - i % 8);

  uint32_t received_crc = 0;
  for (size_t i = 0; i < crc_bits; ++i)
    received_crc = (received_crc << 1) | frame_bits_decoded[payload_bits + i];
  return received_crc == aiot_t2_crc(payload, *payload_len) ? NR_UE_AIOT_T2_DECODE_OK : NR_UE_AIOT_T2_CRC_FAILURE;
}

void nr_get_carrier_frequencies(PHY_VARS_NR_UE *ue, uint64_t *dl_carrier, uint64_t *ul_carrier){

  NR_DL_FRAME_PARMS *fp = &ue->frame_parms;
  if (ue->if_freq!=0) {
    *dl_carrier = ue->if_freq;
    *ul_carrier = *dl_carrier + ue->if_freq_off;
  }
  else{
    *dl_carrier = fp->dl_CarrierFreq;
    *ul_carrier = fp->ul_CarrierFreq;
  }
}




void nr_rf_card_config_gain(openair0_config_t *openair0_cfg,
                            double rx_gain_off){

  uint8_t mod_id     = 0;
  uint8_t cc_id      = 0;
  PHY_VARS_NR_UE *ue = PHY_vars_UE_g[mod_id][cc_id];
  int rf_chain       = ue->rf_map.chain;
  double rx_gain     = ue->rx_total_gain_dB;
  double tx_gain     = ue->tx_total_gain_dB;

  for (int i = rf_chain; i < rf_chain + 4; i++) {

    if (tx_gain)
      openair0_cfg->tx_gain[i] = tx_gain;
    if (rx_gain)
      openair0_cfg->rx_gain[i] = rx_gain - rx_gain_off;

    openair0_cfg->autocal[i] = 1;

    if (i < openair0_cfg->rx_num_channels) {
      LOG_I(PHY, "HW: Configuring channel %d (rf_chain %d): setting tx_gain %.0f, rx_gain %.0f\n",
        i,
        rf_chain,
        openair0_cfg->tx_gain[i],
        openair0_cfg->rx_gain[i]);
    }

  }
}

void nr_rf_card_config_freq(openair0_config_t *openair0_cfg,
                            uint64_t ul_carrier,
                            uint64_t dl_carrier,
                            int freq_offset){

  uint8_t mod_id     = 0;
  uint8_t cc_id      = 0;
  PHY_VARS_NR_UE *ue = PHY_vars_UE_g[mod_id][cc_id];
  int rf_chain       = ue->rf_map.chain;
  double freq_scale  = (double)(dl_carrier + freq_offset) / dl_carrier;

  for (int i = rf_chain; i < rf_chain + 4; i++) {

    if (i < openair0_cfg->rx_num_channels)
      openair0_cfg->rx_freq[i + rf_chain] = dl_carrier * freq_scale;
    else
      openair0_cfg->rx_freq[i] = 0.0;

    if (i<openair0_cfg->tx_num_channels)
      openair0_cfg->tx_freq[i] = ul_carrier * freq_scale;
    else
      openair0_cfg->tx_freq[i] = 0.0;

    openair0_cfg->autocal[i] = 1;

    if (i < openair0_cfg->rx_num_channels) {
      LOG_I(PHY, "HW: Configuring channel %d (rf_chain %d): setting tx_freq %.0f Hz, rx_freq %.0f Hz, tune_offset %.0f\n",
        i,
        rf_chain,
        openair0_cfg->tx_freq[i],
        openair0_cfg->rx_freq[i],
        openair0_cfg->tune_offset);
    }

  }
}


void nr_sl_rf_card_config_freq(PHY_VARS_NR_UE *ue, openair0_config_t *openair0_cfg, int freq_offset) {

  for (int i = 0; i < openair0_cfg->rx_num_channels; i++) {
    openair0_cfg->rx_gain[ue->rf_map.chain + i] = ue->rx_total_gain_dB;
    if (ue->UE_scan_carrier == 1) {
      if (freq_offset >= 0)
        openair0_cfg->rx_freq[ue->rf_map.chain + i] += abs(freq_offset);
      else
        openair0_cfg->rx_freq[ue->rf_map.chain + i] -= abs(freq_offset);
      freq_offset=0;
    }
  }
}
