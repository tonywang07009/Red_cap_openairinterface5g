# Work Daily Log
## Session Metadata
- Date: 2026-04-13 19:30
- Agent Session ID: N/A
- Task Slug: redcap-m5-prepare-ue-containers

## Milestone & Sub-task Reference
- Milestone: Milestone 5 runtime validation
- Sub-task: Convert UE deploy steps to create-but-not-start containers before Attach_UE
- Status: [COMPLETED]

## What Was Done
- Updated `ci-scripts/xml_files/container_5g_flexric_rfsim_redcap.xml` `[000004]` from `[Deploy_Object]` to `[Custom_Command]` using `docker compose ... create oai-nr-ue1`.
- Updated `ci-scripts/xml_files/container_5g_flexric_rfsim_redcap.xml` `[000005]` from `[Deploy_Object]` to `[Custom_Command]` using `docker compose ... create oai-nr-ue2`.
- Preserved the earlier `[000004 -> 333331 -> 302001 -> 000005 -> 333332]` ordering so `[UE1 normal]` is prepared and attached before `[UE2 RedCap]`.
- Re-validated XML parsing and patch formatting after the scenario change.
- Cross-checked `ci-scripts/cls_containerize.py` and `ci-scripts/cls_module.py` to confirm `[Deploy_Object]` starts containers immediately while `[Attach_UE]` only does `docker start`.

## 3GPP Spec Clauses Referenced
- TS 38.331 Section 5.2.2.4.2 — runtime RedCap evidence must be attributed to the intended UE sequence.
- TS 38.306 Section 4.2.21.1 — RedCap capability validation is meaningful only when the correct UE instance is attached and observed.

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| XML parse for `container_5g_flexric_rfsim_redcap.xml` | Pass | N/A | `ElementTree.parse()` succeeded after converting `[000004]/[000005]` |
| `git diff --check` on `container_5g_flexric_rfsim_redcap.xml` | Pass | N/A | No whitespace / patch formatting issues |
| Host runtime log `redcap_runtime_host_disabled_2026-04-13_19-14-06.log` | Fail | Scenario-level | Historical evidence before this patch still shows `[020005]` KO on `UE2` |

## Known Issues / Blockers
- `[020005]` remains the forward blocker until a fresh host rerun validates the new create-before-attach sequencing.
- ⚠ Needs Verification: if `UE2` still shows `100%` packet loss after this patch, the remaining issue is likely standalone `UE2` user-plane connectivity rather than scenario ordering.

## Next Step
- Run a fresh host validation and confirm `[000004]/[000005]` now only prepare the UE containers while `[333331]/[333332]` perform the actual starts.
