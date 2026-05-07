# M4B DRX eDRX PSM

## Scope
- Connected DRX behavior.
- Idle and inactive eDRX support.
- PSM/NAS timer interface hooks and documentation.

## Out of Scope
- Full AMF/CN feature development unless explicitly promoted.
- xApp/rApp/dApp SDK implementation.
- mMTC scaling fixes unrelated to low-power behavior.

## 3GPP Spec Mapping
- TS 38.321 Section 5.7 — Connected DRX.
- TS 38.331 eDRX SIB1/RRC clauses: [Needs Verification].
- TS 24.501 T3324 / periodic registration / PSM behavior: [Needs Verification].

## Target Files
- `openair2/LAYER2/NR_MAC_UE/config_ue.c`
- `openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_dlsch.c`
- `openair2/LAYER2/NR_MAC_gNB/gNB_scheduler.c`
- `openair2/RRC/NR/rrc_gNB.c`
- `openair2/RRC/NR_UE/rrc_UE.c`
- RedCap gNB and UE YAML files referenced by `5g_rfsimulator_flexric_redcap/`.

## Implementation Tasks
- `M4B-T1`: Connected DRX config parse and runtime gating.
- `M4B-T2`: eDRX SIB1 encode/decode and UE state gating.
- `M4B-T3`: PSM timer hooks and CN dependency report.

## Flow Validation
- UE no longer logs `DRX not implemented! Configuration not handled!` when DRX is configured.
- DRX active/inactive periods are visible in logs.
- eDRX and PSM behavior must be marked as [compile-level], [flow-level], or [runtime-level].

## System Unit Tests
- `UT-M4B-001`: DRX config parse.
- `UT-M4B-002`: eDRX SIB1 encode/decode.
- `UT-M4B-003`: PSM timer hook state tracking.

## RFsim Runtime Tests
- `RT-M4B-001`: Connected DRX runtime smoke.
- `RT-M4B-002`: eDRX/PSM compile-level plus log-level validation until CN support is defined.

## Boundary Classification
- [Connected DRX]：[unit/flow-level] PASS.
  - UE MAC parses and stores RRC `DRX-Config`.
  - UE scheduler calls `nr_ue_drx_is_active()` before normal PDCCH/DCI monitoring.
  - Current RFsim source-of-truth compose path does not provide a DRX-enabled runtime config, so [RT-M4B-001] is [NA] rather than PASS.
- [eDRX]：[runtime log-level] PASS.
  - UE logs `SIB1 eDRX allowed: idle=0 inactive=0` in current Case A/B RFsim evidence.
  - Idle/inactive paging extension behavior remains outside current runtime claim.
- [PSM]：[runtime log-level] PASS.
  - UE NAS logs `NAS PSM timers: T3324=-1 sec T3512=1320 sec configured=1 low_power_ready=0`.
  - CN-driven sleep/quiesce behavior is not claimed.

## Closure Evidence
- [M4-B focused CTest PASS] `test_log/compiler_logs/ctest_m4b_lowpower_boundary_2026-05-07_13-24-38_lsanoff.log`
- [M4-B focused CTest false-fail note] `test_log/compiler_logs/ctest_m4b_lowpower_boundary_2026-05-07_13-24-30.log` failed only because LeakSanitizer cannot run under ptrace in this environment.
- [Case A runtime log-level evidence] `test_log/runtime_artifacts/m3_casea_2026-05-07_13-15-07/`
- [Case B runtime log-level evidence] `test_log/runtime_artifacts/m3_caseb_2026-05-07_13-10-12/`
- [Learning report] `test_log/report/m4b_lowpower_boundary_report_2026-05-07_13-25-44.md`

## Completion Criteria
- [source build PASS] No new C/C++ source patch in this boundary closure; previous M4B UE build evidence remains in `test_log/build_logs/`.
- [unit test PASS] Focused M4B CTest: 4/4 passed with `LSAN_OPTIONS=detect_leaks=0`.
- [runtime or compile-level boundary stated]
- [spec traceability updated]
