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

bool nr_redcap_is_approved_long_drx_cycle(uint16_t long_cycle_ms)
{
  static const uint16_t approved_cycles_ms[] = {320, 640, 1280, 2560, 5120, 10240};
  for (size_t i = 0; i < sizeof(approved_cycles_ms) / sizeof(approved_cycles_ms[0]); ++i) {
    if (long_cycle_ms == approved_cycles_ms[i])
      return true;
  }
  return false;
}

static bool nr_redcap_extract_rrc_ue_id(const ue_id_e2sm_t *ue_id, uint64_t *rrc_ue_id)
{
  if (ue_id == NULL || rrc_ue_id == NULL)
    return false;

  switch (ue_id->type) {
    case GNB_UE_ID_E2SM:
      if (ue_id->gnb.ran_ue_id == NULL)
        return false;
      *rrc_ue_id = *ue_id->gnb.ran_ue_id;
      return true;
    case GNB_DU_UE_ID_E2SM:
      if (ue_id->gnb_du.ran_ue_id == NULL)
        return false;
      *rrc_ue_id = *ue_id->gnb_du.ran_ue_id;
      return true;
    default:
      return false;
  }
}

bool nr_redcap_parse_drx_ctrl_message(const e2sm_rc_ctrl_hdr_frmt_1_t *hdr,
                                      const e2sm_rc_ctrl_msg_frmt_1_t *msg,
                                      nr_redcap_rc_drx_ctrl_t *ctrl,
                                      const char **reason)
{
  if (reason != NULL)
    *reason = "e2_decode_error";
  if (hdr == NULL || msg == NULL || ctrl == NULL
      || hdr->ric_style_type != NR_REDCAP_RC_CTRL_STYLE_ID_RADIO_RESOURCE_ALLOCATION
      || hdr->ctrl_act_id != NR_REDCAP_RC_CTRL_ACT_ID_DRX_CONFIGURATION || msg->sz_ran_param != 1
      || msg->ran_param == NULL)
    return false;

  uint64_t rrc_ue_id = 0;
  int64_t long_cycle_ms = 0;
  if (!nr_redcap_extract_rrc_ue_id(&hdr->ue_id, &rrc_ue_id) || rrc_ue_id == 0
      || msg->ran_param[0].ran_param_id != NR_REDCAP_RC_RAN_PARAM_ID_LONG_DRX_CYCLE
      || !nr_redcap_extract_int_ran_param(&msg->ran_param[0], &long_cycle_ms) || long_cycle_ms <= 0
      || long_cycle_ms > UINT16_MAX)
    return false;

  if (!nr_redcap_is_approved_long_drx_cycle((uint16_t)long_cycle_ms)) {
    if (reason != NULL)
      *reason = "unsupported_long_cycle";
    return false;
  }

  *ctrl = (nr_redcap_rc_drx_ctrl_t){.rrc_ue_id = rrc_ue_id, .long_cycle_ms = (uint16_t)long_cycle_ms};
  if (reason != NULL)
    *reason = "ack";
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
