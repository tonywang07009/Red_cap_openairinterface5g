#include "lib/sm/ie/ue_id.h"
#include "sm/rc_sm/ie/ir/ran_parameter_value.h"
#include "sm/rc_sm/ie/ir/seq_ran_param.h"
#include "sm/rc_sm/ie/rc_data_ie.h"
#include "sm/rc_sm/rc_sm_id.h"
#include "xApp/e42_xapp_api.h"
#include "xApp/sm_ran_function_def.h"

#include <errno.h>
#include <inttypes.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <unistd.h>

enum {
  NR_REDCAP_RC_CTRL_ACT_ID_UL_PRB_CAP = 100,
  NR_REDCAP_RC_RAN_PARAM_ID_UE_RNTI = 101,
  NR_REDCAP_RC_RAN_PARAM_ID_MAX_UL_PRB = 102,
};

/**
 * Read a required integer environment variable using either decimal or
 * `0x`-prefixed hexadecimal notation.
 */
static bool read_required_env_u64(const char *name, uint64_t min_value, uint64_t max_value, uint64_t *value)
{
  if (name == NULL || value == NULL)
    return false;

  const char *raw = getenv(name);
  if (raw == NULL || raw[0] == '\0') {
    fprintf(stderr, "Missing required environment variable %s\n", name);
    return false;
  }

  errno = 0;
  char *endptr = NULL;
  const unsigned long long parsed = strtoull(raw, &endptr, 0);
  if (errno != 0 || endptr == raw || *endptr != '\0') {
    fprintf(stderr, "Invalid integer value for %s: %s\n", name, raw);
    return false;
  }

  if (parsed < min_value || parsed > max_value) {
    fprintf(stderr, "Out-of-range value for %s: %s\n", name, raw);
    return false;
  }

  *value = (uint64_t)parsed;
  return true;
}

/**
 * Treat common truthy strings as enabling the local dry-run path.
 */
static bool env_enabled(const char *name)
{
  const char *raw = getenv(name);
  if (raw == NULL)
    return false;

  return strcmp(raw, "1") == 0 || strcmp(raw, "true") == 0 || strcmp(raw, "TRUE") == 0 || strcmp(raw, "yes") == 0;
}

/**
 * Build a minimal gNB UE ID that satisfies the RC control header encoding
 * while keeping the target UE selection anchored on the explicit RNTI
 * carried in the control message body.
 */
static ue_id_e2sm_t make_gnb_ue_id(uint64_t ran_ue_id)
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

/**
 * Encode one integer-valued RC RAN parameter in the format expected by the
 * OAI RedCap control handler.
 */
static seq_ran_param_t make_integer_ran_param(uint32_t ran_param_id, int64_t value)
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

/**
 * Build the RC control request for the RedCap UL PRB cap action.
 */
static rc_ctrl_req_data_t make_redcap_ul_prb_ctrl_req(uint64_t ue_id, uint16_t rnti, uint16_t max_ul_prb)
{
  rc_ctrl_req_data_t ctrl_req = {0};
  ctrl_req.hdr.format = FORMAT_1_E2SM_RC_CTRL_HDR;
  ctrl_req.hdr.frmt_1.ue_id = make_gnb_ue_id(ue_id);
  ctrl_req.hdr.frmt_1.ric_style_type = 1;
  ctrl_req.hdr.frmt_1.ctrl_act_id = NR_REDCAP_RC_CTRL_ACT_ID_UL_PRB_CAP;
  ctrl_req.hdr.frmt_1.ric_ctrl_decision = NULL;

  ctrl_req.msg.format = FORMAT_1_E2SM_RC_CTRL_MSG;
  ctrl_req.msg.frmt_1.sz_ran_param = 2;
  ctrl_req.msg.frmt_1.ran_param = calloc(ctrl_req.msg.frmt_1.sz_ran_param, sizeof(*ctrl_req.msg.frmt_1.ran_param));
  if (ctrl_req.msg.frmt_1.ran_param != NULL) {
    ctrl_req.msg.frmt_1.ran_param[0] = make_integer_ran_param(NR_REDCAP_RC_RAN_PARAM_ID_UE_RNTI, rnti);
    ctrl_req.msg.frmt_1.ran_param[1] = make_integer_ran_param(NR_REDCAP_RC_RAN_PARAM_ID_MAX_UL_PRB, max_ul_prb);
  }

  return ctrl_req;
}

