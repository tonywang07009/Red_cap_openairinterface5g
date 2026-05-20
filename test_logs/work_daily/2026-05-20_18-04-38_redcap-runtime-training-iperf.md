# Work Daily Log
## Session Metadata
- Date: 2026-05-20 18:04
- Agent Session ID: N/A
- Task Slug: redcap-runtime-training-iperf
- Project Path: agent_doc/Project_management/projects/redcap_mmtc_priority_execution_v1/project_plan.md
- Milestone File: milestones/M6_docs_automation.md
- Validation File: validation/test_matrix.md; validation/runtime_checklist.md
- Task ID: M6AB-T1

## Milestone & Sub-task Reference
- Milestone: M6 Docs Automation / Runtime Training Helper
- Sub-task: guided RedCap RFsim UDP uplink iperf validation
- Status: COMPLETED

## What Was Done
- Ran `ci-scripts/redcap_runtime_menu.sh` option 3.
- Validated UDP uplink iperf with current defaults:
  - UE sample: `1`
  - rate: `85M`
  - duration: `30s`
  - UDP mode: enabled
- Confirmed runtime summary markers: `sample=1 running=1 attach=1 pdu=1 tun=1 forward_ping_ok=1 iperf_ul_ok=1 iperf_ul_run=1 gnb_restart=0 failures=0`.
- Ran `ci-scripts/redcap_runtime_menu.sh` option 5.
- Reviewed latest UE1 iperf uplink log: `test_log/compiler_logs/mmtc_smoke_2026-05-20_18-02-35_ue1_iperf3_ul.log`.

## 3GPP Spec Clauses Referenced
- TS 38.214 — PUSCH throughput path and uplink scheduling relevance [Needs Verification].
- TS 38.321 Section 5.4 — UL-SCH data transfer relevance [Needs Verification].
- TS 38.306 Section 4 — RedCap UE capability constraints [Needs Verification].

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| Menu option 3 UDP iperf | PASS | UE1 uplink user-plane throughput | `iperf_ul_ok=1`, `failures=0` |
| UE1 forward ping precheck | PASS | UE1 to ext-dn path | 10 transmitted, 10 received, 0% packet loss |
| UE1 UDP iperf sender | PASS | UE1 uplink sender | 304 MBytes, 85.0 Mbits/sec, 0/220125 loss |
| UE1 UDP iperf receiver | PASS | ext-dn receiver | 304 MBytes, 84.9 Mbits/sec, 0/220125 loss, jitter 0.182 ms |
| Source build | N/A | Bash/runtime helper only | No C/C++ source change |
| Unit test | N/A | Runtime validation only | No CTest target required |
| Container image rebuilt | N/A | No image or C/C++ source change | Not rebuilt |
| RFsim UE/gNB/CN runtime | PASS | Single UE baseline plus UDP UL iperf | `gnb_restart=0` |

## Known Issues / Blockers
- This run validates only one sampled UE.
- Higher UE count or custom rate should be validated separately before claiming mMTC scale behavior.

## Next Step
- For training, explain option 4 custom rate and demonstrate a conservative lower-rate run such as `50M` if needed.
- For project validation, scale from `MMTC_SAMPLE_UES=1` toward the planned staged UE counts in the M5/M6 validation matrix.
