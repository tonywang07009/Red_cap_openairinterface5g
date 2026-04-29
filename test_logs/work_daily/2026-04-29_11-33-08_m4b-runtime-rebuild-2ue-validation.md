# Work Daily Log
## Session Metadata
- Date: 2026-04-29 11:33
- Agent Session ID: N/A
- Task Slug: m4b-runtime-rebuild-2ue-validation
- Project Path: agent_doc/Project_management/projects/redcap_mmtc_priority_execution_v1/project_plan.md

## Milestone & Sub-task Reference
- Milestone: M4B / DRX / eDRX / PSM low-power mMTC behavior
- Sub-task: Rebuild local OAI images and rerun 2-UE RFsim host validation
- Status: COMPLETED

## What Was Done
- Rebuilt local OAI images so runtime included the M4B C patch.
- Ran 2-UE RFsim host validation once; first run failed because UE1 was configured with a RedCap config while the scenario expected UE1 non-RedCap.
- Updated `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/docker-compose.yml` so UE1 defaults to `conf_files/nrue/nrue1.uicc.yaml` and UE2 remains RedCap.
- Reran 2-UE RFsim host validation successfully.

## 3GPP Spec Clauses Referenced
- TS 38.306 Section 4.2.21.1 - RedCap UE radio capability signaling relevance.
- TS 38.331 Section 5.2.2.4.2 - SIB1 acquisition and system information behavior.
- TS 38.331 Section 5.6.1.3 - UE capability transfer relevance for RedCap capability handling.
- TS 24.501 Section 5.5.1 - NAS registration timers used for PSM behavior.

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| Local OAI image rebuild | PASS | `ran-build`, `oai-gnb`, `oai-nr-ue` | Log: `test_log/build_logs/rebuild_local_oai_images_2026-04-29_11-17-28_m4b.log` |
| 2-UE RFsim host validation first run | FAIL | UE1 attach succeeded; UE2 skipped | UE1 was incorrectly RedCap; summary: `test_log/report/redcap_runtime_host_summary_disabled_2026-04-29_11-21-24.md` |
| 2-UE RFsim host validation retry | PASS | UE1 attach/PDU, UE2 attach/PDU, SIB1 RedCap BWP, ping, UE2 iperf | Summary: `test_log/report/redcap_runtime_host_summary_disabled_2026-04-29_11-28-37.md` |
| Ping both UEs | PASS | UE1 `10.0.0.2`, UE2 `10.0.0.3` | 0% packet loss for both UEs |
| UE2 UL iperf 50 Mbps UDP | PASS | RedCap UE2 user-plane throughput | Receiver 50.00 Mbps, packet loss 0% |
| UE2 UL iperf 20 Mbps UDP | PASS | RedCap UE2 user-plane throughput | Receiver 20.00 Mbps, packet loss 0% |

## Known Issues / Blockers
- [E2_AGENT_MODE=disabled] runtime path intentionally skips live UL PRB control; enabled-mode E2 validation remains separate.
- Existing dirty submodules/directories `cmake_targets/swig` and `openair2/E2AP/flexric` were left untouched.

## Next Step
- Continue with the next planned mMTC runtime or E2-enabled validation task after reviewing the M4B patch set.
