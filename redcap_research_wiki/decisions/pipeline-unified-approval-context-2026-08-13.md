---
status: confirmed
source_refs:
  - openspec/changes/govern-skill-pipeline-contract/proposal.md
  - openspec/changes/implement-github-issue-mirror-publisher/proposal.md
  - .agents/skills/to-spec/SKILL.md
evidence_tier: inference
last_reviewed: 2026-08-13
related_pages:
  - redcap_research_wiki/ASK_MATT_ROUTING_MEMO.md
---

# Pipeline Unified Approval Context

- question: How should the governance contract and GitHub Issue publisher be
  approved as one pipeline parent task while retaining independent OpenSpec
  revisions and acceptance?
- operation: decide
- goal: G7 Capture triage
- system_scope: repository skill-pipeline governance and GitHub Issue mirror
  publisher.
- required_pages: `governance.md`, `CONTEXT.md`, `agent_goals.md`, and
  `ASK_MATT_ROUTING_MEMO.md`.
- authoritative_sources: the two OpenSpec proposals, the `to-spec` contract,
  and the human's current decision.
- evidence_required: human scope decision and OpenSpec artifacts.
- claim_boundary: approved scope only; no claim that a tag, GitHub Action, or
  Issue has been created.
- autonomy_level: L3.
- completion_evidence: human confirms the unified scope; both children
  reference it and await independent approved revision tags and acceptance
  evidence.
- stop_conditions: parent record would omit a child scope, make an Issue
  canonical, or permit a child to expand observable behavior.
- capture_route: decision-contract.
- next_action: commit the confirmed revisions when separately authorized, then
  create the two independent approved annotated tags.
- critical_check:
  - counter explanation: separate approvals reduce accidental scope expansion.
  - discriminating evidence: the parent contract explicitly lists both child
    scopes, prohibited changes, and independent acceptance conditions.
  - falsifier: either child needs a new observable behavior, owner, or relaxed
    acceptance condition not present in the parent request.

## Current Human Direction

The two changes SHALL be approved as one pipeline parent task. Each child
retains its own OpenSpec revision, approved tag, TDD/Validation contract, and
code review; no child may use inherited approval to expand scope.

The parent task SHALL be `govern-skill-pipeline-contract`. The publisher change
is its named child, and both proposal entry pages SHALL state the children's
goals, purposes, inherited boundary, and independent acceptance responsibility.

The parent and first publisher child form a bootstrap exception. They retain
human approval, approved-tag evidence, TDD or validation, and review, but do
not require their own Issue mirror before the publisher exists. The next
approved tag uses normal GitHub Actions publication.

The human confirmed this unified scope on 2026-08-13. No tag is created until a
committed revision exists for it to identify.
