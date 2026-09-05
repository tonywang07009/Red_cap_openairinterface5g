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

  puts("PASS R2dResourceAdmissionTable");
  return 0;
}
