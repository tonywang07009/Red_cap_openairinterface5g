# M4B Low-Power Unit Test Report

## 1. Technical Background
M4B introduces low-power behavior for RedCap/mMTC UE operation. Connected DRX reduces PDCCH monitoring in RRC_CONNECTED by limiting monitoring to active time. eDRX extends low-power behavior for RRC_IDLE/RRC_INACTIVE paging behavior when SIB1 permits it. PSM is controlled primarily by NAS timers: T3324 represents active time after data activity, while T3512 is the 5GS periodic registration update timer and corresponds conceptually to LTE/EPS T3412 periodic TAU behavior. This implementation adds testable state hooks and parser/storage support before deeper paging-window and NAS timer expiry integration.

## 2. Key C Functions / Data Structures
- `nr_drx_config_t` in `openair2/LAYER2/NR_MAC_UE/mac_defs.h`
- `nr_ue_drx_is_active_slot()` / `nr_ue_drx_note_activity()` in `openair2/LAYER2/NR_MAC_UE/nr_ue_drx.c`
- `nr_rrc_apply_sib1_edrx()` / `nr_rrc_edrx_allowed_for_state()` in `openair2/RRC/NR_UE/rrc_ue_lowpower.c`
- `nr_nas_psm_update_timers()` / `nr_nas_psm_low_power_ready()` in `openair3/NAS/NR_UE/nr_nas_lowpower.c`

## 3. Test Results Summary Table
| Test Item | Pass-Fail Status | Code Coverage | Modification Logs |
|-----------|------------------|---------------|-------------------|
| `ctest -R test_nr_ue_drx` | Pass | DRX active window, pending SR, inactivity extension | `test_log/compiler_logs/ctest_test_nr_ue_drx_2026-04-28_18-46-03_m4b-drx-gating_escalated.log` |
| `ctest -R test_nr_rrc_lowpower` | Pass | eDRX SIB1 v1700 decode/storage and state gating | `test_log/compiler_logs/ctest_test_nr_rrc_lowpower_2026-04-28_18-52-05_m4b-edrx_escalated.log` |
| `ctest -R test_nr_nas_lowpower` | Pass | PSM T3324/T3512 hook state and low-power readiness | `test_log/compiler_logs/ctest_test_nr_nas_lowpower_2026-04-28_18-59-53_m4b-psm_escalated.log` |
| 2-UE RFsim host validation | Fail | Runtime UE/gNB/CN reaction smoke | UE1 failed to obtain `oaitun_ue1`; see `test_log/report/redcap_runtime_host_summary_disabled_2026-04-28_19-02-01.md` |

## 4. 3GPP Specification Mapping
- TS 38.321 Section 5.7 — DRX active time and PDCCH monitoring behavior.
- TS 38.331 Section 6.3.2 — `DRX-Config` and SIB1 v1700 low-power extension containers.
- TS 24.501 Section 8.2.7 — Registration Accept carries 5GS registration parameters. ⚠ Needs Verification for exact T3324/T3512 IE clause.
- TS 24.501 Section 5.3.5 — 5GS registration management and periodic registration behavior. ⚠ Needs Verification for exact PSM subclause.

## 5. Practice Exercises
- Basic: Explain why DRX should gate PDCCH monitoring but must not block Random Access.
- Applied: Given a 20-slot DRX long cycle and 4-slot on-duration, identify active slots when the offset is 2.
- Advanced: Design a clean integration path from decoded NAS T3324/T3512 values to UE RFsim sleep/quiesce behavior without breaking CN paging reachability.
