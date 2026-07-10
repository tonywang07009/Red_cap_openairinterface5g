#ifndef REDCAP_DAPP_SDK_H
#define REDCAP_DAPP_SDK_H

#include <stdbool.h>
#include <stddef.h>
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

enum {
  REDCAP_DAPP_TEST_BWP_MHZ = 5,
  REDCAP_DAPP_TEST_BWP_PRBS_30KHZ = 12,
  REDCAP_DAPP_TEST_BWP_PRBS_30KHZ_COMPAT = 11,
  REDCAP_DAPP_PROXY_BWP_MHZ = 20,
  REDCAP_DAPP_PROXY_BWP_PRBS_30KHZ = 51,
};

typedef struct {
  uint16_t rnti;
  uint16_t bwp_prbs;
  uint16_t pucch_ratio_permille;
  uint16_t pusch_ratio_permille;
  uint16_t priority_weight;
  bool has_iq_samples;
} redcap_dapp_prb_allocation_request_t;

typedef struct {
  redcap_dapp_guard_decision_t decision;
  uint16_t pucch_prbs;
  uint16_t pusch_prbs;
  uint16_t priority_weight;
  const char *reason;
  const char *marker;
} redcap_dapp_prb_allocation_result_t;

typedef struct {
  uint16_t rnti;
  uint16_t bwp_prbs;
  uint16_t priority_weight;
  bool has_iq_samples;
  uint16_t previous_pressure_permille;
  uint16_t ra_retry_count;
  uint16_t msg3_failure_count;
  uint16_t pucch_resource_reject_count;
  uint16_t crc_discard_count;
} redcap_dapp_access_pressure_request_t;

typedef struct {
  redcap_dapp_prb_allocation_result_t allocation;
  uint16_t current_pressure_permille;
  uint16_t ewma_pressure_permille;
  uint16_t pucch_ratio_permille;
  uint16_t pusch_ratio_permille;
  const char *pressure_level;
  const char *marker;
} redcap_dapp_access_pressure_result_t;

typedef struct {
  bool found;
  size_t selected_index;
  uint16_t selected_rnti;
  uint16_t selected_ra_retry_count;
  redcap_dapp_access_pressure_result_t pressure;
  const char *marker;
} redcap_dapp_access_pressure_selection_t;

enum {
  REDCAP_DAPP_DRX_SCHEMA_VERSION = 1,
  REDCAP_DAPP_DRX_WINDOW_SAMPLES = 30,
  REDCAP_DAPP_DRX_INACTIVITY_MS = 20,
};

typedef struct {
  uint32_t schema_version;
  uint16_t rnti;
  uint64_t policy_version;
  uint16_t sample_count;
  uint64_t lower_3sigma_us;
  uint64_t upper_3sigma_us;
  uint64_t next_arrival_drx_epoch_ms;
  uint16_t requested_long_cycle_ms;
  bool ue_connected;
  bool rrc_reconfiguration_cooldown_elapsed;
} redcap_dapp_drx_policy_request_t;

typedef struct {
  uint16_t rnti;
  uint64_t policy_version;
  uint16_t long_cycle_ms;
  uint16_t on_duration_ms;
  uint16_t start_offset_ms;
  uint16_t inactivity_ms;
  bool rollback_available;
  bool drx_command_enabled;
  const char *profile_id;
} redcap_dapp_drx_config_t;

typedef struct {
  redcap_dapp_guard_decision_t decision;
  redcap_dapp_drx_config_t accepted;
  redcap_dapp_drx_config_t previous;
  const char *reason;
  const char *marker;
} redcap_dapp_drx_guard_result_t;

typedef struct {
  uint16_t rnti;
  uint64_t policy_version;
  uint16_t requested_long_cycle_ms;
  bool ue_connected;
  bool rrc_reconfiguration_cooldown_elapsed;
} redcap_dapp_e2_drx_cycle_request_t;

redcap_dapp_guard_result_t redcap_dapp_guard_ul_prb_cap(const redcap_dapp_ul_prb_request_t *request);
bool redcap_dapp_guard_allows_apply(const redcap_dapp_guard_result_t *result);
redcap_dapp_prb_allocation_result_t redcap_dapp_guard_prb_allocation(
    const redcap_dapp_prb_allocation_request_t *request);
bool redcap_dapp_prb_allocation_allows_apply(const redcap_dapp_prb_allocation_result_t *result);
redcap_dapp_access_pressure_result_t redcap_dapp_access_pressure_policy(
    const redcap_dapp_access_pressure_request_t *request);
bool redcap_dapp_access_pressure_allows_apply(const redcap_dapp_access_pressure_result_t *result);
redcap_dapp_access_pressure_selection_t redcap_dapp_select_ra_pressure_priority(
    const redcap_dapp_access_pressure_request_t *requests,
    size_t request_count);
redcap_dapp_drx_guard_result_t redcap_dapp_guard_drx_policy(
    const redcap_dapp_drx_policy_request_t *request,
    const redcap_dapp_drx_config_t *current);
bool redcap_dapp_drx_guard_allows_apply(const redcap_dapp_drx_guard_result_t *result);
redcap_dapp_drx_guard_result_t redcap_dapp_guard_e2_drx_cycle(
    const redcap_dapp_e2_drx_cycle_request_t *request,
    const redcap_dapp_drx_config_t *current);

#ifdef __cplusplus
}
#endif

#endif
