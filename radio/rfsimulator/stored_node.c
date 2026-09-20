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
* Author and copyright: Laurent Thomas, open-cells.com
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


#include <common/utils/simple_executable.h>
#include "PHY/CODING/coding_defs.h"
#include "radio/COMMON/common_lib.h"
#include <arpa/inet.h>
#include <math.h>
#include <stdlib.h>

#define AIOT_MAX_PAYLOAD_BYTES 16
#define AIOT_MAX_FRAME_BITS (AIOT_MAX_PAYLOAD_BYTES * 8 + 16)
#define AIOT_MANCHESTER_CHIPS_PER_BIT 2
#define AIOT_SFS_FACTOR 1
#define AIOT_D2R_CHIPS_PER_FRAME_BIT (AIOT_MANCHESTER_CHIPS_PER_BIT * AIOT_SFS_FACTOR)
#define AIOT_RESPONSE_TIMEOUT_MS 100
#define AIOT_INVENTORY_COMMAND 0x01
#define AIOT_CBRA_PDU_BYTES 28
#define AIOT_CBRA_PHY_BYTES 30
#define AIOT_CBRA_FRAME_BITS (AIOT_CBRA_PHY_BYTES * 8)
#define AIOT_CBRA_CHIPS_PER_FRAME (AIOT_CBRA_FRAME_BITS * AIOT_MANCHESTER_CHIPS_PER_BIT)
#define AIOT_CBRA_SIP_CHIPS AIOT_T2_CBRA_SIP_CHIPS
#define AIOT_CBRA_CAP_CHIPS AIOT_T2_CBRA_CAP_CHIPS
#define AIOT_CBRA_POSTAMBLE_CHIPS AIOT_T2_CBRA_POSTAMBLE_CHIPS
#define AIOT_CBRA_SAMPLE_RATE_HZ AIOT_T2_CBRA_SAMPLE_RATE_HZ
#define AIOT_CBRA_USEFUL_SAMPLES_PER_SYMBOL AIOT_T2_CBRA_USEFUL_SAMPLES_PER_SYMBOL
#define AIOT_CBRA_DECIMATION 4U
#define AIOT_CBRA_PRE_B0 0.05238376449658677
#define AIOT_CBRA_PRE_B1 0.05238376449658677
#define AIOT_CBRA_PRE_A1 0.8952324710068265
#define AIOT_CBRA_PRE2_B0 0.002887387866824493
#define AIOT_CBRA_PRE2_B1 0.005774775733648986
#define AIOT_CBRA_PRE2_B2 0.002887387866824493
#define AIOT_CBRA_PRE2_A1 -1.8839854240315808
#define AIOT_CBRA_PRE2_A2 0.8955349754988786
#define AIOT_CBRA_SMOOTH_B0 0.09982727525033994
#define AIOT_CBRA_SMOOTH_B1 0.09982727525033994
#define AIOT_CBRA_SMOOTH_A1 0.8003454494993202
#define AIOT_CBRA_SMOOTH2_B0 0.010949419306238512
#define AIOT_CBRA_SMOOTH2_B1 0.021898838612477024
#define AIOT_CBRA_SMOOTH2_B2 0.010949419306238512
#define AIOT_CBRA_SMOOTH2_A1 -1.7587338736641966
#define AIOT_CBRA_SMOOTH2_A2 0.8025315508891506
#define AIOT_CBRA_FROZEN_D2R_SCHEDULING_INFO 0x00006014U
#define AIOT_CBRA_TRIGGER_BITS 3U
#define AIOT_CBRA_TRIGGER_PHY_BITS 9U
#define AIOT_CBRA_TRIGGER_BYTES 2U
#define AIOT_RFSIM_MAX_SAMPLES (1U << 20)
#define AIOT_T2_MAX_TAG_CYCLES 10001U

typedef enum {
  AIOT_RESULT_OK,
  AIOT_RESULT_INVALID_LINE_CODE,
  AIOT_RESULT_CRC_FAILURE,
  AIOT_RESULT_CW_ABSENT,
  AIOT_RESULT_READER_ASLEEP,
  AIOT_RESULT_PAYLOAD_LENGTH,
  AIOT_RESULT_TIMEOUT,
} aiot_result_t;

typedef enum {
  AIOT_FAULT_NONE,
  AIOT_FAULT_INVALID_00,
  AIOT_FAULT_INVALID_11,
  AIOT_FAULT_CRC,
  AIOT_FAULT_TIMEOUT,
} aiot_fault_t;

typedef struct {
  bool cw_present;
  bool reader_awake;
  uint32_t elapsed_ms;
} aiot_tag_state_t;

typedef struct {
  double b0;
  double b1;
  double b2;
  double a1;
  double a2;
  double x1;
  double x2;
  double y1;
  double y2;
} aiot_cbra_iir_section_t;

typedef struct {
  aiot_cbra_iir_section_t real[2];
  aiot_cbra_iir_section_t imag[2];
} aiot_cbra_complex_filter_t;

typedef struct {
  aiot_cbra_complex_filter_t preselection;
  aiot_cbra_iir_section_t smoothing[2];
  uint64_t input_sample_index;
  uint64_t output_sample_index;
  double calibrated_delay_samples;
} aiot_cbra_receiver_t;

static bool aiot_cbra_frame_geometry(uint32_t phy_bits,
                                     uint32_t m,
                                     size_t *frame_chips,
                                     size_t *padding_chips,
                                     size_t *reserved_chips);

static void aiot_cbra_init_section(aiot_cbra_iir_section_t *section,
                                  double b0,
                                  double b1,
                                  double b2,
                                  double a1,
                                  double a2)
{
  *section = (aiot_cbra_iir_section_t){.b0 = b0, .b1 = b1, .b2 = b2, .a1 = a1, .a2 = a2};
}

static double aiot_cbra_process_section(aiot_cbra_iir_section_t *section, double input)
{
  const double output = section->b0 * input + section->b1 * section->x1 + section->b2 * section->x2
                        - section->a1 * section->y1 - section->a2 * section->y2;
  section->x2 = section->x1;
  section->x1 = input;
  section->y2 = section->y1;
  section->y1 = output;
  return output;
}

static double aiot_cbra_process_real_filter(aiot_cbra_iir_section_t sections[2], double input)
{
  input = aiot_cbra_process_section(&sections[0], input);
  return aiot_cbra_process_section(&sections[1], input);
}

static double aiot_cbra_process_complex_filter(aiot_cbra_complex_filter_t *filter, double *real, double *imag)
{
  *real = aiot_cbra_process_real_filter(filter->real, *real);
  *imag = aiot_cbra_process_real_filter(filter->imag, *imag);
  return *real * *real + *imag * *imag;
}

static size_t aiot_cbra_symbol_start_samples(size_t symbol)
{
  const size_t long_cp_count = (symbol + 6U) / 7U;
  const size_t short_cp_count = symbol - long_cp_count;
  return symbol * AIOT_CBRA_USEFUL_SAMPLES_PER_SYMBOL + long_cp_count * 80U + short_cp_count * 72U;
}

static void aiot_cbra_receiver_init(aiot_cbra_receiver_t *receiver)
{
  memset(receiver, 0, sizeof(*receiver));
  aiot_cbra_init_section(&receiver->preselection.real[0],
                        AIOT_CBRA_PRE_B0,
                        AIOT_CBRA_PRE_B1,
                        0.0,
                        AIOT_CBRA_PRE_A1,
                        0.0);
  aiot_cbra_init_section(&receiver->preselection.real[1],
                        AIOT_CBRA_PRE2_B0,
                        AIOT_CBRA_PRE2_B1,
                        AIOT_CBRA_PRE2_B2,
                        AIOT_CBRA_PRE2_A1,
                        AIOT_CBRA_PRE2_A2);
  receiver->preselection.imag[0] = receiver->preselection.real[0];
  receiver->preselection.imag[1] = receiver->preselection.real[1];
  aiot_cbra_init_section(&receiver->smoothing[0],
                        AIOT_CBRA_SMOOTH_B0,
                        AIOT_CBRA_SMOOTH_B1,
                        0.0,
                        AIOT_CBRA_SMOOTH_A1,
                        0.0);
  aiot_cbra_init_section(&receiver->smoothing[1],
                        AIOT_CBRA_SMOOTH2_B0,
                        AIOT_CBRA_SMOOTH2_B1,
                        AIOT_CBRA_SMOOTH2_B2,
                        AIOT_CBRA_SMOOTH2_A1,
                        AIOT_CBRA_SMOOTH2_A2);
}

static bool aiot_cbra_receiver_energies(const c16_t *samples,
                                       size_t sample_count,
                                       uint32_t phy_bits,
                                       uint32_t m,
                                       aiot_cbra_receiver_t *receiver,
                                       double *chip_energies,
                                       size_t chip_capacity,
                                       double *signal_power,
                                       double *noise_power)
{
  if (signal_power != NULL)
    *signal_power = 0.0;
  if (noise_power != NULL)
    *noise_power = 0.0;
  size_t frame_chips = 0;
  size_t padding_chips = 0;
  size_t reserved_chips = 0;
  if (samples == NULL || receiver == NULL || chip_energies == NULL
      || !aiot_cbra_frame_geometry(phy_bits, m, &frame_chips, &padding_chips, &reserved_chips)
      || chip_capacity < frame_chips)
    return false;

  const size_t symbols_after_sip = (frame_chips - AIOT_CBRA_SIP_CHIPS) / m;
  const size_t frame_symbols = 2U + symbols_after_sip;
  const size_t high_rate_samples = aiot_cbra_symbol_start_samples(frame_symbols);
  if (sample_count != high_rate_samples)
    return false;
  const size_t output_capacity = (sample_count + AIOT_CBRA_DECIMATION - 1U) / AIOT_CBRA_DECIMATION;
  double *decimated = calloc(output_capacity, sizeof(*decimated));
  double *preselection_decimated = calloc(output_capacity, sizeof(*preselection_decimated));
  if (decimated == NULL || preselection_decimated == NULL) {
    free(decimated);
    free(preselection_decimated);
    return false;
  }

  size_t output_count = 0;
  size_t symbol = 0;
  size_t symbol_start = 0;
  size_t symbol_end = 80U + AIOT_CBRA_USEFUL_SAMPLES_PER_SYMBOL;
  for (size_t input_index = 0; input_index < sample_count; ++input_index) {
    while (symbol + 1U < frame_symbols && input_index >= symbol_end) {
      ++symbol;
      symbol_start = aiot_cbra_symbol_start_samples(symbol);
      symbol_end = symbol_start + (symbol % 7U == 0 ? 80U : 72U) + AIOT_CBRA_USEFUL_SAMPLES_PER_SYMBOL;
    }
    double real = samples[input_index].r;
    double imag = samples[input_index].i;
    const double preselection_power = aiot_cbra_process_complex_filter(&receiver->preselection, &real, &imag);
    const double power = aiot_cbra_process_real_filter(receiver->smoothing, preselection_power);
    if (receiver->input_sample_index % AIOT_CBRA_DECIMATION == AIOT_CBRA_DECIMATION - 1U) {
      decimated[output_count++] = power;
      preselection_decimated[output_count - 1U] = preselection_power;
    }
    ++receiver->input_sample_index;
  }
  receiver->output_sample_index += output_count;

  size_t sequence_index = 0;
  size_t power_pair_count = 0;
  double signal_power_sum = 0.0;
  double noise_power_sum = 0.0;
  double first_preselection_power = 0.0;
  for (size_t chip_index = 0; chip_index < frame_chips; ++chip_index) {
    const size_t chip_symbol = chip_index < AIOT_CBRA_SIP_CHIPS ? chip_index / 4U
                                                                : 2U + (chip_index - AIOT_CBRA_SIP_CHIPS) / m;
    const size_t chip_position = chip_index < AIOT_CBRA_SIP_CHIPS ? chip_index % 4U
                                                                  : (chip_index - AIOT_CBRA_SIP_CHIPS) % m;
    const double chip_span = chip_index < AIOT_CBRA_SIP_CHIPS ? 256.0 : 1024.0 / m;
    const double useful_start = (double)aiot_cbra_symbol_start_samples(chip_symbol)
                                + (chip_symbol % 7U == 0 ? 80.0 : 72.0) + chip_position * chip_span;
    const double start = useful_start / AIOT_CBRA_DECIMATION + receiver->calibrated_delay_samples;
    const double end = (useful_start + chip_span) / AIOT_CBRA_DECIMATION + receiver->calibrated_delay_samples;
    const size_t first = start > 0.0 ? (size_t)floor(start) : 0;
    const size_t last = (size_t)ceil(end);
    double energy = 0.0;
    double preselection_energy = 0.0;
    for (size_t index = first; index < last && index < output_count; ++index) {
      const double overlap_start = start > (double)index ? start : (double)index;
      const double overlap_end = end < (double)(index + 1U) ? end : (double)(index + 1U);
      if (overlap_end > overlap_start) {
        energy += decimated[index] * (overlap_end - overlap_start);
        preselection_energy += preselection_decimated[index] * (overlap_end - overlap_start);
      }
    }
    const double chip_duration = chip_span / AIOT_CBRA_DECIMATION;
    chip_energies[chip_index] = energy / chip_duration;
    preselection_energy /= chip_duration;
    if (chip_index >= AIOT_CBRA_SIP_CHIPS && !(m == 24 && chip_position >= m - 2U)) {
      if (sequence_index >= AIOT_CBRA_CAP_CHIPS
          && sequence_index < AIOT_CBRA_CAP_CHIPS + phy_bits * AIOT_MANCHESTER_CHIPS_PER_BIT) {
        if ((sequence_index - AIOT_CBRA_CAP_CHIPS) % AIOT_MANCHESTER_CHIPS_PER_BIT == 0) {
          first_preselection_power = preselection_energy;
        } else {
          const double noise = first_preselection_power < preselection_energy ? first_preselection_power : preselection_energy;
          noise_power_sum += noise;
          const double signal = first_preselection_power > preselection_energy ? first_preselection_power : preselection_energy;
          signal_power_sum += signal - noise;
          ++power_pair_count;
        }
      }
      ++sequence_index;
    }
  }
  if (power_pair_count != 0) {
    if (signal_power != NULL)
      *signal_power = signal_power_sum / power_pair_count;
    if (noise_power != NULL)
      *noise_power = noise_power_sum / power_pair_count;
  }
  free(preselection_decimated);
  free(decimated);
  return true;
}

static size_t aiot_crc_length_bits(size_t payload_len)
{
  return payload_len * 8 <= 24 ? 6 : 16;
}

static uint32_t aiot_crc(const uint8_t *payload, size_t payload_len)
{
  return aiot_crc_length_bits(payload_len) == 6 ? crc6((uint8_t *)payload, payload_len * 8) >> 26
                                                : crc16((uint8_t *)payload, payload_len * 8) >> 16;
}

static void aiot_encode_pair(uint8_t bit, uint8_t *pair)
{
  pair[0] = bit ? 0 : 1;
  pair[1] = bit ? 1 : 0;
}

static bool aiot_decode_pair(const uint8_t *pair, uint8_t *bit)
{
  if (pair[0] == 1 && pair[1] == 0) {
    *bit = 0;
    return true;
  }
  if (pair[0] == 0 && pair[1] == 1) {
    *bit = 1;
    return true;
  }
  return false;
}

static void aiot_cbra_put_bits(uint8_t *bytes, size_t *offset, uint64_t value, unsigned int width)
{
  for (unsigned int bit = 0; bit < width; ++bit) {
    const size_t position = *offset + bit;
    if ((value >> (width - 1U - bit)) & 1U)
      bytes[position / 8U] |= (uint8_t)(1U << (7U - position % 8U));
  }
  *offset += width;
}

static uint64_t aiot_cbra_get_bits(const uint8_t *bytes, size_t *offset, unsigned int width)
{
  uint64_t value = 0;
  for (unsigned int bit = 0; bit < width; ++bit) {
    const size_t position = *offset + bit;
    value = (value << 1U) | ((bytes[position / 8U] >> (7U - position % 8U)) & 1U);
  }
  *offset += width;
  return value;
}

