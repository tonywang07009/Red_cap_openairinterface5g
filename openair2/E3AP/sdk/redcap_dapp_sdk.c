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

  if (request->bwp_prbs != REDCAP_DAPP_TEST_BWP_PRBS)
    return (redcap_dapp_prb_allocation_result_t){REDCAP_DAPP_GUARD_NACK, 0, 0, request->priority_weight,
                                                 "unsupported_bwp_prbs", ""};

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
