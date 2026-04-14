# Work Daily Log
## Session Metadata
- Date: 2026-04-13 19:22
- Agent Session ID: N/A
- Task Slug: redcap-m5-split-ue-deploy-order

## Milestone & Sub-task Reference
- Milestone: Milestone 5 runtime validation
- Sub-task: Split UE deployment to enforce UE1-normal then UE2-RedCap attach order
- Status: [COMPLETED]

## What Was Done
- Updated `ci-scripts/xml_files/container_5g_flexric_rfsim_redcap.xml` [TestCaseRequestedList] to insert `[000005]` between `[302001]` and `[333332]`.
- Changed `[000004]` from deploying `oai-nr-ue1 oai-nr-ue2` to deploying only `oai-nr-ue1`.
- Added new `[000005]` [Deploy_Object] entry to deploy `oai-nr-ue2` after `[302001]`.
- Re-validated XML parsing after the scenario sequencing change.
- Re-ran diff hygiene checks on the touched CI files.

## 3GPP Spec Clauses Referenced
- TS 38.331 Section 5.2.2.4.2 — [RedCap] UE capability / RRC configuration evidence must map to the intended UE instance.
- TS 38.306 Section 4.2.21.1 — [RedCap] capability handling must be attributed to the correct UE in runtime validation.

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| XML parse for `container_5g_flexric_rfsim_redcap.xml` | Pass | N/A | `ElementTree.parse()` succeeded after adding `[000005]` |
| `git diff --check` on touched CI files | Pass | N/A | No whitespace / patch formatting issues |
| Host runtime log `redcap_runtime_host_disabled_2026-04-13_19-14-06.log` | Fail | Scenario-level | `[020005]` still failed with `UE2` packet loss `100%` |

## Known Issues / Blockers
- `[020005]` remains the only forward blocker in [REDCAP_E2_AGENT_MODE=disabled] host validation.
- ⚠ Needs Verification: split deployment must be confirmed by a new host rerun before concluding whether `UE2` user-plane failure is scenario-order related or a deeper runtime issue.

## Next Step
- Run a fresh host validation and confirm that `UE2` is no longer started during `[000004]`; if `[020005]` still fails, continue with standalone `UE2` user-plane root-cause analysis.
