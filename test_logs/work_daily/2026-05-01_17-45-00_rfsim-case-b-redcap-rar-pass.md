# Work Daily Log
## Session Metadata
- Date: 2026-05-01 17:45
- Agent Session ID: N/A
- Task Slug: rfsim-case-b-redcap-rar-pass
- Project Path: agent_doc/Project_management/projects/redcap_mmtc_priority_execution_v1/project_plan.md

## Milestone & Sub-task Reference
- Milestone: M3-T2 RedCap RA / Msg2 runtime validation
- Sub-task: RFsim Case B runtime validation after UE Msg2 BWP fix
- Status: [COMPLETED]

## What Was Done
- Rebuilt local OAI Docker images from workspace using `ci-scripts/redcap_rebuild_local_oai_images.sh`.
- Ran RFsim Case B from `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/` via `redcap_runtime_host_validation.sh`.
- Runtime used local `oai-gnb:latest` and `oai-nr-ue:latest`, with `REDCAP_E2_AGENT_MODE=disabled` and `REDCAP_EXPECTED_MODE=case-b`.
- Verified UE2 RedCap moved from previous `[all-zero PDU / LDPC decode failed]` blocker to successful `[RAR]`, attach, ping, and UL iperf.

## 3GPP Spec Clauses Referenced
- TS 38.214 Section 5.1.2.2.2 — DCI 1_0 downlink resource allocation type 1 / RIV domain alignment.
- TS 38.321 Section 5.1.4 — Random Access Response reception.
- TS 38.331 Section 5.2.2.4.2 — SIB1 acquisition and serving cell common configuration context.
- TS 38.306 Clause 4.2.21.1 — RedCap capability context cited by runtime summary.

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| Local OAI Docker image rebuild | PASS | gNB/nrUE runtime packaging | `oai-gnb:latest` and `oai-nr-ue:latest` rebuilt from workspace. |
| RFsim Case B runtime | PASS | End-to-end RedCap UE2 runtime | Scenario passed. UE2 IP `10.0.0.3`. |
| UE2 RAR reception | PASS | RA Msg2 decode path | UE2 log shows `[RedCap RA][UE Msg2 PDSCH]`, `Got RAPID RAR`, and `Found RAR`. |
| UE2 LDPC/all-zero regression | PASS | Previous blocker check | No `RAR reception failed`, no `Received a RAR-Msg2 but LDPC decode failed`, no `received all 0 pdu`. |
| Ping both UEs | PASS | User plane | UE2 packet loss 0%, UE1 packet loss 0%. |
| UE2 UL iperf 50 Mbps UDP | PASS | User plane throughput | Receiver 50.00 Mbps, packet loss 0%. |
| UE2 UL iperf 20 Mbps UDP | PASS | User plane throughput | Receiver 20.00 Mbps, packet loss 0%. |

## Known Issues / Blockers
- E2/xApp UL PRB control was intentionally skipped because this run used `REDCAP_E2_AGENT_MODE=disabled`; this is expected for the current RedCap RA/runtime health-check.
- No dedicated UE DCI extraction unit test exists yet for `[RA-RNTI + common SS + nonzero CORESET]`.

## Next Step
- Update `[M3-T2]` project status and test report to PASS, referencing the runtime summary and log artifacts.
