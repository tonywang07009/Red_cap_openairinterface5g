# Work Daily Log
## Session Metadata
- Date: 2026-04-30 20:25
- Agent Session ID: N/A
- Task Slug: agents-md-scope-cleanup
- Project Path: agent_doc/Project_management/projects/redcap_mmtc_priority_execution_v1/project_plan.md

## Milestone & Sub-task Reference
- Milestone: Project workflow / agent instruction maintenance
- Sub-task: Clarify O-RAN scope, RFsim source of truth, spec paths, and logging rules in AGENTS.md
- Status: COMPLETED

## What Was Done
- Updated `AGENTS.md`.
- Marked commit/MR rules as reference-only unless explicitly requested.
- Unified local RedCap spec references to `spec/redcap_3gpp/`.
- Added `O-RAN Scope Definition`:
  - xApp/rApp/dApp SDK implementation is deferred until RedCap UE/gNB behavior passes the 3GPP-aligned validation flow.
  - Existing FlexRIC work before that point is limited to runtime checks and log inspection.
  - rApp/dApp work requires a separate explicit task plan.
- Added `RFsim RedCap Runtime Source of Truth`:
  - Use `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/` as the primary simulator runtime directory.
  - Use the compose file and directly mounted YAML/config files as the source of truth.
  - Do not edit unrelated simulator XML/YAML files just because they contain similar names.
  - Report unused XML/scenario files before removal and remove only after user confirmation.
- Made Gantt chart rules conditional on explicit Gantt/project-visualization requests.
- Relaxed mandatory rebuild wording from every edit to each atomic C/C++ patch group.
- Allowed `[unit test N/A]` when no meaningful unit test exists.
- Scoped RedCap PHY workflow to actual PHY-side work.
- Fixed work daily read path from `test_log/work_daily/` to `test_logs/work_daily/`.

## 3GPP Spec Clauses Referenced
- N/A — documentation/workflow update only.

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| Documentation diff review | PASS | `AGENTS.md` | Checked diff and searched for stale path/scope markers |
| Source build | N/A | No C/C++ changes | Documentation-only update |
| Unit test | N/A | No executable behavior changed | Documentation-only update |

## Known Issues / Blockers
- No files were removed.
- `Simluation_v2.md` still keeps its existing spelling because it appears to be the actual project file name.

## Next Step
- Continue RedCap RFsim Case B validation only after rebuilding local runtime images for the latest C patch.
