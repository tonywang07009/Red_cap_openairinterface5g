# Work Daily Log
## Session Metadata
- Date: 2026-04-11 22:08
- Agent Session ID: N/A
- Task Slug: redcap-m1-hdfdd-gap-enforcement

## Milestone & Sub-task Reference
- Milestone: Milestone 1
- Sub-task: Enforce the local `[HD-FDD Type A]` `[Tx/Rx switching gap]` for `[RedCap]` in the `[gNB config + UL scheduler]` path
- Status: COMPLETED

## What Was Done
- Updated `openair2/LAYER2/NR_MAC_gNB/nr_mac_redcap.h`:
  - added `NR_REDCAP_HD_FDD_MIN_RXTXTIME`
  - added `nr_redcap_effective_min_rxtxtime()` as the shared helper for `[HD-FDD gap floor]`
- Updated `openair2/GNB_APP/gnb_config.c`:
  - added an early config reader for `halfDuplexRedCapAllowed_r17`
  - when `[RedCap half-duplex]` is enabled, `minRXTXTIME` is now clamped to the project floor before `get_scc_config()` builds UL timing-dependent structures
- Updated `openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_ulsch.c`:
  - the UL scheduler now derives `min_rxtx` from the shared RedCap helper instead of trusting the raw config blindly
- Updated `openair2/LAYER2/NR_MAC_gNB/tests/test_nr_redcap_coreset0.cpp`:
  - added unit coverage for:
    - non-RedCap passthrough
    - RedCap HD-FDD clamp to `[6]`
    - preserving larger configured gaps

## 3GPP Spec Clauses Referenced
- TS 38.306 Section 4.2.21.1 — RedCap reduced-capability profile including `halfDuplexFDD-TypeA-RedCap-r17`
- TS 38.331 [PDF local text around `RedCap-ConfigCommonSIB-r17`] — `halfDuplexRedCapAllowed-r17` conditions UE access and barred-cell behavior for half-duplex-only UEs
- TS 38.101-1 Clause 5.4.4 / Clause 7.3I [inference] — FDD Tx-Rx separation and HD-FDD RedCap RF context motivate the scheduler-side switching-gap floor
- `agent_doc/Project_management/Simluation_v2.md` — project-level simulation assumption explicitly sets `--min_rxtxtime 6` for `[M1 HD-FDD Tx/Rx switching gap]`

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| `ASAN_OPTIONS=detect_leaks=0 LSAN_OPTIONS=detect_leaks=0 cmake --build --preset tests --target nr-softmodem test_nr_redcap_coreset0` | Pass | main build + new HD-FDD helper test target | Log: `test_log/build_logs/redcap_m1_hdfdd_gap_build_2026-04-11_22-07-47.log` |
| `ASAN_OPTIONS=detect_leaks=0 LSAN_OPTIONS=detect_leaks=0 ctest --test-dir cmake_targets/ran_build/build_test -R 'test_nr_frame_params|test_nr_redcap_coreset0|test_nr_redcap_bwp|test_nr_ue_redcap_bwp|test_nr_redcap_sdt_fsm' --output-on-failure` | Pass | M1 + M3 + M4 regression spot-check | Log: `test_log/compiler_logs/redcap_m1_hdfdd_gap_regression_2026-04-11_22-08-16.log` |

## Known Issues / Blockers
- The `[6-slot]` HD-FDD floor is currently the project’s simulation assumption taken from `Simluation_v2.md`; exact 3GPP wording for that exact slot-count mapping still needs final documentation-level verification
- Docker-based runtime evidence for M5 remains blocked in the current sandbox

## Next Step
- Reassess the next non-Docker RedCap gap, with the most likely candidates being `[Milestone 2 encode/decode coverage]` or the remaining `[Milestone 3 CORESET#0 Case B close-out]`
