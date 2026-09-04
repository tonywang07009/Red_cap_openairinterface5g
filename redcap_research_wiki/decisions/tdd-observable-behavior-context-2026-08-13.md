---
status: confirmed
source_refs:
  - .agents/skills/grill-with-docs/SKILL.md
  - .agents/skills/tdd/SKILL.md
  - openspec/changes/implement-github-issue-mirror-publisher/specs/github-issue-mirror-publication/spec.md
evidence_tier: inference
last_reviewed: 2026-08-13
related_pages:
  - redcap_research_wiki/ASK_MATT_ROUTING_MEMO.md
---

# TDD Observable-Behavior Boundary Context

- question: Which implementation details, if any, may TDD contract tests bind
  when the programmer needs freedom to refactor?
- operation: decide
- goal: G7 Capture triage
- system_scope: repository-wide TDD and implementation skills; the GitHub Issue
  mirror publisher is the first consumer.
- required_pages: `governance.md`, `CONTEXT.md`, `agent_goals.md`, and
  `ASK_MATT_ROUTING_MEMO.md`.
- authoritative_sources: the human's current decision, the selected
  `grill-with-docs` skill, the TDD skill, and the approved-publisher proposal.
- evidence_required: human scope decision and repository governance text.
- claim_boundary: human-confirmed TDD governance rule only; no assertion about
  current code behavior, GitHub runtime behavior, or test adequacy.
- autonomy_level: L3.
- completion_evidence: human confirmation plus matching OpenSpec delta and TDD
  skill text, validated by OpenSpec strict validation.
- stop_conditions: the human requires internal implementation structure to be
  fixed, or the exception boundary cannot be stated as observable behavior.
- capture_route: decision-contract.
- next_action: use the boundary gate for the next code-change TDD contract.
- critical_check:
  - counter explanation: avoiding all interaction checks could allow an
    irreversible duplicate publication despite correct end-state assertions.
  - discriminating evidence: whether the contract can express the prohibition
    as an externally visible effect, such as no second Issue or no mutation.
  - falsifier: a necessary rule can only be verified by naming a private
    function, class, data structure, or call implementation rather than a
    visible outcome.

## Current Human Direction

TDD SHALL prioritize external observable behavior and business logic. It SHALL
NOT bind private functions, internal data structures, or incidental call
structure solely to preserve a current implementation.

TDD SHALL enter through the approved-tag/workflow boundary and assert the
resulting mirror state and Issue outcome. `to-spec status`, `diff`, and guarded
`retry` are public operations; publication remains a CI-internal operation.
Retry tests SHALL assert only precondition refusal, one send, and terminal
outcome, not staging payload storage details.

`grill-with-docs` SHALL be required before TDD only when the test boundary,
acceptance condition, or irreversible side effect remains unclear. Otherwise,
the TDD contract records that all three are clear and proceeds without an
interview.

If any of those three items is unclear, TDD SHALL stop before creating or
modifying any test and enter `grill-with-docs`; it resumes only after the human
decision is recorded in the OpenSpec/TDD contract.
