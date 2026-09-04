# Reusable Case Template

Copy this file to `cases/CASE-YYYY-NNN-short-title.md` before filling it. Do
not use the template itself as a case record.

```yaml
---
status: draft | review-required | confirmed | superseded
case_id: CASE-YYYY-NNN
case_type: resolved-problem | blocked-path | experiment-learning | doc-drift
system_scope: bounded system or project scope
source_refs:
  - repository/relative/source-path
evidence_refs:
  - repository/relative/evidence-path
evidence_tier: source-record | 3gpp | paper | runtime | source-trace | mixed | inference
last_reviewed: YYYY-MM-DD
related_pages:
  - redcap_research_wiki/related-page.md
---
```

# CASE-YYYY-NNN: Title

## Question

State the reusable question.

## Context and Reproduction

State the bounded context and repeatable steps or observations.

## Expected versus Observed

Separate the expected result from the observed result.

## Evidence

Use governance labels and cite only retained source or evidence paths.

## Competing Explanations

List plausible explanations and the evidence that distinguishes them.

## Resolution or Next Owner

State the bounded resolution or the owner and criterion for the next action.

## Claim Boundary

State what the evidence supports and what it does not establish.

## Documentation Impact

Propose documentation work only. Do not edit public documentation until human
review confirms the case and approves the route.
