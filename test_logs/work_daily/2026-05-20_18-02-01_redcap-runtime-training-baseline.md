# Work Daily Log
## Session Metadata
- Date: 2026-05-20 18:02
- Agent Session ID: N/A
- Task Slug: redcap-runtime-training-baseline
- Project Path: agent_doc/Project_management/projects/redcap_mmtc_priority_execution_v1/project_plan.md
- Milestone File: milestones/M6_docs_automation.md
- Validation File: validation/test_matrix.md; validation/runtime_checklist.md
- Task ID: M6AB-T1

## Milestone & Sub-task Reference
- Milestone: M6 Docs Automation / Runtime Training Helper
- Sub-task: guided RedCap RFsim runtime menu baseline validation
- Status: COMPLETED

## What Was Done
- Verified `ci-scripts/redcap_runtime_menu.sh` option 1.
- Confirmed final compose gNB config mount:
  - source: `test_log/runtime_configs/gnb.redcap_mmtc_case-b_2026-05-02_12-35-01.yaml`
  - target: `/opt/oai-gnb/etc/gnb.yaml`
- Ran `ci-scripts/redcap_runtime_menu.sh` option 2 for single-sample baseline without iperf.
- Confirmed UE1 TUN interface `oaitun_ue1` with IPv4 `10.0.0.2/24`.
- Confirmed forward ping from UE1 to `10.0.0.1` passed with 10/10 packets received and 0% packet loss.
- Confirmed summary markers: `sample=1 running=1 attach=1 pdu=1 tun=1 forward_ping_ok=1 gnb_restart=0 failures=0`.

## 3GPP Spec Clauses Referenced
- TS 38.321 Section 5.1 — Random Access procedure relevance for UE attach path.
- TS 38.331 Section 5.3 — RRC connection control relevance for UE registration path [Needs Verification].
- TS 38.306 Section 4 — RedCap UE capability constraints [Needs Verification].

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| Menu option 1 mount check | PASS | Compose merge path | gNB config source matched expected Case B runtime config |
| Menu option 2 baseline | PASS | CN/gNB/UE1 runtime | Smoke validation completed |
| UE1 TUN check | PASS | UE user-plane interface | `oaitun_ue1` found with `10.0.0.2/24` |
| UE1 forward ping | PASS | UE1 to ext-dn path | 10 transmitted, 10 received, 0% packet loss |
| Source build | N/A | Bash/runtime helper only | No C/C++ source change |
| Unit test | N/A | Runtime validation only | No CTest target required |
| Container image rebuilt | N/A | No image or C/C++ source change | Not rebuilt |
| RFsim UE/gNB/CN runtime | PASS | Single UE baseline | `failures=0`, `gnb_restart=0` |

## Known Issues / Blockers
- Docker socket permission is required for runtime validation.
- This run validated only one sampled UE and did not run UDP uplink iperf.

## Next Step
- Run `ci-scripts/redcap_runtime_menu.sh` option 3 for UDP uplink iperf with the current default rate `85M`, then inspect option 5 for the latest UE1 iperf log.
