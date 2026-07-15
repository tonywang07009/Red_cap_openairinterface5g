#include "redcap_rapp_policy.h"

#include <string.h>

static const char *const redcap_case_b_allowed_parameters[] = {
    "redcap_ul_prb_cap",
    "drx_profile",
    "edrx_cycle_s",
    "edrx_ptw_s",
    "psm_t3324_active_time_s",
    "psm_t3512_tau_s",
};

redcap_rapp_policy_package_t redcap_rapp_policy_case_b(void)
{
  return (redcap_rapp_policy_package_t){
      .policy_version = "case_b_oran_control_v1",
      .rapp_role = "long_term_policy",
      .control_contract = "redcap_interface/control/redcap_control_contract.yaml",
      .allowed_runtime_parameters = redcap_case_b_allowed_parameters,
      .allowed_runtime_parameters_len =
          sizeof(redcap_case_b_allowed_parameters) / sizeof(redcap_case_b_allowed_parameters[0]),
  };
}

bool redcap_rapp_validate_policy_package(const redcap_rapp_policy_package_t *policy)
{
  if (policy == NULL)
    return false;
  if (policy->policy_version == NULL || policy->policy_version[0] == '\0')
    return false;
  if (policy->rapp_role == NULL || strcmp(policy->rapp_role, "long_term_policy") != 0)
    return false;
  if (policy->control_contract == NULL || policy->control_contract[0] == '\0')
    return false;
  if (policy->allowed_runtime_parameters == NULL || policy->allowed_runtime_parameters_len == 0)
    return false;
  for (size_t i = 0; i < policy->allowed_runtime_parameters_len; ++i) {
    if (policy->allowed_runtime_parameters[i] == NULL || policy->allowed_runtime_parameters[i][0] == '\0')
      return false;
  }
  return true;
}