static bool aiot_cbra_frame_geometry(uint32_t phy_bits,
                                     uint32_t m,
                                     size_t *frame_chips,
                                     size_t *padding_chips,
                                     size_t *reserved_chips)
{
  if (phy_bits == 0 || phy_bits > 240 || (m != 2 && m != 6 && m != 12 && m != 24))
    return false;
  const size_t usable_chips_per_symbol = m == 24 ? 22U : m;
  const size_t data_and_overhead_chips = AIOT_CBRA_CAP_CHIPS + phy_bits * AIOT_MANCHESTER_CHIPS_PER_BIT
                                         + AIOT_CBRA_POSTAMBLE_CHIPS;
  const size_t symbols_after_sip =
      (data_and_overhead_chips + usable_chips_per_symbol - 1U) / usable_chips_per_symbol;
  const size_t mapping_positions = symbols_after_sip * m;
  *reserved_chips = m == 24 ? symbols_after_sip * 2U : 0U;
  *padding_chips = mapping_positions - *reserved_chips - data_and_overhead_chips;
  *frame_chips = AIOT_CBRA_SIP_CHIPS + mapping_positions;
  return *frame_chips <= AIOT_T2_MAX_RF_SAMPLES;
}

/* R-TAS CAP is acquired from the received symbol/chip timing.  The four
 * allowed M values have distinct frame lengths for each CBRA message kind;
 * do not trust the RFsim option metadata as the Tag's density input. */
static bool aiot_cbra_infer_m_from_cap(size_t sample_count, uint32_t phy_bits, uint32_t *m)
{
  static const uint32_t candidates[] = {2, 6, 12, 24};
  uint32_t match = 0;
  for (size_t index = 0; index < sizeof(candidates) / sizeof(candidates[0]); ++index) {
    size_t frame_chips = 0;
    size_t padding_chips = 0;
    size_t reserved_chips = 0;
    if (!aiot_cbra_frame_geometry(phy_bits,
                                  candidates[index],
                                  &frame_chips,
                                  &padding_chips,
                                  &reserved_chips))
      continue;
    const size_t expected_samples = aiot_cbra_symbol_start_samples(
        2U + (frame_chips - AIOT_CBRA_SIP_CHIPS) / candidates[index]);
    if (expected_samples == sample_count) {
      if (match != 0)
        return false;
      match = candidates[index];
    }
  }
  if (m != NULL)
    *m = match;
  return match != 0;
}

static uint8_t aiot_cbra_framing_bit(const uint8_t *phy, uint32_t phy_bits, size_t sequence_index)
{
  if (sequence_index < AIOT_CBRA_CAP_CHIPS)
    return (0xAU >> (AIOT_CBRA_CAP_CHIPS - 1U - sequence_index)) & 1U;

  sequence_index -= AIOT_CBRA_CAP_CHIPS;
  if (sequence_index < phy_bits * AIOT_MANCHESTER_CHIPS_PER_BIT) {
    const size_t bit_index = sequence_index / AIOT_MANCHESTER_CHIPS_PER_BIT;
    const uint8_t bit = (phy[bit_index / 8U] >> (7U - bit_index % 8U)) & 1U;
    return sequence_index % AIOT_MANCHESTER_CHIPS_PER_BIT == 0 ? (uint8_t)!bit : bit;
  }

  sequence_index -= phy_bits * AIOT_MANCHESTER_CHIPS_PER_BIT;
  return (0xFU >> (AIOT_CBRA_POSTAMBLE_CHIPS - 1U - sequence_index)) & 1U;
}

static bool aiot_cbra_test_encode_frame(const uint8_t *phy,
                                       uint32_t phy_bits,
                                       uint32_t m,
                                       c16_t *samples,
                                       size_t sample_capacity,
                                       size_t *sample_count)
{
  size_t frame_chips = 0;
  size_t padding_chips = 0;
  size_t reserved_chips = 0;
  if (phy == NULL || samples == NULL || sample_count == NULL
      || !aiot_cbra_frame_geometry(phy_bits, m, &frame_chips, &padding_chips, &reserved_chips)
      || sample_capacity < frame_chips)
    return false;
  const size_t data_and_overhead_chips = AIOT_CBRA_CAP_CHIPS + phy_bits * AIOT_MANCHESTER_CHIPS_PER_BIT
                                         + AIOT_CBRA_POSTAMBLE_CHIPS;

  memset(samples, 0, frame_chips * sizeof(*samples));
  size_t output_index = 0;
  for (size_t index = 0; index < AIOT_CBRA_SIP_CHIPS; ++index)
    samples[output_index++].r = (0xC8U >> (AIOT_CBRA_SIP_CHIPS - 1U - index)) & 1U ? 2 : 0;

  size_t sequence_index = 0;
  const size_t symbols_after_sip = (frame_chips - AIOT_CBRA_SIP_CHIPS) / m;
  for (size_t symbol = 0; symbol < symbols_after_sip; ++symbol) {
    for (uint32_t position = 0; position < m; ++position) {
      const bool reserved = m == 24 && position >= m - 2U;
      uint8_t chip = 0;
      if (reserved) {
        chip = 1;
      } else if (sequence_index < data_and_overhead_chips) {
        chip = aiot_cbra_framing_bit(phy, phy_bits, sequence_index++);
      } else {
        const size_t padding_index = sequence_index - data_and_overhead_chips;
        chip = m == 24 && padding_chips >= 2U && padding_index >= padding_chips - 2U ? 1U : 0U;
        ++sequence_index;
      }
      samples[output_index++].r = chip ? 2 : 0;
    }
  }
  *sample_count = output_index;
  return output_index == frame_chips
         && sequence_index == data_and_overhead_chips + padding_chips
         && reserved_chips == (m == 24 ? symbols_after_sip * 2U : 0U);
}

static aiot_result_t aiot_decode_cbra_r2d_frame(const c16_t *samples,
                                               size_t sample_count,
                                               uint32_t message_kind,
                                               uint32_t m,
                                               aiot_cbra_receiver_t *receiver,
                                               uint8_t pdu[AIOT_CBRA_PDU_BYTES],
                                               uint32_t *serial,
                                               uint32_t *d2r_scheduling_info,
                                               double *signal_power,
                                               double *noise_power)
{
  const uint32_t mac_bits = message_kind == AIOT_T2_CBRA_KIND_PAGING ? 224U : 3U;
  const uint32_t phy_bits = message_kind == AIOT_T2_CBRA_KIND_PAGING ? 240U : 9U;
  const uint32_t pdu_bytes = message_kind == AIOT_T2_CBRA_KIND_PAGING ? 28U : 2U;
  if (message_kind > AIOT_T2_CBRA_KIND_ACCESS_TRIGGER || pdu == NULL || serial == NULL
      || d2r_scheduling_info == NULL)
    return AIOT_RESULT_PAYLOAD_LENGTH;
  *serial = 0;
  *d2r_scheduling_info = 0;
  if (signal_power != NULL)
    *signal_power = 0.0;
  if (noise_power != NULL)
    *noise_power = 0.0;
  size_t frame_chips = 0;
  size_t padding_chips = 0;
  size_t reserved_chips = 0;
  const size_t data_and_overhead_chips = AIOT_CBRA_CAP_CHIPS + phy_bits * AIOT_MANCHESTER_CHIPS_PER_BIT
                                         + AIOT_CBRA_POSTAMBLE_CHIPS;
  if (samples == NULL || !aiot_cbra_frame_geometry(phy_bits, m, &frame_chips, &padding_chips, &reserved_chips)
      || sample_count != aiot_cbra_symbol_start_samples(2U + (frame_chips - AIOT_CBRA_SIP_CHIPS) / m))
    return AIOT_RESULT_PAYLOAD_LENGTH;

  aiot_cbra_receiver_t local_receiver;
  if (receiver == NULL) {
    aiot_cbra_receiver_init(&local_receiver);
    receiver = &local_receiver;
  }
  double chip_energies[AIOT_T2_MAX_RF_SAMPLES] = {0};
  if (!aiot_cbra_receiver_energies(
          samples,
          sample_count,
          phy_bits,
          m,
          receiver,
          chip_energies,
          sizeofArray(chip_energies),
          signal_power,
          noise_power))
    return AIOT_RESULT_PAYLOAD_LENGTH;

  double prdch_energy[480] = {0};
  size_t sequence_index = 0;
  size_t sample_index = AIOT_CBRA_SIP_CHIPS;
  const size_t symbols_after_sip = (frame_chips - AIOT_CBRA_SIP_CHIPS) / m;
  for (size_t symbol = 0; symbol < symbols_after_sip; ++symbol) {
    for (uint32_t position = 0; position < m; ++position, ++sample_index) {
      if (m == 24 && position >= m - 2U)
        continue;
      if (sequence_index >= AIOT_CBRA_CAP_CHIPS
          && sequence_index < AIOT_CBRA_CAP_CHIPS + phy_bits * AIOT_MANCHESTER_CHIPS_PER_BIT)
        prdch_energy[sequence_index - AIOT_CBRA_CAP_CHIPS] = chip_energies[sample_index];
      ++sequence_index;
    }
  }
  if (sample_index != frame_chips || sequence_index != data_and_overhead_chips + padding_chips)
    return AIOT_RESULT_PAYLOAD_LENGTH;

  memset(pdu, 0, pdu_bytes);
  uint32_t received_crc = 0;
  for (size_t bit_index = 0; bit_index < phy_bits; ++bit_index) {
    const double first_energy = prdch_energy[bit_index * AIOT_MANCHESTER_CHIPS_PER_BIT];
    const double second_energy = prdch_energy[bit_index * AIOT_MANCHESTER_CHIPS_PER_BIT + 1U];
    if (first_energy == second_energy)
      return AIOT_RESULT_INVALID_LINE_CODE;
    const uint8_t bit = second_energy > first_energy;
    if (bit_index < mac_bits) {
      if (bit)
        pdu[bit_index / 8U] |= (uint8_t)(1U << (7U - bit_index % 8U));
    } else {
      received_crc = (received_crc << 1U) | bit;
    }
  }
  const uint32_t expected_crc = message_kind == AIOT_T2_CBRA_KIND_PAGING
                                    ? aiot_crc(pdu, pdu_bytes)
                                    : (crc6(pdu, 3U) >> 26);
  if (received_crc != expected_crc)
    return AIOT_RESULT_CRC_FAILURE;

  size_t offset = 0;
  if (message_kind == AIOT_T2_CBRA_KIND_ACCESS_TRIGGER)
    return aiot_cbra_get_bits(pdu, &offset, 3) == 2 && offset == 3 ? AIOT_RESULT_OK : AIOT_RESULT_INVALID_LINE_CODE;
  if (aiot_cbra_get_bits(pdu, &offset, 3) != 1
      || aiot_cbra_get_bits(pdu, &offset, 7) != 27
      || aiot_cbra_get_bits(pdu, &offset, 1) != 1)
    return AIOT_RESULT_INVALID_LINE_CODE;
  offset += 8U * 16U;
  if (aiot_cbra_get_bits(pdu, &offset, 1) != 1
      || aiot_cbra_get_bits(pdu, &offset, 6) > 63
      || aiot_cbra_get_bits(pdu, &offset, 1) != 1
      || aiot_cbra_get_bits(pdu, &offset, 10) != 42
      || aiot_cbra_get_bits(pdu, &offset, 2) != 1
      || aiot_cbra_get_bits(pdu, &offset, 8) != 0x08)
    return AIOT_RESULT_INVALID_LINE_CODE;
  *serial = (uint32_t)aiot_cbra_get_bits(pdu, &offset, 32);
  if (*serial == 0)
    return AIOT_RESULT_INVALID_LINE_CODE;
  (void)aiot_cbra_get_bits(pdu, &offset, 4);
  *d2r_scheduling_info = (uint32_t)aiot_cbra_get_bits(pdu, &offset, 18);
  const uint8_t schedule_tbit = (uint8_t)((*d2r_scheduling_info >> 14) & 7U);
  const uint8_t schedule_bitmap = (uint8_t)((*d2r_scheduling_info >> 6) & 0xffU);
  const uint8_t schedule_x = (uint8_t)(((*d2r_scheduling_info >> 17) & 1U) + 1U);
  static const uint8_t allowed_sfs[8] = {0xff, 0xfe, 0xfc, 0xf8, 0xf0, 0xe0, 0xc0, 0x80};
  uint8_t schedule_sfs = schedule_bitmap;
  uint8_t schedule_n_sfs = 0;
  while (schedule_sfs != 0) {
    schedule_n_sfs += schedule_sfs & 1U;
    schedule_sfs >>= 1;
  }
  if (schedule_tbit >= 8 || schedule_bitmap == 0 || (schedule_bitmap & (uint8_t)~allowed_sfs[schedule_tbit]) != 0
      || schedule_x == 0 || schedule_n_sfs == 0 || aiot_cbra_get_bits(pdu, &offset, 1) > 1)
    return AIOT_RESULT_INVALID_LINE_CODE;
  (void)aiot_cbra_get_bits(pdu, &offset, 2);
  return offset == mac_bits ? AIOT_RESULT_OK : AIOT_RESULT_INVALID_LINE_CODE;
}

static aiot_result_t aiot_encode_frame(const uint8_t *payload,
                                       size_t payload_len,
                                       bool apply_sfs,
                                       uint8_t *chips,
                                       size_t chips_capacity,
                                       size_t *chips_len)
{
  if (payload_len == 0 || payload_len > AIOT_MAX_PAYLOAD_BYTES)
    return AIOT_RESULT_PAYLOAD_LENGTH;

  const size_t payload_bits = payload_len * 8;
  const size_t crc_bits = aiot_crc_length_bits(payload_len);
  const size_t frame_bits = payload_bits + crc_bits;
  const size_t chips_per_bit = apply_sfs ? AIOT_D2R_CHIPS_PER_FRAME_BIT : AIOT_MANCHESTER_CHIPS_PER_BIT;
  const size_t required_chips = frame_bits * chips_per_bit;
  if (chips_capacity < required_chips)
    return AIOT_RESULT_PAYLOAD_LENGTH;

  const uint32_t crc = aiot_crc(payload, payload_len);
  for (size_t i = 0; i < frame_bits; ++i) {
    const uint8_t bit = i < payload_bits ? (payload[i / 8] >> (7 - i % 8)) & 1
                                         : (crc >> (crc_bits - 1 - (i - payload_bits))) & 1;
    aiot_encode_pair(bit, chips + i * chips_per_bit);
  }
  *chips_len = required_chips;
  return AIOT_RESULT_OK;
}

static aiot_result_t aiot_decode_frame(const uint8_t *chips,
                                       size_t chips_len,
                                       size_t payload_len,
                                       bool apply_sfs,
                                       bool cw_required,
                                       bool cw_present,
                                       uint8_t *payload)
{
  if (payload_len == 0 || payload_len > AIOT_MAX_PAYLOAD_BYTES)
    return AIOT_RESULT_PAYLOAD_LENGTH;
  if (cw_required && !cw_present)
    return AIOT_RESULT_CW_ABSENT;

  const size_t payload_bits = payload_len * 8;
  const size_t crc_bits = aiot_crc_length_bits(payload_len);
  const size_t frame_bits = payload_bits + crc_bits;
  const size_t chips_per_bit = apply_sfs ? AIOT_D2R_CHIPS_PER_FRAME_BIT : AIOT_MANCHESTER_CHIPS_PER_BIT;
  if (chips_len != frame_bits * chips_per_bit)
    return AIOT_RESULT_PAYLOAD_LENGTH;

  uint8_t frame[AIOT_MAX_FRAME_BITS] = {0};
  for (size_t i = 0; i < frame_bits; ++i) {
    const uint8_t *encoded = chips + i * chips_per_bit;
    if (!aiot_decode_pair(encoded, &frame[i]))
      return AIOT_RESULT_INVALID_LINE_CODE;
  }

  memset(payload, 0, payload_len);
  for (size_t i = 0; i < payload_bits; ++i)
    payload[i / 8] |= frame[i] << (7 - i % 8);

  uint32_t received_crc = 0;
  for (size_t i = 0; i < crc_bits; ++i)
    received_crc = (received_crc << 1) | frame[payload_bits + i];
  return received_crc == aiot_crc(payload, payload_len) ? AIOT_RESULT_OK : AIOT_RESULT_CRC_FAILURE;
}

