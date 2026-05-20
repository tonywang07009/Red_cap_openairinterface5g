# Work Daily Log
## Session Metadata
- Date: 2026-05-20 17:53
- Agent Session ID: N/A
- Task Slug: redcap-runtime-menu-helper
- Project Path: agent_doc/Project_management/projects/redcap_mmtc_priority_execution_v1/project_plan.md
- Milestone File: milestones/M6_docs_automation.md
- Validation File: validation/test_matrix.md; validation/runtime_checklist.md
- Task ID: M6AB-T1

## Milestone & Sub-task Reference
- Milestone: M6 Docs Automation / Runtime Training Helper
- Sub-task: interactive RedCap RFsim runtime menu wrapper
- Status: COMPLETED

## What Was Done
- Added `ci-scripts/redcap_runtime_menu.sh`.
- The helper provides an interactive menu for:
  - checking the final gNB config mount,
  - running single-sample baseline validation without iperf,
  - running UDP uplink iperf with the current rate,
  - running UDP uplink iperf with a custom rate,
  - showing the latest UE1 iperf uplink log,
  - configuring gNB config path, CN compose path, sample UE list, iperf UE list, rate, and duration.
- Kept the existing `ci-scripts/redcap_mmtc_smoke_validation.sh` unchanged.
- Preserved the env-var driven runtime model instead of hardcoding the Case B config into the main compose file.

## 3GPP Spec Clauses Referenced
- TS 38.306 Section 4 — RedCap UE capability constraints [Needs Verification].
- TS 38.321 Section 5.1 — Random Access procedure.
- TS 38.214 — PUSCH / MCS / TBS throughput path exact clause [Needs Verification].

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| Bash syntax check | PASS | `ci-scripts/redcap_runtime_menu.sh` | `bash -n` returned success |
| Menu startup / quit smoke | PASS | interactive menu startup path | `printf 'q\n' | ci-scripts/redcap_runtime_menu.sh` exited cleanly |
| Source build | N/A | Bash helper only | No C/C++ source change |
| Unit test | N/A | Bash helper only | No CTest target required |
| Container image rebuilt | N/A | No image or C/C++ source change | Not rebuilt |
| RFsim UE/gNB/CN runtime | N/A | Helper creation only | Runtime not executed in this log |

## Known Issues / Blockers
- The helper still depends on Docker permission and the existing CN/gNB/UE runtime environment.
- The mount check option reports the expected source/target but does not automatically fail the menu if the source differs; the user should compare the printed lines.

## Next Step
- Use `ci-scripts/redcap_runtime_menu.sh` option 1 to confirm the gNB Case B config mount, then option 2 for baseline or option 3/4 for UDP uplink throughput.
