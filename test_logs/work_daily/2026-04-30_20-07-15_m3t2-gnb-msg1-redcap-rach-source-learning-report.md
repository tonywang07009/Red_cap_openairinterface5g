# Educational Learning Report

## 1. Technical Background
- [RedCap UE2] is configured by the runtime compose path under `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap`.
- In that compose file, [UE2] mounts `../../conf_files/nrue_recap/nrue2.uicc.yaml`.
- The UE config enables [RedCap-r17], so UE2 applies [SIB1 RedCap initial UL BWP] and selects [RedCap feature-combination preambles].
- The gNB must classify Msg1 using the same RedCap RACH view; otherwise Msg2 remains on baseline CORESET/BWP while UE2 monitors the RedCap RA search space.
- The fix makes gNB Msg1 marking read [initialUplinkBWP_RedCap_r17] RACH config when available.

## 2. Key C Functions / Data Structures Utilized
- [nr_initiate_ra_proc()] — gNB entry point for creating the RA context after PRACH detection.
- [get_redcap_msg1_rach_config()] — new helper returning RedCap initial UL BWP RACH config.
- [nr_redcap_is_msg1_preamble()] — checks whether a preamble index falls inside the RedCap feature-combination preamble partition.
- [NR_RA_t.is_redcap_msg1] — RA context flag used by Msg2 scheduler gate.
- [NR_BWP_UplinkCommon_t] — carries `initialUplinkBWP_RedCap_r17` RACH configuration.

## 3. Test Results Summary Table
| Test Item | Status | Evidence |
|-----------|--------|----------|
| gNB source build | PASS | `nr-softmodem` rebuilt successfully |
| RedCap helper unit tests | PASS | `test_nr_redcap_bwp` 15/15 passed |
| Runtime validation | PENDING | Docker images need rebuild before RFsim rerun |

## 4. 3GPP Specification Mapping
- TS 38.331 Section 5.2.2.4.2 — [SIB1] carries serving cell common information used by the UE before access.
- TS 38.331 Section 6.3.2 — [RACH-ConfigCommon] includes Random Access common configuration and RedCap-related extensions. [⚠ Needs Verification]
- TS 38.321 Section 5.1 — [Random Access] procedure uses Msg1/Msg2 flow and RA-RNTI monitoring.

## 5. Practice Exercises
- Basic: Explain why [UE2] and [gNB] must use the same RACH preamble partition for Msg1 classification.
- Applied: Locate where `initialUplinkBWP_RedCap_r17` is cloned and where its RACH config is consumed by gNB Msg1 marking.
- Advanced: Design one runtime log assertion that proves `ra->is_redcap_msg1` is true before `configure_redcap_msg2_bwp()` executes.
