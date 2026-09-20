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
#define AIOT_T2_D2R_CHIPS_PER_BIT 2
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

static void nr_ue_aiot_cbra_put_bits(uint8_t *bytes, size_t *offset, uint64_t value, unsigned int width)
{
  for (unsigned int bit = 0; bit < width; ++bit) {
    const size_t position = *offset + bit;
    const uint8_t mask = (uint8_t)(1U << (7U - (position % 8U)));
    if ((value >> (width - 1U - bit)) & 1U)
      bytes[position / 8U] |= mask;
  }
  *offset += width;
}

static uint64_t nr_ue_aiot_cbra_get_bits(const uint8_t *bytes, size_t *offset, unsigned int width)
{
  uint64_t value = 0;
  for (unsigned int bit = 0; bit < width; ++bit) {
    const size_t position = *offset + bit;
    value = (value << 1U) | ((bytes[position / 8U] >> (7U - (position % 8U))) & 1U);
  }
  *offset += width;
  return value;
}

bool nr_ue_aiot_cbra_validate_serial(uint32_t serial,
                                     const uint32_t *existing_serials,
                                     size_t existing_count,
                                     const char **reason)
{
  if (reason != NULL)
    *reason = NULL;
  if (serial == 0) {
    if (reason != NULL)
      *reason = "invalid_serial";
    return false;
  }
  if (existing_count != 0 && existing_serials == NULL) {
    if (reason != NULL)
      *reason = "invalid_serial_set";
    return false;
  }
  for (size_t index = 0; index < existing_count; ++index) {
    if (existing_serials[index] == serial) {
      if (reason != NULL)
        *reason = "duplicate_serial";
      return false;
    }
  }
  return true;
}

bool nr_ue_aiot_cbra_build_paging_pdu(const nr_ue_aiot_cbra_paging_fields_t *fields,
                                      uint8_t pdu[NR_UE_AIOT_CBRA_PAGING_PDU_BYTES],
                                      const char **reason)
{
  if (reason != NULL)
    *reason = NULL;
  if (fields == NULL || pdu == NULL) {
    if (reason != NULL)
      *reason = "invalid_pdu_argument";
    return false;
  }
  if (!nr_ue_aiot_cbra_validate_serial(fields->serial, NULL, 0, reason))
    return false;
  if (fields->transaction_id > 63 || fields->number_of_access_occasions > 15 || fields->k > 1) {
    if (reason != NULL)
      *reason = "invalid_paging_field";
    return false;
  }
  nr_ue_aiot_cbra_d2r_scheduling_t scheduling = {0};
  if (!nr_ue_aiot_cbra_unpack_d2r_scheduling(fields->d2r_scheduling_info, &scheduling, reason)) {
    if (reason != NULL) *reason = "invalid_scheduling_info";
    return false;
  }

  memset(pdu, 0, NR_UE_AIOT_CBRA_PAGING_PDU_BYTES);
  size_t offset = 0;
  nr_ue_aiot_cbra_put_bits(pdu, &offset, 1, 3); /* CBRA Paging */
  nr_ue_aiot_cbra_put_bits(pdu, &offset, 27, 7); /* 28-byte TBS codepoint */
  nr_ue_aiot_cbra_put_bits(pdu, &offset, 1, 1); /* SPPI */
  for (size_t index = 0; index < NR_UE_AIOT_CBRA_SECURITY_BYTES; ++index)
    nr_ue_aiot_cbra_put_bits(pdu, &offset, fields->security_parameter[index], 8);
  nr_ue_aiot_cbra_put_bits(pdu, &offset, 1, 1); /* CBRA */
  nr_ue_aiot_cbra_put_bits(pdu, &offset, fields->transaction_id, 6);
  nr_ue_aiot_cbra_put_bits(pdu, &offset, 1, 1); /* PIPI */
  nr_ue_aiot_cbra_put_bits(pdu, &offset, 42, 10);
  nr_ue_aiot_cbra_put_bits(pdu, &offset, 1, 2); /* Permanent Identifier */
  nr_ue_aiot_cbra_put_bits(pdu, &offset, 0x08, 8); /* unstructured 32-bit ID */
  nr_ue_aiot_cbra_put_bits(pdu, &offset, fields->serial, 32);
  nr_ue_aiot_cbra_put_bits(pdu, &offset, fields->number_of_access_occasions, 4);
  nr_ue_aiot_cbra_put_bits(pdu, &offset, fields->d2r_scheduling_info, 18);
  nr_ue_aiot_cbra_put_bits(pdu, &offset, fields->k, 1);
  nr_ue_aiot_cbra_put_bits(pdu, &offset, 0, 2); /* fill */
  return offset == NR_UE_AIOT_CBRA_PAGING_PDU_BITS;
}

