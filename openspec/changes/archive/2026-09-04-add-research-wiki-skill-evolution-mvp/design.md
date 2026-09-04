## Context

The wiki validator now proves content conformance, but it does not decide when
a task trace merits a skill change. The MVP must keep a Runner's task context
small while preserving evidence and preventing self-promotion.

## Goals / Non-Goals

**Goals:**

- Separate evidence, reviewed knowledge, and executable procedure without
  duplicating existing stores.
- Bound an Evolution Worker to one candidate and a small evidence packet.
- Keep active-skill behavior fail-closed until independent validation and human
  promotion.
- Make the documented packet usable by GPT-5.6 Luna/high; actual model
  availability remains [Needs Verification].

**Non-Goals:**

- Create a daemon, queue, raw-trace database, embedding index, or autonomous
  Water Spider.
- Let a Runner, Water Spider, or Evolution Worker edit wiki evidence, activate
  a candidate, or switch the selected model.
- Claim that a passing content validator proves OAI runtime behavior.

## Decisions

### Reuse the three existing layers

Raw layer inputs remain retained task logs and case evidence; the wiki layer
remains reviewed pages and `blocked-path` cases; the skill layer is the active
research-wiki skill plus an OpenSpec-local candidate diff. The candidate is not
another persistent knowledge store.

### Two roles and one manual pull rule

The Runner receives only the task and active skill. An on-demand Evolution
Worker receives at most two representative traces, one reviewed wiki
pattern/case, and one existing validation command. The manual Water Spider
qualification is: same root cause observed at least twice, plus positive and
negative evidence, with WIP equal to one. It only authorizes proposing work;
it writes nothing.

### Candidate before promotion

The Evolution Worker proposes one minimal active-skill diff with applicability,
counterexample, stop condition, and a validation command. A human reviews and
promotes only after independent validation. Failure or missing evidence keeps
the active skill unchanged and records the rejection in the candidate's
OpenSpec evidence.

### Small contract test

Use one deterministic, read-only contract check for the bounded packet,
water-spider refusal, and no-promotion path. Reuse the full wiki validator for
content evidence; do not introduce an agent framework or live model test.

## Risks / Trade-offs

- [Repeated failures are actually different causes] -> require a stated root
  cause and counterexample before qualification.
- [Candidate context grows without bound] -> enforce the two-trace/one-pattern/
  one-command envelope.
- [A candidate bypasses human review] -> promotion is outside the worker and
  requires an explicit active-skill edit after validation.

## Migration Plan

1. Add one deterministic, read-only contract test and record its RED result.
2. Add the role, packet, and promotion contract to the existing skill asset.
3. Run the contract check and existing full wiki validator.
4. Review the change; rollback removes the new procedure and leaves current
   wiki content and active skill behavior intact.

## TDD contract

- Model / effort: GPT-5.6 Luna/high requested; active metadata [Needs Verification].
- Test boundary: `bash redcap_library/bash_tool/scripts/test_research_wiki_skill_evolution.sh`.
- Acceptance links: `research-wiki-skill-evolution` requirements in this change.
- Irreversible side effects: none; the test reads the skill and prints PASS or FAIL.
- Boundary gate: clear; the bounded packet and no-promotion outcome are explicit.
- Test files: `test_research_wiki_skill_evolution.sh`.
- Test evidence: timestamped RED and GREEN compiler logs.
