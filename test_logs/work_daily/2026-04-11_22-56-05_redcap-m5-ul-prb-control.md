# Work Daily Log
## Session Metadata
- Date: 2026-04-11 22:56
- Agent Session ID: N/A
- Task Slug: redcap-m5-ul-prb-control

## Milestone & Sub-task Reference
- Milestone: Milestone 5: Integration & UL Throughput Targets
- Sub-task: E2/xApp RedCap UL PRB control plumbing
- Status: COMPLETED

## What Was Done
- Added a new RC control action in `openair2/E2AP/RAN_FUNCTION/O-RAN/ran_func_rc.c` for `RedCap UL PRB allocation cap`.
- Added `openair2/E2AP/RAN_FUNCTION/O-RAN/ran_func_rc_redcap.[ch]` to parse a minimal control message carrying:
  - `UE RNTI`
  - `Max UL PRB cap`
- Wired the new RC control path to the live gNB MAC scheduler by updating `NR_UE_sched_ctrl_t` with a per-UE runtime `redcap_ul_prb_cap`.
- Applied the cap in `openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_ulsch.c` so new UL grants are clamped before `nr_find_nb_rb()` sizes the PUSCH allocation.
- Added inline runtime-cap helpers in `openair2/LAYER2/NR_MAC_gNB/nr_mac_redcap.h` for cap sanitization and scheduler-side clamping.
- Added unit coverage:
  - `openair2/LAYER2/NR_MAC_gNB/tests/test_nr_redcap_coreset0.cpp` for cap sanitization/clamping helpers.
  - `openair2/LAYER2/NR_MAC_gNB/tests/test_nr_redcap_rc_ctrl.cpp` for RC message parsing and range rejection.
- Registered the new parser helper in `openair2/E2AP/RAN_FUNCTION/CMakeLists.txt` and the new test in `openair2/LAYER2/NR_MAC_gNB/tests/CMakeLists.txt`.

## 3GPP Spec Clauses Referenced
- TS 38.306 Section 4.2.21.1 — RedCap reduced-bandwidth operation sets the upper envelope that the runtime UL PRB cap is allowed to tighten.
- TS 38.331 Section 5.2.2.4.2 — RedCap common configuration anchors the initial RedCap BWP context that the scheduler remains bound to while the xApp applies a stricter runtime UL PRB limit.
- O-RAN E2SM-RC control-action clause number for this local RedCap action id mapping: ⚠ Needs Verification.

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| `ASAN_OPTIONS=detect_leaks=0 LSAN_OPTIONS=detect_leaks=0 cmake --build --preset tests --target nr-softmodem test_nr_redcap_coreset0 test_nr_redcap_bwp test_nr_redcap_sdt_fsm test_nr_redcap_rc_ctrl test_nr_rrc_redcap` | Pass | `ran_func_rc.c`, `ran_func_rc_redcap.c`, `nr_mac_redcap.h`, `gNB_scheduler_ulsch.c`, `nr_mac_gNB.h` | Log: `test_log/build_logs/redcap_m5_ul_prb_ctrl_build_retry_2026-04-11_22-53-43.log` |
| `test_nr_redcap_rc_ctrl` | Pass | Valid RC parse, missing-param rejection, range rejection | Confirms the new xApp-side control payload can be parsed locally |
| `test_nr_redcap_coreset0` | Pass | UL PRB cap sanitize/clamp helper paths | Confirms scheduler helper behavior for disable/clamp cases |
| `ctest -R 'test_nr_redcap_coreset0|test_nr_redcap_bwp|test_nr_redcap_sdt_fsm|test_nr_redcap_rc_ctrl|test_nr_rrc_redcap|test_nr_ue_redcap_bwp'` | Pass | New RC parser + scheduler helper + adjacent RedCap regression suite | Log: `test_log/compiler_logs/redcap_m5_ul_prb_ctrl_regression_2026-04-11_22-53-43.log` |

## Known Issues / Blockers
- The Docker/FlexRIC runtime path is still unavailable in the sandbox, so this unit proves local RC parsing and scheduler enforcement but not live over-the-air xApp control.
- The current RC control action uses `UE RNTI` inside the control message rather than reconstructing the MAC UE from the E2SM UE ID header.
- Retransmission sizing is intentionally left unchanged; the runtime cap applies to new UL grants and does not override fixed HARQ retransmission TBS requirements.

## Next Step
- Return to Milestone 5 runtime evidence: validate the new RC control path through the existing FlexRIC compose once Docker access is available, then collect UL throughput evidence without using `iperf3 -R`.
