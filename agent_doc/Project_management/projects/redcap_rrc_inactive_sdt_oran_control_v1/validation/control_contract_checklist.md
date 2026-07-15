# O-RAN Control Contract Checklist

## Purpose
- Keep [Case B] AI/O-RAN parameter updates bounded, reproducible, and separable from [Case A] protocol correctness.
- Prevent xApp/rApp/dApp ownership conflicts.

## Required Files
- [MUST] `redcap_interface/control/redcap_control_contract.yaml`
- [MUST] `redcap_interface/control/redcap_policy_case_a.yaml`
- [MUST] `redcap_interface/control/redcap_policy_case_b.yaml`

## Contract Field Requirements
- [MUST] `name`
- [MUST] `owner`
- [MUST] `unit`
- [MUST] `default`
- [MUST] `runtime_mutable`
- [MUST] `allowed_values` or `min` / `max`
- [MUST] `rollback`
- [MUST] `validation_log_marker`

## Ownership Rules
- [MUST] One parameter has one runtime owner.
- [MUST] rApp may set policy but must not directly write OAI runtime state.
- [MUST] xApp may issue control requests but must respect the contract.
- [MUST] dApp/gNB hook may reject unsafe updates.
- [MUST] If two controllers request the same parameter, priority order is dApp/gNB guard, xApp, rApp policy.

## Case A Checks
- [MUST] `dynamic_control.enabled` is false.
- [MUST] KPM-driven control is disabled.
- [MUST] E2SM-RC/custom SM/dApp local API control is disabled.
- [MUST] Fixed baseline parameters are recorded.

## Case B Checks
- [MUST] `dynamic_control.enabled` is true.
- [MUST] KPM is observation only.
- [MUST] Control output path is explicit.
- [MUST] Every update logs old value, new value, policy version, ACK/NACK/timeout, and applied snapshot.

## Validation IDs
| Test ID | Case | Purpose | Pass Criteria | Status |
|---|---|---|---|---|
| CT-T2B-001 | B | Contract schema check | All required fields present | [ ] |
| CT-T2B-002 | B | Ownership check | No duplicate runtime owner conflict | [ ] |
| CT-T2B-003 | B | Bounds check | Out-of-range control is rejected | [ ] |
| CT-T2B-004 | B | Rollback check | Rejected update logs rollback marker | [ ] |
| CT-T2B-005 | B | Case isolation | Case A policy remains unchanged | [ ] |
