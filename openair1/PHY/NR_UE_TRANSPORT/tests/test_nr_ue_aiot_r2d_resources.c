/* Licensed under the OAI Public License, Version 1.1.
 * See the repository NOTICE and http://www.openairinterface.org/?page_id=698.
 */
#include <stdio.h>
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

  const uint8_t security[NR_UE_AIOT_CFA_SECURITY_BYTES] = {
      0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07,
      0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f,
  };
  nr_ue_aiot_cfa_pdu_fields_t cfa_fields = {
      .serial = 100,
      .security_parameter = {0},
      .d2r_scheduling_info = NR_UE_AIOT_CFA_FROZEN_D2R_SCHEDULING_INFO,
  };
  memcpy(cfa_fields.security_parameter, security, sizeof(security));
  uint8_t cfa_pdu[NR_UE_AIOT_CFA_PDU_BYTES] = {0};
  reason = NULL;
  if (!nr_ue_aiot_cfa_build_pdu(&cfa_fields, cfa_pdu, &reason) || reason != NULL) {
    fprintf(stderr, "FAIL Builds216BitCfaPdu\n");
    return 1;
  }
  nr_ue_aiot_cfa_pdu_fields_t parsed_fields = {0};
  reason = NULL;
  if (!nr_ue_aiot_cfa_parse_pdu(cfa_pdu, &parsed_fields, &reason)
      || reason != NULL || parsed_fields.serial != cfa_fields.serial
      || parsed_fields.d2r_scheduling_info != cfa_fields.d2r_scheduling_info
      || memcmp(parsed_fields.security_parameter, security, sizeof(security)) != 0) {
    fprintf(stderr, "FAIL RoundTripsCfaPduFields\n");
    return 1;
  }
  uint8_t cfa_phy[NR_UE_AIOT_CFA_PHY_BYTES] = {0};
  if (!nr_ue_aiot_cfa_append_crc(cfa_pdu, cfa_phy)
      || memcmp(cfa_phy, cfa_pdu, NR_UE_AIOT_CFA_PDU_BYTES) != 0) {
    fprintf(stderr, "FAIL AppendsCfaCrc16\n");
    return 1;
  }
  if (!nr_ue_aiot_cfa_verify_crc(cfa_phy)) {
    fprintf(stderr, "FAIL VerifiesCfaCrc16\n");
    return 1;
  }
  cfa_phy[NR_UE_AIOT_CFA_PHY_BYTES - 1U] ^= 0x01U;
  if (nr_ue_aiot_cfa_verify_crc(cfa_phy)) {
    fprintf(stderr, "FAIL RejectsCorruptedCfaCrc\n");
    return 1;
  }
  if (!nr_ue_aiot_cfa_append_crc(cfa_pdu, cfa_phy)) {
    fprintf(stderr, "FAIL RebuildsCfaCrc16\n");
    return 1;
  }
  nr_ue_aiot_cfa_pdu_fields_t tag_101_fields = cfa_fields;
  tag_101_fields.serial = 101;
  uint8_t tag_101_pdu[NR_UE_AIOT_CFA_PDU_BYTES] = {0};
  if (!nr_ue_aiot_cfa_build_pdu(&tag_101_fields, tag_101_pdu, &reason)
      || memcmp(cfa_pdu, tag_101_pdu, sizeof(cfa_pdu)) == 0) {
    fprintf(stderr, "FAIL DistinguishesTag100And101Pdu\n");
    return 1;
  }
  const uint32_t serials[] = {100, 101};
  reason = NULL;
  if (nr_ue_aiot_cfa_validate_serial(101, serials, 2, &reason)
      || reason == NULL || strcmp(reason, "duplicate_serial") != 0) {
    fprintf(stderr, "FAIL RejectsDuplicateCfaSerial\n");
    return 1;
  }
  reason = NULL;
  if (nr_ue_aiot_cfa_validate_serial(0, NULL, 0, &reason)
      || reason == NULL || strcmp(reason, "invalid_serial") != 0) {
    fprintf(stderr, "FAIL RejectsZeroCfaSerial\n");
    return 1;
  }
  cfa_pdu[0] ^= 0x80;
  reason = NULL;
  if (nr_ue_aiot_cfa_parse_pdu(cfa_pdu, &parsed_fields, &reason)
      || reason == NULL || strcmp(reason, "invalid_message_type") != 0) {
    fprintf(stderr, "FAIL RejectsMalformedCfaPdu\n");
    return 1;
  }

  const nr_ue_aiot_cfa_d2r_scheduling_t cfa_schedule = {
      .bit_duration = NR_UE_AIOT_D2R_TBIT_TAU,
      .frequency_resource_broadcast = 0x80,
      .block_repetition = 0,
      .channel_coding = 1,
      .interval_bits = 1,
      .sequence_length = 0,
      .additional_midamble = 0,
      .d2r_tbs = 16,
  };
  uint32_t packed_schedule = 0;
  reason = NULL;
  if (!nr_ue_aiot_cfa_pack_d2r_scheduling(&cfa_schedule, &packed_schedule, &reason)
      || reason != NULL || packed_schedule != 0x300a0f) {
    fprintf(stderr, "FAIL PacksFrozenCfaD2rScheduling expected=0x300a0f actual=0x%06x\n", packed_schedule);
    return 1;
  }
  const int32_t snr_grid[] = {-10, 0, 10};
  const nr_ue_aiot_cfa_campaign_config_t campaign = {
      .m = 6,
      .prb_count = 3,
      .reference_snr_db_x10 = 100,
      .formal_packet_budget = 10000,
      .data_seed = 7,
      .noise_seed = 11,
      .snr_grid_db_x10 = snr_grid,
      .snr_grid_count = sizeof(snr_grid) / sizeof(snr_grid[0]),
      .d2r_scheduling_info = 0x300a0f,
  };
  reason = NULL;
  if (!nr_ue_aiot_cfa_validate_campaign_config(&campaign, &reason) || reason != NULL) {
    fprintf(stderr, "FAIL AcceptsCompleteCfaCampaignConfig\n");
    return 1;
  }
  nr_ue_aiot_cfa_campaign_config_t invalid_campaign = campaign;
  invalid_campaign.m = 3;
  reason = NULL;
  if (nr_ue_aiot_cfa_validate_campaign_config(&invalid_campaign, &reason)
      || reason == NULL || strcmp(reason, "invalid_m") != 0) {
    fprintf(stderr, "FAIL RejectsUnsupportedCfaM\n");
    return 1;
  }
  invalid_campaign = campaign;
  invalid_campaign.prb_count = 2;
  reason = NULL;
  if (nr_ue_aiot_cfa_validate_campaign_config(&invalid_campaign, &reason)
      || reason == NULL || strcmp(reason, "invalid_prb_count") != 0) {
    fprintf(stderr, "FAIL RejectsNonThreePrbCfaProfile\n");
    return 1;
  }
  invalid_campaign = campaign;
  invalid_campaign.data_seed = invalid_campaign.noise_seed;
  reason = NULL;
  if (nr_ue_aiot_cfa_validate_campaign_config(&invalid_campaign, &reason)
      || reason == NULL || strcmp(reason, "duplicate_seed") != 0) {
    fprintf(stderr, "FAIL RejectsDuplicateCfaSeeds\n");
    return 1;
  }
  invalid_campaign = campaign;
  invalid_campaign.d2r_scheduling_info = 0x123456;
  reason = NULL;
  if (nr_ue_aiot_cfa_validate_campaign_config(&invalid_campaign, &reason)
      || reason == NULL || strcmp(reason, "invalid_scheduling_info") != 0) {
    fprintf(stderr, "FAIL RejectsNonFrozenCfaSchedulingInfo\n");
    return 1;
  }
  nr_ue_aiot_cfa_pdu_fields_t invalid_cfa_fields = cfa_fields;
  invalid_cfa_fields.d2r_scheduling_info = 0x123456;
  aiot_t2_rf_packet_t invalid_cfa_packet;
  memset(&invalid_cfa_packet, 0xA5, sizeof(invalid_cfa_packet));
  const aiot_t2_rf_packet_t invalid_cfa_before = invalid_cfa_packet;
  reason = NULL;
  if (nr_ue_aiot_cfa_prepare_r2d(&invalid_cfa_fields, 100, 1, 100, 6, 3, &invalid_cfa_packet, &reason)
      || reason == NULL || strcmp(reason, "invalid_scheduling_info") != 0
      || memcmp(&invalid_cfa_packet, &invalid_cfa_before, sizeof(invalid_cfa_packet)) != 0) {
    fprintf(stderr, "FAIL RefusesNonFrozenCfaSchedulingInfoBeforeTx\n");
    return 1;
  }
  uint8_t invalid_cfa_pdu[NR_UE_AIOT_CFA_PDU_BYTES];
  uint8_t invalid_cfa_pdu_before[NR_UE_AIOT_CFA_PDU_BYTES];
  memset(invalid_cfa_pdu, 0xA5, sizeof(invalid_cfa_pdu));
  memset(invalid_cfa_pdu_before, 0xA5, sizeof(invalid_cfa_pdu_before));
  reason = NULL;
  if (nr_ue_aiot_cfa_build_pdu(&invalid_cfa_fields, invalid_cfa_pdu, &reason)
      || reason == NULL || strcmp(reason, "invalid_scheduling_info") != 0
      || memcmp(invalid_cfa_pdu, invalid_cfa_pdu_before, sizeof(invalid_cfa_pdu)) != 0) {
    fprintf(stderr, "FAIL RefusesNonFrozenCfaPduBeforeSerialization\n");
    return 1;
  }

  const uint8_t cfa_m_values[] = {2, 6, 12, 24};
  const uint16_t expected_symbols[] = {238, 81, 42, 24};
  const uint16_t expected_occupied_chips[] = {480, 482, 488, 536};
  for (size_t index = 0; index < sizeof(cfa_m_values) / sizeof(cfa_m_values[0]); ++index) {
    nr_ue_aiot_cfa_frame_t frame = {0};
    reason = NULL;
    if (!nr_ue_aiot_cfa_derive_frame(cfa_m_values[index], 3, &frame, &reason)
        || reason != NULL || frame.prdch_chips != 464 || frame.frame_symbols != expected_symbols[index]
        || frame.occupied_chip_positions != expected_occupied_chips[index]) {
      fprintf(stderr, "FAIL DerivesCfaFrame m=%u symbols=%u occupied=%u\n",
              cfa_m_values[index], frame.frame_symbols, frame.occupied_chip_positions);
      return 1;
    }
    aiot_t2_rf_packet_t cfa_packet = {0};
    reason = NULL;
    if (!nr_ue_aiot_cfa_prepare_r2d(&cfa_fields, 100, 1, 100, cfa_m_values[index], 3, &cfa_packet, &reason)
        || reason != NULL || cfa_packet.header.size != 464
        || (cfa_packet.header.option_flag & (OPTION_AIOT_T2_R2D | OPTION_AIOT_T2_R2D_CFA))
               != (OPTION_AIOT_T2_R2D | OPTION_AIOT_T2_R2D_CFA)
        || AIOT_T2_UNPACK_CFA_M(cfa_packet.header.option_value) != cfa_m_values[index]
        || AIOT_T2_UNPACK_R2D_READER(cfa_packet.header.option_value) != 1) {
      fprintf(stderr, "FAIL PreparesCfaR2dFrame m=%u samples=%u\n", cfa_m_values[index], cfa_packet.header.size);
      return 1;
    }
  }

  puts("PASS R2dResourceAdmissionTable");
  return 0;
}
