## Why

The repository has separate skills for planning, specification, implementation,
and review, but their current contracts permit divergent requirements, test
mutation during implementation, and inconsistent tool use. A single governed
pipeline is needed before an approved change reaches implementation.

## What Changes

- Define OpenSpec as the canonical requirement, design, acceptance, status, and
  scheduling record; the issue tracker becomes a read-only mirror.
- Define human-created approved tags as the only publication trigger and record
  the automated mirror, retry, and read-only diagnosis contract in `to-spec`.
- Add a TDD contract, protected-test rules, model/effort recording, and a
  minimal implementation design check.
- Extend review from two axes to evidence-backed boundary, business-logic, and
  readability lenses; define the documentation/governance review path.
- Establish mandatory Symdex, rtk, and filesystem MCP routing in root guidance
  and align the affected skills and router memo.

## Capabilities

### New Capabilities

- `skill-pipeline-contract`: Governs the approved OpenSpec-to-implementation
  workflow, immutable test contract, review behavior, and tool routing.

### Modified Capabilities

- `oai-tool-routing`: Tightens repository tool selection and fallback rules.
- `oai-workflow-routing`: Aligns formal OpenSpec routing with the new pipeline.

## Impact

- Affected guidance: root `AGENTS.md`, routing memo, and planning, mirror, TDD,
  implementation, and review skills.
- Follow-up infrastructure: CI/tag publication and issue-tracker adapter work.
- No RAN source or runtime behavior changes.

## Pipeline Parent Task

This change is the parent task for the approved pipeline. It defines the rules
that every child must obey; it does not implement remote publication itself.

| Child change | Goal | Purpose | Independent acceptance |
|---|---|---|---|
| `govern-skill-pipeline-contract` | Establish one canonical workflow and immutable TDD/review/tool-routing contracts. | Prevent a tracker, agent, or implementation detail from changing approved scope or protected tests. | OpenSpec strict validation and documentation/governance code review. |
| [`implement-github-issue-mirror-publisher`](../implement-github-issue-mirror-publisher/proposal.md) | Turn a valid approved tag into one idempotent GitHub Issue mirror. | Provide the actual GitHub Actions publisher, bounded retry, and read-only diagnosis required by this contract. | Frozen local-fake API TDD, implementation review, and separately authorized live GitHub acceptance. |

Each child keeps its own revision, approved annotated tag, validation contract,
and code review. Child work inherits this parent scope only; a new observable
behavior, owner, or relaxed acceptance condition requires a new approval.

## Human Scope Confirmation

**Confirmed on 2026-08-13.** The human approved this change and its named child
as one pipeline parent task.

- Can change: pipeline skills, TDD boundary gate, GitHub Actions publisher,
  GitHub Issue mirror, and `redcap_library/` local fake-API validation.
- Must not change: OpenSpec canonical status, existing Jenkins CI, immutable
  tags, Issue-to-OpenSpec direction, or repository credentials.
- Acceptance: each child keeps an independent approved revision, validation
  contract, and code review. The bootstrap pair may install the first publisher
  without a self-mirror; every later approved tag uses the normal mirror route.
