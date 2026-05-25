# gNB Config Library

## Contents
| File | Role |
|---|---|
| `gnb_redcap_mmtc_case_b_final.yaml` | Default mMTC Case B runtime config used by `redcap_runtime_menu.sh` |
| `gnb_redcap_case_a_final.yaml` | Final Case A config retained for comparison |
| `gnb_redcap_case_b_final.yaml` | Final Case B config retained for comparison |
| `gnb_redcap_case_a_e2_disabled_final.yaml` | Case A config with E2 disabled for focused RFsim validation |
| `gnb_redcap_case_b_e2_disabled_final.yaml` | Case B config with E2 disabled for focused RFsim validation |

## Usage
- For Paper 07 or mMTC runtime tests, start from `gnb_redcap_mmtc_case_b_final.yaml` unless a PRB-specific config is required.
- 51PRB/106PRB production-style configs remain under `ci-scripts/conf_files/` because they are active script inputs.
- Promote a new config here only when it is a reusable final baseline.
