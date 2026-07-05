#ifndef REDCAP_DAPP_SDK_H
#define REDCAP_DAPP_SDK_H

#include <stdbool.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
  REDCAP_DAPP_GUARD_ACK = 0,
  REDCAP_DAPP_GUARD_NACK = 1,
} redcap_dapp_guard_decision_t;

typedef struct {
  uint16_t rnti;
  uint16_t requested_ul_prb_cap;
  uint16_t min_ul_prb_cap;
  uint16_t max_ul_prb_cap;
} redcap_dapp_ul_prb_request_t;

typedef struct {
  redcap_dapp_guard_decision_t decision;
  uint16_t applied_ul_prb_cap;
  const char *reason;
} redcap_dapp_guard_result_t;

redcap_dapp_guard_result_t redcap_dapp_guard_ul_prb_cap(const redcap_dapp_ul_prb_request_t *request);
bool redcap_dapp_guard_allows_apply(const redcap_dapp_guard_result_t *result);

#ifdef __cplusplus
}
#endif

#endif
