# SDK Seed Inventory

## Purpose

- Record the current reusable RedCap O-RAN control seed before runtime SDK work starts.
- Separate existing evidence from future SDK claims.
- Keep exact O-RAN clause mappings `[Needs Verification]` until local references are extracted.

## Role Boundary

| Role | Current seed | Responsibility | Boundary |
|---|---|---|---|
| [rApp] | `control/redcap_policy_case_b.yaml` | Long-term policy intent and allowed runtime parameter list | Must not directly mutate OAI runtime state |
| [xApp] | `ci-scripts/redcap_ul_prb_ctrl_xapp.c` | C/C++ E2SM-RC request construction and send path | Existing helper targets UL PRB cap only |
| [dApp/gNB guard] | `redcap_control_contract.yaml`; `openair2/E2AP/RAN_FUNCTION/O-RAN/ran_func_rc.c` | Contract validation concept and local apply/reject boundary | Current UL PRB handler uses local scheduler checks, but contract coverage is incomplete |
| [Operator] | `redcap_interface/bash_library/fc_send_ul_prb_control.sh` | Build/send wrapper and dry-run path | Writes logs under `test_log/`, not a stable SDK API |

## Existing xApp Seed

| Item | Evidence | Notes |
|---|---|---|
| Request builder | `make_redcap_ul_prb_ctrl_req` in `ci-scripts/redcap_ul_prb_ctrl_xapp.c` | Builds RC control request with RNTI and max UL PRB cap |
| Dry run | `REDCAP_CTRL_DRY_RUN=1` | Prints request fields without connecting to nearRT-RIC |
| Runtime send | `control_sm_xapp_api` in `ci-scripts/redcap_ul_prb_ctrl_xapp.c` | Requires connected E2 node and RC RAN function |
| Build wrapper | `redcap_interface/bash_library/fc_send_ul_prb_control.sh` | Compiles helper against local FlexRIC build and stages service-model libs |

## Existing dApp/gNB Apply Seed

| Item | Evidence | Notes |
|---|---|---|
| RC parse path | `openair2/E2AP/RAN_FUNCTION/O-RAN/ran_func_rc_redcap.c` | Parses RedCap UL PRB control message |
| Apply path | `apply_redcap_ul_prb_control` in `openair2/E2AP/RAN_FUNCTION/O-RAN/ran_func_rc.c` | Applies sanitized UL PRB cap to the serving gNB MAC UE context |
| Scheduler guard | `nr_redcap_sanitize_ul_prb_cap` | Keeps the requested cap compatible with scheduler minimum grant size |
| Validation hook | `redcap_interface/validate_redcap_interface.sh` | Checks the xApp source exists as part of interface validation |

## Gap Before SDK Runtime V1

- `redcap_ul_prb_cap` is now listed in `redcap_control_contract.yaml` with owner, unit, default, mutability, range, rollback, and validation marker.
- The existing UL PRB seed can guide xApp SDK shape, and the sender wrapper now validates policy/contract before dry-run or live control.
- Case B policy now allows `redcap_ul_prb_cap`, while the remaining runtime gap is live RFsim marker evidence.

## First G2 Recommendation

- [Recommended]: use the contract-backed `redcap_ul_prb_cap` slice because existing C/C++ xApp and gNB RC apply code already exist.
- [Current evidence]: build-only PASS and dry-run PASS on 2026-07-04.
- [Required before runtime PASS]: RFsim Case B marker evidence.
