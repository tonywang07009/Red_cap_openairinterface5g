# M4B Low-Power Boundary Report

## 1. Technical Background
- [Connected DRX] gates UE PDCCH monitoring in [RRC_CONNECTED] by using active-time conditions such as [on-duration], [inactivity timer], and pending scheduling request.
- [eDRX] extends low-power paging behavior for [RRC_IDLE] / [RRC_INACTIVE], but the current RFsim evidence only proves SIB1 flag decode/logging.
- [PSM] depends on NAS timers. The current UE path decodes/tracks [T3324] and [T3512], but no CN-driven UE sleep/quiesce behavior is claimed.

## 2. Key C Functions / Data Structures
- `nr_ue_drx_is_active_slot()` / `nr_ue_drx_note_activity()` in `openair2/LAYER2/NR_MAC_UE/nr_ue_drx.c`.
- `configure_drx()` in `openair2/LAYER2/NR_MAC_UE/config_ue.c`.
- `nr_rrc_apply_sib1_edrx()` / `nr_rrc_edrx_allowed_for_state()` in `openair2/RRC/NR_UE/rrc_ue_lowpower.c`.
- `nr_nas_psm_update_timers()` / `nr_nas_psm_low_power_ready()` in `openair3/NAS/NR_UE/nr_nas_lowpower.c`.

## 3. Test Results Summary Table
| Test Item | Pass-Fail Status | Code Coverage | Modification Logs |
|-----------|------------------|---------------|-------------------|
| `ctest -R "test_nr_ue_drx|test_nr_rrc_lowpower|test_nr_nas_lowpower|nas_lib_test"` | PASS | DRX active-time helper, eDRX SIB1 flags, PSM/NAS timer hooks | `test_log/compiler_logs/ctest_m4b_lowpower_boundary_2026-05-07_13-24-38_lsanoff.log` |
| Case A RFsim log scan | PASS | eDRX/PSM log-level evidence | `test_log/runtime_artifacts/m3_casea_2026-05-07_13-15-07/` |
| Case B RFsim log scan | PASS | eDRX/PSM log-level evidence | `test_log/runtime_artifacts/m3_caseb_2026-05-07_13-10-12/` |
| Connected DRX runtime smoke | N/A | Current RFsim source-of-truth compose has no DRX-enabled runtime config | Boundary documented in M4B milestone file |

## 4. 3GPP Specification Mapping
- TS 38.321 Section 5.7 — [Connected DRX] active-time and PDCCH monitoring behavior.
- TS 38.331 Section 6.3.2 — [DRX-Config] / SIB1 low-power extension container context. Exact eDRX subsection: [Needs Verification].
- TS 38.304 — [eDRX] paging behavior for [RRC_IDLE] / [RRC_INACTIVE]. Exact clause: [Needs Verification].
- TS 24.501 Section 8.2.7.1.1 — [Registration Accept] optional IE table for [T3324] / [T3512]. [Needs Verification].
- TS 24.501 Section 5.5.1 — [T3324] active time and [T3512] periodic registration behavior for PSM. [Needs Verification].

## 5. Practice Exercises
- Basic: Explain why [Connected DRX] must not block [Random Access] before the UE reaches [RRC_CONNECTED].
- Applied: Given on-duration 4 slots, long cycle 20 slots, and offset 2, identify which slots in the first cycle are active.
- Advanced: Design a runtime scenario that can prove DRX active/inactive transitions without breaking UE attach or PDU session establishment.
