#include "redcap_xapp_sdk.h"

#include "sm/rc_sm/ie/ir/ran_parameter_value.h"

#include <assert.h>
#include <stdlib.h>

int main(void)
{
  rc_ctrl_req_data_t request = {0};
  assert(redcap_xapp_make_drx_ctrl_req(17, 1280, &request));
  assert(request.hdr.frmt_1.ric_style_type == NR_REDCAP_RC_CTRL_STYLE_ID_RADIO_RESOURCE_ALLOCATION);
  assert(request.hdr.frmt_1.ctrl_act_id == NR_REDCAP_RC_CTRL_ACT_ID_DRX_CONFIGURATION);
  assert(request.msg.frmt_1.sz_ran_param == 1);
  assert(request.msg.frmt_1.ran_param[0].ran_param_id == NR_REDCAP_RC_RAN_PARAM_ID_LONG_DRX_CYCLE);
  assert(request.msg.frmt_1.ran_param[0].ran_param_val.flag_true->int_ran == 1280);

  free(request.msg.frmt_1.ran_param[0].ran_param_val.flag_true);
  free(request.msg.frmt_1.ran_param);
  free(request.hdr.frmt_1.ue_id.gnb.ran_ue_id);
  assert(!redcap_xapp_make_drx_ctrl_req(17, 512, &request));
  return 0;
}
