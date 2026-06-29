# 2026-06-28 RedCap BWP/SDT Gate 5 Matrix Blocker

- Project Path: `agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/project_BWP_SDT.md`
- [Case]: A
- [Gate]: BWP Gate 5 and SDT Gate 6 hook audit
- [source build PASS/FAIL/NA]: NA; no C source rebuild was run in this continuation.
- [unit test PASS/FAIL/NA]: PASS for BWP/SDT extractor tests, merge smoke test, syntax checks, and Python compile checks.
- [RFsim runtime PASS/FAIL/NA]: BLOCKED for BWP Gate 5; 8/8 matrix rows ran, but every BWP 0 trigger crashed gNB.
- [exit 139]: YES for BWP telnet trigger path.

## Completed

- Used [SymDex] first for OAI hook lookup.
- Confirmed RA/SDT gate env hooks exist for `MMTC_RRC_INACTIVE_GATE2_RESUME_TRIGGER` and `MMTC_RRC_INACTIVE_GATE3_CG_CONFIG`.
- Confirmed `MMTC_RA_ACCESS_STEPS`, `slot10`, and `lambda_dp_5` are `[wrapper_label]` dimensions in current SDT wiring.
- Updated `run_bwp_matrix.sh` to:
  - use `BWP_TRIGGER_SEQUENCE='1 0'`
  - continue after per-scenario runner failures
  - default `STOP_AFTER_RUN=1`
  - default `REDCAP_COMPOSE_FORCE_RECREATE=1`
- Updated `redcap_runtime_common.sh` to support `REDCAP_COMPOSE_FORCE_RECREATE=1`.
- Ran `20260628_151500_bwp_matrix_recreate`: 8/8 BWP matrix rows generated runtime CSVs.
- Ran `20260628_154000_bwp_trigger0_bt` with `MMTC_SEGV_BACKTRACE=1`.
- Added `merge_runtime_metrics.py --replace-scenario` and `test_merge_runtime_metrics.py` to prevent stale local metric leakage.
- Added `BWP_runtime_evidence_20260628_151500.md`.

## Evidence

- [BWP matrix run id]: `20260628_151500_bwp_matrix_recreate`
- [BWP runtime CSV count]: 8
- [BWP rows]: every row had `active_ue_count = 1`, `bwp_gnb_reconfiguration_count = 1`, and `bwp_inactivity_timer_gap_seen = 1`.
- [Crash count]: 8/8 matrix rows contain `Segmentation fault` after BWP 0 trigger.
- [Backtrace run id]: `20260628_154000_bwp_trigger0_bt`
- [Backtrace frame]: `update_cellGroupConfig_for_BWP_switch+0x151`
- [Caller path]: `nr_mac_trigger_reconfiguration` -> `nr_trigger_bwp_switch` -> `trigger_bwp_switch`

## Validation

- `rtk bash -n .../redcap_runtime_common.sh`
- `rtk bash -n .../run_bwp_matrix.sh`
- `rtk bash .../run_bwp_matrix.sh --dry-run`
- `rtk python .../test_extract_bwp_metrics.py`
- `rtk python .../test_extract_sdt_metrics.py`
- `rtk python .../test_merge_runtime_metrics.py`
- `rtk python .../audit_oai_hooks.py`
- `rtk python .../exp_pictture/plot_paper_vs_local.py`

## Stop Point

- [BWP Gate 5]: [BLOCKED], not PASS. Runtime exists, but BWP 0 telnet trigger crashes gNB before switch-delay/PDU-delay evidence.
- [BWP semantics]: `MMTC_BWP_TRAFFIC_PROFILE`, `MMTC_BWP_INACTIVITY_TIMER_MS`, and `MMTC_BWP_SWITCH_DELAY_MS` are `[wrapper_label]` until OAI hooks are implemented.
- [SDT Gate 6]: numeric repeated-run aggregation is complete, but 2-step/slot/lambda dimensions are `[wrapper_label]`.
- [Gate 7]: not complete; CSV/plots/docs now align to the blocker instead of overclaiming PASS.

## Next Action

- Debug and fix `update_cellGroupConfig_for_BWP_switch()` for BWP 1 -> BWP 0 reconfiguration.
- Rebuild `nr-softmodem`, rerun a single `BWP_TRIGGER_SEQUENCE=0` backtrace case, then rerun the 8-row BWP matrix.
