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
  const uint32_t pressure = (uint32_t)request->ra_retry_count * 50u
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