bool nr_ue_aiot_cbra_parse_paging_pdu(const uint8_t pdu[NR_UE_AIOT_CBRA_PAGING_PDU_BYTES],
                                      nr_ue_aiot_cbra_paging_fields_t *fields,
                                      const char **reason)
{
  if (reason != NULL)
    *reason = NULL;
  if (pdu == NULL || fields == NULL) {
    if (reason != NULL)
      *reason = "invalid_pdu_argument";
    return false;
  }

  nr_ue_aiot_cbra_paging_fields_t parsed = {0};
  size_t offset = 0;
  if (nr_ue_aiot_cbra_get_bits(pdu, &offset, 3) != 1) {
    if (reason != NULL)
      *reason = "invalid_message_type";
    return false;
  }
  if (nr_ue_aiot_cbra_get_bits(pdu, &offset, 7) != 27) {
    if (reason != NULL)
      *reason = "invalid_tbs";
    return false;
  }
  if (nr_ue_aiot_cbra_get_bits(pdu, &offset, 1) != 1) {
    if (reason != NULL)
      *reason = "security_parameter_absent";
    return false;
  }
  for (size_t index = 0; index < NR_UE_AIOT_CBRA_SECURITY_BYTES; ++index)
    parsed.security_parameter[index] = (uint8_t)nr_ue_aiot_cbra_get_bits(pdu, &offset, 8);
  if (nr_ue_aiot_cbra_get_bits(pdu, &offset, 1) != 1) {
    if (reason != NULL)
      *reason = "invalid_access_type";
    return false;
  }
  parsed.transaction_id = (uint8_t)nr_ue_aiot_cbra_get_bits(pdu, &offset, 6);
  if (nr_ue_aiot_cbra_get_bits(pdu, &offset, 1) != 1) {
    if (reason != NULL)
      *reason = "paging_id_present_missing";
    return false;
  }
  if (nr_ue_aiot_cbra_get_bits(pdu, &offset, 10) != 42) {
    if (reason != NULL)
      *reason = "invalid_paging_id_length";
    return false;
  }
  if (nr_ue_aiot_cbra_get_bits(pdu, &offset, 2) != 1
      || nr_ue_aiot_cbra_get_bits(pdu, &offset, 8) != 0x08) {
    if (reason != NULL)
      *reason = "invalid_paging_id_type";
    return false;
  }
  parsed.serial = (uint32_t)nr_ue_aiot_cbra_get_bits(pdu, &offset, 32);
  if (!nr_ue_aiot_cbra_validate_serial(parsed.serial, NULL, 0, reason))
    return false;
  parsed.number_of_access_occasions = (uint8_t)nr_ue_aiot_cbra_get_bits(pdu, &offset, 4);
  parsed.d2r_scheduling_info = (uint32_t)nr_ue_aiot_cbra_get_bits(pdu, &offset, 18);
  nr_ue_aiot_cbra_d2r_scheduling_t scheduling = {0};
  if (!nr_ue_aiot_cbra_unpack_d2r_scheduling(parsed.d2r_scheduling_info, &scheduling, reason)) {
    if (reason != NULL) *reason = "invalid_scheduling_info";
    return false;
  }
  parsed.k = (uint8_t)nr_ue_aiot_cbra_get_bits(pdu, &offset, 1);
  if (parsed.k > 1) {
    if (reason != NULL)
      *reason = "invalid_k";
    return false;
  }
  (void)nr_ue_aiot_cbra_get_bits(pdu, &offset, 2);
  if (offset != NR_UE_AIOT_CBRA_PAGING_PDU_BITS)
    return false;
  *fields = parsed;
  return true;
}

