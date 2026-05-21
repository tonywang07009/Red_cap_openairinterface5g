# RedCap Simulator Performance Evaluation Project (v1)

## Project Metadata
- Project Path: `agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/project_plan.md`
- Created Date: 2026-05-20
- Updated Date: 2026-05-21
- Objective: design and validate whether this OAI RFsim-based platform can be used for RedCap performance simulation.
- Agent Rules Path: `agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/agent_rules.md`
- Primary Simulator Path: `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/`
- Paper Reference Path: `evaluation_paper/`
- Experiment Skill Path: `agent_doc/exp_skill/`
- Validation Directory: `agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/validation/`
- Literature Directory: `agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/literature/`
- Analysis Directory: `agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/analysis/`
- Daily Log Path: `test_logs/work_daily/`

## Project Goal
- [Validation Question]: Can this OAI RFsim platform produce RedCap performance behavior that is directionally comparable to the selected RedCap reference papers?
- [Primary Metrics]: throughput, latency, jitter, packet loss, attach success, PDU session success, tunnel readiness, gNB restart count.
- [Secondary Metrics]: PRB allocation pressure, RA/Msg2/Msg4 counters, CPU/memory pressure, UE scale threshold.
- [Experiment Method]: Taguchi-style design of experiments where factor count and level count allow it.
- [Plotting Method]: Python + matplotlib, with CSV input and reproducible scripts.

## Token-Efficient Reading Rule
- Read only these files before each work item:
  1. `project_plan.md`
  2. `agent_rules.md`
  3. one target milestone file under `milestones/`
  4. one target validation file under `validation/`
  5. `literature/paper_index.md` only when paper evidence is needed
  6. latest `test_logs/work_daily/*.md`
- Do not bulk-read all PDFs.
- Extract only targeted pages/sections from a paper when a metric, graph, or assumption is needed.
- Mark paper-derived claims as [Paper Evidence] and spec-derived claims as [3GPP Evidence].
- Mark uncertain paper or spec interpretation as [Needs Verification].

## Document Model
- `project_plan.md` is the active index.
- One milestone equals one Markdown execution contract under `milestones/`.
- Literature extraction lives in `literature/paper_index.md` and follow-up paper notes.
- Metric definitions and validation criteria live under `validation/`.
- Experiment success criteria live in `validation/success_criteria.md`.
- Raw experiment output should go under `analysis/data/`.
- Generated plots should go under `analysis/plots/`.
- Plot scripts should go under `analysis/scripts/`.
- Repository audit output should go under `validation/repo_audit_inventory.md`.

## Milestone Index
| Milestone | File | Purpose | Status |
|---|---|---|---|
| P0 | `milestones/P0_agent_project_scaffold.md` | AGENTS.md rules, project paths, folder model | [x] |
| P1 | `milestones/P1_literature_metric_baseline.md` | Extract metrics and baseline assumptions from RedCap papers | [x] |
| P2 | `milestones/P2_taguchi_experiment_design.md` | Build factor/level matrix using Taguchi DOE | [x] |
| P3 | `milestones/P3_runtime_metric_capture.md` | Define and run RFsim throughput/latency/scale metric capture | [x] |
| P4 | `milestones/P4_matplotlib_analysis.md` | Generate throughput/latency/jitter plots from simulator data | [x] |
| P5 | `milestones/P5_platform_validity_report.md` | Decide whether platform is credible for RedCap performance simulation | [x] |
| P6 | `milestones/P6_repo_audit_inventory.md` | Inventory unused files/logs/manuals without deleting anything | [x] |

## Priority Backlog
| Task ID | Milestone | Task Name | Prerequisite Tasks | Evidence Output | Status |
|---|---|---|---|---|---|
| P0-T1 | P0 | Update AGENTS.md with this project path model | None | AGENTS.md router + project `agent_rules.md` | [x] |
| P0-T2 | P0 | Create project folders and guide files | None | project skeleton | [x] |
| P1-T1 | P1 | Build paper inventory and metric extraction table | P0 | `literature/paper_index.md`; `literature/p1_metric_baseline.md` | [x] |
| P1-T2 | P1 | Select comparable paper graphs/tables for OAI replication | P1-T1 | paper-to-simulator metric map | [x] |
| P2-T1 | P2 | Define Taguchi factors and levels | P1 | `validation/taguchi_doe_matrix.md` | [x] |
| P2-T2 | P2 | Choose orthogonal array and run order | P2-T1 | `analysis/data/p2_taguchi_l9_run_matrix.csv` | [x] |
| P3-T1 | P3 | Define RFsim runtime capture workflow | P2 | runtime checklist; `validation/success_criteria.md`; `analysis/scripts/p3_capture_workflow.py` | [x] |
| P3-T2 | P3 | Run baseline throughput and latency validation | P3-T1 | logs + CSV | [x] |
| P3-T3 | P3 | Run DOE-L9 metric capture | P3-T2 | `analysis/data/p3_runtime_metrics.csv`; failure-to-improvement records | [x] |
| P4-T1 | P4 | Build matplotlib plotting scripts | P3 | PNG/PDF plots | [x] |
| P5-T1 | P5 | Compare simulator results with paper evidence | P4 | validity report | [x] |
| P6-T1 | P6 | Repo folder inventory and unused-candidate list | P0 | audit inventory | [x] |

## 3GPP Traceability Seeds
- TS 38.306 Section 4 — RedCap UE capability constraints [Needs Verification].
- TS 38.321 Section 5.4 — UL-SCH data transfer relevance for uplink throughput [Needs Verification].
- TS 38.331 Section 5.3 — RRC connection control relevance for attach/session readiness [Needs Verification].
- TS 38.214 Section 6.1 — PUSCH-related scheduling/throughput relevance [Needs Verification].

## Current Decisions
- Use `evaluation_paper/` as the formal paper source for this project.
- Use `agent_doc/exp_skill/` for Taguchi DOE notes and PDF references.
- Do not start repo-wide deletion or cleanup. P6 is inventory-only unless the user explicitly approves removals.

## Next Action
- Review remaining high-risk archive candidates in `validation/repo_audit_inventory.md` before cleaning logs, build trees, or historical manuals.
