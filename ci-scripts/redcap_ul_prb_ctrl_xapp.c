#include "openair2/E2AP/REDCAP_SDK/xapp/redcap_xapp_sdk.h"

#include "lib/sm/ie/ue_id.h"
#include "sm/rc_sm/ie/rc_data_ie.h"
#include "xApp/e42_xapp_api.h"

#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

/**
 * Entry point for the standalone RedCap RC control helper.
 */
int main(int argc, char *argv[])
{
  uint64_t ue_id = 0;
  uint64_t rnti = 0;
  uint64_t max_ul_prb = 0;
  if (!redcap_xapp_read_required_env_u64("REDCAP_CTRL_UE_ID", 0, UINT64_MAX, &ue_id) ||
      !redcap_xapp_read_required_env_u64("REDCAP_CTRL_RNTI", 1, UINT16_MAX, &rnti) ||
      !redcap_xapp_read_required_env_u64("REDCAP_CTRL_UL_PRB_CAP", 0, UINT16_MAX, &max_ul_prb)) {
    fprintf(stderr, "Missing, invalid, or out-of-range RedCap control environment\n");
    return EXIT_FAILURE;
  }

  rc_ctrl_req_data_t ctrl_req = redcap_xapp_make_ul_prb_ctrl_req((uint64_t)ue_id, (uint16_t)rnti, (uint16_t)max_ul_prb);
  if (ctrl_req.hdr.frmt_1.ue_id.gnb.ran_ue_id == NULL || ctrl_req.msg.frmt_1.ran_param == NULL ||
      ctrl_req.msg.frmt_1.ran_param[0].ran_param_val.flag_true == NULL ||
      ctrl_req.msg.frmt_1.ran_param[1].ran_param_val.flag_true == NULL) {
    fprintf(stderr, "Failed to allocate RedCap RC control request\n");
    free_rc_ctrl_req_data(&ctrl_req);
    return EXIT_FAILURE;
  }

  if (redcap_xapp_env_enabled("REDCAP_CTRL_DRY_RUN")) {
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
    const ssize_t rf_idx = redcap_xapp_find_rc_ran_func_idx(&nodes.n[i]);
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