bool nr_ue_aiot_cbra_append_paging_crc(const uint8_t pdu[NR_UE_AIOT_CBRA_PAGING_PDU_BYTES],
                                       uint8_t phy_payload[NR_UE_AIOT_CBRA_PAGING_PHY_BYTES])
{
  if (pdu == NULL || phy_payload == NULL)
    return false;
  memset(phy_payload, 0, NR_UE_AIOT_CBRA_PAGING_PHY_BYTES);
  memcpy(phy_payload, pdu, NR_UE_AIOT_CBRA_PAGING_PDU_BYTES);
  const uint16_t crc = (uint16_t)(crc16((uint8_t *)pdu, NR_UE_AIOT_CBRA_PAGING_PDU_BITS) >> 16);
  size_t offset = NR_UE_AIOT_CBRA_PAGING_PDU_BITS;
  nr_ue_aiot_cbra_put_bits(phy_payload, &offset, crc, 16);
  return true;
}

bool nr_ue_aiot_cbra_verify_paging_crc(const uint8_t phy_payload[NR_UE_AIOT_CBRA_PAGING_PHY_BYTES])
{
  if (phy_payload == NULL)
    return false;
  const uint16_t expected = (uint16_t)(crc16((uint8_t *)phy_payload, NR_UE_AIOT_CBRA_PAGING_PDU_BITS) >> 16);
  size_t offset = NR_UE_AIOT_CBRA_PAGING_PDU_BITS;
  const uint16_t received = (uint16_t)nr_ue_aiot_cbra_get_bits(phy_payload, &offset, 16);
  return expected == received;
}

bool nr_ue_aiot_cbra_build_access_trigger(uint8_t trigger[NR_UE_AIOT_CBRA_TRIGGER_BYTES])
{
  if (trigger == NULL)
    return false;
  memset(trigger, 0, NR_UE_AIOT_CBRA_TRIGGER_BYTES);
  size_t offset = 0;
  nr_ue_aiot_cbra_put_bits(trigger, &offset, 2, NR_UE_AIOT_CBRA_TRIGGER_BITS);
  return true;
}

bool nr_ue_aiot_cbra_parse_access_trigger(const uint8_t trigger[NR_UE_AIOT_CBRA_TRIGGER_BYTES])
{
  if (trigger == NULL)
    return false;
  size_t offset = 0;
  return nr_ue_aiot_cbra_get_bits(trigger, &offset, NR_UE_AIOT_CBRA_TRIGGER_BITS) == 2;
}

bool nr_ue_aiot_cbra_append_access_trigger_crc(const uint8_t trigger[NR_UE_AIOT_CBRA_TRIGGER_BYTES],
                                               uint8_t phy_payload[NR_UE_AIOT_CBRA_TRIGGER_PHY_BYTES])
{
  if (trigger == NULL || phy_payload == NULL || !nr_ue_aiot_cbra_parse_access_trigger(trigger))
    return false;
  memset(phy_payload, 0, NR_UE_AIOT_CBRA_TRIGGER_PHY_BYTES);
  size_t offset = 0;
  nr_ue_aiot_cbra_put_bits(phy_payload, &offset, 2, NR_UE_AIOT_CBRA_TRIGGER_BITS);
  const uint8_t crc = (uint8_t)(crc6((uint8_t *)trigger, NR_UE_AIOT_CBRA_TRIGGER_BITS) >> 26);
  nr_ue_aiot_cbra_put_bits(phy_payload, &offset, crc, 6);
  return true;
}

bool nr_ue_aiot_cbra_verify_access_trigger_crc(const uint8_t phy_payload[NR_UE_AIOT_CBRA_TRIGGER_PHY_BYTES])
{
  if (phy_payload == NULL)
    return false;
  size_t offset = 0;
  if (nr_ue_aiot_cbra_get_bits(phy_payload, &offset, NR_UE_AIOT_CBRA_TRIGGER_BITS) != 2)
    return false;
  const uint8_t expected = (uint8_t)(crc6((uint8_t *)phy_payload, NR_UE_AIOT_CBRA_TRIGGER_BITS) >> 26);
  const uint8_t received = (uint8_t)nr_ue_aiot_cbra_get_bits(phy_payload, &offset, 6);
  return expected == received;
}

