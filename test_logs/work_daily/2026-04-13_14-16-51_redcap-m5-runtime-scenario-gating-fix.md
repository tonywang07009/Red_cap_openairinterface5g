# Work Daily Log
## Session Metadata
- Date: 2026-04-13 14:16
- Agent Session ID: N/A
- Task Slug: redcap-m5-runtime-scenario-gating-fix

## Milestone & Sub-task Reference
- Milestone: Milestone 5: Integration & UL Throughput Targets
- Sub-task: Fix RedCap runtime scenario gating for `[302001]` and make `[302005] / [302006]` mode-aware under `[REDCAP_E2_AGENT_MODE=disabled]`
- Status: [COMPLETED]

## What Was Done
- Updated `ci-scripts/xml_files/container_5g_flexric_rfsim_redcap.xml` so `[302001]` now verifies `[UE1 non-RedCap]` from `rfsim5g-oai-nr-ue1_redcap` logs instead of counting RedCap markers in the shared gNB log after both UEs are already deployed.
- Added disabled-mode guards to `[302005]` and `[302006]` so the `[disabled]` host health-check no longer hard-fails on E2/xApp RC control steps that are intentionally unavailable without a registered E2 node.
- Updated `ci-scripts/redcap_runtime_summary.py` to detect `[E2 Agent Mode]`, mark `[302005] / [302006]` as `[N/A]` in `[disabled]` mode, and print explicit `[xApp]` / `[nearRT-RIC]` zero-node evidence in the summary.
- Replayed the new summary logic against the latest archived disabled-mode run and confirmed the report now distinguishes `[scenario gating failure]` from `[expected disabled-mode E2 behavior]`.

## 3GPP Spec Clauses Referenced
- TS 38.331 Section 5.2.2.4.2 — RedCap-specific initial BWP signaling remains the runtime evidence used to distinguish normal UE1 behavior from RedCap UE2 behavior.
- TS 38.306 Section 4.2.21.1 — FR1 RedCap bandwidth constraints remain part of the same Milestone 5 runtime evidence path that the scenario gating now allows to progress.
- TS 38.331 Section 5.6.1.3 — UE capability / configuration exchange remains the attach-stage evidence path that is being validated by the revised CI checks.

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| `python3 -m py_compile ci-scripts/redcap_runtime_summary.py` | Pass | Syntax | Summary script parses after E2-mode-aware reporting changes |
| `python3 -c 'import xml.etree.ElementTree as ET; ET.parse("ci-scripts/xml_files/container_5g_flexric_rfsim_redcap.xml")'` | Pass | XML validity | RedCap runtime scenario XML remains parseable after test command updates |
| `git diff --check -- ci-scripts/xml_files/container_5g_flexric_rfsim_redcap.xml ci-scripts/redcap_runtime_summary.py` | Pass | Diff hygiene | No whitespace or patch formatting issues |
| `grep -Ec 'Built UE NR capability from nrue_recap YAML|nrue_recap RedCap config|Applying SIB1 RedCap initial (DL|UL) BWP' ...ue1.logs` | Pass | Archived runtime evidence | UE1 archived log returns `0`, matching `[302001]` intended non-RedCap semantics |
| `grep -Ec 'Built UE NR capability from nrue_recap YAML|nrue_recap RedCap config|Applying SIB1 RedCap initial (DL|UL) BWP' ...ue2.logs` | Pass | Archived runtime evidence | UE2 archived log returns `7`, confirming the new `[302001]` condition discriminates UE1 from UE2 |
| `python3 ci-scripts/redcap_runtime_summary.py --scenario ... --run-log ... --config ...` | Pass | Disabled-mode reporting | Summary now shows `[E2 Agent Mode]=disabled`, `[302005]/[302006]=N/A`, and the expected zero-node xApp/nearRT-RIC markers |

## Known Issues / Blockers
- A fresh host rerun is still required because `test_results.html` and the current scenario result were generated before this XML gating fix.
- `[enabled]` mode E2 RC control still needs a separate end-to-end rerun to prove `[302005] / [302006]` with a real registered E2 node.

## Next Step
- Re-run `REDCAP_USE_LOCAL_OAI_IMAGES=1 REDCAP_E2_AGENT_MODE=disabled bash ci-scripts/redcap_runtime_host_validation.sh` on the Docker-capable host and confirm the scenario progresses past `[302001]` into `[302002] / [302003] / [302004] / [020005] / [030001]`.