static void aiot_apply_fault(uint8_t *chips, size_t chips_len, aiot_fault_t fault)
{
  if (fault == AIOT_FAULT_INVALID_00) {
    chips[0] = 0;
    chips[1] = 0;
  } else if (fault == AIOT_FAULT_INVALID_11) {
    chips[0] = 1;
    chips[1] = 1;
  } else if (fault == AIOT_FAULT_CRC) {
    for (size_t i = chips_len - AIOT_D2R_CHIPS_PER_FRAME_BIT; i < chips_len; ++i)
      chips[i] ^= 1;
  }
}

static aiot_result_t aiot_tag_exchange(const aiot_tag_state_t *state,
                                       const uint8_t *inventory,
                                       size_t inventory_len,
                                       aiot_fault_t fault,
                                       uint8_t *decoded_inventory)
{
  if (inventory_len == 0 || inventory_len > AIOT_MAX_PAYLOAD_BYTES)
    return AIOT_RESULT_PAYLOAD_LENGTH;
  if (!state->reader_awake)
    return AIOT_RESULT_READER_ASLEEP;

  const uint8_t command[] = {AIOT_INVENTORY_COMMAND};
  uint8_t chips[AIOT_MAX_FRAME_BITS * AIOT_D2R_CHIPS_PER_FRAME_BIT];
  size_t chips_len = 0;
  aiot_result_t result = aiot_encode_frame(command, sizeof(command), false, chips, sizeof(chips), &chips_len);
  if (result != AIOT_RESULT_OK)
    return result;

  uint8_t decoded_command[sizeof(command)];
  result = aiot_decode_frame(chips, chips_len, sizeof(command), false, false, state->cw_present, decoded_command);
  if (result != AIOT_RESULT_OK || decoded_command[0] != AIOT_INVENTORY_COMMAND)
    return result == AIOT_RESULT_OK ? AIOT_RESULT_INVALID_LINE_CODE : result;
  if (fault == AIOT_FAULT_TIMEOUT || state->elapsed_ms >= AIOT_RESPONSE_TIMEOUT_MS)
    return AIOT_RESULT_TIMEOUT;

  result = aiot_encode_frame(inventory, inventory_len, true, chips, sizeof(chips), &chips_len);
  if (result != AIOT_RESULT_OK)
    return result;
  aiot_apply_fault(chips, chips_len, fault);
  return aiot_decode_frame(chips, chips_len, inventory_len, true, true, state->cw_present, decoded_inventory);
}

static int aiot_hex_nibble(char value)
{
  if (value >= '0' && value <= '9')
    return value - '0';
  if (value >= 'a' && value <= 'f')
    return value - 'a' + 10;
  if (value >= 'A' && value <= 'F')
    return value - 'A' + 10;
  return -1;
}

static bool aiot_parse_hex(const char *text, uint8_t *payload, size_t *payload_len)
{
  const size_t text_len = strlen(text);
  if (text_len == 0 || text_len % 2 != 0 || text_len / 2 > AIOT_MAX_PAYLOAD_BYTES)
    return false;
  *payload_len = text_len / 2;
  for (size_t i = 0; i < *payload_len; ++i) {
    const int high = aiot_hex_nibble(text[2 * i]);
    const int low = aiot_hex_nibble(text[2 * i + 1]);
    if (high < 0 || low < 0)
      return false;
    payload[i] = high << 4 | low;
  }
  return true;
}

static uint64_t aiot_t2_htonll(uint64_t value)
{
  return ((uint64_t)htonl((uint32_t)value) << 32) | htonl((uint32_t)(value >> 32));
}

static uint64_t aiot_cbra_power_q16(double power)
{
  if (!isfinite(power) || power <= 0.0)
    return 0;
  const double scaled = power * AIOT_T2_CBRA_POWER_Q_SCALE;
  if (scaled >= (double)UINT64_MAX)
    return aiot_t2_htonll(UINT64_MAX);
  return aiot_t2_htonll((uint64_t)(scaled + 0.5));
}

static void aiot_write_rfsim_packet(int fd, const samplesBlockHeader_t *header, const c16_t *samples);

static bool aiot_tag_send_cbra_observation(int socket,
                                           uint32_t tag_id,
                                           uint32_t reader_handle,
                                           uint32_t message_kind,
                                           uint32_t m,
                                           uint8_t context_eligible,
                                           uint8_t setup,
                                           uint64_t tx_timestamp,
                                           uint64_t completion_timestamp,
                                           uint32_t full_airtime_samples,
                                           uint8_t status,
                                           uint8_t gate_status,
                                           uint8_t d2r_attempted,
                                           uint8_t crc_ok,
                                           uint8_t comparable,
                                           uint8_t decode_result,
                                           double signal_power,
                                           double noise_power,
                                           uint16_t random_id,
                                           uint8_t access_occasion,
                                           uint8_t msg2_status,
                                           uint32_t config_version,
                                           uint32_t config_round,
                                           const uint8_t *decoded_pdu)
{
  aiot_t2_cbra_observation_report_t report = {0};
  const uint16_t mac_bits = message_kind == AIOT_T2_CBRA_KIND_PAGING ? 224U : 3U;
  const uint16_t phy_bits = message_kind == AIOT_T2_CBRA_KIND_PAGING ? 240U : 9U;
  const size_t pdu_bytes = d2r_attempted ? AIOT_T2_CBRA_REFLECTION_PAYLOAD_BYTES
                                         : (message_kind == AIOT_T2_CBRA_KIND_PAGING ? 28U : 2U);
  report.magic = htonl(AIOT_T2_OBSERVATION_MAGIC);
  report.version = AIOT_T2_CBRA_OBSERVATION_VERSION;
  report.status = status;
  report.flags = htons(AIOT_T2_OBS_FLAG_IDEAL_ACQUISITION
                       | (crc_ok ? AIOT_T2_OBS_FLAG_CRC_VALID : 0)
                       | (setup ? AIOT_T2_OBS_FLAG_SETUP : 0));
  report.reader_handle = htonl(reader_handle);
  report.tag_id = htonl(tag_id);
  report.message_kind = message_kind;
  report.m = (uint8_t)m;
  report.prb_count = 3;
  report.pdu_profile_version = AIOT_T2_CBRA_PDU_PROFILE_VERSION;
  report.gate_status = gate_status;
  report.context_eligible = context_eligible;
  report.mac_bits = htons(mac_bits);
  report.phy_bits = htons(phy_bits);
  report.tx_timestamp = aiot_t2_htonll(tx_timestamp);
  report.completion_timestamp = aiot_t2_htonll(completion_timestamp);
  report.epoch_readback = 0;
  report.d2r_attempted = d2r_attempted;
  report.crc_ok = crc_ok;
  report.payload_match = 0;
  report.decode_result = decode_result;
  report.compared_bits = htons(d2r_attempted ? 0 : (comparable ? mac_bits : 0));
  report.reserved_status[0] = (uint8_t)pdu_bytes;
  if (d2r_attempted && decoded_pdu != NULL)
    report.reserved_header = htons(aiot_t2_cbra_crc16(decoded_pdu, pdu_bytes));
  report.full_airtime_samples = htonl(full_airtime_samples);
  report.full_airtime_ns = aiot_t2_htonll(((uint64_t)full_airtime_samples * 1000000000ULL
                                           + AIOT_CBRA_SAMPLE_RATE_HZ / 2U)
                                          / AIOT_CBRA_SAMPLE_RATE_HZ);
  report.signal_power_q16 = aiot_cbra_power_q16(signal_power);
  report.noise_power_q16 = aiot_cbra_power_q16(noise_power);
  report.random_id = htons(random_id);
  report.access_occasion = access_occasion;
  report.msg2_status = msg2_status;
  report.config_version = htonl(config_version);
  report.config_round = htonl(config_round);
  if (decoded_pdu != NULL)
    memcpy(report.decoded_pdu, decoded_pdu, pdu_bytes);

  fprintf(stderr,
          "AIOT_T2_CBRA_OBSERVATION_TX tag_id=%u reader_handle=%u status=%u crc_ok=%u d2r_attempted=%u "
          "random_id=%u ao=%u\n",
          tag_id,
          reader_handle,
          report.status,
          report.crc_ok,
          report.d2r_attempted,
          ntohs(report.random_id),
          report.access_occasion);
  const samplesBlockHeader_t header = {
      .size = sizeof(report) / sizeof(c16_t),
      .nbAnt = 1,
      .timestamp = tx_timestamp,
      .option_value = AIOT_T2_PACK_CBRA_R2D_TARGET_WITH_CONFIG(tag_id,
                                                                reader_handle,
                                                                m,
                                                                message_kind,
                                                                config_version,
                                                                config_round),
      .option_flag = OPTION_AIOT_T2_CBRA_OBSERVATION,
      .beam_map = 1,
  };
  c16_t wire_samples[sizeof(report) / sizeof(c16_t)];
  memcpy(wire_samples, &report, sizeof(report));
  aiot_write_rfsim_packet(socket, &header, wire_samples);
  return true;
}

typedef struct {
  bool valid;
  uint32_t reader_handle;
  uint32_t message_kind;
  uint8_t context_eligible;
  uint8_t setup;
  uint32_t m;
  uint64_t tx_timestamp;
  uint32_t full_airtime_samples;
  uint16_t random_id;
  uint8_t access_occasion;
  uint8_t msg2_status;
  uint32_t config_version;
  uint32_t config_round;
  uint8_t decoded_pdu[AIOT_CBRA_PDU_BYTES];
} aiot_cbra_pending_observation_t;

typedef struct {
  bool context_valid;
  uint16_t n;
  uint16_t m;
  uint8_t r2d_m;
  uint8_t x;
  uint8_t sfs_bitmap;
  uint16_t counter;
  uint16_t selected_access_occasion;
  uint8_t selected_frequency_factor;
  uint8_t selected_time_resource;
  uint16_t random_id;
  uint32_t random_state;
  uint8_t k;
  uint8_t msg2_remaining;
  bool msg1_sent;
  bool waiting_msg2;
  bool msg2_received;
  bool waiting_msg3;
  bool completed;
  bool failed;
  uint8_t terminal_status;
  uint32_t reader_handle;
  uint32_t message_kind;
  uint32_t config_version;
  uint32_t config_round;
  uint64_t reflection_timestamp;
  uint8_t reflection_payload[AIOT_T2_CBRA_REFLECTION_PAYLOAD_BYTES];
} aiot_cbra_access_state_t;

static uint16_t aiot_cbra_next_random(aiot_cbra_access_state_t *state)
{
  state->random_state ^= state->random_state << 13;
  state->random_state ^= state->random_state >> 17;
  state->random_state ^= state->random_state << 5;
  uint16_t random_id = (uint16_t)(state->random_state >> 8);
  return random_id == 0 ? 1 : random_id;
}

static uint16_t aiot_cbra_access_m(uint32_t scheduling_info)
{
  static const uint8_t allowed_sfs[8] = {0xff, 0xfe, 0xfc, 0xf8, 0xf0, 0xe0, 0xc0, 0x80};
  const uint8_t x = (uint8_t)(((scheduling_info >> 17) & 1U) + 1U);
  const uint8_t tbit = (uint8_t)((scheduling_info >> 14) & 7U);
  const uint8_t bitmap = (uint8_t)((scheduling_info >> 6) & 0xffU);
  if (bitmap == 0 || tbit >= 8 || (bitmap & (uint8_t)~allowed_sfs[tbit]) != 0)
    return 0;
  uint16_t n_sfs = 0;
  for (uint8_t bits = bitmap; bits != 0; bits >>= 1)
    n_sfs += bits & 1U;
  return (uint16_t)(n_sfs * x);
}

static bool aiot_cbra_decode_paging_access(const uint8_t pdu[AIOT_CBRA_PDU_BYTES], uint8_t *n_code, uint8_t *k)
{
  if (pdu == NULL || n_code == NULL || k == NULL)
    return false;
  size_t offset = 0;
  offset += 3 + 7 + 1 + 8 * 16 + 1 + 6 + 1 + 10 + 2 + 8 + 32;
  *n_code = (uint8_t)aiot_cbra_get_bits(pdu, &offset, 4);
  offset += 18;
  *k = (uint8_t)aiot_cbra_get_bits(pdu, &offset, 1);
  return *n_code <= 15 && *k <= 1;
}

static bool aiot_cbra_start_msg1(aiot_cbra_access_state_t *state)
{
  if (state == NULL || state->selected_access_occasion == 0 || state->msg1_sent)
    return false;
  state->random_id = aiot_cbra_next_random(state);
  state->msg1_sent = true;
  state->waiting_msg2 = true;
  state->msg2_received = false;
  state->waiting_msg3 = false;
  state->completed = false;
  state->terminal_status = 0;
  state->msg2_remaining = state->k ? 4 : 1;
  return true;
}

static bool aiot_cbra_on_control(aiot_cbra_access_state_t *state,
                                 uint32_t tag_id,
                                 const samplesBlockHeader_t *header,
                                 const c16_t *samples)
{
  if (state == NULL || header == NULL || samples == NULL || header->nbAnt != 1
      || header->size != sizeof(aiot_t2_cbra_control_t) / sizeof(c16_t)
      || AIOT_T2_UNPACK_R2D_TAG(header->option_value) != tag_id)
    return false;

  aiot_t2_cbra_control_t control = {0};
  memcpy(&control, samples, sizeof(control));
  if (!aiot_t2_cbra_control_valid(&control))
    return false;

  const uint32_t reader_handle = AIOT_T2_UNPACK_R2D_READER(header->option_value);
  const uint32_t kind = AIOT_T2_UNPACK_CBRA_KIND(header->option_value);
  const uint32_t m = AIOT_T2_UNPACK_CBRA_M(header->option_value);
  const uint32_t config_version = AIOT_T2_UNPACK_CBRA_CONFIG_VERSION(header->option_value);
  const uint32_t config_round = AIOT_T2_UNPACK_CBRA_CONFIG_ROUND(header->option_value);
  const uint16_t transaction_id = aiot_t2_cbra_control_get_u16(control.transaction_id);
  const uint16_t access_occasion = aiot_t2_cbra_control_get_u16(control.access_occasion);
  const bool context_match = state->msg1_sent && reader_handle == state->reader_handle && m == state->r2d_m
                             && config_version == state->config_version && config_round == state->config_round
                             && transaction_id == state->random_id
                             && access_occasion == state->selected_access_occasion;
  if (!context_match) {
    fprintf(stderr,
            "AIOT_T2_CBRA_CONTROL_REJECT tag_id=%u reader_handle=%u kind=%u transaction_id=%u ao=%u reason=stale_or_mismatch\n",
            tag_id,
            reader_handle,
            kind,
            transaction_id,
            access_occasion);
    return false;
  }

  if (kind == AIOT_T2_CBRA_KIND_MSG2) {
    if (!state->waiting_msg2
        || (control.status != AIOT_T2_CBRA_CONTROL_MSG2_GRANT
            && control.status != AIOT_T2_CBRA_CONTROL_MSG2_REJECT))
      return false;
    state->waiting_msg2 = false;
    state->msg2_received = control.status == AIOT_T2_CBRA_CONTROL_MSG2_GRANT;
    state->failed = !state->msg2_received;
    state->terminal_status = state->failed ? AIOT_T2_CBRA_CONTROL_MSG3_NACK : 0;
    fprintf(stderr,
            "AIOT_T2_CBRA_MSG2_RX tag_id=%u transaction_id=%u ao=%u status=%u\n",
            tag_id,
            transaction_id,
            access_occasion,
            control.status);
    return true;
  }

  if (kind == AIOT_T2_CBRA_KIND_MSG3) {
    if (!state->waiting_msg3
        || (control.status != AIOT_T2_CBRA_CONTROL_MSG3_ACK
            && control.status != AIOT_T2_CBRA_CONTROL_MSG3_NACK))
      return false;
    state->waiting_msg3 = false;
    state->completed = control.status == AIOT_T2_CBRA_CONTROL_MSG3_ACK;
    state->failed = !state->completed;
    state->terminal_status = control.status;
    fprintf(stderr,
            "AIOT_T2_CBRA_MSG3_RX tag_id=%u transaction_id=%u ao=%u status=%u\n",
            tag_id,
            transaction_id,
            access_occasion,
            control.status);
    return true;
  }
  return false;
}