bool nr_ue_aiot_cbra_pack_d2r_scheduling(const nr_ue_aiot_cbra_d2r_scheduling_t *scheduling,
                                         uint32_t *packed,
                                         const char **reason)
{
  if (reason != NULL)
    *reason = NULL;
  if (scheduling == NULL || packed == NULL) {
    if (reason != NULL)
      *reason = "invalid_scheduling_argument";
    return false;
  }
  if (scheduling->x < 1 || scheduling->x > 2 || scheduling->bit_duration >= NR_UE_AIOT_D2R_TBIT_COUNT) {
    if (reason != NULL)
      *reason = "invalid_d2r_tbit";
    return false;
  }
  const nr_ue_aiot_d2r_scheduling_t legacy_schedule = {
      .x = scheduling->x,
      .tbit = (nr_ue_aiot_d2r_tbit_t)scheduling->bit_duration,
      .sfs_bitmap = scheduling->frequency_resource_broadcast,
  };
  if (nr_ue_aiot_validate_d2r_scheduling(&legacy_schedule, NULL, NULL, reason)
      != NR_UE_AIOT_D2R_SCHED_OK)
    return false;
  if (scheduling->block_repetition > 1 || scheduling->channel_coding > 1
      || scheduling->interval_bits > 3 || scheduling->sequence_length > 1
      || scheduling->additional_midamble > 1) {
    if (reason != NULL)
      *reason = "invalid_scheduling_field";
    return false;
  }

  uint8_t bytes[3] = {0};
  size_t offset = 0;
  nr_ue_aiot_cbra_put_bits(bytes, &offset, scheduling->x - 1U, 1);
  nr_ue_aiot_cbra_put_bits(bytes, &offset, scheduling->bit_duration, 3);
  nr_ue_aiot_cbra_put_bits(bytes, &offset, scheduling->frequency_resource_broadcast, 8);
  nr_ue_aiot_cbra_put_bits(bytes, &offset, scheduling->block_repetition, 1);
  nr_ue_aiot_cbra_put_bits(bytes, &offset, scheduling->channel_coding, 1);
  nr_ue_aiot_cbra_put_bits(bytes, &offset, scheduling->interval_bits, 2);
  nr_ue_aiot_cbra_put_bits(bytes, &offset, scheduling->sequence_length, 1);
  nr_ue_aiot_cbra_put_bits(bytes, &offset, scheduling->additional_midamble, 1);
  *packed = (((uint32_t)bytes[0] << 16) | ((uint32_t)bytes[1] << 8) | bytes[2]) >> 6;
  return true;
}

bool nr_ue_aiot_cbra_unpack_d2r_scheduling(uint32_t packed,
                                           nr_ue_aiot_cbra_d2r_scheduling_t *scheduling,
                                           const char **reason)
{
  if (reason != NULL)
    *reason = NULL;
  if (scheduling == NULL || (packed & ~0x3ffffU) != 0) {
    if (reason != NULL)
      *reason = "invalid_scheduling_info";
    return false;
  }
  nr_ue_aiot_cbra_d2r_scheduling_t decoded = {
      .x = (uint8_t)(((packed >> 17) & 1U) + 1U),
      .bit_duration = (uint8_t)((packed >> 14) & 7U),
      .frequency_resource_broadcast = (uint8_t)((packed >> 6) & 0xffU),
      .block_repetition = (uint8_t)((packed >> 5) & 1U),
      .channel_coding = (uint8_t)((packed >> 4) & 1U),
      .interval_bits = (uint8_t)((packed >> 2) & 3U),
      .sequence_length = (uint8_t)((packed >> 1) & 1U),
      .additional_midamble = (uint8_t)(packed & 1U),
  };
  const nr_ue_aiot_d2r_scheduling_t legacy_schedule = {
      .x = decoded.x,
      .tbit = (nr_ue_aiot_d2r_tbit_t)decoded.bit_duration,
      .sfs_bitmap = decoded.frequency_resource_broadcast,
  };
  if (nr_ue_aiot_validate_d2r_scheduling(&legacy_schedule, NULL, NULL, reason) != NR_UE_AIOT_D2R_SCHED_OK
      || decoded.block_repetition > 1 || decoded.channel_coding > 1 || decoded.interval_bits > 3
      || decoded.sequence_length > 1 || decoded.additional_midamble > 1)
    return false;
  *scheduling = decoded;
  return true;
}