/**
 * Locate the RC RAN function announced by the connected E2 node.
 */
static ssize_t find_rc_ran_func_idx(const e2_node_connected_xapp_t *node)
{
  if (node == NULL)
    return -1;

  for (size_t i = 0; i < node->len_rf; ++i) {
    if (node->rf[i].id == SM_RC_ID || node->rf[i].defn.type == RC_RAN_FUNC_DEF_E)
      return (ssize_t)i;
  }

  return -1;
}

/**
 * Entry point for the standalone RedCap RC control helper.
 */
int main(int argc, char *argv[])
{
  uint64_t ue_id = 0;
  uint64_t rnti = 0;
  uint64_t max_ul_prb = 0;
  if (!read_required_env_u64("REDCAP_CTRL_UE_ID", 0, UINT64_MAX, &ue_id) ||
      !read_required_env_u64("REDCAP_CTRL_RNTI", 1, UINT16_MAX, &rnti) ||
      !read_required_env_u64("REDCAP_CTRL_UL_PRB_CAP", 0, UINT16_MAX, &max_ul_prb)) {
    return EXIT_FAILURE;
  }

  rc_ctrl_req_data_t ctrl_req = make_redcap_ul_prb_ctrl_req((uint64_t)ue_id, (uint16_t)rnti, (uint16_t)max_ul_prb);
  if (ctrl_req.hdr.frmt_1.ue_id.gnb.ran_ue_id == NULL || ctrl_req.msg.frmt_1.ran_param == NULL ||
      ctrl_req.msg.frmt_1.ran_param[0].ran_param_val.flag_true == NULL ||
      ctrl_req.msg.frmt_1.ran_param[1].ran_param_val.flag_true == NULL) {
    fprintf(stderr, "Failed to allocate RedCap RC control request\n");
    free_rc_ctrl_req_data(&ctrl_req);
    return EXIT_FAILURE;
  }

  if (env_enabled("REDCAP_CTRL_DRY_RUN")) {
    printf("mode=dry-run ue_id=%" PRIu64 " rnti=0x%04" PRIx64 " max_ul_prb=%" PRIu64 " action_id=%u\n",
           ue_id,
           rnti,
           max_ul_prb,
           NR_REDCAP_RC_CTRL_ACT_ID_UL_PRB_CAP);
    free_rc_ctrl_req_data(&ctrl_req);
    return EXIT_SUCCESS;
  }

  fr_args_t args = init_fr_args(argc, argv);
  init_xapp_api(&args);
  sleep(1);

  e2_node_arr_xapp_t nodes = e2_nodes_xapp_api();
  if (nodes.len == 0) {
    fprintf(stderr, "No connected E2 nodes available for RedCap RC control\n");
    free_rc_ctrl_req_data(&ctrl_req);
    while (try_stop_xapp_api() == false)
      usleep(1000);
    return EXIT_FAILURE;
  }

  size_t sent = 0;
  int rc = EXIT_SUCCESS;
  for (size_t i = 0; i < nodes.len; ++i) {
    const ssize_t rf_idx = find_rc_ran_func_idx(&nodes.n[i]);
    if (rf_idx < 0)
      continue;

    const uint32_t ran_func_id = nodes.n[i].rf[rf_idx].id;
    sm_ans_xapp_t ans = control_sm_xapp_api(&nodes.n[i].id, ran_func_id, &ctrl_req);
    if (!ans.success) {
      fprintf(stderr, "RedCap RC control failed on node %zu ran_func=%u\n", i, ran_func_id);
      rc = EXIT_FAILURE;
      continue;
    }

    ++sent;
    printf("RedCap RC control sent node=%zu ran_func=%u ue_id=%" PRIu64 " rnti=0x%04" PRIx64 " max_ul_prb=%" PRIu64 "\n",
           i,
           ran_func_id,
           ue_id,
           rnti,
           max_ul_prb);
  }

  free_rc_ctrl_req_data(&ctrl_req);
  free_e2_node_arr_xapp(&nodes);

  while (try_stop_xapp_api() == false)
    usleep(1000);

  if (sent == 0) {
    fprintf(stderr, "No RC-capable E2 node accepted the RedCap UL PRB control request\n");
    return EXIT_FAILURE;
  }

  return rc;
}
