#include "redcap_dapp_sdk.h"

redcap_dapp_guard_result_t redcap_dapp_guard_ul_prb_cap(const redcap_dapp_ul_prb_request_t *request)
{
  if (request == 0)
    return (redcap_dapp_guard_result_t){REDCAP_DAPP_GUARD_NACK, 0, "missing_request"};

  if (request->rnti == 0)
    return (redcap_dapp_guard_result_t){REDCAP_DAPP_GUARD_NACK, 0, "invalid_rnti"};

  if (request->min_ul_prb_cap > request->max_ul_prb_cap)
    return (redcap_dapp_guard_result_t){REDCAP_DAPP_GUARD_NACK, 0, "invalid_contract_range"};

  if (request->requested_ul_prb_cap < request->min_ul_prb_cap || request->requested_ul_prb_cap > request->max_ul_prb_cap)
    return (redcap_dapp_guard_result_t){REDCAP_DAPP_GUARD_NACK, 0, "outside_contract_range"};

  return (redcap_dapp_guard_result_t){REDCAP_DAPP_GUARD_ACK, request->requested_ul_prb_cap, "ack"};
}

bool redcap_dapp_guard_allows_apply(const redcap_dapp_guard_result_t *result)
{
  return result != 0 && result->decision == REDCAP_DAPP_GUARD_ACK;
}

static uint16_t redcap_dapp_ratio_to_prbs(uint16_t bwp_prbs, uint16_t ratio_permille)
{
  return (uint16_t)((bwp_prbs * ratio_permille + 999u) / 1000u);
}

static bool redcap_dapp_is_supported_bwp_profile(uint16_t bwp_prbs)
{
  return bwp_prbs == REDCAP_DAPP_TEST_BWP_PRBS_30KHZ
         || bwp_prbs == REDCAP_DAPP_TEST_BWP_PRBS_30KHZ_COMPAT
         || bwp_prbs == REDCAP_DAPP_PROXY_BWP_PRBS_30KHZ;
}

redcap_dapp_prb_allocation_result_t redcap_dapp_guard_prb_allocation(
    const redcap_dapp_prb_allocation_request_t *request)
{
  if (request == 0)
    return (redcap_dapp_prb_allocation_result_t){REDCAP_DAPP_GUARD_NACK, 0, 0, 0, "missing_request", ""};

  if (request->rnti == 0)
    return (redcap_dapp_prb_allocation_result_t){REDCAP_DAPP_GUARD_NACK, 0, 0, 0, "invalid_rnti", ""};

  if (!request->has_iq_samples)
    return (redcap_dapp_prb_allocation_result_t){REDCAP_DAPP_GUARD_NACK, 0, 0, request->priority_weight,
                                                 "missing_iq_samples", ""};

  if (!redcap_dapp_is_supported_bwp_profile(request->bwp_prbs))
    return (redcap_dapp_prb_allocation_result_t){REDCAP_DAPP_GUARD_NACK, 0, 0, request->priority_weight,
                                                 "unsupported_bwp_profile", ""};

  if (request->pucch_ratio_permille > 1000 || request->pusch_ratio_permille > 1000 ||
      request->pucch_ratio_permille + request->pusch_ratio_permille > 1000)
    return (redcap_dapp_prb_allocation_result_t){REDCAP_DAPP_GUARD_NACK, 0, 0, request->priority_weight,
                                                 "invalid_prb_ratio", ""};

  return (redcap_dapp_prb_allocation_result_t){
      REDCAP_DAPP_GUARD_ACK,
      redcap_dapp_ratio_to_prbs(request->bwp_prbs, request->pucch_ratio_permille),
      redcap_dapp_ratio_to_prbs(request->bwp_prbs, request->pusch_ratio_permille),
      request->priority_weight,
      "ack",
      "RedCap dApp PRB decision"};
}

bool redcap_dapp_prb_allocation_allows_apply(const redcap_dapp_prb_allocation_result_t *result)
{
  return result != 0 && result->decision == REDCAP_DAPP_GUARD_ACK;
}

static uint16_t redcap_dapp_clamp_permille(uint32_t value)
{
  return (uint16_t)(value > 1000u ? 1000u : value);
}