bool nr_ue_aiot_cbra_validate_campaign_config(const nr_ue_aiot_cbra_campaign_config_t *config,
                                              const char **reason)
{
  if (reason != NULL)
    *reason = NULL;
  if (config == NULL) {
    if (reason != NULL)
      *reason = "invalid_campaign_argument";
    return false;
  }
  if (config->message_kind != NR_UE_AIOT_CBRA_PAGING
      && config->message_kind != NR_UE_AIOT_CBRA_ACCESS_TRIGGER) {
    if (reason != NULL)
      *reason = "invalid_message_kind";
    return false;
  }
  if (config->m != 2 && config->m != 6 && config->m != 12 && config->m != 24) {
    if (reason != NULL)
      *reason = "invalid_m";
    return false;
  }
  if (config->prb_count != 3) {
    if (reason != NULL)
      *reason = "invalid_prb_count";
    return false;
  }
  if (config->formal_packet_budget != 10000) {
    if (reason != NULL)
      *reason = "invalid_formal_budget";
    return false;
  }
  if (config->data_seed == 0 || config->noise_seed == 0 || config->data_seed == config->noise_seed) {
    if (reason != NULL)
      *reason = config->data_seed == config->noise_seed ? "duplicate_seed" : "invalid_seed";
    return false;
  }
  if (config->snr_grid_db_x10 == NULL || config->snr_grid_count == 0) {
    if (reason != NULL)
      *reason = "invalid_snr_grid";
    return false;
  }
  for (size_t index = 1; index < config->snr_grid_count; ++index) {
    if (config->snr_grid_db_x10[index] <= config->snr_grid_db_x10[index - 1]) {
      if (reason != NULL)
        *reason = "invalid_snr_grid";
      return false;
    }
  }
  nr_ue_aiot_cbra_d2r_scheduling_t scheduling = {0};
  if (!nr_ue_aiot_cbra_unpack_d2r_scheduling(config->d2r_scheduling_info, &scheduling, reason)) {
    if (reason != NULL) *reason = "invalid_scheduling_info";
    return false;
  }
  return true;
}

