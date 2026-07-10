#include "ran_func_rc_redcap.h"

#include "openair2/E2AP/flexric/src/sm/rc_sm/ie/ir/ran_parameter_value.h"

#include <assert.h>
#include <string.h>

int main(void)
{
  uint64_t rrc_ue_id = 17;
  e2sm_rc_ctrl_hdr_frmt_1_t hdr = {
      .ue_id = {.type = GNB_UE_ID_E2SM, .gnb = {.ran_ue_id = &rrc_ue_id}},
      .ric_style_type = NR_REDCAP_RC_CTRL_STYLE_ID_RADIO_RESOURCE_ALLOCATION,
      .ctrl_act_id = NR_REDCAP_RC_CTRL_ACT_ID_DRX_CONFIGURATION,
  };
  ran_parameter_value_t value = {.type = INTEGER_RAN_PARAMETER_VALUE, .int_ran = 1280};
  seq_ran_param_t param = {
      .ran_param_id = NR_REDCAP_RC_RAN_PARAM_ID_LONG_DRX_CYCLE,
      .ran_param_val = {.type = ELEMENT_KEY_FLAG_TRUE_RAN_PARAMETER_VAL_TYPE, .flag_true = &value},
  };
  e2sm_rc_ctrl_msg_frmt_1_t msg = {.sz_ran_param = 1, .ran_param = &param};
  nr_redcap_rc_drx_ctrl_t ctrl = {0};
  const char *reason = 0;

  assert(nr_redcap_parse_drx_ctrl_message(&hdr, &msg, &ctrl, &reason));
  assert(ctrl.rrc_ue_id == rrc_ue_id);
  assert(ctrl.long_cycle_ms == 1280);
  assert(strcmp(reason, "ack") == 0);

  msg.sz_ran_param = 2;
  assert(!nr_redcap_parse_drx_ctrl_message(&hdr, &msg, &ctrl, &reason));
  assert(strcmp(reason, "e2_decode_error") == 0);

  msg.sz_ran_param = 1;
  value.int_ran = 512;
  assert(!nr_redcap_parse_drx_ctrl_message(&hdr, &msg, &ctrl, &reason));
  assert(strcmp(reason, "unsupported_long_cycle") == 0);

  value.int_ran = 640;
  param.ran_param_id = 2;
  assert(!nr_redcap_parse_drx_ctrl_message(&hdr, &msg, &ctrl, &reason));
  assert(strcmp(reason, "e2_decode_error") == 0);
  return 0;
}