static uint16_t redcap_dapp_access_pressure_current(const redcap_dapp_access_pressure_request_t *request)
{
  const uint32_t pressure = (uint32_t)request->ra_retry_count * 100u
                            + (uint32_t)request->msg3_failure_count * 120u
                            + (uint32_t)request->pucch_resource_reject_count * 160u
                            + (uint32_t)request->crc_discard_count * 40u;
  return redcap_dapp_clamp_permille(pressure);
}

static uint16_t redcap_dapp_access_pressure_ewma(uint16_t previous_pressure_permille, uint16_t current_pressure_permille)
{
  return (uint16_t)(((uint32_t)redcap_dapp_clamp_permille(previous_pressure_permille) * 7u
                     + (uint32_t)current_pressure_permille * 3u + 5u)
                    / 10u);
}

static void redcap_dapp_access_pressure_ratios(uint16_t ewma_pressure_permille,
                                               uint16_t *pucch_ratio_permille,
                                               uint16_t *pusch_ratio_permille,
                                               const char **pressure_level)
{
  // ponytail: fixed thresholds keep the first policy testable; replace with measured tuning after RFsim data exists.
  if (ewma_pressure_permille >= 600) {
    *pucch_ratio_permille = 400;
    *pusch_ratio_permille = 400;
    *pressure_level = "high";
  } else if (ewma_pressure_permille >= 250) {
    *pucch_ratio_permille = 300;
    *pusch_ratio_permille = 500;
    *pressure_level = "medium";
  } else {
    *pucch_ratio_permille = 200;
    *pusch_ratio_permille = 600;
    *pressure_level = "low";
  }
}

redcap_dapp_access_pressure_result_t redcap_dapp_access_pressure_policy(
    const redcap_dapp_access_pressure_request_t *request)
{
  if (request == 0)
    return (redcap_dapp_access_pressure_result_t){
        redcap_dapp_guard_prb_allocation(0), 0, 0, 0, 0, "invalid", "RedCap dApp access pressure policy"};

  const uint16_t current_pressure = redcap_dapp_access_pressure_current(request);
  const uint16_t ewma_pressure = redcap_dapp_access_pressure_ewma(request->previous_pressure_permille, current_pressure);
  uint16_t pucch_ratio = 0;
  uint16_t pusch_ratio = 0;
  const char *pressure_level = "invalid";
  redcap_dapp_access_pressure_ratios(ewma_pressure, &pucch_ratio, &pusch_ratio, &pressure_level);

  const redcap_dapp_prb_allocation_request_t allocation_request = {
      .rnti = request->rnti,
      .bwp_prbs = request->bwp_prbs,
      .pucch_ratio_permille = pucch_ratio,
      .pusch_ratio_permille = pusch_ratio,
      .priority_weight = request->priority_weight,
      .has_iq_samples = request->has_iq_samples,
  };

  return (redcap_dapp_access_pressure_result_t){
      redcap_dapp_guard_prb_allocation(&allocation_request),
      current_pressure,
      ewma_pressure,
      pucch_ratio,
      pusch_ratio,
      pressure_level,
      "RedCap dApp access pressure policy"};
}

bool redcap_dapp_access_pressure_allows_apply(const redcap_dapp_access_pressure_result_t *result)
{
  return result != 0 && redcap_dapp_prb_allocation_allows_apply(&result->allocation);
}

static bool redcap_dapp_ra_pressure_candidate_is_better(const redcap_dapp_access_pressure_request_t *candidate,
                                                        const redcap_dapp_access_pressure_request_t *best)
{
  if (candidate->ra_retry_count != best->ra_retry_count)
    return candidate->ra_retry_count > best->ra_retry_count;

  const uint16_t candidate_pressure = redcap_dapp_access_pressure_current(candidate);
  const uint16_t best_pressure = redcap_dapp_access_pressure_current(best);
  if (candidate_pressure != best_pressure)
    return candidate_pressure > best_pressure;

  if (candidate->priority_weight != best->priority_weight)
    return candidate->priority_weight > best->priority_weight;

  return candidate->rnti < best->rnti;
}