bool nr_ue_aiot_cbra_derive_frame(nr_ue_aiot_cbra_message_kind_t message_kind,
                                  uint8_t m,
                                  uint8_t prb_count,
                                  nr_ue_aiot_cbra_frame_t *frame,
                                  const char **reason)
{
  if (reason != NULL)
    *reason = NULL;
  if (frame == NULL
      || (message_kind != NR_UE_AIOT_CBRA_PAGING && message_kind != NR_UE_AIOT_CBRA_ACCESS_TRIGGER)) {
    if (reason != NULL)
      *reason = "invalid_frame_argument";
    return false;
  }
  if (prb_count != 3) {
    if (reason != NULL)
      *reason = "invalid_prb_count";
    return false;
  }
  if (nr_ue_aiot_validate_r2d_resources(prb_count, m, reason) != NR_UE_AIOT_R2D_RESOURCE_OK)
    return false;

  const uint16_t mac_bits = message_kind == NR_UE_AIOT_CBRA_PAGING ? NR_UE_AIOT_CBRA_PAGING_PDU_BITS
                                                                     : NR_UE_AIOT_CBRA_TRIGGER_BITS;
  const uint16_t phy_bits = message_kind == NR_UE_AIOT_CBRA_PAGING ? NR_UE_AIOT_CBRA_PAGING_PHY_BITS
                                                                     : NR_UE_AIOT_CBRA_TRIGGER_PHY_BITS;
  const uint16_t data_and_overhead_chips = AIOT_T2_CBRA_CAP_CHIPS
                                           + phy_bits * AIOT_T2_MANCHESTER_CHIPS_PER_BIT
                                           + AIOT_T2_CBRA_POSTAMBLE_CHIPS;
  const uint16_t usable_chips_per_symbol = m == 24 ? 22 : m;
  const uint16_t symbols_after_sip = (data_and_overhead_chips + usable_chips_per_symbol - 1U)
                                     / usable_chips_per_symbol;
  const uint16_t frame_symbols = (uint16_t)(2U + symbols_after_sip);
  const uint32_t mapping_positions = (uint32_t)symbols_after_sip * m;
  const uint32_t mapping_reserved_chips = m == 24 ? (uint32_t)symbols_after_sip * 2U : 0U;
  const uint32_t padding_chips = mapping_positions - mapping_reserved_chips - data_and_overhead_chips;
  const uint32_t emitted_chip_count = AIOT_T2_CBRA_SIP_CHIPS + mapping_positions;
  const uint32_t long_cp_count = (frame_symbols + 6U) / 7U;
  const uint32_t short_cp_count = frame_symbols - long_cp_count;
  const uint32_t ofdm_sample_count = frame_symbols * NR_UE_AIOT_CBRA_USEFUL_SAMPLES_PER_SYMBOL
                                     + long_cp_count * NR_UE_AIOT_CBRA_LONG_CP_SAMPLES
                                     + short_cp_count * NR_UE_AIOT_CBRA_SHORT_CP_SAMPLES;
  *frame = (nr_ue_aiot_cbra_frame_t){
      .message_kind = message_kind,
      .m = m,
      .prb_count = prb_count,
      .mac_bits = mac_bits,
      .phy_bits = phy_bits,
      .prdch_chips = phy_bits * AIOT_T2_MANCHESTER_CHIPS_PER_BIT,
      .frame_symbols = frame_symbols,
      .occupied_chip_positions = (uint16_t)emitted_chip_count,
      .r_tas_sip_chips = AIOT_T2_CBRA_SIP_CHIPS,
      .r_tas_cap_chips = AIOT_T2_CBRA_CAP_CHIPS,
      .postamble_chips = AIOT_T2_CBRA_POSTAMBLE_CHIPS,
      .data_and_overhead_chips = data_and_overhead_chips,
      .padding_chips = (uint16_t)padding_chips,
      .mapping_reserved_chips = (uint16_t)mapping_reserved_chips,
      .emitted_chip_count = emitted_chip_count,
      .ofdm_sample_count = ofdm_sample_count,
      .on_air_duration_ns = ((uint64_t)ofdm_sample_count * 1000000000ULL
                             + NR_UE_AIOT_CBRA_SAMPLE_RATE_HZ / 2U)
                            / NR_UE_AIOT_CBRA_SAMPLE_RATE_HZ,
  };
  return true;
}

static uint8_t nr_ue_aiot_cbra_framing_bit(const uint8_t *phy_payload,
                                           uint16_t phy_bits,
                                           size_t sequence_index)
{
  if (sequence_index < AIOT_T2_CBRA_CAP_CHIPS)
    return (0xAU >> (AIOT_T2_CBRA_CAP_CHIPS - 1U - sequence_index)) & 1U;

  sequence_index -= AIOT_T2_CBRA_CAP_CHIPS;
  if (sequence_index < phy_bits * AIOT_T2_MANCHESTER_CHIPS_PER_BIT) {
    const size_t bit_index = sequence_index / AIOT_T2_MANCHESTER_CHIPS_PER_BIT;
    const uint8_t bit = (phy_payload[bit_index / 8U] >> (7U - (bit_index % 8U))) & 1U;
    return sequence_index % AIOT_T2_MANCHESTER_CHIPS_PER_BIT == 0 ? (uint8_t)!bit : bit;
  }

  sequence_index -= phy_bits * AIOT_T2_MANCHESTER_CHIPS_PER_BIT;
  return (0xFU >> (AIOT_T2_CBRA_POSTAMBLE_CHIPS - 1U - sequence_index)) & 1U;
}

