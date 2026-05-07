# Educational Learning Report

## 1. Technical Background
- This validation checks the non-Docker unit baseline for the RedCap/mMTC milestones before returning to large RFsim scaling.
- [M1] protects RedCap PHY constraints, including FR1 PRB caps, UE antenna limits, and HD-FDD assumptions.
- [M2] protects RedCap SIB1 encode/decode and barring behavior.
- [M3] protects RedCap BWP / CORESET#0 / RA-RNTI BWP-domain helper behavior.
- [M4-B] protects low-power helper logic for DRX, eDRX, and PSM.
- The only code change was a test expectation alignment: the gNB common carrier grid may exceed 20 MHz when the RedCap-specific BWP and UE paths still enforce the RedCap bandwidth limit.

## 2. Key C Functions / Data Structures Utilized
- `nr_validate_redcap_gnb_frame_parms()` — gNB-side RedCap frame-parameter validation.
- `nr_validate_redcap_ue_frame_parms()` — UE-side RedCap frame-parameter validation.
- `NR_DL_FRAME_PARMS` — PHY frame-parameter carrier, PRB, and antenna context.
- `nr_rrc_apply_sib1_edrx()` — UE RRC eDRX SIB1 low-power flag application.
- `nr_nas_psm_update_timers()` — UE NAS PSM timer-state update helper.
- `test_nr_redcap_bwp` / `test_nr_redcap_coreset0` — RedCap BWP and CORESET helper unit targets.

## 3. Test Results Summary Table
| Test Item | Result | Coverage | Notes |
|-----------|--------|----------|-------|
| test_nr_frame_params | PASS | M1 PHY RedCap PRB / antenna checks | Updated stale gNB common-grid expectation. |
| test_nr_redcap_coreset0 | PASS | M1/M3 HD-FDD and CORESET parser helper path | CTest passed. |
| test_nr_redcap_bwp | PASS | M3 gNB RedCap BWP / RACH helper path | CTest passed. |
| test_nr_ue_redcap_bwp | PASS | M3 UE RA-RNTI BWP-domain path | CTest passed. |
| test_nr_rrc_redcap | PASS | M2 SIB1 RedCap encode/decode / barring | CTest passed. |
| test_nr_ue_drx | PASS | M4B connected DRX helper path | CTest passed. |
| test_nr_rrc_lowpower | PASS | M4B eDRX SIB1 helper path | CTest passed. |
| test_nr_nas_lowpower | PASS | M4B PSM NAS timer helper path | CTest passed. |

## 4. 3GPP Specification Mapping
- TS 38.101-1 Section 5.3 — FR1 channel bandwidth / PRB limits. [Needs Verification]
- TS 38.306 Section 4 — RedCap UE reduced capability assumptions. [Needs Verification]
- TS 38.331 Section 6.3.1 / 6.3.2 — SIB1 and RedCap-related RRC fields. [Needs Verification]
- TS 38.213 Section 13 — CORESET#0 / Type0 CSS context. [Needs Verification]
- TS 38.321 Section 5.7 — Connected DRX.
- TS 24.501 PSM timer behavior — exact clause pending. [Needs Verification]

## 5. Practice Exercises
- [Basic] Why should the UE RedCap frame-parameter validation still reject `N_RB_DL=52` at 30 kHz SCS?
- [Applied] In the current design, why can the gNB common serving-cell carrier be wider than the RedCap-specific BWP?
- [Advanced] Design a unit test that verifies Case B Msg2 uses the same BWP-domain assumption on both gNB DCI allocation and UE RA-RNTI monitoring.