redcap_dapp_access_pressure_selection_t redcap_dapp_select_ra_pressure_priority(
    const redcap_dapp_access_pressure_request_t *requests,
    size_t request_count)
{
  if (requests == 0 || request_count == 0)
    return (redcap_dapp_access_pressure_selection_t){
        false, 0, 0, 0, redcap_dapp_access_pressure_policy(0), "RedCap dApp RA pressure priority"};

  size_t selected_index = 0;
  bool found = false;
  for (size_t i = 0; i < request_count; i++) {
    if (requests[i].rnti == 0)
      continue;
    if (!found || redcap_dapp_ra_pressure_candidate_is_better(&requests[i], &requests[selected_index])) {
      selected_index = i;
      found = true;
    }
  }

  if (!found)
    return (redcap_dapp_access_pressure_selection_t){
        false, 0, 0, 0, redcap_dapp_access_pressure_policy(0), "RedCap dApp RA pressure priority"};

  return (redcap_dapp_access_pressure_selection_t){
      true,
      selected_index,
      requests[selected_index].rnti,
      requests[selected_index].ra_retry_count,
      redcap_dapp_access_pressure_policy(&requests[selected_index]),
      "RedCap dApp RA pressure priority"};
}

typedef struct {
  uint16_t long_cycle_ms;
  uint16_t on_duration_ms;
  const char *profile_id;
} redcap_dapp_drx_profile_t;

static const redcap_dapp_drx_profile_t redcap_dapp_drx_profiles[] = {
    {320, 10, "drx-320-10"},
    {640, 10, "drx-640-10"},
    {1280, 20, "drx-1280-20"},
    {2560, 20, "drx-2560-20"},
    {5120, 40, "drx-5120-40"},
    {10240, 40, "drx-10240-40"},
};

static const redcap_dapp_drx_profile_t *redcap_dapp_find_drx_profile(uint16_t long_cycle_ms)
{
  for (size_t i = 0; i < sizeof(redcap_dapp_drx_profiles) / sizeof(redcap_dapp_drx_profiles[0]); ++i) {
    if (redcap_dapp_drx_profiles[i].long_cycle_ms == long_cycle_ms)
      return &redcap_dapp_drx_profiles[i];
  }
  return 0;
}

static const redcap_dapp_drx_profile_t *redcap_dapp_select_drx_profile(uint64_t lower_3sigma_us)
{
  const redcap_dapp_drx_profile_t *selected = &redcap_dapp_drx_profiles[0];
  for (size_t i = 1; i < sizeof(redcap_dapp_drx_profiles) / sizeof(redcap_dapp_drx_profiles[0]); ++i) {
    if ((uint64_t)redcap_dapp_drx_profiles[i].long_cycle_ms * 1000u > lower_3sigma_us)
      break;
    selected = &redcap_dapp_drx_profiles[i];
  }
  return selected;
}

static redcap_dapp_drx_guard_result_t redcap_dapp_reject_drx_policy(const char *reason)
{
  return (redcap_dapp_drx_guard_result_t){
      .decision = REDCAP_DAPP_GUARD_NACK,
      .reason = reason,
      .marker = "[RedCap DRX][dApp REJECT]",
  };
}

static bool redcap_dapp_valid_rollback_config(const redcap_dapp_drx_config_t *current, uint16_t rnti)
{
  if (current == 0 || !current->rollback_available || current->rnti != rnti
      || current->start_offset_ms >= current->long_cycle_ms)
    return false;

  const redcap_dapp_drx_profile_t *profile = redcap_dapp_find_drx_profile(current->long_cycle_ms);
  return profile != 0 && current->on_duration_ms == profile->on_duration_ms
         && current->inactivity_ms == REDCAP_DAPP_DRX_INACTIVITY_MS;
}

