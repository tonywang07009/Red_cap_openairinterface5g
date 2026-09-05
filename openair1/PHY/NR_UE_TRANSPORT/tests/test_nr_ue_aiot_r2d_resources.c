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

  puts("PASS R2dResourceAdmissionTable");
  return 0;
}