static bool aiot_cbra_observation_timed_out(uint64_t timestamp, uint64_t start_timestamp)
{
  return timestamp > start_timestamp && timestamp - start_timestamp > AIOT_T2_OBSERVATION_TIMEOUT_SAMPLES;
}

static bool aiot_cbra_control_self_test(void)
{
  aiot_cbra_access_state_t state = {
      .msg1_sent = true,
      .waiting_msg2 = true,
      .m = 24,
      .r2d_m = 2,
      .random_id = 0x1234,
      .selected_access_occasion = 3,
      .reader_handle = 1,
      .config_version = 5,
      .config_round = 6,
  };
  aiot_t2_cbra_control_t control = {0};
  c16_t samples[sizeof(control) / sizeof(c16_t)] = {0};
  samplesBlockHeader_t header = {
      .size = sizeof(control) / sizeof(c16_t),
      .nbAnt = 1,
      .option_value = AIOT_T2_PACK_CBRA_R2D_TARGET_WITH_CONFIG(7, 1, 2, AIOT_T2_CBRA_KIND_MSG2, 5, 6),
      .option_flag = OPTION_AIOT_T2_CBRA_CONTROL,
  };
  aiot_t2_cbra_control_set_u16(control.transaction_id, state.random_id);
  aiot_t2_cbra_control_set_u16(control.access_occasion, state.selected_access_occasion);
  control.status = AIOT_T2_CBRA_CONTROL_MSG2_GRANT;
  aiot_t2_cbra_control_finalize(&control);
  memcpy(samples, &control, sizeof(control));
  if (!aiot_cbra_on_control(&state, 7, &header, samples) || !state.msg2_received || state.waiting_msg2)
    return false;

  state.waiting_msg3 = true;
  header.option_value = AIOT_T2_PACK_CBRA_R2D_TARGET_WITH_CONFIG(7, 1, 2, AIOT_T2_CBRA_KIND_MSG3, 5, 6);
  aiot_t2_cbra_control_set_u16(control.transaction_id, state.random_id);
  control.status = AIOT_T2_CBRA_CONTROL_MSG3_ACK;
  aiot_t2_cbra_control_finalize(&control);
  memcpy(samples, &control, sizeof(control));
  header.option_value = AIOT_T2_PACK_CBRA_R2D_TARGET_WITH_CONFIG(7, 2, 2, AIOT_T2_CBRA_KIND_MSG3, 5, 6);
  if (aiot_cbra_on_control(&state, 7, &header, samples))
    return false;
  header.option_value = AIOT_T2_PACK_CBRA_R2D_TARGET_WITH_CONFIG(7, 1, 2, AIOT_T2_CBRA_KIND_MSG3, 4, 6);
  if (aiot_cbra_on_control(&state, 7, &header, samples))
    return false;
  header.option_value = AIOT_T2_PACK_CBRA_R2D_TARGET_WITH_CONFIG(7, 1, 2, AIOT_T2_CBRA_KIND_MSG3, 5, 6);
  if (aiot_cbra_on_control(&state, 8, &header, samples))
    return false;
  aiot_t2_cbra_control_set_u16(control.transaction_id, (uint16_t)(state.random_id + 1U));
  aiot_t2_cbra_control_finalize(&control);
  memcpy(samples, &control, sizeof(control));
  if (aiot_cbra_on_control(&state, 7, &header, samples))
    return false;
  aiot_t2_cbra_control_set_u16(control.transaction_id, state.random_id);
  aiot_t2_cbra_control_set_u16(control.access_occasion, (uint16_t)(state.selected_access_occasion + 1U));
  aiot_t2_cbra_control_finalize(&control);
  memcpy(samples, &control, sizeof(control));
  if (aiot_cbra_on_control(&state, 7, &header, samples))
    return false;
  aiot_t2_cbra_control_set_u16(control.access_occasion, state.selected_access_occasion);
  aiot_t2_cbra_control_finalize(&control);
  memcpy(samples, &control, sizeof(control));
  aiot_t2_cbra_control_set_u16(control.transaction_id, state.random_id);
  aiot_t2_cbra_control_finalize(&control);
  memcpy(samples, &control, sizeof(control));
  if (!aiot_cbra_on_control(&state, 7, &header, samples) || !state.completed || state.failed)
    return false;
  if (aiot_cbra_on_control(&state, 7, &header, samples))
    return false;

  aiot_cbra_access_state_t nack_state = state;
  nack_state.waiting_msg3 = true;
  nack_state.completed = false;
  nack_state.failed = false;
  nack_state.terminal_status = 0;
  control.status = AIOT_T2_CBRA_CONTROL_MSG3_NACK;
  aiot_t2_cbra_control_finalize(&control);
  memcpy(samples, &control, sizeof(control));
  if (!aiot_cbra_on_control(&nack_state, 7, &header, samples) || !nack_state.failed
      || nack_state.completed || nack_state.terminal_status != AIOT_T2_CBRA_CONTROL_MSG3_NACK
      || aiot_cbra_on_control(&nack_state, 7, &header, samples))
    return false;

  const uint64_t timeout = AIOT_T2_OBSERVATION_TIMEOUT_SAMPLES;
  return !aiot_cbra_observation_timed_out(100, 100)
         && !aiot_cbra_observation_timed_out(100 + timeout - 1U, 100)
         && !aiot_cbra_observation_timed_out(100 + timeout, 100)
         && aiot_cbra_observation_timed_out(100 + timeout + 1U, 100)
         && !aiot_cbra_observation_timed_out(99, 100);
}

