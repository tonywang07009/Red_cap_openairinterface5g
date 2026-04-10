# Work Daily Log
## Session Metadata
- Date: 2026-04-10 16:57
- Agent Session ID: N/A
- Task Slug: redcap-runtime-ue-id-fix

## Milestone & Sub-task Reference
- Milestone: Milestone 3 / Milestone 5
- Sub-task: Fix RedCap runtime UE attach orchestration IDs for FlexRIC RF simulator scenario
- Status: [COMPLETED]

## What Was Done
- Added dedicated [RedCap UE] runtime targets in `ci-scripts/ci_infra.yaml` for `rfsim5g-oai-nr-ue1_redcap` and `rfsim5g-oai-nr-ue2_redcap`.
- Updated `ci-scripts/xml_files/container_5g_flexric_rfsim_redcap.xml` so [Attach_UE], [Ping], [Iperf], and [Detach_UE] steps use the new RedCap-specific UE IDs.
- Confirmed from the latest host log that [Deploy_Object 000004] already passed and the first runtime blocker was the wrong container name lookup in [Attach_UE 333331].
- Confirmed the RedCap compose file still parses with `docker compose ... config` after the ID mapping changes.

## 3GPP Spec Clauses Referenced
- TS 38.331 Section 5.6.1.3 — runtime attach evidence remains the current validation gate for RedCap UE capability handling.
- TS 38.331 Section 5.2.2.4.2 — runtime scenario still targets RedCap SIB1 / initial BWP delivery checks.
- TS 38.306 Section 4.2.21.1 — runtime scenario remains tied to FR1 RedCap reduced-bandwidth validation.

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| `docker compose -f ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/docker-compose.yml config` | Pass | compose syntax | RedCap runtime compose still resolves after UE ID fix |
| `rg -n "rfsim5g_redcap_ue1|rfsim5g_redcap_ue2" ci-scripts/ci_infra.yaml ci-scripts/xml_files/container_5g_flexric_rfsim_redcap.xml` | Pass | reference consistency | XML runtime IDs now resolve to ci_infra targets |
| Host log analysis of `test_log/compiler_logs/redcap_runtime_host_case-a_2026-04-10_13-29-28.log` | Pass | blocker isolation | Confirmed first failing step was wrong UE container lookup, not UE deployment |

## Known Issues / Blockers
- The archived host log still reported `[NR-UE could NOT synch!]` and `[UE ended with a Segmentation Fault!]` for both UE logs after undeploy. [⚠ Needs Verification]
- The current scenario still contains a DL iperf case with `-R`, while project plan notes say RedCap throughput validation should target UL only. [⚠ Needs Verification]
- Docker runtime re-test is still required on the host to confirm whether fixing the UE IDs exposes a remaining [UE sync / radio config] issue.

## Next Step
- Re-run `ci-scripts/redcap_runtime_case_matrix.sh` on the Docker-capable host and inspect whether [333331] / [333332] now reach real UE attach before analyzing any remaining [sync / segmentation fault] evidence.