redcap_dapp_drx_guard_result_t redcap_dapp_guard_drx_policy(
    const redcap_dapp_drx_policy_request_t *request,
    const redcap_dapp_drx_config_t *current)
{
  if (request == 0 || request->schema_version != REDCAP_DAPP_DRX_SCHEMA_VERSION)
    return redcap_dapp_reject_drx_policy("invalid_schema_version");
  if (request->rnti == 0)
    return redcap_dapp_reject_drx_policy("unknown_rnti");
  if (!request->ue_connected)
    return redcap_dapp_reject_drx_policy("ue_not_connected");
  if (current != 0 && request->policy_version <= current->policy_version)
    return redcap_dapp_reject_drx_policy("stale_policy_version");
  if (request->sample_count != REDCAP_DAPP_DRX_WINDOW_SAMPLES)
    return redcap_dapp_reject_drx_policy("sample_count_not_30");
  if (request->lower_3sigma_us < 300000u || request->upper_3sigma_us > 10240000u
      || request->lower_3sigma_us > request->upper_3sigma_us)
    return redcap_dapp_reject_drx_policy("prediction_out_of_bounds");

  const redcap_dapp_drx_profile_t *requested = redcap_dapp_find_drx_profile(request->requested_long_cycle_ms);
  if (requested == 0)
    return redcap_dapp_reject_drx_policy("unsupported_long_cycle");
  if (requested != redcap_dapp_select_drx_profile(request->lower_3sigma_us))
    return redcap_dapp_reject_drx_policy("prediction_out_of_bounds");
  if (!request->rrc_reconfiguration_cooldown_elapsed)
    return redcap_dapp_reject_drx_policy("cooldown_active");
  if (!redcap_dapp_valid_rollback_config(current, request->rnti))
    return redcap_dapp_reject_drx_policy("rollback_unavailable");

  const redcap_dapp_drx_config_t accepted = {
      .rnti = request->rnti,
      .policy_version = request->policy_version,
      .long_cycle_ms = requested->long_cycle_ms,
      .on_duration_ms = requested->on_duration_ms,
      .start_offset_ms = (uint16_t)(request->next_arrival_drx_epoch_ms % requested->long_cycle_ms),
      .inactivity_ms = REDCAP_DAPP_DRX_INACTIVITY_MS,
      .rollback_available = true,
      .drx_command_enabled = false,
      .profile_id = requested->profile_id,
  };

  return (redcap_dapp_drx_guard_result_t){
      .decision = REDCAP_DAPP_GUARD_ACK,
      .accepted = accepted,
      .previous = *current,
      .reason = "ack",
      .marker = "[RedCap DRX][dApp ACCEPT]",
  };
}

bool redcap_dapp_drx_guard_allows_apply(const redcap_dapp_drx_guard_result_t *result)
{
  return result != 0 && result->decision == REDCAP_DAPP_GUARD_ACK && result->accepted.rollback_available;
}

redcap_dapp_drx_guard_result_t redcap_dapp_guard_e2_drx_cycle(
    const redcap_dapp_e2_drx_cycle_request_t *request,
    const redcap_dapp_drx_config_t *current)
{
  if (request == 0 || request->rnti == 0)
    return redcap_dapp_reject_drx_policy("unknown_rnti");
  if (!request->ue_connected)
    return redcap_dapp_reject_drx_policy("ue_not_connected");
  if (request->policy_version == 0 || (current != 0 && request->policy_version <= current->policy_version))
    return redcap_dapp_reject_drx_policy("stale_policy_version");
  const redcap_dapp_drx_profile_t *profile = redcap_dapp_find_drx_profile(request->requested_long_cycle_ms);
  if (profile == 0)
    return redcap_dapp_reject_drx_policy("unsupported_long_cycle");
  if (!request->rrc_reconfiguration_cooldown_elapsed)
    return redcap_dapp_reject_drx_policy("cooldown_active");
  if (!redcap_dapp_valid_rollback_config(current, request->rnti))
    return redcap_dapp_reject_drx_policy("rollback_unavailable");

  const redcap_dapp_drx_config_t accepted = {
      .rnti = request->rnti,
      .policy_version = request->policy_version,
      .long_cycle_ms = profile->long_cycle_ms,
      .on_duration_ms = profile->on_duration_ms,
      .start_offset_ms = 0,
      .inactivity_ms = REDCAP_DAPP_DRX_INACTIVITY_MS,
      .rollback_available = true,
      .drx_command_enabled = false,
      .profile_id = profile->profile_id,
  };
  return (redcap_dapp_drx_guard_result_t){
      .decision = REDCAP_DAPP_GUARD_ACK,
      .accepted = accepted,
      .previous = *current,
      .reason = "ack",
      .marker = "[RedCap DRX][dApp ACCEPT]",
  };
}
