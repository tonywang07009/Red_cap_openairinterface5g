## Why

The BWP Gate 5 RFsim matrix currently executes all eight rows, but every `ci trigger_bwp_switch 0` attempt crashes the gNB in `update_cellGroupConfig_for_BWP_switch()`. This blocks any evidence-based claim for BWP switch delay, PDU scheduling delay, and paper-comparable BWP residency metrics.

This fix is needed now because the existing `redcap-bwp-sdt-validation` OpenSpec change is a validation scaffold and explicitly treated OAI C-code changes as out of scope; the crash requires a separate runtime reconfiguration change.

## What Changes

- Add a transactional BWP runtime reconfiguration path for switching a UE from additional BWP 1 back to initial BWP 0.
- Ensure BWP reconfiguration candidate data is encoded successfully before it is assigned to pending UE state.
- Prevent failed BWP reconfiguration attempts from mutating the live `UE->CellGroup` or leaving stale `UE->local_bwp_id` state.
- Preserve the existing `ci trigger_bwp_switch` command syntax and existing BWP/SDT validation CSV schemas.
- Add an explicit code-review gate for the current `RedCap_BWP_SDT_validation` project implementation scope.

## Capabilities

### New Capabilities

- `redcap-bwp-runtime-reconfiguration`: Runtime-safe RedCap/OAI BWP reconfiguration from additional BWP 1 to initial BWP 0, with non-crashing behavior, encode-before-submit semantics, and evidence-backed Gate 5 validation status.

### Modified Capabilities

- None.

## Impact

- Affected C code: `openair2/LAYER2/NR_MAC_gNB/nr_radio_config.c`, `openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_primitives.c`, and related MAC/RRC/F1AP reconfiguration boundaries.
- Affected validation project: `agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/`.
- Affected OpenSpec records: new change artifacts under `openspec/changes/fix-bwp-trigger0-reconfiguration-crash/`, plus an optional English review task in the existing `redcap-bwp-sdt-validation` task list.
- Affected runtime evidence: single trigger0 RFsim proof, bidirectional BWP trigger sanity run, and the eight-row BWP matrix rerun after the crash fix.
