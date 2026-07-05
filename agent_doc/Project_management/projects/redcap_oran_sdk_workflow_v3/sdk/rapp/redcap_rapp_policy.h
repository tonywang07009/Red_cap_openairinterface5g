#ifndef REDCAP_RAPP_POLICY_H
#define REDCAP_RAPP_POLICY_H

#include <stdbool.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
  const char *policy_version;
  const char *rapp_role;
  const char *control_contract;
  const char *const *allowed_runtime_parameters;
  size_t allowed_runtime_parameters_len;
} redcap_rapp_policy_package_t;

redcap_rapp_policy_package_t redcap_rapp_policy_case_b(void);
bool redcap_rapp_validate_policy_package(const redcap_rapp_policy_package_t *policy);

#ifdef __cplusplus
}
#endif

#endif
