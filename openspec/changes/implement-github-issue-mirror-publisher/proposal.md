## Why

An approved OpenSpec tag currently has no repository-owned publisher. The
confirmed workflow requires a GitHub Issue mirror that cannot create duplicate
issues when a CI response is lost or a human performs the single permitted
retry.

## What Changes

- Add a GitHub Actions workflow triggered only by a pushed, valid approved
  annotated tag.
- Publish one GitHub Issue mirror from the approved OpenSpec revision using a
  stable idempotency key.
- Retry the same request at most three times after the first attempt, one
  minute apart; diagnose read-only after exhaustion.
- Store only redacted, repository-local publication evidence and expose the
  agreed `to-spec status`, `to-spec diff`, and `to-spec retry` operations.
- Do not let GitHub Issue content grant approval, alter scope, or become a
  planning source.

## Capabilities

### New Capabilities

- `github-issue-mirror-publication`: Publish and reconcile the approved
  OpenSpec revision as a GitHub Issue mirror.

### Modified Capabilities

None.

## Impact

- New GitHub Actions workflow and a minimal repository-owned publisher.
- GitHub Actions `issues: write` permission and a GitHub Issue generated only
  after a human-approved tag is pushed.
- Local, redacted publication evidence; no credential is stored in the
  repository.

## Parent Task and Child Responsibility

**Parent task:** [`govern-skill-pipeline-contract`](../govern-skill-pipeline-contract/proposal.md)

| Item | This child change is responsible for |
|---|---|
| Goal | Create one idempotent GitHub Issue mirror for a valid approved tag. |
| Purpose | Make the parent's mirror, retry, diagnosis, and token-redaction contract executable in GitHub Actions. |
| Inherited boundary | OpenSpec remains canonical; GitHub Issues never approve or add requirements; protected TDD tests remain immutable. |
| Own acceptance | Local fake-API TDD, SHA-256 and frozen test-diff baseline, code review, and separately authorized live GitHub acceptance. |

This child has its own approved annotated tag and review evidence. It cannot
expand the parent scope by adding a new observable behavior, changing an owner,
or relaxing acceptance conditions.

## Inherited Human Scope Confirmation

**Confirmed on 2026-08-13** under
[the pipeline parent task](../govern-skill-pipeline-contract/proposal.md#human-scope-confirmation).
This child may implement only the GitHub Actions publisher, GitHub Issue mirror,
and local fake-API validation stated there. It retains its own approved revision,
TDD contract, and code review.
