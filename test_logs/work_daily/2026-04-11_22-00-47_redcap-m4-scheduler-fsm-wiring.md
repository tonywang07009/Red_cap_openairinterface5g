# Work Daily Log
## Session Metadata
- Date: 2026-04-11 22:00
- Agent Session ID: N/A
- Task Slug: redcap-m4-scheduler-fsm-wiring

## Milestone & Sub-task Reference
- Milestone: Milestone 4
- Sub-task: Wire the local `[SDT FSM]` into the active `[gNB MAC UL scheduler]` path and persist runtime transition logs for `[RedCap UE]`
- Status: COMPLETED

## What Was Done
- Added scheduler-facing `[SDT burst start / complete]` helper APIs in:
  - `openair2/LAYER2/NR_MAC_gNB/nr_mac_sdt_fsm.h`
  - `openair2/LAYER2/NR_MAC_gNB/nr_mac_sdt_fsm.c`
- Extended `NR_UE_sched_ctrl_t` with per-UE `redcap_sdt_fsm` state in:
  - `openair2/LAYER2/NR_MAC_gNB/nr_mac_gNB.h`
- Initialized the per-UE FSM at UE creation and refreshed it with gNB-side `redcap_inactive_allowed` when the UE enters the connected list in:
  - `openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_primitives.c`
- Wired the live scheduler path in:
  - `openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_ulsch.c`
  - new grant path now expands to `[UL_DATA_ARRIVAL -> SELECT_PATH -> UL_GRANT_READY]`
  - post-reception path now closes the burst with `[UL_BURST_COMPLETE]` only when the scheduler view has no pending UL bytes
  - accepted transitions are appended to runtime file `nrMAC_redcap_sdt.log` by default, or to the path pointed to `OAI_REDCAP_SDT_LOG`
- Extended the unit test in:
  - `openair2/LAYER2/NR_MAC_gNB/tests/test_nr_redcap_sdt_fsm.cpp`
  - added coverage for scheduler-facing helper expansion and burst completion gating

## 3GPP Spec Clauses Referenced
- TS 38.321 [⚠ Needs Verification for exact subclause] — SDT `[MsgA / Msg3]` path selection and `[UL burst complete]` behavior are the MAC-level basis for the FSM transitions
- TS 38.306 Section 4.2.21.1 — RedCap reduced-capability profile remains the project context for lightweight UL burst handling
- `spec/redcap_3gpp/spec.md` — local project mapping for `[Early Indication]` and `[ncd-SSB-RedCapInitialBWP-SDT-r17]`

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| `ASAN_OPTIONS=detect_leaks=0 LSAN_OPTIONS=detect_leaks=0 cmake --build --preset tests --target nr-softmodem test_nr_redcap_sdt_fsm` | Pass | main build + SDT test target | Log: `test_log/build_logs/redcap_m4_scheduler_wiring_build_nolsan_2026-04-11_21-59-09.log` |
| `ASAN_OPTIONS=detect_leaks=0 LSAN_OPTIONS=detect_leaks=0 ctest --test-dir cmake_targets/ran_build/build_test -R test_nr_redcap_sdt_fsm --output-on-failure` | Pass | updated SDT FSM unit test | Log: `test_log/compiler_logs/redcap_m4_scheduler_wiring_ctest_2026-04-11_21-58-49.log` |
| `ASAN_OPTIONS=detect_leaks=0 LSAN_OPTIONS=detect_leaks=0 ctest --test-dir cmake_targets/ran_build/build_test -R 'test_nr_redcap_sdt_fsm|test_nr_redcap_bwp|test_nr_ue_redcap_bwp' --output-on-failure` | Pass | M4 helper + M3/M5 BWP regression spot-check | Log: `test_log/compiler_logs/redcap_m4_scheduler_wiring_regression_final_2026-04-11_22-00-27.log` |

## Known Issues / Blockers
- Default sanitized builds in this sandbox can still fail in the repo’s `check_vcd` step unless `[LSAN leak detection]` is disabled; this is an environment constraint, not a compiler error from the new SDT wiring
- The new runtime log file path is available in the scheduler code, but live Docker-based `[MsgA / Msg3]` evidence collection remains blocked in the current sandbox
- `[TS 38.321]` exact SDT clause numbers still need confirmation before final documentation close-out

## Next Step
- Continue the next non-Docker code gap by revisiting `[Milestone 1]` `[HD-FDD switching gap]` enforcement in the UL scheduler / `minRXTXTIME` path, with a spec cross-check against `spec/redcap_3gpp/spec.md` and TS 38.306 / 38.101-1 first
