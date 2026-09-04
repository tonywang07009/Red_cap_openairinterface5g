## Why

The research wiki now has a canonical root and a passing validator, but a task
trace can still become an unbounded context dump or an unreviewed skill edit.
The MVP needs a small, fail-closed route from repeated evidence to one
reviewable skill candidate.

## What Changes

- Define three layers: immutable existing task evidence, reviewed wiki
  patterns, and rollback-safe active/candidate skill procedures.
- Define two roles: a Runner that consumes the active skill and an on-demand
  Evolution Worker that proposes one bounded candidate.
- Define a manual water-spider pull rule: require the same root cause twice
  plus positive and negative evidence; set candidate work-in-progress to one.
- Require independent validation before a human promotes a candidate; failed
  candidates retain the prior active skill and a rejection reason.
- Reuse existing cases, logs, validator, and skill layout. Do not add a raw
  trace store, background service, or automatic promotion.

## Capabilities

### New Capabilities

- `research-wiki-skill-evolution`: Define bounded evidence selection,
  water-spider qualification, candidate proposal, validation, and promotion
  boundaries for research-wiki skills.

### Modified Capabilities

- None.

## Impact

- `redcap_library/skills/redcap_research_wiki/`
- `redcap_research_wiki/cases/` and governance references only as existing
  evidence inputs
- Existing `validate_redcap_research_wiki.py` public CLI as content-gate input
- Documentation/skill procedure only; no OAI runtime, protocol, Docker, or
  automatic agent/model switching behavior.
