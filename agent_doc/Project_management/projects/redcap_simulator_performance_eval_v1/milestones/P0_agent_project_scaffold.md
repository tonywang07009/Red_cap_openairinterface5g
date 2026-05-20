# P0 Agent Project Scaffold

## Milestone Metadata
- Milestone: P0
- Task IDs: P0-T1, P0-T2
- Project Path: `agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/project_plan.md`
- Status: [COMPLETED]

## Purpose
- Define the [AGENTS.md] rules needed to make future work token-efficient.
- Create stable paths for [paper evidence], [Taguchi DOE skill material], [validation], and [plotting outputs].

## Execution Contract
| Task ID | Task Name | Output | Status |
|---|---|---|---|
| P0-T1 | Update AGENTS.md with this project path model | root `AGENTS.md` router + project `agent_rules.md` | [x] |
| P0-T2 | Create project folders and guide files | project skeleton and README files | [x] |

## Required Paths
- Project root: `agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/`
- Paper source: `evaluation_paper/`
- Taguchi skill source: `agent_doc/exp_skill/`
- Metric validation: `validation/`
- Paper index: `literature/paper_index.md`
- Plot data: `analysis/data/`
- Plot scripts: `analysis/scripts/`
- Plot output: `analysis/plots/`

## Acceptance Criteria
- [x] Project folder exists.
- [x] AGENTS.md references the new project without replacing the active RedCap implementation project.
- [x] Paper source is formally set to `evaluation_paper/`.
- [x] Future PDF reading is constrained to targeted extracts, not bulk reading.

## Discussion Points
- [Paper Path]: use `evaluation_paper/` as the formal source.
- [DOE Depth]: use Taguchi L4/L8/L9 first, or start from a simple full-factorial baseline for validation sanity.
- [Repo Audit Scope]: inventory only in P6; removal requires explicit user approval.
