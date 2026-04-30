# Work Daily Log
## Session Metadata
- Date: 2026-04-30 20:07
- Agent Session ID: N/A
- Task Slug: m3t2-gnb-msg1-redcap-rach-source
- Project Path: agent_doc/Project_management/projects/redcap_mmtc_priority_execution_v1/project_plan.md

## Milestone & Sub-task Reference
- Milestone: M3-T2 RedCap RA / CORESET#0 Case B runtime validation
- Sub-task: Fix gNB Msg1 RedCap marking to use RedCap initial UL BWP RACH config
- Status: COMPLETED

## What Was Done
- Confirmed the runtime UE2 path is `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/docker-compose.yml`.
- Confirmed UE2 mounts `../../conf_files/nrue_recap/nrue2.uicc.yaml`.
- Confirmed `nrue2.uicc.yaml` enables `nrue_recap.support_of_redcap_r17: 1`.
- Found the mismatch:
  - UE2 uses RedCap SIB1 initial UL BWP and chooses preambles 60-63.
  - gNB `nr_initiate_ra_proc()` was checking only baseline `scc->uplinkConfigCommon->initialUplinkBWP->rach_ConfigCommon`.
  - The RedCap feature-combination preamble partition is configured on `initialUplinkBWP_RedCap_r17`.
- Added `get_redcap_msg1_rach_config()` in `openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_RA.c`.
- Updated `nr_initiate_ra_proc()` to use the RedCap initial UL BWP RACH config for `nr_redcap_is_msg1_preamble()` when present.

## 3GPP Spec Clauses Referenced
- TS 38.331 Section 5.2.2.4.2 — SIB1 broadcast of serving cell common configuration and RedCap initial BWP relevance.
- TS 38.331 Section 6.3.2 — RACH-ConfigCommon and RedCap extension IE mapping. [⚠ Needs Verification]
- TS 38.321 Section 5.1 — Random Access procedure overview.

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| Source build: nr-softmodem | PASS | gNB MAC scheduler | `test_log/build_logs/build_nr-softmodem_2026-04-30_20-05-25_m3t2-msg1-redcap-rach-source-escalated.log` |
| Unit test build: test_nr_redcap_bwp | PASS | RedCap BWP/RACH helper unit test binary | `ninja: no work to do` |
| Unit test: test_nr_redcap_bwp | PASS | 15 RedCap BWP/RACH helper tests | `test_log/compiler_logs/ctest_test_nr_redcap_bwp_2026-04-30_20-05-45_m3t2-msg1-redcap-rach-source-asanoff.log` |
| RFsim runtime | NOT RUN | Case B end-to-end | Needs local image rebuild and rerun after this source patch |

## Known Issues / Blockers
- RFsim Case B runtime still needs rerun because the Docker images currently do not include this latest source patch.
- Previous runtime failure should be rechecked for `[RedCap RA][gNB Msg1]`, `[RedCap RA][gNB Msg2 gate]`, and `[RedCap RA][gNB Msg2 DCI] coreset_id 1`.

## Next Step
- Rebuild local OAI runtime images again, then rerun RFsim Case B validation from `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap`.