static bool nr_ue_aiot_cbra_encode_frame(const uint8_t *phy_payload,
                                         const nr_ue_aiot_cbra_frame_t *frame,
                                         c16_t *samples,
                                         size_t sample_capacity,
                                         const char **reason)
{
  if (reason != NULL)
    *reason = NULL;
  if (phy_payload == NULL || frame == NULL || samples == NULL) {
    if (reason != NULL)
      *reason = "invalid_frame_encoder_argument";
    return false;
  }
  if (frame->emitted_chip_count > sample_capacity) {
    if (reason != NULL)
      *reason = "frame_exceeds_sample_capacity";
    return false;
  }

  size_t output_index = 0;
  for (size_t index = 0; index < AIOT_T2_CBRA_SIP_CHIPS; ++index) {
    samples[output_index].r = (0xC8U >> (AIOT_T2_CBRA_SIP_CHIPS - 1U - index)) & 1U;
    samples[output_index].i = 0;
    ++output_index;
  }

  size_t sequence_index = 0;
  for (uint16_t symbol = 0; symbol < frame->frame_symbols - 2U; ++symbol) {
    for (uint8_t position = 0; position < frame->m; ++position) {
      const bool reserved = frame->m == 24 && position >= frame->m - 2U;
      uint8_t chip;
      if (reserved) {
        chip = 1;
      } else if (sequence_index < frame->data_and_overhead_chips) {
        chip = nr_ue_aiot_cbra_framing_bit(phy_payload, frame->phy_bits, sequence_index++);
      } else {
        const size_t padding_index = sequence_index - frame->data_and_overhead_chips;
        chip = frame->m == 24 && frame->padding_chips >= 2 && padding_index >= frame->padding_chips - 2U ? 1U : 0U;
        ++sequence_index;
      }
      samples[output_index].r = chip;
      samples[output_index].i = 0;
      ++output_index;
    }
  }

  if (output_index != frame->emitted_chip_count
      || sequence_index != frame->data_and_overhead_chips + frame->padding_chips) {
    if (reason != NULL)
      *reason = "frame_geometry_mismatch";
    return false;
  }
  return true;
}

static bool nr_ue_aiot_cbra_prepare_r2d(nr_ue_aiot_cbra_message_kind_t message_kind,
                                        const uint8_t *phy_payload,
                                        uint32_t tag_id,
                                        uint32_t reader_handle,
                                        openair0_timestamp timestamp,
                                        uint8_t m,
                                        uint8_t prb_count,
                                        aiot_t2_rf_packet_t *packet,
                                        const char **reason)
{
  if (reason != NULL)
    *reason = NULL;
  if (phy_payload == NULL || packet == NULL) {
    if (reason != NULL)
      *reason = "invalid_r2d_request";
    return false;
  }
  if (tag_id == 0 || tag_id > AIOT_T2_MAX_TAG_ID) {
    if (reason != NULL)
      *reason = "invalid_tag_id";
    return false;
  }
  if (reader_handle == 0 || reader_handle > AIOT_T2_MAX_READER_HANDLES) {
    if (reason != NULL)
      *reason = "invalid_reader_handle";
    return false;
  }
  nr_ue_aiot_cbra_frame_t frame;
  if (!nr_ue_aiot_cbra_derive_frame(message_kind, m, prb_count, &frame, reason))
    return false;

  aiot_t2_rf_packet_t prepared = {
      .header = {
          .size = frame.emitted_chip_count,
          .nbAnt = 1,
          .timestamp = timestamp,
          .option_value = AIOT_T2_PACK_CBRA_R2D_TARGET(tag_id, reader_handle, m, message_kind),
          .option_flag = OPTION_AIOT_T2_R2D | OPTION_AIOT_T2_R2D_CBRA,
          .beam_map = 1,
      },
  };
  if (!nr_ue_aiot_cbra_encode_frame(phy_payload, &frame, prepared.samples, AIOT_T2_MAX_RF_SAMPLES, reason))
    return false;
  *packet = prepared;
  return true;
}

