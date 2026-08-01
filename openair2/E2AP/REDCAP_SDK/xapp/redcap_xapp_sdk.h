#ifndef REDCAP_XAPP_SDK_H
#define REDCAP_XAPP_SDK_H

#include "sm/rc_sm/ie/rc_data_ie.h"
#include "xApp/e2_node_connected_xapp.h"

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <sys/types.h>

#ifdef __cplusplus
extern "C" {
#endif

enum {
  NR_REDCAP_RC_CTRL_STYLE_ID_RADIO_RESOURCE_ALLOCATION = 2,
  NR_REDCAP_RC_CTRL_ACT_ID_DRX_CONFIGURATION = 1,
  NR_REDCAP_RC_RAN_PARAM_ID_LONG_DRX_CYCLE = 1,
  NR_REDCAP_RC_CTRL_ACT_ID_UL_PRB_CAP = 100,
  NR_REDCAP_RC_RAN_PARAM_ID_UE_RNTI = 101,
  NR_REDCAP_RC_RAN_PARAM_ID_MAX_UL_PRB = 102,
};

bool redcap_xapp_parse_u64(const char *raw, uint64_t min_value, uint64_t max_value, uint64_t *value);
bool redcap_xapp_read_required_env_u64(const char *name, uint64_t min_value, uint64_t max_value, uint64_t *value);
bool redcap_xapp_env_enabled(const char *name);
rc_ctrl_req_data_t redcap_xapp_make_ul_prb_ctrl_req(uint64_t ue_id, uint16_t rnti, uint16_t max_ul_prb);
bool redcap_xapp_make_drx_ctrl_req(uint64_t ue_id, uint16_t long_cycle_ms, rc_ctrl_req_data_t *ctrl_req);
ssize_t redcap_xapp_find_rc_ran_func_idx(const e2_node_connected_xapp_t *node);

typedef struct {
  uint16_t rnti;
  uint32_t ul_buffer_bytes;
  uint16_t qos_weight;
  uint16_t redcap_weight;
} redcap_xapp_ue_metric_t;

typedef struct {
  uint16_t rnti;
  uint16_t priority_weight;
  uint16_t validity_ms;
  const char *marker;
} redcap_xapp_priority_hint_t;

bool redcap_xapp_make_priority_hint(const redcap_xapp_ue_metric_t *metric,
                                    uint16_t validity_ms,
                                    redcap_xapp_priority_hint_t *hint);
bool redcap_xapp_select_top_priority_hint(const redcap_xapp_ue_metric_t *metrics,
                                          size_t metrics_len,
                                          uint16_t validity_ms,
                                          redcap_xapp_priority_hint_t *hint);

#ifdef __cplusplus
}
#endif

#endif
