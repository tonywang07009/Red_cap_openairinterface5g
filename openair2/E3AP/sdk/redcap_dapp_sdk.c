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
