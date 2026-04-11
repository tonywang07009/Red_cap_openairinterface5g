#ifndef RRC_UE_REDCAP_H
#define RRC_UE_REDCAP_H

#include <stdbool.h>

#include "NR_SIB1-v1700-IEs.h"
#include "NR_UE-NR-Capability.h"
#include "openair3/UICC/usim_interface.h"

#ifdef __cplusplus
extern "C" {
#endif

NR_UE_NR_Capability_t *nr_rrc_build_redcap_ue_capability(const nr_redcap_cfg_t *cfg);
bool nr_rrc_redcap_sib1_access_allowed(const nr_redcap_cfg_t *cfg, const NR_SIB1_v1700_IEs_t *sib1_v1700);

#ifdef __cplusplus
}
#endif

#endif
