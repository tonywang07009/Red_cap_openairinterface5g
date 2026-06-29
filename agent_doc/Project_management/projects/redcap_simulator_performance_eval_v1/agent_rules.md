# RedCap Simulator Performance Evaluation Agent Rules

## Project Entry
- Project plan: `agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/project_plan.md`
- Milestones: `agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/milestones/`
- Validation: `agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/validation/`
- Literature index: `agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/literature/paper_index.md`
- Analysis workspace: `agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/analysis/`
- Folder guide: `agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/folder_guide.md`
- Paper source: `redcap_doc/evaluation_papers/`
- Experiment skill source: `agent_doc/exp_skill/`

## Token-Efficient Context Pack
- Read only:
  1. `project_plan.md`
  2. target milestone file
  3. relevant validation file
  4. `literature/paper_index.md` only when paper evidence is needed
  5. latest `test_log/work_daily/*.md`

## Review And Validation Workflow
- For RedCap code review, functional validation, and learning reports, use:
  - `agent_doc/Project_management/redcap_ai_native_review_validation_workflow.md`
- For MCP routing, command selection, and known tool limitations, use:
  - `agent_doc/Project_management/redcap_toolbox.md`
- Keep `AGENTS.md` as the router; do not copy workflow templates or command tables into root guidance.

## Paper Extraction
- Do not bulk-read all PDFs.
- Extract only targeted pages, figures, tables, or metric definitions needed for the active task.
- For paper-derived claims, cite paper file and page/figure/table when available.
- Mark unclear paper interpretation as `[Needs Verification]`.
- Prefer paper results with explicit X/Y axes and units.

## Experiment Design
- Use Taguchi DOE from `agent_doc/exp_skill/` when factors and levels are defined.
- State:
  - factors
  - levels
  - response metrics
  - orthogonal array choice
  - assumptions
  - limitations
- Do not claim interaction effects unless the selected design can support them.

## Plotting
- Use Python + matplotlib.
- Store raw/parsed CSV under `analysis/data/`.
- Store scripts under `analysis/scripts/`.
- Store generated figures under `analysis/plots/`.
- X-axis must match a simulator-controlled factor.
- Y-axis must match a simulator-measured metric from `validation/metric_dictionary.md`.

## Repo Audit
- Audit work is inventory-only unless the user explicitly approves cleanup.
- For each cleanup candidate, list:
  - path
  - reason
  - references checked
  - expected impact
  - recommendation

## Sub-task Closeout Knowledge Capture
- At the end of each experiment, audit, or analysis sub-task, decide whether the work produced a reusable [trace step] or recurring [problem pattern].
- If useful, add a concise candidate to `agent_doc/Project_management/redcap_trace_problem_kb/candidate_inbox.md`.
- Candidate entries should include:
  - [Experiment or Audit Item]
  - [source evidence path]
  - [success marker]
  - [failure marker]
  - [step-by-step draft]
- After every 5 completed sub-tasks, run `agent_doc/Project_management/redcap_trace_problem_kb/maintenance_rule.md`.
- Keep retained fix procedures numbered and step-by-step.
- Do not store raw logs, heavy generated outputs, packet captures, or one-off command mistakes in the KB.
