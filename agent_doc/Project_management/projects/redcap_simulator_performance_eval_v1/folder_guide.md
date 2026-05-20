# RedCap Simulator Performance Evaluation Folder Guide

## Fast Lookup
| Need | Path | Notes |
|---|---|---|
| Project index | `project_plan.md` | Start here for scope and status |
| Project agent rules | `agent_rules.md` | Project-specific workflow rules |
| Milestone contracts | `milestones/` | One file per work phase |
| Validation rules | `validation/` | Metric dictionary and test matrix |
| Paper inventory | `literature/paper_index.md` | Compact paper source of truth |
| P1 metric baseline | `literature/p1_metric_baseline.md` | Paper-to-simulator metric map |
| Paper PDFs | `../../../../evaluation_paper/` | Formal paper source path |
| Experiment skill notes | `../../../exp_skill/` | Taguchi DOE references and notes |
| Parsed data | `analysis/data/` | CSV generated from RFsim logs |
| Plot scripts | `analysis/scripts/` | Python + matplotlib scripts |
| Plot outputs | `analysis/plots/` | PNG/PDF figures |
| P2 DOE matrix | `validation/taguchi_doe_matrix.md` | Human-readable Taguchi design |
| P2 run matrix CSV | `analysis/data/p2_taguchi_l9_run_matrix.csv` | P3 execution input |

## Recommended Navigation
- For [planning]: read `project_plan.md` then one milestone.
- For [paper comparison]: read `literature/paper_index.md`, then targeted PDF extracts only.
- For [experiment design]: read `milestones/P2_taguchi_experiment_design.md` and `../../../exp_skill/README.md`.
- For [runtime validation]: read `milestones/P3_runtime_metric_capture.md` and `validation/test_matrix.md`.
- For [plotting]: read `milestones/P4_matplotlib_analysis.md`, `validation/metric_dictionary.md`, and `analysis/README.md`.
- For [repo audit]: read `milestones/P6_repo_audit_inventory.md`; do not delete files during inventory.

## Naming Rules
- CSV files: `YYYY-MM-DD_<run-set>_<metric-scope>.csv`
- Plot scripts: `plot_<metric>_vs_<factor>.py`
- Plot files: `YYYY-MM-DD_<metric>_vs_<factor>.png`
- Paper notes: `PAPER-XX_<short-title>_notes.md`

## Minimal Context Pack
- `project_plan.md`
- `agent_rules.md`
- one active milestone file
- one active validation file
- `literature/paper_index.md` only when needed
- latest work daily log