static bool aiot_cbra_select_access_occasion(aiot_cbra_access_state_t *state, uint16_t ordinal)
{
  if (state == NULL || state->m == 0 || state->x == 0 || ordinal == 0 || ordinal > state->m)
    return false;
  const unsigned int frequency_ordinal = (ordinal - 1U) / state->x;
  const unsigned int time_ordinal = (ordinal - 1U) % state->x;
  unsigned int enabled_frequency = 0;
  for (unsigned int bit = 0; bit < 8; ++bit) {
    if ((state->sfs_bitmap & (uint8_t)(0x80U >> bit)) == 0)
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

static bool aiot_cbra_on_paging(aiot_cbra_access_state_t *state,
                                const uint8_t pdu[AIOT_CBRA_PDU_BYTES],
                                uint32_t scheduling_info)
{
  uint8_t n_code = 0;
  uint8_t k = 0;
  if (!aiot_cbra_decode_paging_access(pdu, &n_code, &k))
    return false;
  state->n = 1U << n_code;
  state->x = (uint8_t)(((scheduling_info >> 17) & 1U) + 1U);
  state->sfs_bitmap = (uint8_t)((scheduling_info >> 6) & 0xffU);
  state->m = aiot_cbra_access_m(scheduling_info);
  state->counter = (uint16_t)(state->random_state % state->n);
  state->selected_access_occasion = 0;
  state->selected_frequency_factor = 0;
  state->selected_time_resource = 0;
  state->msg1_sent = false;
  state->waiting_msg2 = false;
  state->msg2_received = false;
  state->waiting_msg3 = false;
  state->completed = false;
  state->failed = false;
  state->terminal_status = 0;
  state->k = k;
  state->msg2_remaining = 0;
  state->context_valid = state->m != 0;
  if (state->context_valid && state->counter < state->m) {
    return aiot_cbra_select_access_occasion(state, (uint16_t)(state->counter + 1U))
           && aiot_cbra_start_msg1(state);
  }
  return state->context_valid;
}

static bool aiot_cbra_on_access_trigger(aiot_cbra_access_state_t *state)
{
  if (state == NULL || !state->context_valid)
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
  if (state->msg1_sent || state->counter < state->m)
    return false;
  state->counter = (uint16_t)(state->counter - state->m);
  if (state->counter < state->m) {
    return aiot_cbra_select_access_occasion(state, (uint16_t)(state->counter + 1U))
           && aiot_cbra_start_msg1(state);
  }
  return false;
}

static bool aiot_cbra_lifecycle_self_test(void)
{
  aiot_cbra_access_state_t state = {
      .context_valid = true,
      .m = 8,
      .x = 2,
      .counter = 8,
      .msg1_sent = true,
      .waiting_msg2 = true,
      .msg2_remaining = 4,
  };
  for (unsigned int attempt = 0; attempt < 3; ++attempt) {
    if (aiot_cbra_on_access_trigger(&state) || !state.waiting_msg2 || state.failed)
      return false;
  }
  if (aiot_cbra_on_access_trigger(&state) || state.waiting_msg2 || !state.failed || !state.msg1_sent)
    return false;
  if (aiot_cbra_on_access_trigger(&state))
    return false;

  uint8_t paging[AIOT_CBRA_PDU_BYTES] = {0};
  size_t offset = 3 + 7 + 1 + 8 * 16 + 1 + 6 + 1 + 10 + 2 + 8 + 32;
  aiot_cbra_put_bits(paging, &offset, 0, 4);
  offset += 18;
  aiot_cbra_put_bits(paging, &offset, 0, 1);
  state.random_state = 1;
  if (!aiot_cbra_on_paging(&state, paging, AIOT_CBRA_FROZEN_D2R_SCHEDULING_INFO)
      || !state.context_valid || state.failed || !state.msg1_sent || !state.waiting_msg2)
    return false;
  return state.selected_access_occasion != 0;
}

static bool aiot_samples_to_chips(const c16_t *samples, size_t sample_count, uint32_t tbit, uint8_t *chips);

static aiot_fault_t aiot_parse_fault(const char *text, bool *valid)
{
  *valid = true;
  if (strcmp(text, "none") == 0)
    return AIOT_FAULT_NONE;
  if (strcmp(text, "invalid00") == 0)
    return AIOT_FAULT_INVALID_00;
  if (strcmp(text, "invalid11") == 0)
    return AIOT_FAULT_INVALID_11;
  if (strcmp(text, "crc") == 0)
    return AIOT_FAULT_CRC;
  if (strcmp(text, "timeout") == 0)
    return AIOT_FAULT_TIMEOUT;
  *valid = false;
  return AIOT_FAULT_NONE;
}

static int aiot_tag_cli(int argc, char **argv)
{
  if (argc != 6) {
    fprintf(stderr,
            "Usage: %s --aiot-tag <cw:on|off> <reader:awake|asleep> "
            "<none|invalid00|invalid11|crc|timeout> <inventory-hex>\n",
            argv[0]);
    return 2;
  }

  aiot_tag_state_t state = {
      .cw_present = strcmp(argv[2], "cw:on") == 0,
      .reader_awake = strcmp(argv[3], "reader:awake") == 0,
      .elapsed_ms = 0,
  };
  if ((!state.cw_present && strcmp(argv[2], "cw:off") != 0)
      || (!state.reader_awake && strcmp(argv[3], "reader:asleep") != 0)) {
    fprintf(stderr, "AIOT_T2_ARGUMENT_REJECT\n");
    return 2;
  }

  bool fault_valid = false;
  const aiot_fault_t fault = aiot_parse_fault(argv[4], &fault_valid);
  uint8_t inventory[AIOT_MAX_PAYLOAD_BYTES];
  size_t inventory_len = 0;
  const size_t inventory_hex_len = strlen(argv[5]);
  if (inventory_hex_len == 0 || inventory_hex_len / 2 > AIOT_MAX_PAYLOAD_BYTES) {
    printf("AIOT_T2_LENGTH_REJECT\n");
    return 1;
  }
  if (!fault_valid || !aiot_parse_hex(argv[5], inventory, &inventory_len)) {
    fprintf(stderr, "AIOT_T2_ARGUMENT_REJECT\n");
    return 2;
  }

  uint8_t decoded_inventory[AIOT_MAX_PAYLOAD_BYTES];
  printf("AIOT_T2_CW state=%s\n", state.cw_present ? "on" : "off");
  printf("AIOT_T2_D2R_PROFILE modulation=OOK sfs=%d experimental_manchester=true\n", AIOT_SFS_FACTOR);
  const aiot_result_t result = aiot_tag_exchange(&state, inventory, inventory_len, fault, decoded_inventory);
  if (result == AIOT_RESULT_OK) {
    printf("AIOT_T2_R2D_ACCEPT\nAIOT_T2_D2R_CRC_OK\nAIOT_T2_ROUNDTRIP_OK payload=");
    for (size_t i = 0; i < inventory_len; ++i)
      printf("%02x", decoded_inventory[i]);
    printf("\n");
    return 0;
  }
  if (result == AIOT_RESULT_INVALID_LINE_CODE)
    printf("AIOT_T2_LINECODE_REJECT pair=%s\n", fault == AIOT_FAULT_INVALID_11 ? "11" : "00");
  else if (result == AIOT_RESULT_CRC_FAILURE)
    printf("AIOT_T2_CRC_REJECT\n");
  else if (result == AIOT_RESULT_CW_ABSENT)
    printf("AIOT_T2_CW_REJECT state=off\n");
  else if (result == AIOT_RESULT_READER_ASLEEP)
    printf("AIOT_T2_R2D_REJECT reason=reader_asleep\n");
  else if (result == AIOT_RESULT_PAYLOAD_LENGTH)
    printf("AIOT_T2_LENGTH_REJECT\n");
  else if (result == AIOT_RESULT_TIMEOUT)
    printf("AIOT_T2_TIMEOUT timeout_ms=%d\n", AIOT_RESPONSE_TIMEOUT_MS);
  return 1;
}

static bool aiot_expect(aiot_result_t expected,
                        const aiot_tag_state_t *state,
                        const uint8_t *inventory,
                        size_t inventory_len,
                        aiot_fault_t fault)
{
  uint8_t decoded[AIOT_MAX_PAYLOAD_BYTES];
  return aiot_tag_exchange(state, inventory, inventory_len, fault, decoded) == expected
         && (expected != AIOT_RESULT_OK || memcmp(decoded, inventory, inventory_len) == 0);
}

static int aiot_tag_self_test(void)
{
  crcTableInit();
  const aiot_tag_state_t ready = {.cw_present = true, .reader_awake = true, .elapsed_ms = 0};
  const aiot_tag_state_t cw_off = {.cw_present = false, .reader_awake = true, .elapsed_ms = 0};
  const aiot_tag_state_t asleep = {.cw_present = true, .reader_awake = false, .elapsed_ms = 0};
  const aiot_tag_state_t late = {.cw_present = true, .reader_awake = true, .elapsed_ms = AIOT_RESPONSE_TIMEOUT_MS};
  const uint8_t one_byte[] = {0xa5};
  const uint8_t max_payload[AIOT_MAX_PAYLOAD_BYTES] = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15};
  const uint8_t too_long[AIOT_MAX_PAYLOAD_BYTES + 1] = {0};
  uint8_t direction_chips[AIOT_MAX_FRAME_BITS * AIOT_D2R_CHIPS_PER_FRAME_BIT];
  size_t r2d_chips_len = 0;
  size_t d2r_chips_len = 0;
  const c16_t cw_samples[2] = {{.r = 100, .i = -50}, {.r = 100, .i = -50}};
  const uint8_t ook_chips[2] = {1, 0};
  c16_t reflected[2] = {0};
  const c16_t noisy_pair[2] = {{.r = 1}, {.r = 3}};
  uint8_t noisy_pair_chips[2] = {0};
  uint8_t cbra_pdu[AIOT_CBRA_PDU_BYTES] = {0};
  uint8_t cbra_phy[AIOT_CBRA_PHY_BYTES] = {0};
  uint8_t cbra_decoded[AIOT_CBRA_PDU_BYTES] = {0};
  uint8_t cbra_bad_field_pdu[AIOT_CBRA_PDU_BYTES] = {0};
  uint8_t cbra_bad_field_phy[AIOT_CBRA_PHY_BYTES] = {0};
  uint8_t trigger[AIOT_CBRA_TRIGGER_BYTES] = {0};
  uint8_t trigger_phy[AIOT_CBRA_TRIGGER_BYTES] = {0};
  c16_t cbra_samples[AIOT_T2_MAX_RF_SAMPLES] = {0};
  c16_t cbra_bad_crc_samples[AIOT_T2_MAX_RF_SAMPLES] = {0};
  c16_t cbra_bad_field_samples[AIOT_T2_MAX_RF_SAMPLES] = {0};
  c16_t trigger_samples[AIOT_T2_MAX_RF_SAMPLES] = {0};
  c16_t trigger_bad_crc_samples[AIOT_T2_MAX_RF_SAMPLES] = {0};
  c16_t cbra_short_samples[2] = {0};
  c16_t *cbra_waveform = NULL;
  c16_t *cbra_bad_crc_waveform = NULL;
  c16_t *cbra_bad_field_waveform = NULL;
  c16_t *trigger_waveform = NULL;
  c16_t *trigger_bad_crc_waveform = NULL;
  size_t cbra_sample_count = 0;
  size_t cbra_bad_field_sample_count = 0;
  size_t cbra_waveform_count = 0;
  size_t cbra_bad_crc_waveform_count = 0;
  size_t cbra_bad_field_waveform_count = 0;
  size_t trigger_sample_count = 0;
  size_t trigger_waveform_count = 0;
  size_t trigger_bad_crc_waveform_count = 0;
  uint8_t cbra_reject_pdu[AIOT_CBRA_PDU_BYTES] = {0};
  uint32_t cbra_reject_serial = 0;
  uint32_t cbra_reject_schedule = 0;
  for (size_t i = 0; i < sizeofArray(ook_chips); ++i) {
    reflected[i].r = cw_samples[i].r * ook_chips[i];
    reflected[i].i = cw_samples[i].i * ook_chips[i];
  }

  const bool passed = aiot_encode_frame(one_byte, sizeof(one_byte), false, direction_chips, sizeof(direction_chips), &r2d_chips_len)
                          == AIOT_RESULT_OK
                      && aiot_encode_frame(
                             one_byte, sizeof(one_byte), true, direction_chips, sizeof(direction_chips), &d2r_chips_len)
                             == AIOT_RESULT_OK
                      && d2r_chips_len == r2d_chips_len
                      && aiot_expect(AIOT_RESULT_OK, &ready, one_byte, sizeof(one_byte), AIOT_FAULT_NONE)
                      && aiot_expect(AIOT_RESULT_OK, &ready, max_payload, sizeof(max_payload), AIOT_FAULT_NONE)
                      && aiot_expect(AIOT_RESULT_INVALID_LINE_CODE, &ready, one_byte, sizeof(one_byte), AIOT_FAULT_INVALID_00)
                      && aiot_expect(AIOT_RESULT_INVALID_LINE_CODE, &ready, one_byte, sizeof(one_byte), AIOT_FAULT_INVALID_11)
                      && aiot_expect(AIOT_RESULT_CRC_FAILURE, &ready, one_byte, sizeof(one_byte), AIOT_FAULT_CRC)
                      && aiot_expect(AIOT_RESULT_CW_ABSENT, &cw_off, one_byte, sizeof(one_byte), AIOT_FAULT_NONE)
                      && aiot_expect(AIOT_RESULT_READER_ASLEEP, &asleep, one_byte, sizeof(one_byte), AIOT_FAULT_NONE)
                      && aiot_expect(AIOT_RESULT_PAYLOAD_LENGTH, &ready, one_byte, 0, AIOT_FAULT_NONE)
                      && aiot_expect(AIOT_RESULT_PAYLOAD_LENGTH, &ready, too_long, sizeof(too_long), AIOT_FAULT_NONE)
                      && aiot_expect(AIOT_RESULT_TIMEOUT, &late, one_byte, sizeof(one_byte), AIOT_FAULT_NONE)
                      && aiot_expect(AIOT_RESULT_TIMEOUT, &ready, one_byte, sizeof(one_byte), AIOT_FAULT_TIMEOUT)
                      && reflected[0].r == cw_samples[0].r && reflected[0].i == cw_samples[0].i
                      && reflected[1].r == 0 && reflected[1].i == 0;
  const bool noisy_pair_decodes_by_energy = aiot_samples_to_chips(noisy_pair, sizeofArray(noisy_pair), 1, noisy_pair_chips)
                                             && noisy_pair_chips[0] == 0 && noisy_pair_chips[1] == 1;
  size_t cbra_offset = 0;
  aiot_cbra_put_bits(cbra_pdu, &cbra_offset, 1, 3);
  aiot_cbra_put_bits(cbra_pdu, &cbra_offset, 27, 7);
  aiot_cbra_put_bits(cbra_pdu, &cbra_offset, 1, 1);
  for (size_t i = 0; i < 16; ++i)
    aiot_cbra_put_bits(cbra_pdu, &cbra_offset, i, 8);
  aiot_cbra_put_bits(cbra_pdu, &cbra_offset, 1, 1);
  aiot_cbra_put_bits(cbra_pdu, &cbra_offset, 0, 6);
  aiot_cbra_put_bits(cbra_pdu, &cbra_offset, 1, 1);
  aiot_cbra_put_bits(cbra_pdu, &cbra_offset, 42, 10);
  aiot_cbra_put_bits(cbra_pdu, &cbra_offset, 1, 2);
  aiot_cbra_put_bits(cbra_pdu, &cbra_offset, 0x08, 8);
  aiot_cbra_put_bits(cbra_pdu, &cbra_offset, 100, 32);
  aiot_cbra_put_bits(cbra_pdu, &cbra_offset, 1, 4);
  aiot_cbra_put_bits(cbra_pdu, &cbra_offset, AIOT_CBRA_FROZEN_D2R_SCHEDULING_INFO, 18);
  aiot_cbra_put_bits(cbra_pdu, &cbra_offset, 0, 1);
  aiot_cbra_put_bits(cbra_pdu, &cbra_offset, 0, 2);
  memcpy(cbra_phy, cbra_pdu, sizeof(cbra_pdu));
  const uint16_t cbra_crc = (uint16_t)aiot_crc(cbra_pdu, sizeof(cbra_pdu));
  cbra_phy[AIOT_CBRA_PDU_BYTES] = (uint8_t)(cbra_crc >> 8);
  cbra_phy[AIOT_CBRA_PDU_BYTES + 1U] = (uint8_t)cbra_crc;
  const bool cbra_encoded = aiot_cbra_test_encode_frame(
      cbra_phy, AIOT_CBRA_PHY_BYTES * 8U, 2, cbra_samples, sizeofArray(cbra_samples), &cbra_sample_count);
  cbra_waveform = calloc(AIOT_T2_CBRA_MAX_OFDM_SAMPLES, sizeof(*cbra_waveform));
  memcpy(cbra_bad_crc_samples, cbra_samples, cbra_sample_count * sizeof(*cbra_samples));
  const c16_t cbra_first_chip = cbra_bad_crc_samples[AIOT_CBRA_SIP_CHIPS + AIOT_CBRA_CAP_CHIPS];
  cbra_bad_crc_samples[AIOT_CBRA_SIP_CHIPS + AIOT_CBRA_CAP_CHIPS] =
      cbra_bad_crc_samples[AIOT_CBRA_SIP_CHIPS + AIOT_CBRA_CAP_CHIPS + 1U];
  cbra_bad_crc_samples[AIOT_CBRA_SIP_CHIPS + AIOT_CBRA_CAP_CHIPS + 1U] = cbra_first_chip;
  memcpy(cbra_bad_field_pdu, cbra_pdu, sizeof(cbra_pdu));
  cbra_bad_field_pdu[0] ^= 0x80U;
  memcpy(cbra_bad_field_phy, cbra_bad_field_pdu, sizeof(cbra_bad_field_pdu));
  const uint16_t bad_field_crc = (uint16_t)aiot_crc(cbra_bad_field_pdu, sizeof(cbra_bad_field_pdu));
  cbra_bad_field_phy[AIOT_CBRA_PDU_BYTES] = (uint8_t)(bad_field_crc >> 8);
  cbra_bad_field_phy[AIOT_CBRA_PDU_BYTES + 1U] = (uint8_t)bad_field_crc;
  const bool cbra_bad_field_encoded = aiot_cbra_test_encode_frame(
      cbra_bad_field_phy,
      AIOT_CBRA_PHY_BYTES * 8U,
      2,
      cbra_bad_field_samples,
      sizeofArray(cbra_bad_field_samples),
      &cbra_bad_field_sample_count);
  cbra_bad_crc_waveform = calloc(AIOT_T2_CBRA_MAX_OFDM_SAMPLES, sizeof(*cbra_bad_crc_waveform));
  cbra_bad_field_waveform = calloc(AIOT_T2_CBRA_MAX_OFDM_SAMPLES, sizeof(*cbra_bad_field_waveform));
  const bool cbra_waveforms_encoded =
      cbra_encoded
      && aiot_t2_cbra_expand_compact_frame(cbra_samples,
                                           cbra_sample_count,
                                           AIOT_CBRA_PHY_BYTES * 8U,
                                           2,
                                           cbra_waveform,
                                           AIOT_T2_CBRA_MAX_OFDM_SAMPLES,
                                           &cbra_waveform_count)
      && aiot_t2_cbra_expand_compact_frame(cbra_bad_crc_samples,
                                           cbra_sample_count,
                                           AIOT_CBRA_PHY_BYTES * 8U,
                                           2,
                                           cbra_bad_crc_waveform,
                                           AIOT_T2_CBRA_MAX_OFDM_SAMPLES,
                                           &cbra_bad_crc_waveform_count)
      && aiot_t2_cbra_expand_compact_frame(cbra_bad_field_samples,
                                           cbra_bad_field_sample_count,
                                           AIOT_CBRA_PHY_BYTES * 8U,
                                           2,
                                           cbra_bad_field_waveform,
                                           AIOT_T2_CBRA_MAX_OFDM_SAMPLES,
                                           &cbra_bad_field_waveform_count);
  const aiot_result_t cbra_accept_result = aiot_decode_cbra_r2d_frame(
      cbra_waveform,
      cbra_waveform_count,
      AIOT_T2_CBRA_KIND_PAGING,
      2,
      NULL,
      cbra_decoded,
      &cbra_reject_serial,
      &cbra_reject_schedule,
      NULL,
      NULL);
  const bool cbra_accepts_valid_frame = cbra_waveforms_encoded && cbra_accept_result == AIOT_RESULT_OK
                                       && cbra_reject_serial == 100
                                       && cbra_reject_schedule == AIOT_CBRA_FROZEN_D2R_SCHEDULING_INFO
                                       && memcmp(cbra_decoded, cbra_pdu, sizeof(cbra_pdu)) == 0;
  bool cbra_all_m_decode = true;
  bool cbra_cap_infers_m = true;
  const uint32_t cbra_m_values[] = {2, 6, 12, 24};
  for (size_t index = 0; index < sizeofArray(cbra_m_values); ++index) {
    c16_t frame_samples[AIOT_T2_MAX_RF_SAMPLES] = {0};
    c16_t *frame_waveform = calloc(AIOT_T2_CBRA_MAX_OFDM_SAMPLES, sizeof(*frame_waveform));
    size_t frame_sample_count = 0;
    size_t frame_waveform_count = 0;
    uint8_t decoded[AIOT_CBRA_PDU_BYTES] = {0};
    uint32_t serial = 0;
    uint32_t schedule = 0;
    const bool frame_decodes = aiot_cbra_test_encode_frame(cbra_phy,
                                                          AIOT_CBRA_PHY_BYTES * 8U,
                                                          cbra_m_values[index],
                                                          frame_samples,
                                                          sizeofArray(frame_samples),
                                                          &frame_sample_count)
                               && aiot_t2_cbra_expand_compact_frame(frame_samples,
                                                                    frame_sample_count,
                                                                    AIOT_CBRA_PHY_BYTES * 8U,
                                                                    cbra_m_values[index],
                                                                    frame_waveform,
                                                                    AIOT_T2_CBRA_MAX_OFDM_SAMPLES,
                                                                    &frame_waveform_count)
                               && aiot_decode_cbra_r2d_frame(frame_waveform,
                                                            frame_waveform_count,
                                                            AIOT_T2_CBRA_KIND_PAGING,
                                                            cbra_m_values[index],
                                                            NULL,
                                                            decoded,
                                                            &serial,
                                                            &schedule,
                                                            NULL,
                                                            NULL) == AIOT_RESULT_OK
                               && serial == 100
                               && schedule == AIOT_CBRA_FROZEN_D2R_SCHEDULING_INFO
                               && memcmp(decoded, cbra_pdu, sizeof(cbra_pdu)) == 0;
    uint32_t inferred_m = 0;
    const bool cap_infers_m = aiot_cbra_infer_m_from_cap(frame_waveform_count,
                                                         AIOT_CBRA_PHY_BYTES * 8U,
                                                         &inferred_m)
                              && inferred_m == cbra_m_values[index];
    cbra_all_m_decode = cbra_all_m_decode && frame_decodes;
    cbra_cap_infers_m = cbra_cap_infers_m && cap_infers_m;
    free(frame_waveform);
  }
  const bool cbra_crc_rejected = aiot_decode_cbra_r2d_frame(
                                    cbra_bad_crc_waveform,
                                    cbra_bad_crc_waveform_count,
                                    AIOT_T2_CBRA_KIND_PAGING,
                                    2,
                                    NULL,
                                    cbra_decoded,
                                    &cbra_reject_serial,
                                    &cbra_reject_schedule,
                                    NULL,
                                    NULL)
                                 == AIOT_RESULT_CRC_FAILURE;
  const bool cbra_bad_field_rejected = aiot_decode_cbra_r2d_frame(
                                          cbra_bad_field_waveform,
                                          cbra_bad_field_waveform_count,
                                          AIOT_T2_CBRA_KIND_PAGING,
                                          2,
                                          NULL,
                                          cbra_decoded,
                                          &cbra_reject_serial,
                                          &cbra_reject_schedule,
                                          NULL,
                                          NULL)
                                      == AIOT_RESULT_INVALID_LINE_CODE && cbra_bad_field_encoded;
  const bool cbra_short_frame_rejected = aiot_decode_cbra_r2d_frame(
                                            cbra_short_samples,
                                            sizeofArray(cbra_short_samples),
                                            AIOT_T2_CBRA_KIND_PAGING,
                                            2,
                                            NULL,
                                            cbra_reject_pdu,
                                            &cbra_reject_serial,
                                            &cbra_reject_schedule,
                                            NULL,
                                            NULL)
                                         == AIOT_RESULT_PAYLOAD_LENGTH;
  size_t trigger_offset = 0;
  aiot_cbra_put_bits(trigger, &trigger_offset, 2, AIOT_CBRA_TRIGGER_BITS);
  size_t trigger_phy_offset = 0;
  aiot_cbra_put_bits(trigger_phy, &trigger_phy_offset, 2, AIOT_CBRA_TRIGGER_BITS);
  aiot_cbra_put_bits(trigger_phy, &trigger_phy_offset, crc6(trigger, AIOT_CBRA_TRIGGER_BITS) >> 26, 6);
  const bool trigger_encoded = aiot_cbra_test_encode_frame(trigger_phy,
                                                          AIOT_CBRA_TRIGGER_PHY_BITS,
                                                          24,
                                                          trigger_samples,
                                                          sizeofArray(trigger_samples),
                                                          &trigger_sample_count);
  trigger_waveform = calloc(AIOT_T2_CBRA_MAX_OFDM_SAMPLES, sizeof(*trigger_waveform));
  trigger_bad_crc_waveform = calloc(AIOT_T2_CBRA_MAX_OFDM_SAMPLES, sizeof(*trigger_bad_crc_waveform));
  memcpy(trigger_bad_crc_samples, trigger_samples, trigger_sample_count * sizeof(*trigger_samples));
  const size_t trigger_crc_chip = AIOT_CBRA_SIP_CHIPS + AIOT_CBRA_CAP_CHIPS + 3U * 2U;
  const c16_t trigger_first_crc_chip = trigger_bad_crc_samples[trigger_crc_chip];
  trigger_bad_crc_samples[trigger_crc_chip] = trigger_bad_crc_samples[trigger_crc_chip + 1U];
  trigger_bad_crc_samples[trigger_crc_chip + 1U] = trigger_first_crc_chip;
  uint8_t trigger_decoded[AIOT_CBRA_PDU_BYTES] = {0};
  uint32_t trigger_serial = 0;
  uint32_t trigger_schedule = 0;
  const bool trigger_waveforms_encoded =
      trigger_encoded
      && aiot_t2_cbra_expand_compact_frame(trigger_samples,
                                           trigger_sample_count,
                                           AIOT_CBRA_TRIGGER_PHY_BITS,
                                           24,
                                           trigger_waveform,
                                           AIOT_T2_CBRA_MAX_OFDM_SAMPLES,
                                           &trigger_waveform_count)
      && aiot_t2_cbra_expand_compact_frame(trigger_bad_crc_samples,
                                           trigger_sample_count,
                                           AIOT_CBRA_TRIGGER_PHY_BITS,
                                           24,
                                           trigger_bad_crc_waveform,
                                           AIOT_T2_CBRA_MAX_OFDM_SAMPLES,
                                           &trigger_bad_crc_waveform_count);
  const aiot_result_t trigger_result = aiot_decode_cbra_r2d_frame(trigger_waveform,
                                                                  trigger_waveform_count,
                                                                  AIOT_T2_CBRA_KIND_ACCESS_TRIGGER,
                                                                  24,
                                                                  NULL,
                                                                  trigger_decoded,
                                                                  &trigger_serial,
                                                                  &trigger_schedule,
                                                                  NULL,
                                                                  NULL);
  const bool trigger_decodes = trigger_waveforms_encoded && trigger_result == AIOT_RESULT_OK
                               && trigger_serial == 0 && trigger_schedule == 0
                               && memcmp(trigger_decoded, trigger, sizeof(trigger)) == 0;
  const bool trigger_crc_rejected = aiot_decode_cbra_r2d_frame(trigger_bad_crc_waveform,
                                                               trigger_bad_crc_waveform_count,
                                                               AIOT_T2_CBRA_KIND_ACCESS_TRIGGER,
                                                               24,
                                                               NULL,
                                                               trigger_decoded,
                                                               &trigger_serial,
                                                               &trigger_schedule,
                                                               NULL,
                                                               NULL)
                                    == AIOT_RESULT_CRC_FAILURE;
    const bool all_checks_pass = passed && noisy_pair_decodes_by_energy && cbra_accepts_valid_frame && cbra_all_m_decode
                               && cbra_cap_infers_m
                               && cbra_crc_rejected && cbra_bad_field_rejected && cbra_short_frame_rejected
                               && trigger_decodes && trigger_crc_rejected && aiot_cbra_control_self_test()
                               && aiot_cbra_lifecycle_self_test();
  free(cbra_waveform);
  free(cbra_bad_crc_waveform);
  free(cbra_bad_field_waveform);
  free(trigger_waveform);
  free(trigger_bad_crc_waveform);
  printf("AIOT_T2_SELF_TEST %s\n", all_checks_pass ? "PASS" : "FAIL");
  return all_checks_pass ? 0 : 1;
}

volatile int             oai_exit = 0;

int fullread(int fd, void *_buf, int count) {
  char *buf = _buf;
  int ret = 0;
  int l;

  while (count) {
    l = read(fd, buf, count);

    if (l <= 0)
      return -1;

    count -= l;
    buf += l;
    ret += l;
  }

  return ret;
}

void fullwrite(int fd, void *_buf, int count) {
  char *buf = _buf;
  int l;

  while (count) {
    l = write(fd, buf, count);

    if (l <= 0) {
      if (errno==EINTR)
        continue;

      if(errno==EAGAIN) {
        continue;
      } else {
        AssertFatal(false,"Lost socket\n");
      }
    } else {
      count -= l;
      buf += l;
    }
  }
}

int server_start(short port) {
  int listen_sock;
  AssertFatal((listen_sock = socket(AF_INET, SOCK_STREAM, 0)) >= 0, "");
  int enable = 1;
  AssertFatal(setsockopt(listen_sock, SOL_SOCKET, SO_REUSEADDR, &enable, sizeof(int)) == 0, "");
  struct sockaddr_in addr = {
sin_family:
    AF_INET,
sin_port:
    htons(port),
sin_addr:
    { s_addr: INADDR_ANY }
  };
  bind(listen_sock, (struct sockaddr *)&addr, sizeof(addr));
  AssertFatal(listen(listen_sock, 5) == 0, "");
  return accept(listen_sock,NULL,NULL);
}

int client_start(char *IP, short port) {
  int sock;
  AssertFatal((sock = socket(AF_INET, SOCK_STREAM, 0)) >= 0, "");
  struct sockaddr_in addr = {
sin_family:
    AF_INET,
sin_port:
    htons(port),
sin_addr:
    { s_addr: INADDR_ANY }
  };
  addr.sin_addr.s_addr = inet_addr(IP);
  bool connected=false;

  while(!connected) {
    //LOG_I(HW,"rfsimulator: trying to connect to %s:%d\n", IP, port);
    if (connect(sock, (struct sockaddr *)&addr, sizeof(addr)) == 0) {
      //LOG_I(HW,"rfsimulator: connection established\n");
      connected=true;
    }

    perror("simulated node");
    sleep(1);
  }

  return sock;
}

enum  blocking_t {
  notBlocking,
  blocking
};

void setblocking(int sock, enum blocking_t active) {
  int opts;
  AssertFatal( (opts = fcntl(sock, F_GETFL)) >= 0,"");

  if (active==blocking)
    opts = opts & ~O_NONBLOCK;
  else
    opts = opts | O_NONBLOCK;

  AssertFatal(fcntl(sock, F_SETFL, opts) >= 0, "");
}

static bool aiot_read_exact(int fd, void *buffer, size_t count)
{
  uint8_t *cursor = buffer;
  while (count > 0) {
    const ssize_t received = read(fd, cursor, count);
    if (received == 0)
      return false;
    if (received < 0) {
      if (errno == EINTR)
        continue;
      return false;
    }
    cursor += received;
    count -= received;
  }
  return true;
}

static bool aiot_read_rfsim_packet(int fd, samplesBlockHeader_t *header, c16_t **samples, size_t *capacity)
{
  if (!aiot_read_exact(fd, header, sizeof(*header)) || header->size == 0 || header->nbAnt == 0
      || header->size > AIOT_RFSIM_MAX_SAMPLES || header->nbAnt > 64)
    return false;

  const size_t sample_count = (size_t)header->size * header->nbAnt;
  if (sample_count > AIOT_RFSIM_MAX_SAMPLES || sample_count > SIZE_MAX / sizeof(**samples))
    return false;
  if (*capacity < sample_count) {
    c16_t *resized = realloc(*samples, sample_count * sizeof(*resized));
    if (resized == NULL)
      return false;
    *samples = resized;
    *capacity = sample_count;
  }
  return aiot_read_exact(fd, *samples, sample_count * sizeof(**samples));
}

static bool aiot_parse_u32(const char *text, uint32_t minimum, uint32_t maximum, uint32_t *value)
{
  char *end = NULL;
  errno = 0;
  const unsigned long parsed = strtoul(text, &end, 10);
  if (errno != 0 || end == text || *end != '\0' || parsed < minimum || parsed > maximum)
    return false;
  *value = parsed;
  return true;
}

static bool aiot_samples_to_chips(const c16_t *samples, size_t sample_count, uint32_t tbit, uint8_t *chips)
{
  const size_t samples_per_bit = aiot_t2_d2r_samples_per_bit(tbit);
  const size_t samples_per_chip = samples_per_bit / 2U;
  if (samples == NULL || chips == NULL || sample_count == 0 || sample_count > AIOT_T2_MAX_RF_SAMPLES
      || sample_count % samples_per_bit != 0)
    return false;
  size_t chip_index = 0;
  for (size_t i = 0; i < sample_count; i += samples_per_bit) {
    uint64_t first_energy = 0;
    uint64_t second_energy = 0;
    for (size_t repeat = 0; repeat < samples_per_chip; ++repeat) {
      const int64_t first_real = samples[i + repeat].r;
      const int64_t first_imag = samples[i + repeat].i;
      const int64_t second_real = samples[i + samples_per_chip + repeat].r;
      const int64_t second_imag = samples[i + samples_per_chip + repeat].i;
      first_energy += (uint64_t)(first_real * first_real + first_imag * first_imag);
      second_energy += (uint64_t)(second_real * second_real + second_imag * second_imag);
    }
    if (first_energy == second_energy)
      return false;
    const uint8_t bit = second_energy > first_energy;
    aiot_encode_pair(bit, &chips[chip_index]);
    chip_index += 2U;
  }
  return true;
}

static bool aiot_d2r_payload_length(size_t sample_count, uint32_t tbit, size_t *payload_len)
{
  const size_t samples_per_bit = aiot_t2_d2r_samples_per_bit(tbit);
  if (sample_count == 0 || sample_count % samples_per_bit != 0)
    return false;
  const size_t frame_bits = sample_count / samples_per_bit;
  const size_t crc_bits = frame_bits <= 30 ? 6 : 16;
  if (frame_bits <= crc_bits || (frame_bits - crc_bits) % 8 != 0)
    return false;
  *payload_len = (frame_bits - crc_bits) / 8;
  return *payload_len > 0 && *payload_len <= AIOT_MAX_PAYLOAD_BYTES;
}

static void aiot_write_rfsim_packet(int fd, const samplesBlockHeader_t *header, const c16_t *samples)
{
  fullwrite(fd, (void *)header, sizeof(*header));
  fullwrite(fd, (void *)samples, header->size * header->nbAnt * sizeof(*samples));
}

static int aiot_cw_rfsim_cli(int argc, char **argv)
{
  if (argc != 6 && argc != 7) {
    fprintf(stderr, "Usage: %s --aiot-cw-rfsim <server> <port> <samples> <amplitude> [cycles]\n", argv[0]);
    return 2;
  }

  uint32_t port = 0;
  uint32_t sample_count = 0;
  uint32_t amplitude = 0;
  uint32_t cycles = 1;
  if (!aiot_parse_u32(argv[3], 1, UINT16_MAX, &port)
      || !aiot_parse_u32(argv[4], 1, AIOT_RFSIM_MAX_SAMPLES, &sample_count)
      || !aiot_parse_u32(argv[5], 1, INT16_MAX, &amplitude)
      || (argc == 7 && !aiot_parse_u32(argv[6], 1, AIOT_T2_MAX_TAG_CYCLES, &cycles))) {
    fprintf(stderr, "AIOT_T2_ARGUMENT_REJECT\n");
    return 2;
  }

  c16_t *cw = calloc(sample_count, sizeof(*cw));
  if (cw == NULL)
    return 1;
  for (size_t i = 0; i < sample_count; ++i)
    cw[i].r = amplitude;
  const int socket = client_start(argv[2], port);
  setblocking(socket, blocking);
  samplesBlockHeader_t sync_header;
  c16_t *sync_samples = NULL;
  size_t sync_capacity = 0;
  if (!aiot_read_rfsim_packet(socket, &sync_header, &sync_samples, &sync_capacity)) {
    free(sync_samples);
    close(socket);
    free(cw);
    fprintf(stderr, "AIOT_T2_RFSIM_SYNC_REJECT\n");
    return 1;
  }
  free(sync_samples);
  for (uint32_t cycle = 0; cycle < cycles; ++cycle) {
    const samplesBlockHeader_t header = {
        .size = sample_count,
        .nbAnt = 1,
        .timestamp = sync_header.timestamp + sync_header.size + (uint64_t)cycle * sample_count,
        .option_value = 0,
        .option_flag = OPTION_AIOT_T2_CW,
        .beam_map = 1,
    };
    aiot_write_rfsim_packet(socket, &header, cw);
    printf("AIOT_T2_CW_SOURCE samples=%u amplitude=%u cycle=%u/%u\n",
           sample_count,
           amplitude,
           cycle + 1,
           cycles);
    if (cycle + 1 < cycles)
      usleep(500000);
  }
  free(cw);
  close(socket);
  return 0;
}

static int aiot_tag_rfsim_cli(int argc, char **argv)
{
  if (argc != 6 && argc != 7) {
    fprintf(stderr, "Usage: %s --aiot-tag-rfsim <server> <port> <tag-id> <inventory-hex> [cycles]\n", argv[0]);
    return 2;
  }

  uint32_t port = 0;
  uint32_t tag_id = 0;
  uint32_t cycles = 1;
  uint8_t inventory[AIOT_MAX_PAYLOAD_BYTES];
  size_t inventory_len = 0;
  if (!aiot_parse_u32(argv[3], 1, UINT16_MAX, &port) || !aiot_parse_u32(argv[4], 1, AIOT_T2_MAX_TAG_ID, &tag_id)
      || !aiot_parse_hex(argv[5], inventory, &inventory_len)
      || (argc == 7 && !aiot_parse_u32(argv[6], 1, AIOT_T2_MAX_TAG_CYCLES, &cycles))) {
    fprintf(stderr, "AIOT_T2_ARGUMENT_REJECT\n");
    return 2;
  }

  uint8_t chips[AIOT_MAX_FRAME_BITS * AIOT_D2R_CHIPS_PER_FRAME_BIT];
  size_t chips_len = 0;
  if (aiot_encode_frame(inventory, inventory_len, true, chips, sizeof(chips), &chips_len) != AIOT_RESULT_OK)
    return 1;

  const int socket = client_start(argv[2], port);
  setblocking(socket, blocking);
  samplesBlockHeader_t header;
  c16_t *samples = NULL;
  size_t capacity = 0;
  if (!aiot_read_rfsim_packet(socket, &header, &samples, &capacity)) {
    free(samples);
    fprintf(stderr, "AIOT_T2_RFSIM_SYNC_REJECT\n");
    return 1;
  }

  const c16_t registration_sample = {0};
  const samplesBlockHeader_t registration = {
      .size = 1,
      .nbAnt = 1,
      .timestamp = header.timestamp + header.size,
      .option_value = tag_id,
      .option_flag = OPTION_AIOT_T2_TAG_REGISTER,
      .beam_map = 1,
  };
  aiot_write_rfsim_packet(socket, &registration, &registration_sample);
  printf("AIOT_T2_TAG_REGISTER_SENT tag_id=%u\n", tag_id);

  c16_t cw[AIOT_T2_MAX_RF_SAMPLES];
  size_t cw_samples = 0;
  uint64_t cw_timestamp = 0;
  uint32_t r2d_tbit = 0;
  bool r2d_received = false;
  bool cbra_received = false;
  bool cbra_context_valid = false;
  uint64_t r2d_timestamp = 0;
  uint32_t completed_cycles = 0;
  aiot_cbra_pending_observation_t pending_observation = {0};
  aiot_cbra_receiver_t cbra_receiver;
  aiot_cbra_access_state_t cbra_access = {.random_state = 0x6d2b79f5U ^ tag_id};
  aiot_cbra_receiver_init(&cbra_receiver);
  while (aiot_read_rfsim_packet(socket, &header, &samples, &capacity)) {
    if (cbra_access.waiting_msg3
        && aiot_cbra_observation_timed_out(header.timestamp, cbra_access.reflection_timestamp)) {
      aiot_tag_send_cbra_observation(socket,
                                    tag_id,
                                    cbra_access.reader_handle,
                                    cbra_access.message_kind,
                                    cbra_access.m,
                                    1,
                                    0,
                                    cbra_access.reflection_timestamp,
                                    header.timestamp,
                                    0,
                                    AIOT_T2_OBS_UNDETECTED,
                                    AIOT_T2_CBRA_GATE_D2R_ATTEMPTED,
                                    1,
                                    0,
                                    0,
                                    AIOT_RESULT_TIMEOUT,
                                    0.0,
                                    0.0,
                                    cbra_access.random_id,
                                    (uint8_t)cbra_access.selected_access_occasion,
                                    AIOT_T2_CBRA_REPORT_MSG3_MISSING,
                                    cbra_access.config_version,
                                    cbra_access.config_round,
                                    cbra_access.reflection_payload);
      fprintf(stderr,
              "AIOT_T2_CBRA_MSG3_TIMEOUT tag_id=%u random_id=%u ao=%u\n",
              tag_id,
              cbra_access.random_id,
              cbra_access.selected_access_occasion);
      cbra_access.waiting_msg3 = false;
      cbra_access.failed = true;
      cbra_access.terminal_status = AIOT_T2_CBRA_REPORT_MSG3_MISSING;
      cbra_received = false;
      r2d_received = false;
      pending_observation.valid = false;
    }
    if (pending_observation.valid && aiot_cbra_observation_timed_out(header.timestamp, pending_observation.tx_timestamp)) {
      aiot_tag_send_cbra_observation(socket,
                                    tag_id,
                                    pending_observation.reader_handle,
                                    pending_observation.message_kind,
                                    pending_observation.m,
                                    pending_observation.context_eligible,
                                    pending_observation.setup,
                                    pending_observation.tx_timestamp,
                                    header.timestamp,
                                    pending_observation.full_airtime_samples,
                                    AIOT_T2_OBS_UNDETECTED,
                                    AIOT_T2_CBRA_GATE_REFUSED,
                                    0,
                                    0,
                                    0,
                                    AIOT_RESULT_TIMEOUT,
                                    0.0,
                                    0.0,
                                    pending_observation.random_id,
                                    pending_observation.access_occasion,
                                    AIOT_T2_CBRA_REPORT_MSG2_TIMEOUT,
                                    pending_observation.config_version,
                                    pending_observation.config_round,
                                    pending_observation.decoded_pdu);
      pending_observation.valid = false;
      cbra_access.waiting_msg2 = false;
      cbra_access.msg2_received = false;
      cbra_access.failed = true;
      cbra_access.terminal_status = AIOT_T2_CBRA_REPORT_MSG2_TIMEOUT;
      r2d_received = false;
      cbra_received = false;
    }
    if (header.option_flag & OPTION_AIOT_T2_CBRA_CONTROL) {
      if (AIOT_T2_UNPACK_R2D_TAG(header.option_value) != tag_id
          || header.nbAnt != 1 || header.size != sizeof(aiot_t2_cbra_control_t) / sizeof(c16_t)) {
        fprintf(stderr, "AIOT_T2_CBRA_CONTROL_REJECT tag_id=%u reason=invalid_header\n", tag_id);
        continue;
      }
      const bool accepted = aiot_cbra_on_control(&cbra_access, tag_id, &header, samples);
      if (!accepted)
        continue;
      if (cbra_access.completed) {
        ++completed_cycles;
        printf("AIOT_T2_CBRA_COMPLETE tag_id=%u random_id=%u ao=%u cycle=%u/%u\n",
               tag_id,
               cbra_access.random_id,
               cbra_access.selected_access_occasion,
               completed_cycles,
               cycles);
        if (completed_cycles >= cycles) {
          free(samples);
          close(socket);
          return 0;
        }
        cbra_access.completed = false;
        cbra_access.failed = false;
        cbra_access.msg1_sent = false;
        cbra_access.msg2_received = false;
        cbra_access.counter = cbra_access.m;
        cbra_received = false;
        r2d_received = false;
        pending_observation.valid = false;
        cw_samples = 0;
        continue;
      }
      if (cbra_access.failed) {
        fprintf(stderr,
                "AIOT_T2_CBRA_FAILURE tag_id=%u random_id=%u ao=%u status=%u\n",
                tag_id,
                cbra_access.random_id,
                cbra_access.selected_access_occasion,
                cbra_access.terminal_status);
        cbra_received = false;
        r2d_received = false;
        pending_observation.valid = false;
        cw_samples = 0;
        continue;
      }
      /* Msg2 acceptance may arrive after the R2D and CW blocks. Fall through
       * so the already captured pair is reflected without another trigger. */
    }
    if (header.option_flag & OPTION_AIOT_T2_CW) {
      if (header.nbAnt != 1 || header.size == 0 || header.size > AIOT_T2_MAX_RF_SAMPLES - cw_samples) {
        fprintf(stderr,
                "AIOT_T2_CW_REJECT reason=invalid_block samples=%u buffered=%zu\n",
                header.size,
                cw_samples);
        continue;
      }
      if (cw_samples == 0)
        cw_timestamp = header.timestamp;
      memcpy(cw + cw_samples, samples, header.size * sizeof(*cw));
      cw_samples += header.size;
      printf("AIOT_T2_CW_CAPTURE chunk=%u buffered=%zu required=%zu\n", header.size, cw_samples, chips_len);
      if (cw_samples < chips_len)
        continue;
    }

    const uint32_t r2d_target_tag = AIOT_T2_UNPACK_R2D_TAG(header.option_value);
    if ((header.option_flag & OPTION_AIOT_T2_R2D)
        && (r2d_target_tag == tag_id || r2d_target_tag == AIOT_T2_CBRA_BROADCAST_TAG_ID)) {
      uint8_t r2d_chips[AIOT_T2_MAX_RF_SAMPLES];
      const bool cbra = (header.option_flag & OPTION_AIOT_T2_R2D_CBRA) != 0;
      if (cbra) {
        const uint32_t message_kind = AIOT_T2_UNPACK_CBRA_KIND(header.option_value);
        uint32_t m = AIOT_T2_UNPACK_CBRA_M(header.option_value);
        const uint32_t reader_handle = AIOT_T2_UNPACK_R2D_READER(header.option_value);
        const uint8_t setup = AIOT_T2_UNPACK_CBRA_SETUP(header.option_value);
        const uint32_t config_version = AIOT_T2_UNPACK_CBRA_CONFIG_VERSION(header.option_value);
        const uint32_t config_round = AIOT_T2_UNPACK_CBRA_CONFIG_ROUND(header.option_value);
        uint8_t cbra_pdu[AIOT_CBRA_PDU_BYTES] = {0};
        uint32_t serial = 0;
        uint32_t d2r_scheduling_info = 0;
        double signal_power = 0.0;
        double noise_power = 0.0;
        const uint32_t phy_bits = message_kind == AIOT_T2_CBRA_KIND_PAGING ? 240U : 9U;
        const bool cap_valid = header.nbAnt == 1 && aiot_cbra_infer_m_from_cap(header.size, phy_bits, &m);
        const aiot_result_t result = cap_valid
                                         ? aiot_decode_cbra_r2d_frame(samples,
                                                                       header.size,
                                                                       message_kind,
                                                                     m,
                                                                     &cbra_receiver,
                                                                     cbra_pdu,
                                                                     &serial,
                                                                     &d2r_scheduling_info,
                                                                     &signal_power,
                                                                     &noise_power)
                                         : AIOT_RESULT_PAYLOAD_LENGTH;
        const bool serial_matches = message_kind == AIOT_T2_CBRA_KIND_ACCESS_TRIGGER || serial == tag_id
                                     || serial == AIOT_T2_CBRA_BROADCAST_SERIAL;
        const bool context_eligible = result == AIOT_RESULT_OK
                                      && (message_kind == AIOT_T2_CBRA_KIND_PAGING ? serial_matches : cbra_context_valid);
        if (result != AIOT_RESULT_OK || !serial_matches || !context_eligible) {
          const char *gate_reason = result == AIOT_RESULT_CRC_FAILURE
                                        ? "crc_failure"
                                        : (result == AIOT_RESULT_PAYLOAD_LENGTH
                                               ? "frame_length"
                                               : (!serial_matches ? "id_mismatch"
                                                                   : (!context_eligible ? "missing_paging_context" : "malformed_pdu")));
          fprintf(stderr,
                  "AIOT_T2_R2D_REJECT reason=%s tag_id=%u serial=%u m=%u result=%d\n",
                  gate_reason,
                  tag_id,
                  serial,
                  m,
                  result);
          const uint8_t status = result == AIOT_RESULT_CRC_FAILURE
                                     ? AIOT_T2_OBS_CRC_FAILURE
                                     : (result == AIOT_RESULT_INVALID_LINE_CODE ? AIOT_T2_OBS_UNALIGNED
                                                                                  : AIOT_T2_OBS_INVALID);
          aiot_tag_send_cbra_observation(socket,
                                        tag_id,
                                        reader_handle,
                                        AIOT_T2_UNPACK_CBRA_KIND(header.option_value),
                                        m,
                                        0,
                                        setup,
                                        header.timestamp,
                                        header.timestamp + header.size,
                                        header.size,
                                        status,
                                        AIOT_T2_CBRA_GATE_REFUSED,
                                        0,
                                        result == AIOT_RESULT_CRC_FAILURE ? 0 : 1,
                                        result == AIOT_RESULT_CRC_FAILURE || result == AIOT_RESULT_OK,
                                        result,
                                        signal_power,
                                        noise_power,
                                        0,
                                        0,
                                        0,
                                        config_version,
                                        config_round,
                                        result == AIOT_RESULT_CRC_FAILURE || result == AIOT_RESULT_OK ? cbra_pdu : NULL);
          fprintf(stderr,
                  "AIOT_T2_CBRA_GATE_REFUSED reason=%s tag_id=%u crc_ok=%u d2r_attempted=0\n",
                  gate_reason,
                  tag_id,
                  result == AIOT_RESULT_CRC_FAILURE ? 0U : 1U);
          continue;
        }
        bool selected_msg1 = false;
        if (message_kind == AIOT_T2_CBRA_KIND_PAGING) {
          selected_msg1 = aiot_cbra_on_paging(&cbra_access, cbra_pdu, d2r_scheduling_info);
          cbra_context_valid = cbra_access.context_valid;
        } else {
          selected_msg1 = aiot_cbra_on_access_trigger(&cbra_access);
        }
        if (message_kind == AIOT_T2_CBRA_KIND_ACCESS_TRIGGER && !cbra_context_valid)
          continue;
        const uint8_t msg2_status = cbra_access.failed ? 2 : (cbra_access.waiting_msg2 ? 1 : 0);
        if (selected_msg1) {
          cbra_access.reader_handle = reader_handle;
          cbra_access.message_kind = message_kind;
          cbra_access.r2d_m = (uint8_t)m;
          cbra_access.config_version = config_version;
          cbra_access.config_round = config_round;
          pending_observation.valid = true;
          pending_observation.reader_handle = reader_handle;
          pending_observation.message_kind = message_kind;
          pending_observation.context_eligible = 1;
          pending_observation.setup = setup;
          pending_observation.m = m;
          pending_observation.tx_timestamp = header.timestamp;
          pending_observation.full_airtime_samples = header.size;
          pending_observation.random_id = cbra_access.random_id;
          pending_observation.access_occasion = (uint8_t)cbra_access.selected_access_occasion;
          pending_observation.msg2_status = msg2_status;
          pending_observation.config_version = config_version;
          pending_observation.config_round = config_round;
          memcpy(pending_observation.decoded_pdu, cbra_pdu, sizeof(pending_observation.decoded_pdu));
          cbra_received = true;
          fprintf(stderr,
                  "AIOT_T2_CBRA_MSG1_SELECTED tag_id=%u ao=%u random_id=%u n=%u m=%u k=%u\n",
                  tag_id,
                  cbra_access.selected_access_occasion,
                  cbra_access.random_id,
                  cbra_access.n,
                  cbra_access.m,
                  cbra_access.k);
          r2d_received = true;
          r2d_timestamp = header.timestamp;
          r2d_tbit = AIOT_T2_UNPACK_R2D_TBIT(header.option_value);
        }
        aiot_tag_send_cbra_observation(socket,
                                       tag_id,
                                       reader_handle,
                                       message_kind,
                                       m,
                                       1,
                                       setup,
                                       header.timestamp,
                                       header.timestamp + header.size,
                                       header.size,
                                       AIOT_T2_OBS_COMPLETE,
                                       cbra_access.failed ? AIOT_T2_CBRA_GATE_REFUSED : AIOT_T2_CBRA_GATE_ELIGIBLE,
                                       0,
                                       1,
                                       1,
                                       AIOT_RESULT_OK,
                                       signal_power,
                                       noise_power,
                                       selected_msg1 ? cbra_access.random_id : 0,
                                       selected_msg1 ? (uint8_t)cbra_access.selected_access_occasion : 0,
                                       msg2_status,
                                       config_version,
                                       config_round,
                                       cbra_pdu);
        fprintf(stderr,
                "AIOT_T2_CBRA_GATE_ELIGIBLE tag_id=%u kind=%u serial=%u crc_ok=1 payload_match=unknown d2r_attempted=0\n",
                tag_id,
                message_kind,
                serial);
        printf("AIOT_T2_R2D_CBRA_ACCEPT tag_id=%u kind=%u serial=%u m=%u\n", tag_id, message_kind, serial, m);
        if (!selected_msg1)
          continue;
      } else {
        if (header.nbAnt != 1
            || !aiot_samples_to_chips(samples,
                                      header.size,
                                      (header.option_flag & OPTION_AIOT_T2_R2D_CBRA)
                                          ? AIOT_T2_UNPACK_R2D_TBIT(header.option_value)
                                          : 1,
                                      r2d_chips)) {
          fprintf(stderr, "AIOT_T2_R2D_REJECT reason=decode tag_id=%u\n", tag_id);
          continue;
        }
        uint8_t command = 0;
        if (aiot_decode_frame(r2d_chips, header.size, sizeof(command), false, false, true, &command) != AIOT_RESULT_OK
            || command != AIOT_INVENTORY_COMMAND) {
          fprintf(stderr, "AIOT_T2_R2D_REJECT reason=decode tag_id=%u\n", tag_id);
          continue;
        }
        r2d_tbit = AIOT_T2_UNPACK_R2D_TBIT(header.option_value);
      }
      r2d_received = true;
      r2d_timestamp = header.timestamp;
      printf("AIOT_T2_R2D_ACCEPT tag_id=%u\n", tag_id);
    }

    if (cw_samples == 0 || !r2d_received)
      continue;

    const uint8_t *reflection_chips = chips;
    size_t reflection_chips_len = chips_len;
    uint8_t reflection_payload[AIOT_T2_CBRA_REFLECTION_PAYLOAD_BYTES] = {0};
    uint8_t reflection_encoded_chips[AIOT_MAX_FRAME_BITS * AIOT_D2R_CHIPS_PER_FRAME_BIT] = {0};
    if (cbra_received) {
      if (!cbra_access.msg2_received || cbra_access.waiting_msg3 || cbra_access.failed)
        continue;
      reflection_payload[0] = (uint8_t)tag_id;
      reflection_payload[1] = (uint8_t)(cbra_access.random_id >> 8);
      reflection_payload[2] = (uint8_t)cbra_access.random_id;
      reflection_payload[3] = (uint8_t)cbra_access.selected_access_occasion;
      if (aiot_encode_frame(reflection_payload,
                            sizeof(reflection_payload),
                            true,
                            reflection_encoded_chips,
                            sizeof(reflection_encoded_chips),
                            &reflection_chips_len)
          != AIOT_RESULT_OK) {
        fprintf(stderr,
                "AIOT_T2_CBRA_REFLECTION_REJECT tag_id=%u random_id=%u reason=encode\n",
                tag_id,
                cbra_access.random_id);
        cbra_access.failed = true;
        continue;
      }
      reflection_chips = reflection_encoded_chips;
    }
    if (cw_samples < reflection_chips_len) {
      fprintf(stderr,
              "AIOT_T2_CBRA_REFLECTION_REJECT tag_id=%u reason=short_cw samples=%zu required=%zu\n",
              tag_id,
              cw_samples,
              reflection_chips_len);
      continue;
    }

    const size_t d2r_repeat = aiot_t2_d2r_sample_repeat(r2d_tbit);
    const size_t d2r_samples = reflection_chips_len * d2r_repeat;
    c16_t *reflected = calloc(d2r_samples, sizeof(*reflected));
    if (reflected == NULL) {
      free(samples);
      return 1;
    }
    for (size_t i = 0; i < reflection_chips_len; ++i) {
      for (size_t repeat = 0; repeat < d2r_repeat; ++repeat) {
        reflected[i * d2r_repeat + repeat].r = cw[i].r * reflection_chips[i];
        reflected[i * d2r_repeat + repeat].i = cw[i].i * reflection_chips[i];
      }
    }
    const samplesBlockHeader_t d2r = {
        .size = d2r_samples,
        .nbAnt = 1,
        .timestamp = cw_timestamp > r2d_timestamp ? cw_timestamp : r2d_timestamp,
        .option_value = AIOT_T2_PACK_CBRA_R2D_TARGET_WITH_CONFIG(tag_id,
                                                                cbra_access.reader_handle,
                                                                cbra_access.r2d_m,
                                                                cbra_access.message_kind,
                                                                cbra_access.config_version,
                                                                cbra_access.config_round),
        .option_flag = OPTION_AIOT_T2_D2R | AIOT_T2_PACK_D2R_TBIT(r2d_tbit),
        .beam_map = 1,
    };
    if (cbra_received) {
      memcpy(cbra_access.reflection_payload, reflection_payload, sizeof(reflection_payload));
      cbra_access.reflection_timestamp = d2r.timestamp;
      cbra_access.waiting_msg3 = true;
      aiot_tag_send_cbra_observation(socket,
                                    tag_id,
                                    pending_observation.reader_handle,
                                    pending_observation.message_kind,
                                    pending_observation.m,
                                    pending_observation.context_eligible,
                                    pending_observation.setup,
                                    pending_observation.tx_timestamp,
                                    d2r.timestamp,
                                    pending_observation.full_airtime_samples,
                                    AIOT_T2_OBS_COMPLETE,
                                    AIOT_T2_CBRA_GATE_D2R_ATTEMPTED,
                                    1,
                                    1,
                                    0,
                                    AIOT_RESULT_OK,
                                    0.0,
                                    0.0,
                                    pending_observation.random_id,
                                    pending_observation.access_occasion,
                                    AIOT_T2_CBRA_REPORT_MSG2_ACCEPTED,
                                    pending_observation.config_version,
                                    pending_observation.config_round,
                                    reflection_payload);
      pending_observation.valid = false;
      fprintf(stderr,
              "AIOT_T2_CBRA_REFLECTION_SENT tag_id=%u random_id=%u ao=%u samples=%zu waiting_msg3=1\n",
              tag_id,
              cbra_access.random_id,
              cbra_access.selected_access_occasion,
              d2r_samples);
    } else {
      c16_t tx_truth[AIOT_T2_MAX_PAYLOAD_BYTES] = {0};
      for (size_t i = 0; i < inventory_len; ++i)
        tx_truth[i].r = inventory[i];
      const samplesBlockHeader_t truth = {
          .size = inventory_len,
          .nbAnt = 1,
          .timestamp = d2r.timestamp,
          .option_value = tag_id,
          .option_flag = OPTION_AIOT_T2_TX_TRUTH | AIOT_T2_PACK_D2R_TBIT(r2d_tbit),
          .beam_map = 1,
      };
      aiot_write_rfsim_packet(socket, &truth, tx_truth);
      printf("AIOT_T2_TX_TRUTH_SENT tag_id=%u payload_bytes=%zu\n", tag_id, inventory_len);
    }
    aiot_write_rfsim_packet(socket, &d2r, reflected);
    if (!cbra_received) {
      ++completed_cycles;
      printf("AIOT_T2_BACKSCATTER tag_id=%u tbit=%u cw_samples=%zu d2r_samples=%zu cycle=%u/%u\n",
             tag_id,
             r2d_tbit,
             cw_samples,
             d2r_samples,
             completed_cycles,
             cycles);
    } else {
      printf("AIOT_T2_CBRA_BACKSCATTER_PENDING tag_id=%u tbit=%u cw_samples=%zu d2r_samples=%zu\n",
             tag_id,
             r2d_tbit,
             cw_samples,
             d2r_samples);
    }
    free(reflected);
    if (completed_cycles >= cycles) {
      free(samples);
      close(socket);
      return 0;
    }
    cw_samples = 0;
    cw_timestamp = 0;
    r2d_received = false;
    cbra_received = false;
    r2d_timestamp = 0;
  }

  if (cbra_access.waiting_msg3) {
    aiot_tag_send_cbra_observation(socket,
                                  tag_id,
                                  cbra_access.reader_handle,
                                  cbra_access.message_kind,
                                  cbra_access.m,
                                  1,
                                  0,
                                  cbra_access.reflection_timestamp,
                                  header.timestamp,
                                  0,
                                  AIOT_T2_OBS_UNDETECTED,
                                  AIOT_T2_CBRA_GATE_D2R_ATTEMPTED,
                                  1,
                                  0,
                                  0,
                                  AIOT_RESULT_TIMEOUT,
                                  0.0,
                                  0.0,
                                  cbra_access.random_id,
                                  (uint8_t)cbra_access.selected_access_occasion,
                                  AIOT_T2_CBRA_REPORT_MSG3_MISSING,
                                  cbra_access.config_version,
                                  cbra_access.config_round,
                                  cbra_access.reflection_payload);
  }
  if (pending_observation.valid) {
    aiot_tag_send_cbra_observation(socket,
                                  tag_id,
                                  pending_observation.reader_handle,
                                  pending_observation.message_kind,
                                  pending_observation.m,
                                  pending_observation.context_eligible,
                                  pending_observation.setup,
                                  pending_observation.tx_timestamp,
                                  header.timestamp,
                                  pending_observation.full_airtime_samples,
                                  AIOT_T2_OBS_UNDETECTED,
                                  AIOT_T2_CBRA_GATE_REFUSED,
                                  0,
                                  0,
                                  0,
                                  AIOT_RESULT_TIMEOUT,
                                  0.0,
                                  0.0,
                                  pending_observation.random_id,
                                  pending_observation.access_occasion,
                                  AIOT_T2_CBRA_REPORT_MSG2_TIMEOUT,
                                  pending_observation.config_version,
                                  pending_observation.config_round,
                                  pending_observation.decoded_pdu);
  }
  free(samples);
  fprintf(stderr, "AIOT_T2_CW_REJECT reason=connection_closed\n");
  return 1;
}

static int aiot_reader_rfsim_cli(int argc, char **argv)
{
  if (argc != 6) {
    fprintf(stderr, "Usage: %s --aiot-reader-rfsim <server> <port> <tag-id> <reader:awake|reader:asleep>\n", argv[0]);
    return 2;
  }

  uint32_t port = 0;
  uint32_t tag_id = 0;
  if (!aiot_parse_u32(argv[3], 1, UINT16_MAX, &port) || !aiot_parse_u32(argv[4], 1, AIOT_T2_MAX_TAG_ID, &tag_id)
      || (strcmp(argv[5], "reader:awake") != 0 && strcmp(argv[5], "reader:asleep") != 0)) {
    fprintf(stderr, "AIOT_T2_ARGUMENT_REJECT\n");
    return 2;
  }

  const int socket = client_start(argv[2], port);
  setblocking(socket, blocking);
  samplesBlockHeader_t header;
  c16_t *samples = NULL;
  size_t capacity = 0;
  if (!aiot_read_rfsim_packet(socket, &header, &samples, &capacity)) {
    free(samples);
    fprintf(stderr, "AIOT_T2_RFSIM_SYNC_REJECT\n");
    return 1;
  }

  if (strcmp(argv[5], "reader:asleep") == 0) {
    printf("AIOT_T2_R2D_REJECT reason=reader_asleep tag_id=%u\n", tag_id);
    free(samples);
    close(socket);
    return 0;
  }

  const uint8_t command = AIOT_INVENTORY_COMMAND;
  uint8_t r2d_chips[AIOT_T2_MAX_RF_SAMPLES];
  size_t r2d_chips_len = 0;
  if (aiot_encode_frame(&command, sizeof(command), false, r2d_chips, sizeof(r2d_chips), &r2d_chips_len)
      != AIOT_RESULT_OK) {
    free(samples);
    close(socket);
    return 1;
  }
  c16_t r2d[AIOT_T2_MAX_RF_SAMPLES] = {0};
  for (size_t i = 0; i < r2d_chips_len; ++i)
    r2d[i].r = r2d_chips[i];
  const samplesBlockHeader_t r2d_header = {
      .size = r2d_chips_len,
      .nbAnt = 1,
      .timestamp = header.timestamp + header.size,
      .option_value = tag_id,
      .option_flag = OPTION_AIOT_T2_R2D,
      .beam_map = 1,
  };
  aiot_write_rfsim_packet(socket, &r2d_header, r2d);
  printf("AIOT_T2_R2D_SENT tag_id=%u samples=%zu\n", tag_id, r2d_chips_len);

  while (aiot_read_rfsim_packet(socket, &header, &samples, &capacity)) {
    if ((header.option_flag & OPTION_AIOT_T2_D2R) == 0 || header.option_value != tag_id)
      continue;
    const uint32_t tbit = AIOT_T2_UNPACK_D2R_TBIT(header.option_flag);
    uint8_t chips[AIOT_T2_MAX_RF_SAMPLES];
    size_t inventory_len = 0;
    uint8_t inventory[AIOT_MAX_PAYLOAD_BYTES];
    const size_t samples_per_bit = aiot_t2_d2r_samples_per_bit(tbit);
    const size_t logical_chips = header.size / samples_per_bit * AIOT_D2R_CHIPS_PER_FRAME_BIT;
    if (header.nbAnt != 1 || !aiot_samples_to_chips(samples, header.size, tbit, chips)
        || !aiot_d2r_payload_length(header.size, tbit, &inventory_len)
        || aiot_decode_frame(chips, logical_chips, inventory_len, true, true, true, inventory) != AIOT_RESULT_OK) {
      fprintf(stderr, "AIOT_T2_D2R_REJECT reason=decode tag_id=%u\n", tag_id);
      free(samples);
      close(socket);
      return 1;
    }
    printf("AIOT_T2_D2R_CRC_OK tag_id=%u payload=", tag_id);
    for (size_t i = 0; i < inventory_len; ++i)
      printf("%02x", inventory[i]);
    printf("\nAIOT_T2_UE_REPORT_READY tag_id=%u transport=pending\n", tag_id);
    free(samples);
    close(socket);
    return 0;
  }

  free(samples);
  fprintf(stderr, "AIOT_T2_TIMEOUT tag_id=%u\n", tag_id);
  return 1;
}

int main(int argc, char *argv[]) {
  if (argc >= 2 && strcmp(argv[1], "--aiot-tag-self-test") == 0)
    return aiot_tag_self_test();
  if (argc >= 2 && strcmp(argv[1], "--aiot-tag") == 0) {
    crcTableInit();
    return aiot_tag_cli(argc, argv);
  }
  if (argc >= 2 && strcmp(argv[1], "--aiot-cw-rfsim") == 0)
    return aiot_cw_rfsim_cli(argc, argv);
  if (argc >= 2 && strcmp(argv[1], "--aiot-tag-rfsim") == 0) {
    crcTableInit();
    return aiot_tag_rfsim_cli(argc, argv);
  }
  if (argc >= 2 && strcmp(argv[1], "--aiot-reader-rfsim") == 0) {
    crcTableInit();
    return aiot_reader_rfsim_cli(argc, argv);
  }

  if(argc < 4) {
    printf("Need parameters: source file, server or destination IP, TCP port (4043), "
           "'UL|DL' if raw 2*16bits format: UL for UL IQ, DL for DL IQs\n"
           "Or: --aiot-tag-self-test\n"
           "Or: --aiot-tag <cw:on|off> <reader:awake|asleep> <none|invalid00|invalid11|crc|timeout> <inventory-hex>\n"
           "Or: --aiot-cw-rfsim <server> <port> <samples> <amplitude>\n"
           "Or: --aiot-tag-rfsim <server> <port> <tag-id> <inventory-hex>\n"
           "Or: --aiot-reader-rfsim <server> <port> <tag-id> <reader:awake|reader:asleep>\n");
    exit(1);
  }

  int fd;
  AssertFatal((fd=open(argv[1],O_RDONLY)) != -1, "file: %s", argv[1]);
  off_t fileSize=lseek(fd, 0, SEEK_END);
  int serviceSock;

  if (strcmp(argv[2],"server")==0) {
    serviceSock=server_start(atoi(argv[3]));
  } else {
    serviceSock=client_start(argv[2],atoi(argv[3]));
  }

  bool raw = false;

  if ( argc == 5 ) {
    raw=true;
  }

  samplesBlockHeader_t header;
  int bufSize=100000;
  void *buff=malloc(bufSize);
  uint64_t timestamp=0;
  const int blockSize=1920;
  // If fileSize is not multiple of blockSize*4 then discard remaining samples
  fileSize = (fileSize/(blockSize<<2))*(blockSize<<2);

  while (1) {
    //Rewind the file to loop on the samples
    if ( lseek(fd, 0, SEEK_CUR) >= fileSize )
      lseek(fd, 0, SEEK_SET);

    // Read one block and send it
    setblocking(serviceSock, blocking);

    if ( raw ) {
      header.size=blockSize;
      header.nbAnt=1;
      header.timestamp=timestamp;
      timestamp+=blockSize;
      header.option_value=0;
      header.option_flag=0;
    } else {
      AssertFatal(read(fd,&header,sizeof(header)), "");
    }

    fullwrite(serviceSock, &header, sizeof(header));
    int dataSize=sizeof(int32_t)*header.size*header.nbAnt;

    if (dataSize>bufSize) {
      void *new_buff = realloc(buff, dataSize);

      if (new_buff == NULL) {
        free(buff);
        AssertFatal(1, "Could not reallocate");
      } else {
        buff = new_buff;
      }
    }

    AssertFatal(read(fd,buff,dataSize) == dataSize, "");

    if (raw) // UHD shifts the 12 ADC values in MSB
      for (int i=0; i<header.size*header.nbAnt*2; i++)
        ((int16_t *)buff)[i]/=16;

    usleep(1000);
    printf("sending at ts: %lu, number of samples: %d\n",
           header.timestamp, header.size);
    fullwrite(serviceSock, buff, dataSize);
    // Purge incoming samples
    setblocking(serviceSock, notBlocking);
    int ret;

    do {
      char buff[64000];
      ret=read(serviceSock, buff, 64000);

      if ( ret<0 && !( errno == EAGAIN || errno == EWOULDBLOCK ) ) {
        printf("error: %s\n", strerror(errno));
        exit(1);
      }
    } while ( ret > 0 ) ;
  }

  return 0;
}
