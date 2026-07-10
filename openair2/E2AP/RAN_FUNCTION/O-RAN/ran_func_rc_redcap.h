#ifndef RAN_FUNC_RC_REDCAP_H
#define RAN_FUNC_RC_REDCAP_H

#include <stdbool.h>
#include <stdint.h>

#include "openair2/E2AP/flexric/src/sm/rc_sm/ie/ir/e2sm_rc_ctrl_hdr_frmt_1.h"
#include "openair2/E2AP/flexric/src/sm/rc_sm/ie/ir/e2sm_rc_ctrl_msg_frmt_1.h"

enum {
  NR_REDCAP_RC_CTRL_STYLE_ID_RADIO_RESOURCE_ALLOCATION = 2,
  NR_REDCAP_RC_CTRL_ACT_ID_DRX_CONFIGURATION = 1,
  NR_REDCAP_RC_RAN_PARAM_ID_LONG_DRX_CYCLE = 1,
  NR_REDCAP_RC_CTRL_ACT_ID_UL_PRB_CAP = 100,
  NR_REDCAP_RC_RAN_PARAM_ID_UE_RNTI = 101,
  NR_REDCAP_RC_RAN_PARAM_ID_MAX_UL_PRB = 102,
};

typedef struct {
  uint16_t rnti;
  uint16_t max_ul_prbs;
} nr_redcap_rc_ul_prb_ctrl_t;

typedef struct {
  uint64_t rrc_ue_id;
  uint16_t long_cycle_ms;
} nr_redcap_rc_drx_ctrl_t;

bool nr_redcap_parse_ul_prb_ctrl_message(const e2sm_rc_ctrl_msg_frmt_1_t *msg, nr_redcap_rc_ul_prb_ctrl_t *ctrl);
bool nr_redcap_is_approved_long_drx_cycle(uint16_t long_cycle_ms);
bool nr_redcap_parse_drx_ctrl_message(const e2sm_rc_ctrl_hdr_frmt_1_t *hdr,
                                      const e2sm_rc_ctrl_msg_frmt_1_t *msg,
                                      nr_redcap_rc_drx_ctrl_t *ctrl,
                                      const char **reason);

#endif
