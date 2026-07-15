# G1 SDK Contract

## Scope

- Define SDK v1 ownership for [rApp], [xApp], and [dApp/gNB guard].
- Reuse existing Case A/B control contract files.
- Inventory existing OAI/FlexRIC RedCap control seed code.

## Target Inputs

- `redcap_interface/control/redcap_control_contract.yaml`
- `redcap_interface/control/redcap_policy_case_a.yaml`
- `redcap_interface/control/redcap_policy_case_b.yaml`
- `ci-scripts/redcap_ul_prb_ctrl_xapp.c`
- `openair2/E2AP/RAN_FUNCTION/O-RAN/ran_func_rc.c`

## Acceptance Criteria

- [rApp] is documented as policy intent only.
- [xApp] is documented as C/C++ first for existing KPM/RC capability.
- [dApp/gNB guard] is documented as the apply/reject/rollback boundary.
- KPM is explicitly marked observation only.
- Exact O-RAN clause mappings are marked `[Needs Verification]` until extracted.
- `validation/sdk_seed_inventory.md` records reusable seed files and gaps.

## Status

- [x] Ownership model exists in project rules.
- [x] Detailed seed-code inventory recorded.
