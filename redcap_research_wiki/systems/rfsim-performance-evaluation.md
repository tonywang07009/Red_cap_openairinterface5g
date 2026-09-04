---
status: review-required
source_refs:
  - agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/project_plan.md
  - agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/agent_rules.md
  - agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/literature/paper_index.md
  - agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/validation/success_criteria.md
evidence_tier: mixed
last_reviewed: 2026-07-30
related_pages:
  - redcap_research_wiki/concepts/evidence-first-research-method.md
  - redcap_research_wiki/decisions/simulator-decision-contract.md
---

# RFsim Performance Evaluation

[Source Trace] The simulator project already owns the paper inventory, metric
definitions, DOE records, runtime criteria, parsed data, plots, and final
validity reports. The wiki links these assets; it does not recreate parallel
versions.

[Paper Evidence] Papers select questions, metrics, and trends. Absolute
comparability requires verified radio, channel, traffic, and measurement
equivalence.

[Runtime Evidence] A run supports trend analysis only when the project success
criteria classifies it as usable and its measurement gaps are retained.

[Needs Verification] RFsim latency and monitoring values are proxies. They do
not establish real-network end-to-end latency or physical-power conclusions.

## Minimal Research Route

1. Read the project plan and rules.
2. Read `literature/paper_index.md` and only the targeted source pages.
3. Select metrics from `validation/metric_dictionary.md`.
4. Freeze factors, levels, traffic, markers, and the claim boundary.
5. Apply `validation/success_criteria.md`.
6. Retain failures as failure-to-improvement records.
