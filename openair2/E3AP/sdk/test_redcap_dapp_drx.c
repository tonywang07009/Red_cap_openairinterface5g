#include "redcap_dapp_sdk.h"

#include <assert.h>
#include <string.h>

int main(void)
{
  const redcap_dapp_drx_config_t baseline = {
      .rnti = 0xe349,
      .policy_version = 1,
      .long_cycle_ms = 320,
      .on_duration_ms = 10,
      .start_offset_ms = 0,
      .inactivity_ms = REDCAP_DAPP_DRX_INACTIVITY_MS,
      .profile_id = "drx-320-10",
  };
  redcap_dapp_drx_policy_request_t request = {
      .schema_version = REDCAP_DAPP_DRX_SCHEMA_VERSION,
      .rnti = 0xe349,
      .policy_version = 2,
      .sample_count = REDCAP_DAPP_DRX_WINDOW_SAMPLES,
      .lower_3sigma_us = 1400000,
      .upper_3sigma_us = 2100000,
      .next_arrival_drx_epoch_ms = 5001,
      .requested_long_cycle_ms = 1280,
      .ue_connected = true,
      .rrc_reconfiguration_cooldown_elapsed = true,
  };

  redcap_dapp_drx_guard_result_t result = redcap_dapp_guard_drx_policy(&request, &baseline);
  assert(redcap_dapp_drx_guard_allows_apply(&result));
  assert(result.accepted.long_cycle_ms == 1280);
  assert(result.accepted.on_duration_ms == 20);
  assert(result.accepted.start_offset_ms == 1161);
  assert(result.accepted.inactivity_ms == REDCAP_DAPP_DRX_INACTIVITY_MS);
  assert(result.accepted.rollback_available);
  assert(!result.accepted.drx_command_enabled);
  assert(strcmp(result.accepted.profile_id, "drx-1280-20") == 0);
  assert(result.previous.policy_version == baseline.policy_version);
  assert(strcmp(result.marker, "[RedCap DRX][dApp ACCEPT]") == 0);

  request.policy_version = 1;
  result = redcap_dapp_guard_drx_policy(&request, &baseline);
  assert(!redcap_dapp_drx_guard_allows_apply(&result));
  assert(strcmp(result.reason, "stale_policy_version") == 0);

  request.policy_version = 2;
  request.requested_long_cycle_ms = 512;
  result = redcap_dapp_guard_drx_policy(&request, &baseline);
  assert(strcmp(result.reason, "unsupported_long_cycle") == 0);

  request.requested_long_cycle_ms = 1280;
  request.rrc_reconfiguration_cooldown_elapsed = false;
  result = redcap_dapp_guard_drx_policy(&request, &baseline);
  assert(strcmp(result.reason, "cooldown_active") == 0);

  request.rrc_reconfiguration_cooldown_elapsed = true;
  result = redcap_dapp_guard_drx_policy(&request, 0);
  assert(strcmp(result.reason, "rollback_unavailable") == 0);
  assert(strcmp(result.marker, "[RedCap DRX][dApp REJECT]") == 0);

  redcap_dapp_e2_drx_cycle_request_t e2_request = {
      .rnti = baseline.rnti,
      .policy_version = 3,
      .requested_long_cycle_ms = 640,
      .ue_connected = true,
      .rrc_reconfiguration_cooldown_elapsed = true,
  };
  result = redcap_dapp_guard_e2_drx_cycle(&e2_request, &baseline);
  assert(redcap_dapp_drx_guard_allows_apply(&result));
  assert(result.accepted.long_cycle_ms == 640);
  assert(result.accepted.on_duration_ms == 10);
  assert(result.accepted.start_offset_ms == 0);

  e2_request.policy_version = baseline.policy_version;
  result = redcap_dapp_guard_e2_drx_cycle(&e2_request, &baseline);
  assert(strcmp(result.reason, "stale_policy_version") == 0);
  return 0;
}
