/* Licensed under the OAI Public License, Version 1.1.
 * See the repository NOTICE and http://www.openairinterface.org/?page_id=698.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "PHY/NR_UE_TRANSPORT/nr_transport_proto_ue.h"

int main(void)
{
  /* TS 38.291 V19.3.0 table 4.3.3.3-1: density 12 requires at least two R2D PRBs.
   * Explicit checks remain active in RelWithDebInfo builds with NDEBUG. */
  const struct {
    const char *name;
    unsigned int prb_count;
    unsigned int chips_per_symbol;
    nr_ue_aiot_r2d_resource_result_t expected;
    const char *expected_reason;
  } cases[] = {
      {"AcceptsTwoChipsWithOneR2dPrb", 1, 2, NR_UE_AIOT_R2D_RESOURCE_OK, NULL},
      {"AcceptsSixChipsWithOneR2dPrb", 1, 6, NR_UE_AIOT_R2D_RESOURCE_OK, NULL},
      {"RejectsTwelveChipsWithOneR2dPrb", 1, 12, NR_UE_AIOT_R2D_INSUFFICIENT_PRBS, "insufficient_r2d_prbs"},
      {"AcceptsTwelveChipsWithTwoR2dPrbs", 2, 12, NR_UE_AIOT_R2D_RESOURCE_OK, NULL},
      {"RejectsTwentyFourChipsWithTwoR2dPrbs", 2, 24, NR_UE_AIOT_R2D_INSUFFICIENT_PRBS, "insufficient_r2d_prbs"},
      {"AcceptsTwentyFourChipsWithThreeR2dPrbs", 3, 24, NR_UE_AIOT_R2D_RESOURCE_OK, NULL},
      {"RejectsZeroR2dPrbs", 0, 6, NR_UE_AIOT_R2D_INVALID_RESOURCE, "invalid_r2d_prbs"},
      {"RejectsUnknownR2dDensity", 1, 1, NR_UE_AIOT_R2D_INVALID_RESOURCE, "invalid_r2d_density"},
  };

  for (size_t i = 0; i < sizeof(cases) / sizeof(cases[0]); ++i) {
    const char *reason = NULL;
    const nr_ue_aiot_r2d_resource_result_t actual =
        nr_ue_aiot_validate_r2d_resources(cases[i].prb_count, cases[i].chips_per_symbol, &reason);
    if (actual != cases[i].expected
        || (cases[i].expected_reason != NULL
            && (reason == NULL || strcmp(reason, cases[i].expected_reason) != 0))) {
      fprintf(stderr,
              "FAIL %s: expected status=%d reason=%s; actual status=%d reason=%s\n",
              cases[i].name,
              cases[i].expected,
              cases[i].expected_reason != NULL ? cases[i].expected_reason : "<any>",
              actual,
              reason != NULL ? reason : "<null>");
      return 1;
    }
  }

  if (nr_ue_aiot_validate_r2d_resources(1, 12, NULL) != NR_UE_AIOT_R2D_INSUFFICIENT_PRBS) {
    fprintf(stderr, "FAIL AllowsOptionalReasonOutput: reason=NULL must not change admission\n");
    return 1;
  }

  const uint32_t packed_target = AIOT_T2_PACK_R2D_TARGET(100, 3, 7);
  if (AIOT_T2_UNPACK_R2D_TAG(packed_target) != 100
      || AIOT_T2_UNPACK_R2D_READER(packed_target) != 3
      || AIOT_T2_UNPACK_R2D_TBIT(packed_target) != 7) {
    fprintf(stderr, "FAIL PacksR2dReaderWithoutChangingBeamSelector\n");
    return 1;
  }

  const nr_ue_aiot_d2r_scheduling_t factor_eight = {
      .x = 1,
      .tbit = NR_UE_AIOT_D2R_TBIT_TAU_OVER_16,
      .sfs_bitmap = 0x10,
  };
  unsigned int n_sfs = 99;
  unsigned int m = 99;
  const char *scheduling_reason = NULL;
  if (nr_ue_aiot_validate_d2r_scheduling(&factor_eight, &n_sfs, &m, &scheduling_reason)
          != NR_UE_AIOT_D2R_SCHED_ILLEGAL_SFS
      || scheduling_reason == NULL || strcmp(scheduling_reason, "illegal_sfs_for_tbit") != 0 || n_sfs != 99 || m != 99) {
    fprintf(stderr, "FAIL RejectsFactorEightForTauOver16\n");
    return 1;
  }

  const nr_ue_aiot_d2r_scheduling_t counted_factors = {
      .x = 2,
      .tbit = NR_UE_AIOT_D2R_TBIT_TAU_OVER_16,
      .sfs_bitmap = 0xe0,
  };
  n_sfs = 0;
  m = 0;
  scheduling_reason = NULL;
  if (nr_ue_aiot_validate_d2r_scheduling(&counted_factors, &n_sfs, &m, &scheduling_reason)
          != NR_UE_AIOT_D2R_SCHED_OK
      || n_sfs != 3 || m != 6 || scheduling_reason != NULL) {
    fprintf(stderr, "FAIL CountsEnabledFactorsNotLargestFactor\n");
    return 1;
  }

  const struct {
    nr_ue_aiot_d2r_tbit_t tbit;
    uint8_t allowed_bitmap;
  } tbit_rows[] = {
      {NR_UE_AIOT_D2R_TBIT_2_TAU, 0xff},
      {NR_UE_AIOT_D2R_TBIT_TAU, 0xfe},
      {NR_UE_AIOT_D2R_TBIT_TAU_OVER_2, 0xfc},
      {NR_UE_AIOT_D2R_TBIT_TAU_OVER_4, 0xf8},
      {NR_UE_AIOT_D2R_TBIT_TAU_OVER_8, 0xf0},
      {NR_UE_AIOT_D2R_TBIT_TAU_OVER_16, 0xe0},
      {NR_UE_AIOT_D2R_TBIT_TAU_OVER_32, 0xc0},
      {NR_UE_AIOT_D2R_TBIT_TAU_OVER_96, 0x80},
  };
  for (size_t i = 0; i < sizeof(tbit_rows) / sizeof(tbit_rows[0]); ++i) {
    const nr_ue_aiot_d2r_scheduling_t row = {
        .x = 1,
        .tbit = tbit_rows[i].tbit,
        .sfs_bitmap = tbit_rows[i].allowed_bitmap,
    };
    n_sfs = 99;
    m = 99;
    scheduling_reason = NULL;
    if (nr_ue_aiot_validate_d2r_scheduling(&row, &n_sfs, &m, &scheduling_reason)
            != NR_UE_AIOT_D2R_SCHED_OK
        || n_sfs != 8 - i || m != 8 - i || scheduling_reason != NULL) {
      fprintf(stderr, "FAIL AcceptsAllEightTbitRows row=%zu\n", i);
      return 1;
    }
    if (i > 0) {
      const nr_ue_aiot_d2r_scheduling_t illegal_row = {
          .x = 1,
          .tbit = tbit_rows[i].tbit,
          .sfs_bitmap = (uint8_t)(tbit_rows[i].allowed_bitmap | (1U << (i - 1))),
      };
      if (nr_ue_aiot_validate_d2r_scheduling(&illegal_row, NULL, NULL, &scheduling_reason)
          != NR_UE_AIOT_D2R_SCHED_ILLEGAL_SFS) {
        fprintf(stderr, "FAIL RejectsOutOfRangeTbitFactor row=%zu\n", i);
        return 1;
      }
    }
  }

  const nr_ue_aiot_d2r_scheduling_t empty_bitmap = {
      .x = 1,
      .tbit = NR_UE_AIOT_D2R_TBIT_TAU,
      .sfs_bitmap = 0,
  };
  if (nr_ue_aiot_validate_d2r_scheduling(&empty_bitmap, NULL, NULL, &scheduling_reason)
          != NR_UE_AIOT_D2R_SCHED_INVALID
      || scheduling_reason == NULL || strcmp(scheduling_reason, "empty_sfs_bitmap") != 0) {
    fprintf(stderr, "FAIL RejectsEmptySfsBitmap\n");
    return 1;
  }

  const nr_ue_aiot_d2r_scheduling_t invalid_x = {
      .x = 3,
      .tbit = NR_UE_AIOT_D2R_TBIT_TAU,
      .sfs_bitmap = 0x80,
  };
  if (nr_ue_aiot_validate_d2r_scheduling(&invalid_x, NULL, NULL, &scheduling_reason)
          != NR_UE_AIOT_D2R_SCHED_INVALID
      || scheduling_reason == NULL || strcmp(scheduling_reason, "invalid_d2r_x") != 0) {
    fprintf(stderr, "FAIL RejectsInvalidTimeResourceCount\n");
    return 1;
  }

  const nr_ue_aiot_d2r_scheduling_t zero_x = {
      .x = 0,
      .tbit = NR_UE_AIOT_D2R_TBIT_TAU,
      .sfs_bitmap = 0x80,
  };
  if (nr_ue_aiot_validate_d2r_scheduling(&zero_x, NULL, NULL, &scheduling_reason)
          != NR_UE_AIOT_D2R_SCHED_INVALID
      || scheduling_reason == NULL || strcmp(scheduling_reason, "invalid_d2r_x") != 0) {
    fprintf(stderr, "FAIL RejectsZeroTimeResourceCount\n");
    return 1;
  }

  const nr_ue_aiot_d2r_scheduling_t invalid_tbit = {
      .x = 1,
      .tbit = NR_UE_AIOT_D2R_TBIT_COUNT,
      .sfs_bitmap = 0x80,
  };
  if (nr_ue_aiot_validate_d2r_scheduling(&invalid_tbit, NULL, NULL, &scheduling_reason)
          != NR_UE_AIOT_D2R_SCHED_INVALID
      || scheduling_reason == NULL || strcmp(scheduling_reason, "invalid_d2r_tbit") != 0) {
    fprintf(stderr, "FAIL RejectsInvalidTbit\n");
    return 1;
  }

  const nr_ue_aiot_d2r_scheduling_t set_32_64 = {
      .x = 1,
      .tbit = NR_UE_AIOT_D2R_TBIT_TAU,
      .sfs_bitmap = 0x06,
  };
  nr_ue_aiot_d2r_timing_t timing;
  scheduling_reason = NULL;
  if (!nr_ue_aiot_derive_d2r_timing(&set_32_64, 2, &timing, &scheduling_reason)
      || timing.tchip_prime.numerator != 1 || timing.tchip_prime.denominator != 64
      || timing.toffset.numerator != 1 || timing.toffset.denominator != 1 || scheduling_reason != NULL) {
    fprintf(stderr, "FAIL UsesLargestChipDurationOfIndicatedSet\n");
    return 1;
  }

  const nr_ue_aiot_d2r_scheduling_t singleton_64 = {
      .x = 1,
      .tbit = NR_UE_AIOT_D2R_TBIT_TAU,
      .sfs_bitmap = 0x02,
  };
  const unsigned int response_densities[] = {2, 6, 12, 24};
  const nr_ue_aiot_time_ratio_t expected_offsets[] = {
      {.numerator = 1, .denominator = 1},
      {.numerator = 1, .denominator = 4},
      {.numerator = 1, .denominator = 4},
      {.numerator = 1, .denominator = 4},
  };
  for (size_t i = 0; i < sizeof(response_densities) / sizeof(response_densities[0]); ++i) {
    scheduling_reason = NULL;
    if (!nr_ue_aiot_derive_d2r_timing(&singleton_64, response_densities[i], &timing, &scheduling_reason)
        || timing.tchip_prime.numerator != 1 || timing.tchip_prime.denominator != 128
        || timing.toffset.numerator != expected_offsets[i].numerator
        || timing.toffset.denominator != expected_offsets[i].denominator || scheduling_reason != NULL) {
      fprintf(stderr, "FAIL ChangesResponseOffsetWithR2dDensity density=%u\n", response_densities[i]);
      return 1;
    }
  }

  const nr_ue_aiot_d2r_scheduling_t invalid_timing_density = {
      .x = 1,
      .tbit = NR_UE_AIOT_D2R_TBIT_TAU,
      .sfs_bitmap = 0x02,
  };
  if (nr_ue_aiot_derive_d2r_timing(&invalid_timing_density, 3, &timing, &scheduling_reason)
      || scheduling_reason == NULL || strcmp(scheduling_reason, "invalid_r2d_density") != 0) {
    fprintf(stderr, "FAIL RejectsInvalidR2dDensityForResponseTiming\n");
    return 1;
  }

  const char *reason = NULL;
  aiot_t2_rf_packet_t invalid_request_packet;
  memset(&invalid_request_packet, 0x5A, sizeof(invalid_request_packet));
  const aiot_t2_rf_packet_t invalid_request_before = invalid_request_packet;
  reason = NULL;
  if (nr_ue_aiot_t2_prepare_r2d_with_resources(NULL, &invalid_request_packet, &reason)
          || reason == NULL || strcmp(reason, "invalid_r2d_request") != 0
          || memcmp(&invalid_request_packet, &invalid_request_before, sizeof(invalid_request_packet)) != 0) {
    fprintf(stderr, "FAIL RejectsNullR2dRequest\n");
    return 1;
  }

  const nr_ue_aiot_r2d_request_t invalid_tag_request = {
      .tag_id = 0,
      .timestamp = 100,
      .prb_count = 2,
      .chips_per_symbol = 12,
  };
  aiot_t2_rf_packet_t invalid_tag_packet;
  memset(&invalid_tag_packet, 0x5A, sizeof(invalid_tag_packet));
  const aiot_t2_rf_packet_t invalid_tag_before = invalid_tag_packet;
  reason = NULL;
  if (nr_ue_aiot_t2_prepare_r2d_with_resources(&invalid_tag_request, &invalid_tag_packet, &reason)
          || reason == NULL || strcmp(reason, "invalid_tag_id") != 0
          || memcmp(&invalid_tag_packet, &invalid_tag_before, sizeof(invalid_tag_packet)) != 0) {
    fprintf(stderr, "FAIL RejectsInvalidTagWithoutProducingPacket\n");
    return 1;
  }

  nr_ue_aiot_r2d_request_t rejected_request = {
      .tag_id = 1,
      .timestamp = 100,
      .prb_count = 1,
      .chips_per_symbol = 12,
  };
  aiot_t2_rf_packet_t rejected_packet;
  memset(&rejected_packet, 0xA5, sizeof(rejected_packet));
  aiot_t2_rf_packet_t rejected_before = rejected_packet;
  if (nr_ue_aiot_t2_prepare_r2d_with_resources(&rejected_request, &rejected_packet, &reason)
          || reason == NULL || strcmp(reason, "insufficient_r2d_prbs") != 0
          || memcmp(&rejected_packet, &rejected_before, sizeof(rejected_packet)) != 0) {
    fprintf(stderr, "FAIL RejectsInsufficientGrantWithoutProducingPacket\n");
    return 1;
  }

  const nr_ue_aiot_r2d_request_t invalid_schedule_request = {
      .tag_id = 1,
      .timestamp = 100,
      .prb_count = 2,
      .chips_per_symbol = 12,
      .d2r_scheduling = &factor_eight,
  };
  aiot_t2_rf_packet_t invalid_schedule_packet;
  memset(&invalid_schedule_packet, 0xA5, sizeof(invalid_schedule_packet));
  const aiot_t2_rf_packet_t invalid_schedule_before = invalid_schedule_packet;
  reason = NULL;
  if (nr_ue_aiot_t2_prepare_r2d_with_resources(&invalid_schedule_request, &invalid_schedule_packet, &reason)
          || reason == NULL || strcmp(reason, "illegal_sfs_for_tbit") != 0
          || memcmp(&invalid_schedule_packet, &invalid_schedule_before, sizeof(invalid_schedule_packet)) != 0) {
    fprintf(stderr, "FAIL RejectsIllegalSchedulingBeforeR2dOutput\n");
    return 1;
  }

  const nr_ue_aiot_r2d_request_t accepted_request = {
      .tag_id = 1,
      .timestamp = 100,
      .prb_count = 2,
      .chips_per_symbol = 12,
      .d2r_scheduling = &counted_factors,
  };
  aiot_t2_rf_packet_t accepted_packet;
  memset(&accepted_packet, 0xA5, sizeof(accepted_packet));
  reason = NULL;
  if (!nr_ue_aiot_t2_prepare_r2d_with_resources(&accepted_request, &accepted_packet, &reason)
      || reason != NULL || accepted_packet.header.option_value != accepted_request.tag_id
      || accepted_packet.header.option_flag != OPTION_AIOT_T2_R2D) {
    fprintf(stderr, "FAIL AcceptsSupportedGrantAndProducesPacket\n");
    return 1;
  }

  aiot_t2_rf_packet_t d2r_packet;
  if (!nr_ue_aiot_t2_prepare_r2d(1, 100, &d2r_packet)) {
    fprintf(stderr, "FAIL PreparesKnownTwoChipD2rPacket\n");
    return 1;
  }
  d2r_packet.header.option_flag = OPTION_AIOT_T2_D2R | AIOT_T2_PACK_D2R_TBIT(6);
  if (AIOT_T2_UNPACK_D2R_TBIT(d2r_packet.header.option_flag) != 6) {
    fprintf(stderr, "FAIL CarriesD2rTbitMetadata\n");
    return 1;
  }
  uint8_t decoded_payload[AIOT_T2_MAX_PAYLOAD_BYTES] = {0};
  size_t decoded_payload_len = 0;
  if (nr_ue_aiot_t2_decode_d2r(&d2r_packet, decoded_payload, sizeof(decoded_payload), &decoded_payload_len)
          != NR_UE_AIOT_T2_DECODE_OK
      || decoded_payload_len != 1 || decoded_payload[0] != 0x01) {
    fprintf(stderr, "FAIL DecodesSingleLayerTwoChipD2rFrame\n");
    return 1;
  }

  if (aiot_t2_d2r_samples_per_bit(0) != 4 || aiot_t2_d2r_samples_per_bit(1) != 2
      || aiot_t2_d2r_samples_per_bit(2) != 2) {
    fprintf(stderr, "FAIL UsesExpectedD2rSampleQuantization\n");
    return 1;
  }
  aiot_t2_rf_packet_t slow_d2r = {0};
  slow_d2r.header = d2r_packet.header;
  slow_d2r.header.option_flag = OPTION_AIOT_T2_D2R | AIOT_T2_PACK_D2R_TBIT(0);
  slow_d2r.header.size = d2r_packet.header.size * 2;
  for (size_t sample = 0; sample < d2r_packet.header.size; ++sample) {
    slow_d2r.samples[sample * 2] = d2r_packet.samples[sample];
    slow_d2r.samples[sample * 2 + 1] = d2r_packet.samples[sample];
  }
  if (nr_ue_aiot_t2_decode_d2r(&slow_d2r, decoded_payload, sizeof(decoded_payload), &decoded_payload_len)
          != NR_UE_AIOT_T2_DECODE_OK
      || decoded_payload_len != 1 || decoded_payload[0] != 0x01) {
    fprintf(stderr, "FAIL DecodesTwoTauD2rFrame\n");
    return 1;
  }

  d2r_packet.samples[7 * 2].r = 1;
  d2r_packet.samples[7 * 2 + 1].r = 3;
  if (nr_ue_aiot_t2_decode_d2r(&d2r_packet, decoded_payload, sizeof(decoded_payload), &decoded_payload_len)
          != NR_UE_AIOT_T2_DECODE_OK
      || decoded_payload_len != 1 || decoded_payload[0] != 0x01) {
    fprintf(stderr, "FAIL DecodesNoisyTwoChipEnergyOrdering\n");
    return 1;
  }

  d2r_packet.header.option_value = AIOT_T2_PACK_TAG_PROVENANCE(1, 42);
  if (nr_ue_aiot_t2_decode_d2r(&d2r_packet, decoded_payload, sizeof(decoded_payload), &decoded_payload_len)
          != NR_UE_AIOT_T2_DECODE_OK
      || decoded_payload_len != 1 || decoded_payload[0] != 0x01) {
    fprintf(stderr, "FAIL DecodesPackedTagProvenance\n");
    return 1;
  }

  if (!nr_ue_aiot_t2_prepare_r2d(100, 100, &d2r_packet)) {
    fprintf(stderr, "FAIL AcceptsScenarioMaximumTagId\n");
    return 1;
  }

  const uint8_t security[NR_UE_AIOT_CBRA_SECURITY_BYTES] = {
      0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07,
      0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f,
  };
  nr_ue_aiot_cbra_paging_fields_t paging_fields = {
      .serial = 100,
      .security_parameter = {0},
      .transaction_id = 0,
      .number_of_access_occasions = 1,
      .k = 0,
      .d2r_scheduling_info = NR_UE_AIOT_CBRA_FROZEN_D2R_SCHEDULING_INFO,
  };
  memcpy(paging_fields.security_parameter, security, sizeof(security));
  uint8_t paging_pdu[NR_UE_AIOT_CBRA_PAGING_PDU_BYTES] = {0};
  reason = NULL;
  if (!nr_ue_aiot_cbra_build_paging_pdu(&paging_fields, paging_pdu, &reason) || reason != NULL) {
    fprintf(stderr, "FAIL Builds224BitCbraPagingPdu\n");
    return 1;
  }
  nr_ue_aiot_cbra_d2r_scheduling_t decoded_schedule = {0};
  reason = NULL;
  if (!nr_ue_aiot_cbra_unpack_d2r_scheduling(paging_fields.d2r_scheduling_info, &decoded_schedule, &reason)
      || decoded_schedule.x != 1 || decoded_schedule.bit_duration != NR_UE_AIOT_D2R_TBIT_TAU
      || decoded_schedule.frequency_resource_broadcast != 0x80 || reason != NULL) {
    fprintf(stderr, "FAIL UnpacksCbraSchedulingFields\n");
    return 1;
  }
  nr_ue_aiot_cbra_paging_fields_t parsed_fields = {0};
  reason = NULL;
  if (!nr_ue_aiot_cbra_parse_paging_pdu(paging_pdu, &parsed_fields, &reason)
      || reason != NULL || parsed_fields.serial != paging_fields.serial
      || parsed_fields.transaction_id != paging_fields.transaction_id
      || parsed_fields.number_of_access_occasions != paging_fields.number_of_access_occasions
      || parsed_fields.k != paging_fields.k
      || parsed_fields.d2r_scheduling_info != paging_fields.d2r_scheduling_info
      || memcmp(parsed_fields.security_parameter, security, sizeof(security)) != 0) {
    fprintf(stderr, "FAIL RoundTripsCbraPagingFields\n");
    return 1;
  }
  uint8_t paging_phy[NR_UE_AIOT_CBRA_PAGING_PHY_BYTES] = {0};
  if (!nr_ue_aiot_cbra_append_paging_crc(paging_pdu, paging_phy)
      || memcmp(paging_phy, paging_pdu, NR_UE_AIOT_CBRA_PAGING_PDU_BYTES) != 0) {
    fprintf(stderr, "FAIL AppendsCbraPagingCrc16\n");
    return 1;
  }
  if (!nr_ue_aiot_cbra_verify_paging_crc(paging_phy)) {
    fprintf(stderr, "FAIL VerifiesCbraPagingCrc16\n");
    return 1;
  }
  paging_phy[NR_UE_AIOT_CBRA_PAGING_PHY_BYTES - 1U] ^= 0x01U;
  if (nr_ue_aiot_cbra_verify_paging_crc(paging_phy)) {
    fprintf(stderr, "FAIL RejectsCorruptedCbraPagingCrc\n");
    return 1;
  }
  if (!nr_ue_aiot_cbra_append_paging_crc(paging_pdu, paging_phy)) {
    fprintf(stderr, "FAIL RebuildsCbraPagingCrc16\n");
    return 1;
  }
  nr_ue_aiot_cbra_paging_fields_t tag_101_fields = paging_fields;
  tag_101_fields.serial = 101;
  uint8_t tag_101_pdu[NR_UE_AIOT_CBRA_PAGING_PDU_BYTES] = {0};
  if (!nr_ue_aiot_cbra_build_paging_pdu(&tag_101_fields, tag_101_pdu, &reason)
      || memcmp(paging_pdu, tag_101_pdu, sizeof(paging_pdu)) == 0) {
    fprintf(stderr, "FAIL DistinguishesTag100And101Pdu\n");
    return 1;
  }
  const uint32_t serials[] = {100, 101};
  reason = NULL;
  if (nr_ue_aiot_cbra_validate_serial(101, serials, 2, &reason)
      || reason == NULL || strcmp(reason, "duplicate_serial") != 0) {
    fprintf(stderr, "FAIL RejectsDuplicateCbraSerial\n");
    return 1;
  }
  reason = NULL;
  if (nr_ue_aiot_cbra_validate_serial(0, NULL, 0, &reason)
      || reason == NULL || strcmp(reason, "invalid_serial") != 0) {
    fprintf(stderr, "FAIL RejectsZeroCbraSerial\n");
    return 1;
  }
  paging_pdu[0] ^= 0x80;
  reason = NULL;
  if (nr_ue_aiot_cbra_parse_paging_pdu(paging_pdu, &parsed_fields, &reason)
      || reason == NULL || strcmp(reason, "invalid_message_type") != 0) {
    fprintf(stderr, "FAIL RejectsMalformedCbraPagingPdu\n");
    return 1;
  }
  if (nr_ue_aiot_cbra_parse_paging_pdu_length(tag_101_pdu,
                                              NR_UE_AIOT_CBRA_PAGING_PDU_BYTES - 1U,
                                              &parsed_fields,
                                              &reason)
      || reason == NULL || strcmp(reason, "invalid_pdu_length") != 0) {
    fprintf(stderr, "FAIL RejectsTruncatedCbraPagingPdu\n");
    return 1;
  }

  uint8_t invalid_paging_pdu[NR_UE_AIOT_CBRA_PAGING_PDU_BYTES];
  const uint8_t invalid_paging_before = 0xA5;
  memset(invalid_paging_pdu, invalid_paging_before, sizeof(invalid_paging_pdu));
  nr_ue_aiot_cbra_paging_fields_t invalid_paging_fields = paging_fields;
  invalid_paging_fields.d2r_scheduling_info = 0x123456;
  reason = NULL;
  if (nr_ue_aiot_cbra_build_paging_pdu(&invalid_paging_fields, invalid_paging_pdu, &reason)
      || reason == NULL || strcmp(reason, "invalid_scheduling_info") != 0
      || invalid_paging_pdu[0] != invalid_paging_before
      || invalid_paging_pdu[NR_UE_AIOT_CBRA_PAGING_PDU_BYTES - 1U] != invalid_paging_before) {
    fprintf(stderr, "FAIL RefusesNonFrozenCbraPagingBeforeSerialization\n");
    return 1;
  }

  const nr_ue_aiot_cbra_d2r_scheduling_t cbra_schedule = {
      .x = 1,
      .bit_duration = NR_UE_AIOT_D2R_TBIT_TAU,
      .frequency_resource_broadcast = 0x80,
      .block_repetition = 0,
      .channel_coding = 1,
      .interval_bits = 1,
      .sequence_length = 0,
      .additional_midamble = 0,
  };
  uint32_t packed_schedule = 0;
  reason = NULL;
  if (!nr_ue_aiot_cbra_pack_d2r_scheduling(&cbra_schedule, &packed_schedule, &reason)
      || reason != NULL || packed_schedule != NR_UE_AIOT_CBRA_FROZEN_D2R_SCHEDULING_INFO) {
    fprintf(stderr, "FAIL PacksFrozenCbraD2rScheduling expected=0x%06x actual=0x%06x\n",
            NR_UE_AIOT_CBRA_FROZEN_D2R_SCHEDULING_INFO, packed_schedule);
    return 1;
  }
  const nr_ue_aiot_cbra_d2r_scheduling_t dynamic_schedule = {
      .x = 2,
      .bit_duration = NR_UE_AIOT_D2R_TBIT_TAU_OVER_2,
      .frequency_resource_broadcast = 0xc0,
      .block_repetition = 1,
      .channel_coding = 1,
      .interval_bits = 3,
      .sequence_length = 1,
      .additional_midamble = 1,
  };
  reason = NULL;
  if (!nr_ue_aiot_cbra_pack_d2r_scheduling(&dynamic_schedule, &packed_schedule, &reason)
      || reason != NULL) {
    fprintf(stderr, "FAIL PacksDynamicCbraD2rScheduling\n");
    return 1;
  }
  nr_ue_aiot_cbra_d2r_scheduling_t unpacked_dynamic_schedule = {0};
  reason = NULL;
  if (!nr_ue_aiot_cbra_unpack_d2r_scheduling(packed_schedule, &unpacked_dynamic_schedule, &reason)
      || memcmp(&dynamic_schedule, &unpacked_dynamic_schedule, sizeof(dynamic_schedule)) != 0
      || reason != NULL) {
    fprintf(stderr, "FAIL RoundTripsDynamicCbraD2rScheduling\n");
    return 1;
  }
  nr_ue_aiot_cbra_paging_fields_t dynamic_fields = paging_fields;
  dynamic_fields.number_of_access_occasions = 5;
  dynamic_fields.k = 1;
  dynamic_fields.d2r_scheduling_info = packed_schedule;
  uint8_t dynamic_pdu[NR_UE_AIOT_CBRA_PAGING_PDU_BYTES] = {0};
  if (!nr_ue_aiot_cbra_build_paging_pdu(&dynamic_fields, dynamic_pdu, &reason)) {
    fprintf(stderr, "FAIL BuildsDynamicCbraPagingPdu\n");
    return 1;
  }
  nr_ue_aiot_cbra_paging_fields_t dynamic_parsed = {0};
  if (!nr_ue_aiot_cbra_parse_paging_pdu(dynamic_pdu, &dynamic_parsed, &reason)
      || dynamic_parsed.number_of_access_occasions != 5 || dynamic_parsed.k != 1
      || dynamic_parsed.d2r_scheduling_info != packed_schedule) {
    fprintf(stderr, "FAIL RoundTripsDynamicCbraPagingFields\n");
    return 1;
  }
  const int32_t snr_grid[] = {-10, 0, 10};
  const nr_ue_aiot_cbra_campaign_config_t campaign = {
      .message_kind = NR_UE_AIOT_CBRA_PAGING,
      .m = 6,
      .prb_count = 3,
      .reference_snr_db_x10 = 100,
      .formal_packet_budget = 10000,
      .data_seed = 7,
      .noise_seed = 11,
      .snr_grid_db_x10 = snr_grid,
      .snr_grid_count = sizeof(snr_grid) / sizeof(snr_grid[0]),
      .d2r_scheduling_info = NR_UE_AIOT_CBRA_FROZEN_D2R_SCHEDULING_INFO,
  };
  reason = NULL;
  if (!nr_ue_aiot_cbra_validate_campaign_config(&campaign, &reason) || reason != NULL) {
    fprintf(stderr, "FAIL AcceptsCompleteCbraPagingCampaignConfig\n");
    return 1;
  }
  nr_ue_aiot_cbra_campaign_config_t invalid_campaign = campaign;
  invalid_campaign.m = 3;
  reason = NULL;
  if (nr_ue_aiot_cbra_validate_campaign_config(&invalid_campaign, &reason)
      || reason == NULL || strcmp(reason, "invalid_m") != 0) {
    fprintf(stderr, "FAIL RejectsUnsupportedCbraM\n");
    return 1;
  }
  invalid_campaign = campaign;
  invalid_campaign.prb_count = 2;
  reason = NULL;
  if (nr_ue_aiot_cbra_validate_campaign_config(&invalid_campaign, &reason)
      || reason == NULL || strcmp(reason, "invalid_prb_count") != 0) {
    fprintf(stderr, "FAIL RejectsNonThreePrbCbraProfile\n");
    return 1;
  }
  invalid_campaign = campaign;
  invalid_campaign.data_seed = invalid_campaign.noise_seed;
  reason = NULL;
  if (nr_ue_aiot_cbra_validate_campaign_config(&invalid_campaign, &reason)
      || reason == NULL || strcmp(reason, "duplicate_seed") != 0) {
    fprintf(stderr, "FAIL RejectsDuplicateCbraSeeds\n");
    return 1;
  }
  invalid_campaign = campaign;
  invalid_campaign.d2r_scheduling_info = 0x123456;
  reason = NULL;
  if (nr_ue_aiot_cbra_validate_campaign_config(&invalid_campaign, &reason)
      || reason == NULL || strcmp(reason, "invalid_scheduling_info") != 0) {
    fprintf(stderr, "FAIL RejectsNonFrozenCbraSchedulingInfo\n");
    return 1;
  }
  invalid_campaign = campaign;
  invalid_campaign.message_kind = (nr_ue_aiot_cbra_message_kind_t)2;
  reason = NULL;
  if (nr_ue_aiot_cbra_validate_campaign_config(&invalid_campaign, &reason)
      || reason == NULL || strcmp(reason, "invalid_message_kind") != 0) {
    fprintf(stderr, "FAIL RejectsUnknownCbraMessageKind\n");
    return 1;
  }
  const uint8_t cbra_m_values[] = {2, 6, 12, 24};
  const uint16_t expected_symbols[] = {246, 84, 43, 25};
  const uint16_t expected_occupied_chips[] = {496, 500, 500, 560};
  const uint16_t expected_padding_chips[] = {0, 4, 4, 18};
  const uint16_t expected_reserved_chips[] = {0, 0, 0, 46};
  const uint32_t expected_ofdm_samples[] = {269904, 92160, 47184, 27432};
  const uint64_t expected_airtime_ns[] = {17571875, 6000000, 3071875, 1785938};
  for (size_t index = 0; index < sizeof(cbra_m_values) / sizeof(cbra_m_values[0]); ++index) {
    nr_ue_aiot_cbra_frame_t frame = {0};
    reason = NULL;
    if (!nr_ue_aiot_cbra_derive_frame(NR_UE_AIOT_CBRA_PAGING, cbra_m_values[index], 3, &frame, &reason)
        || reason != NULL || frame.mac_bits != NR_UE_AIOT_CBRA_PAGING_PDU_BITS
        || frame.phy_bits != NR_UE_AIOT_CBRA_PAGING_PHY_BITS
        || frame.prdch_chips != 480 || frame.data_and_overhead_chips != 488
        || frame.frame_symbols != expected_symbols[index]
        || frame.occupied_chip_positions != expected_occupied_chips[index]
        || frame.r_tas_sip_chips != 8 || frame.r_tas_cap_chips != 4 || frame.postamble_chips != 4
        || frame.padding_chips != expected_padding_chips[index]
        || frame.mapping_reserved_chips != expected_reserved_chips[index]
        || frame.emitted_chip_count != expected_occupied_chips[index]
        || frame.ofdm_sample_count != expected_ofdm_samples[index]
        || frame.on_air_duration_ns != expected_airtime_ns[index]) {
      fprintf(stderr, "FAIL DerivesCbraPagingFrame m=%u symbols=%u occupied=%u\n",
              cbra_m_values[index], frame.frame_symbols, frame.occupied_chip_positions);
      return 1;
    }
    aiot_t2_rf_packet_t cbra_packet = {0};
    reason = NULL;
    if (!nr_ue_aiot_cbra_prepare_paging_r2d(&paging_fields, 100, 1, 100, cbra_m_values[index], 3,
                                            &cbra_packet, &reason)
        || reason != NULL || cbra_packet.header.size != expected_occupied_chips[index]
        || (cbra_packet.header.option_flag & (OPTION_AIOT_T2_R2D | OPTION_AIOT_T2_R2D_CBRA))
               != (OPTION_AIOT_T2_R2D | OPTION_AIOT_T2_R2D_CBRA)
        || AIOT_T2_UNPACK_CBRA_M(cbra_packet.header.option_value) != cbra_m_values[index]
        || AIOT_T2_UNPACK_CBRA_KIND(cbra_packet.header.option_value) != AIOT_T2_CBRA_KIND_PAGING
        || AIOT_T2_UNPACK_R2D_READER(cbra_packet.header.option_value) != 1
        || AIOT_T2_UNPACK_R2D_TAG(cbra_packet.header.option_value) != 100
        || cbra_packet.samples[0].r != 1 || cbra_packet.samples[1].r != 1
        || cbra_packet.samples[2].r != 0 || cbra_packet.samples[3].r != 0
        || cbra_packet.samples[4].r != 1 || cbra_packet.samples[5].r != 0
        || cbra_packet.samples[6].r != 0 || cbra_packet.samples[7].r != 0
        || cbra_packet.samples[8].r != 1 || cbra_packet.samples[9].r != 0
        || cbra_packet.samples[10].r != 1 || cbra_packet.samples[11].r != 0) {
      fprintf(stderr, "FAIL PreparesCbraPagingR2dFrame m=%u samples=%u\n",
              cbra_m_values[index], cbra_packet.header.size);
      return 1;
    }
    size_t frame_chips = 0;
    size_t frame_symbols = 0;
    size_t ofdm_samples = 0;
    c16_t *waveform = calloc(AIOT_T2_CBRA_MAX_OFDM_SAMPLES, sizeof(*waveform));
    size_t waveform_count = 0;
    if (!aiot_t2_cbra_frame_dimensions(NR_UE_AIOT_CBRA_PAGING_PHY_BITS,
                                       cbra_m_values[index], &frame_chips, &frame_symbols, &ofdm_samples)
        || frame_chips != expected_occupied_chips[index] || frame_symbols != expected_symbols[index]
        || ofdm_samples != expected_ofdm_samples[index]
        || waveform == NULL
        || !aiot_t2_cbra_expand_compact_frame(cbra_packet.samples,
                                               cbra_packet.header.size,
                                               NR_UE_AIOT_CBRA_PAGING_PHY_BITS,
                                               cbra_m_values[index],
                                               waveform,
                                               AIOT_T2_CBRA_MAX_OFDM_SAMPLES,
                                               &waveform_count)
        || waveform_count != expected_ofdm_samples[index]) {
      free(waveform);
      fprintf(stderr, "FAIL ExpandsFullCbraPagingWaveform m=%u samples=%zu\n",
              cbra_m_values[index], waveform_count);
      return 1;
    }
    free(waveform);
  }

  uint8_t access_trigger[NR_UE_AIOT_CBRA_TRIGGER_BYTES] = {0xA5, 0xA5};
  uint8_t access_trigger_phy[NR_UE_AIOT_CBRA_TRIGGER_PHY_BYTES] = {0};
  if (!nr_ue_aiot_cbra_build_access_trigger(access_trigger)
      || !nr_ue_aiot_cbra_parse_access_trigger(access_trigger)
      || access_trigger[0] != 0x40 || access_trigger[1] != 0
      || !nr_ue_aiot_cbra_append_access_trigger_crc(access_trigger, access_trigger_phy)
      || !nr_ue_aiot_cbra_verify_access_trigger_crc(access_trigger_phy)) {
    fprintf(stderr, "FAIL BuildsAndVerifiesCbraAccessTrigger\n");
    return 1;
  }
  access_trigger_phy[1] ^= 0x80U;
  if (nr_ue_aiot_cbra_verify_access_trigger_crc(access_trigger_phy)) {
    fprintf(stderr, "FAIL RejectsCorruptedCbraAccessTriggerCrc\n");
    return 1;
  }
  if (nr_ue_aiot_cbra_parse_access_trigger_length(access_trigger, NR_UE_AIOT_CBRA_TRIGGER_BYTES - 1U)) {
    fprintf(stderr, "FAIL RejectsTruncatedCbraAccessTrigger\n");
    return 1;
  }
  access_trigger[1] = 0xFF;
  if (!nr_ue_aiot_cbra_parse_access_trigger(access_trigger)) {
    fprintf(stderr, "FAIL IgnoresCbraAccessTriggerStoragePadding\n");
    return 1;
  }

  nr_ue_aiot_cbra_frame_t trigger_frame = {0};
  reason = NULL;
  if (!nr_ue_aiot_cbra_derive_frame(NR_UE_AIOT_CBRA_ACCESS_TRIGGER, 24, 3, &trigger_frame, &reason)
      || reason != NULL || trigger_frame.mac_bits != NR_UE_AIOT_CBRA_TRIGGER_BITS
      || trigger_frame.phy_bits != NR_UE_AIOT_CBRA_TRIGGER_PHY_BITS || trigger_frame.data_and_overhead_chips != 26
      || trigger_frame.emitted_chip_count != 56 || trigger_frame.ofdm_sample_count != 4392) {
    fprintf(stderr, "FAIL DerivesCbraAccessTriggerFrame\n");
    return 1;
  }
  aiot_t2_rf_packet_t trigger_packet = {0};
  c16_t *trigger_waveform = calloc(trigger_frame.ofdm_sample_count, sizeof(*trigger_waveform));
  size_t trigger_waveform_count = 0;
  reason = NULL;
  if (!nr_ue_aiot_cbra_prepare_access_trigger_r2d(100, 1, 100, 24, 3, &trigger_packet, &reason)
      || reason != NULL || trigger_packet.header.size != trigger_frame.emitted_chip_count
      || AIOT_T2_UNPACK_CBRA_KIND(trigger_packet.header.option_value) != AIOT_T2_CBRA_KIND_ACCESS_TRIGGER
      || trigger_waveform == NULL
      || !aiot_t2_cbra_expand_compact_frame(trigger_packet.samples,
                                             trigger_packet.header.size,
                                             NR_UE_AIOT_CBRA_TRIGGER_PHY_BITS,
                                             24,
                                             trigger_waveform,
                                             trigger_frame.ofdm_sample_count,
                                             &trigger_waveform_count)
      || trigger_waveform_count != trigger_frame.ofdm_sample_count) {
    free(trigger_waveform);
    fprintf(stderr, "FAIL PreparesCbraAccessTriggerR2dFrame\n");
    return 1;
  }
  free(trigger_waveform);

  const aiot_t2_cbra_collision_key_t collision_key = {
      .reader_handle = 1,
      .config_version = 9,
      .config_round = 17,
      .access_occasion = 3,
  };
  const aiot_t2_cbra_collision_key_t same_key = collision_key;
  const aiot_t2_cbra_collision_key_t other_reader = {
      .reader_handle = 2,
      .config_version = 9,
      .config_round = 17,
      .access_occasion = 3,
  };
  const aiot_t2_cbra_collision_key_t other_round = {
      .reader_handle = 1,
      .config_version = 9,
      .config_round = 18,
      .access_occasion = 3,
  };
  const aiot_t2_cbra_collision_key_t other_ao = {
      .reader_handle = 1,
      .config_version = 9,
      .config_round = 17,
      .access_occasion = 4,
  };
  if (!aiot_t2_cbra_collision_key_equal(&collision_key, &same_key)
      || aiot_t2_cbra_collision_key_equal(&collision_key, &other_reader)
      || aiot_t2_cbra_collision_key_equal(&collision_key, &other_round)
      || aiot_t2_cbra_collision_key_equal(&collision_key, &other_ao)) {
    fprintf(stderr, "FAIL ScopesCbraCollisionByReaderRoundAndAo\n");
    return 1;
  }

  nr_ue_aiot_cbra_paging_fields_t broadcast_fields = {
      .serial = AIOT_T2_CBRA_BROADCAST_SERIAL,
      .number_of_access_occasions = 1,
      .d2r_scheduling_info = 0x06014,
  };
  aiot_t2_rf_packet_t broadcast_packet = {0};
  reason = NULL;
  if (!nr_ue_aiot_cbra_prepare_paging_r2d(&broadcast_fields,
                                          AIOT_T2_CBRA_BROADCAST_TAG_ID,
                                          collision_key.reader_handle,
                                          123,
                                          2,
                                          3,
                                          &broadcast_packet,
                                          &reason)
      || reason != NULL
      || AIOT_T2_UNPACK_R2D_TAG(broadcast_packet.header.option_value) != AIOT_T2_CBRA_BROADCAST_TAG_ID) {
    fprintf(stderr, "FAIL AllowsCbraBroadcastPagingTarget\n");
    return 1;
  }

  aiot_t2_cbra_control_t control = {0};
  aiot_t2_cbra_control_set_u16(control.transaction_id, 0x1234);
  aiot_t2_cbra_control_set_u16(control.access_occasion, collision_key.access_occasion);
  control.status = AIOT_T2_CBRA_CONTROL_MSG2_GRANT;
  aiot_t2_cbra_control_finalize(&control);
  if (!aiot_t2_cbra_control_valid(&control)
      || aiot_t2_cbra_control_get_u16(control.transaction_id) != 0x1234
      || aiot_t2_cbra_control_get_u16(control.access_occasion) != collision_key.access_occasion) {
    fprintf(stderr, "FAIL ValidatesCbraMsg2ControlCorrelation\n");
    return 1;
  }
  control.crc16[1] ^= 0x01U;
  if (aiot_t2_cbra_control_valid(&control)) {
    fprintf(stderr, "FAIL RejectsCorruptedCbraMsg3Control\n");
    return 1;
  }

  puts("PASS R2dResourceAdmissionTable");
  return 0;
}
