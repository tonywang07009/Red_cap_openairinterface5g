#ifndef RAN_FUNC_RC_REDCAP_H
#define RAN_FUNC_RC_REDCAP_H

#include <stdbool.h>
#include <stdint.h>

#include "openair2/E2AP/flexric/src/sm/rc_sm/ie/ir/e2sm_rc_ctrl_msg_frmt_1.h"

enum {
  NR_REDCAP_RC_CTRL_ACT_ID_UL_PRB_CAP = 100,
  NR_REDCAP_RC_RAN_PARAM_ID_UE_RNTI = 101,
  NR_REDCAP_RC_RAN_PARAM_ID_MAX_UL_PRB = 102,
};

typedef struct {
  uint16_t rnti;
  uint16_t max_ul_prbs;
} nr_redcap_rc_ul_prb_ctrl_t;

bool nr_redcap_parse_ul_prb_ctrl_message(const e2sm_rc_ctrl_msg_frmt_1_t *msg, nr_redcap_rc_ul_prb_ctrl_t *ctrl);

#endif
