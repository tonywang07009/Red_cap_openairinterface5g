---
status: review-required
source_refs:
  - redcap_research_wiki/concepts/evidence-first-research-method.md
  - agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/validation/success_criteria.md
  - agent_doc/Project_management/redcap_ai_native_review_validation_workflow.md
evidence_tier: inference
last_reviewed: 2026-07-30
related_pages:
  - redcap_research_wiki/systems/rfsim-performance-evaluation.md
  - redcap_research_wiki/agent_goals.md
---

# Simulator Decision Contract

Complete this contract before source modification or RFsim execution.

| Field | Required content |
|---|---|
| Research question | One falsifiable question |
| Scope | RRC state, UE count, traffic direction, control owner |
| Sources | Exact spec clauses, paper pages/figures, source symbols, retained evidence |
| Current implementation | Implemented/called, partial, dormant, definition-only, or missing |
| Hypothesis | Expected behavior and causal mechanism |
| Controlled factors | Parameters held fixed and changed |
| Observables | gNB, UE, CN, O-RAN, traffic, and stability markers |
| Acceptance | PASS/PARTIAL/BLOCKED criteria and measurement gaps |
| Claim boundary | Strongest statement supported by evidence |
| Risks | Confounders, missing instrumentation, resource, and timing effects |
| Stop condition | Evidence or failure that stops implementation/execution |
| Rollback | Files/state to restore and verification marker |
| Documentation | Existing README, guide, report, or wiki page affected after approval |

## Decision Rule

[Inference] Select the first existing mechanism that satisfies the research
requirement: current code path, standard mechanism, installed dependency, or
registered tool. Add custom behavior only when documented evidence shows these
options cannot meet the requirement.

[Needs Verification] Do not approve the contract when source/spec support
exists at only one protocol endpoint or the requested metric cannot support the
intended claim.
