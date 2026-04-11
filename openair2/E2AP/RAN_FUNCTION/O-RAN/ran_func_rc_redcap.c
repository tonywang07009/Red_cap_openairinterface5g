#include "ran_func_rc_redcap.h"

#include "openair2/E2AP/flexric/src/sm/rc_sm/ie/ir/ran_parameter_value.h"

static bool nr_redcap_extract_int_ran_param(const seq_ran_param_t *ran_param, int64_t *value)
{
  if (ran_param == NULL || value == NULL)
    return false;

  if (ran_param->ran_param_val.type != ELEMENT_KEY_FLAG_TRUE_RAN_PARAMETER_VAL_TYPE || ran_param->ran_param_val.flag_true == NULL)
    return false;

  if (ran_param->ran_param_val.flag_true->type != INTEGER_RAN_PARAMETER_VALUE)
    return false;

  *value = ran_param->ran_param_val.flag_true->int_ran;
  return true;
}

bool nr_redcap_parse_ul_prb_ctrl_message(const e2sm_rc_ctrl_msg_frmt_1_t *msg, nr_redcap_rc_ul_prb_ctrl_t *ctrl)
{
  if (msg == NULL || ctrl == NULL || msg->ran_param == NULL)
    return false;

  bool seen_rnti = false;
  bool seen_max_ul_prb = false;
  int64_t parsed_rnti = 0;
  int64_t parsed_max_ul_prb = 0;

  for (size_t i = 0; i < msg->sz_ran_param; ++i) {
    int64_t value = 0;
    if (!nr_redcap_extract_int_ran_param(&msg->ran_param[i], &value))
      return false;

    switch (msg->ran_param[i].ran_param_id) {
      case NR_REDCAP_RC_RAN_PARAM_ID_UE_RNTI:
        seen_rnti = true;
        parsed_rnti = value;
        break;
      case NR_REDCAP_RC_RAN_PARAM_ID_MAX_UL_PRB:
        seen_max_ul_prb = true;
        parsed_max_ul_prb = value;
        break;
      default:
        return false;
    }
  }

  if (!seen_rnti || !seen_max_ul_prb)
    return false;

  if (parsed_rnti <= 0 || parsed_rnti > UINT16_MAX)
    return false;

  if (parsed_max_ul_prb < 0 || parsed_max_ul_prb > UINT16_MAX)
    return false;

  ctrl->rnti = (uint16_t)parsed_rnti;
  ctrl->max_ul_prbs = (uint16_t)parsed_max_ul_prb;
  return true;
}
