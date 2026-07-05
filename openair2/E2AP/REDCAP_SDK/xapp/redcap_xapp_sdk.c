#include "redcap_xapp_sdk.h"

#include "lib/sm/ie/ue_id.h"
#include "sm/rc_sm/ie/ir/ran_parameter_value.h"
#include "sm/rc_sm/ie/ir/seq_ran_param.h"
#include "sm/rc_sm/rc_sm_id.h"
#include "xApp/sm_ran_function_def.h"

#include <errno.h>
#include <stdlib.h>
#include <string.h>

bool redcap_xapp_parse_u64(const char *raw, uint64_t min_value, uint64_t max_value, uint64_t *value)
{
  if (raw == NULL || raw[0] == '\0' || value == NULL)
    return false;

  errno = 0;
  char *endptr = NULL;
  const unsigned long long parsed = strtoull(raw, &endptr, 0);
  if (errno != 0 || endptr == raw || *endptr != '\0')
    return false;

  if (parsed < min_value || parsed > max_value)
    return false;

  *value = (uint64_t)parsed;
  return true;
}

bool redcap_xapp_read_required_env_u64(const char *name, uint64_t min_value, uint64_t max_value, uint64_t *value)
{
  if (name == NULL)
    return false;

  return redcap_xapp_parse_u64(getenv(name), min_value, max_value, value);
}

bool redcap_xapp_env_enabled(const char *name)
{
  const char *raw = getenv(name);
  if (raw == NULL)
    return false;

  return strcmp(raw, "1") == 0 || strcmp(raw, "true") == 0 || strcmp(raw, "TRUE") == 0 || strcmp(raw, "yes") == 0;
}

static ue_id_e2sm_t redcap_xapp_make_gnb_ue_id(uint64_t ran_ue_id)
{
  ue_id_e2sm_t ue_id = {0};
  ue_id.type = GNB_UE_ID_E2SM;
  ue_id.gnb.amf_ue_ngap_id = 0;
  ue_id.gnb.guami.plmn_id = (e2sm_plmn_t){.mcc = 1, .mnc = 1, .mnc_digit_len = 2};
  ue_id.gnb.guami.amf_region_id = 0;
  ue_id.gnb.guami.amf_set_id = 0;
  ue_id.gnb.guami.amf_ptr = 0;
  ue_id.gnb.ran_ue_id = calloc(1, sizeof(*ue_id.gnb.ran_ue_id));
  if (ue_id.gnb.ran_ue_id != NULL)
    *ue_id.gnb.ran_ue_id = ran_ue_id;
  return ue_id;
}

static seq_ran_param_t redcap_xapp_make_integer_ran_param(uint32_t ran_param_id, int64_t value)
{
  seq_ran_param_t ran_param = {0};
  ran_param.ran_param_id = ran_param_id;
  ran_param.ran_param_val.type = ELEMENT_KEY_FLAG_TRUE_RAN_PARAMETER_VAL_TYPE;
  ran_param.ran_param_val.flag_true = calloc(1, sizeof(*ran_param.ran_param_val.flag_true));
  if (ran_param.ran_param_val.flag_true != NULL) {
    ran_param.ran_param_val.flag_true->type = INTEGER_RAN_PARAMETER_VALUE;
    ran_param.ran_param_val.flag_true->int_ran = value;
  }
  return ran_param;
}

rc_ctrl_req_data_t redcap_xapp_make_ul_prb_ctrl_req(uint64_t ue_id, uint16_t rnti, uint16_t max_ul_prb)
{
  rc_ctrl_req_data_t ctrl_req = {0};
  ctrl_req.hdr.format = FORMAT_1_E2SM_RC_CTRL_HDR;
  ctrl_req.hdr.frmt_1.ue_id = redcap_xapp_make_gnb_ue_id(ue_id);
  ctrl_req.hdr.frmt_1.ric_style_type = 1;
  ctrl_req.hdr.frmt_1.ctrl_act_id = NR_REDCAP_RC_CTRL_ACT_ID_UL_PRB_CAP;
  ctrl_req.hdr.frmt_1.ric_ctrl_decision = NULL;

  ctrl_req.msg.format = FORMAT_1_E2SM_RC_CTRL_MSG;
  ctrl_req.msg.frmt_1.sz_ran_param = 2;
  ctrl_req.msg.frmt_1.ran_param = calloc(ctrl_req.msg.frmt_1.sz_ran_param, sizeof(*ctrl_req.msg.frmt_1.ran_param));
  if (ctrl_req.msg.frmt_1.ran_param != NULL) {
    ctrl_req.msg.frmt_1.ran_param[0] =
        redcap_xapp_make_integer_ran_param(NR_REDCAP_RC_RAN_PARAM_ID_UE_RNTI, rnti);
    ctrl_req.msg.frmt_1.ran_param[1] =
        redcap_xapp_make_integer_ran_param(NR_REDCAP_RC_RAN_PARAM_ID_MAX_UL_PRB, max_ul_prb);
  }

  return ctrl_req;
}

ssize_t redcap_xapp_find_rc_ran_func_idx(const e2_node_connected_xapp_t *node)
{
  if (node == NULL)
    return -1;

  for (size_t i = 0; i < node->len_rf; ++i) {
    if (node->rf[i].id == SM_RC_ID || node->rf[i].defn.type == RC_RAN_FUNC_DEF_E)
      return (ssize_t)i;
  }

  return -1;
}
