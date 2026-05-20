# Work Daily Log
## Session Metadata
- Date: 2026-05-20 22:09
- Agent Session ID: N/A
- Task Slug: p2-taguchi-doe-matrix
- Project Path: agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/project_plan.md
- Milestone File: milestones/P2_taguchi_experiment_design.md
- Validation File: validation/taguchi_doe_matrix.md; validation/test_matrix.md
- Task ID: P2-T1 / P2-T2

## Milestone & Sub-task Reference
- Milestone: P2 Taguchi Experiment Design
- Sub-task: convert P1 metric baseline into first executable L9 RFsim DOE matrix
- Status: [COMPLETED]

## What Was Done
- Loaded minimal P2 context pack:
  - `project_plan.md`
  - `agent_rules.md`
  - `milestones/P2_taguchi_experiment_design.md`
  - `literature/p1_metric_baseline.md`
  - `validation/test_matrix.md`
  - latest work daily log
- Checked actual runtime knobs in:
  - `ci-scripts/redcap_runtime_menu.sh`
  - `ci-scripts/redcap_mmtc_smoke_validation.sh`
- Confirmed current helper supports UL iperf but does not expose DL iperf.
- Created human-readable DOE design:
  - `agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/validation/taguchi_doe_matrix.md`
- Created executable CSV run matrix:
  - `agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/analysis/data/p2_taguchi_l9_run_matrix.csv`
- Selected first DOE:
  - `DOE-BASE-001` single-UE calibration baseline
  - `DOE-L9-01..09` using L9 with three active factors and one dummy column
- Factors selected:
  - [A] UE scale: 16 / 32 / 56 UEs
  - [B] UDP uplink offered rate: 10M / 50M / 85M
  - [C] validation sample depth: 1 / 4 / 8 sampled UEs
  - [D] dummy residual/error column
- Updated `P2_taguchi_experiment_design.md`, `project_plan.md`, `test_matrix.md`, and `folder_guide.md`.

## 3GPP Spec Clauses Referenced
- TS 38.306 Section 4 — RedCap UE capability and reduced-complexity constraints seed [Needs Verification].
- TS 38.321 Section 5.4 — UL-SCH throughput relevance seed [Needs Verification].
- TS 38.214 Section 6.1 — PUSCH throughput relevance seed [Needs Verification].

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| Runtime knob check | PASS | P2 executability | Required env vars exist in runtime helper/smoke script |
| DOE matrix document | PASS | P2-T1/P2-T2 | `validation/taguchi_doe_matrix.md` created |
| CSV run matrix parse | PASS | P3 input readiness | 10 rows: 1 baseline + 9 L9 rows |
| Project plan update | PASS | project tracking | P2 and P2 tasks marked `[x]` |
| Test matrix update | PASS | validation tracking | `PERF-DOE-001` marked `[x]` |
| Source build | N/A | documentation only | No C/C++ source change |
| Unit test | N/A | documentation only | No CTest target required |
| Container image rebuilt | N/A | no container change | Not rebuilt |
| RFsim UE/gNB/CN runtime | N/A | design only | Not run |

## Known Issues / Blockers
- First DOE excludes DL throughput because existing helper is UL-only.
- First DOE excludes SNR/BLER/MIL/MCL because RFsim does not expose those as direct axes.
- PDCCH blocking probability remains a proxy metric unless scheduler/control-channel instrumentation is added.
- Sample depth is not true simultaneous traffic concurrency; current script runs selected iperf checks sequentially.

## Next Step
- Start P3 by converting `validation/taguchi_doe_matrix.md` and `analysis/data/p2_taguchi_l9_run_matrix.csv` into a repeatable RFsim metric-capture workflow.

## Append-Only Revision Notes
- 2026-05-20 22:09 — Updated `project_plan.md`, `milestones/P2_taguchi_experiment_design.md`, `validation/test_matrix.md`, and `folder_guide.md` after completing P2. Revised Milestone: P2. Revised Sub-task: P2-T1 / P2-T2.