bool nr_ue_aiot_cbra_prepare_paging_r2d(const nr_ue_aiot_cbra_paging_fields_t *fields,
                                        uint32_t tag_id,
                                        uint32_t reader_handle,
                                        openair0_timestamp timestamp,
                                        uint8_t m,
                                        uint8_t prb_count,
                                        aiot_t2_rf_packet_t *packet,
                                        const char **reason)
{
  uint8_t pdu[NR_UE_AIOT_CBRA_PAGING_PDU_BYTES] = {0};
  uint8_t phy_payload[NR_UE_AIOT_CBRA_PAGING_PHY_BYTES] = {0};
  if (!nr_ue_aiot_cbra_build_paging_pdu(fields, pdu, reason)
      || !nr_ue_aiot_cbra_append_paging_crc(pdu, phy_payload))
    return false;
  return nr_ue_aiot_cbra_prepare_r2d(NR_UE_AIOT_CBRA_PAGING,
                                     phy_payload,
                                     tag_id,
                                     reader_handle,
                                     timestamp,
                                     m,
                                     prb_count,
                                     packet,
                                     reason);
}

bool nr_ue_aiot_cbra_prepare_access_trigger_r2d(uint32_t tag_id,
                                               uint32_t reader_handle,
                                               openair0_timestamp timestamp,
                                               uint8_t m,
                                               uint8_t prb_count,
                                               aiot_t2_rf_packet_t *packet,
                                               const char **reason)
{
  uint8_t trigger[NR_UE_AIOT_CBRA_TRIGGER_BYTES] = {0};
  uint8_t phy_payload[NR_UE_AIOT_CBRA_TRIGGER_PHY_BYTES] = {0};
  if (!nr_ue_aiot_cbra_build_access_trigger(trigger)
      || !nr_ue_aiot_cbra_append_access_trigger_crc(trigger, phy_payload))
    return false;
  return nr_ue_aiot_cbra_prepare_r2d(NR_UE_AIOT_CBRA_ACCESS_TRIGGER,
                                     phy_payload,
                                     tag_id,
                                     reader_handle,
                                     timestamp,
                                     m,
                                     prb_count,
                                     packet,
                                     reason);
}

static void aiot_t2_encode_pair(uint8_t bit, c16_t *pair)
{
  pair[0].r = bit ? 0 : 1;
  pair[1].r = bit ? 1 : 0;
}

bool nr_ue_aiot_t2_prepare_r2d(uint32_t tag_id, openair0_timestamp timestamp, aiot_t2_rf_packet_t *packet)
{
  if (packet == NULL || tag_id == 0 || tag_id > AIOT_T2_MAX_TAG_ID)
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

  if (request->tag_id == 0 || request->tag_id > AIOT_T2_MAX_TAG_ID) {
    if (reason != NULL)
      *reason = "invalid_tag_id";
    return false;
  }

  return nr_ue_aiot_t2_prepare_r2d(request->tag_id, request->timestamp, packet);
}

static uint64_t aiot_t2_sample_energy(const c16_t *sample)
{
  const int64_t real = sample->r;
  const int64_t imag = sample->i;
  return (uint64_t)(real * real + imag * imag);
}

static bool aiot_t2_decode_pair(const c16_t *pair, uint8_t *bit)
{
  const uint64_t first_energy = aiot_t2_sample_energy(&pair[0]);
  const uint64_t second_energy = aiot_t2_sample_energy(&pair[1]);
  if (first_energy == second_energy)
    return false;
  *bit = second_energy > first_energy;
  return true;
}

nr_ue_aiot_t2_decode_result_t nr_ue_aiot_t2_decode_d2r(const aiot_t2_rf_packet_t *packet,
                                                       uint8_t *payload,
                                                       size_t payload_capacity,
                                                       size_t *payload_len)
{
  const uint32_t tag_id = packet == NULL ? 0 : AIOT_T2_UNPACK_TAG(packet->header.option_value);
  if (packet == NULL || payload == NULL || payload_len == NULL || packet->header.nbAnt != 1
      || (packet->header.option_flag & OPTION_AIOT_T2_D2R) == 0 || tag_id == 0
      || tag_id > AIOT_T2_MAX_TAG_ID || packet->header.size == 0 || packet->header.size > AIOT_T2_MAX_RF_SAMPLES
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
    const c16_t *encoded = &packet->samples[i * AIOT_T2_D2R_CHIPS_PER_BIT];
    if (!aiot_t2_decode_pair(encoded, &frame_bits_decoded[i]))
      return NR_UE_AIOT_T2_INVALID_LINE_CODE;
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
