---
name: to-spec
description: Mirror a human-approved OpenSpec revision to the project issue tracker and report its publication state.
disable-model-invocation: true
---

OpenSpec is the canonical requirement, design, task, acceptance, and schedule
record. The issue tracker is a read-only synchronization mirror. This skill
never creates requirements, changes an OpenSpec revision, or grants approval.

Follow the mandatory lookup route in [root AGENTS.md](../../../AGENTS.md#file-query-workflow).

## Approval input

Only accept an immutable annotated tag matching:

```text
openspec/<change-id>/approved/<short-sha>
```

Its annotation MUST identify the parent task, full revision SHA, and the
OpenSpec `proposal.md` path. Verify that the tag points to that full SHA, the
short SHA is its prefix, and `proposal.md` resolves below the matching change
directory. The proposal is the reader entry point and links to its design,
specifications, and tasks.

Before a human creates that tag, show the request in this form:

```md
## 1. Result

The decision requested; use "request approval" until approved.

## 2. How to do

The proposed design, boundaries, and acceptance conditions.

## 3. Introduction

Facts, inference from those facts, and what remains out of scope.

## Approval scope

- Can change:
- Must not change:
- Acceptance conditions:

## Subtask rules

- Subtasks stay inside this scope.
- A new observable behavior, owner, or relaxed acceptance condition requires
  a new approval request.
- Each subtask names its parent task and approved revision.
```

## Future public operations

```text
to-spec status <change-id>  # read mirror state and diagnosis
to-spec diff <change-id>    # preview the mirror payload
to-spec retry <change-id>   # one human-requested resend after diagnosis
```

Reject `retry` unless the change is `failed`, its read-only diagnosis is
complete, a human records that the diagnosed cause has been remedied, and a
human requests the action. Reject every operation that lacks a valid approved
tag.

This is a future CI/publisher contract, not current behavior. A separately
approved implementation change must add it before any tag can publish. After
implementation, pushing a valid approved tag is the only automatic publication
trigger. The publisher creates one staging payload and idempotency key, attempts
once and then retries three times at one-minute intervals. After exhaustion it
runs only read-only diagnosis: local tag/SHA, staging payload/key, matching
existing issue, and a redacted tracker response summary.

Mirror state is:

```text
draft → approved → publishing → published
                         └→ diagnosing → failed
```

`failed` means automatic retries are exhausted and diagnosis is available for
human action. It is not a request to retry blindly.

If the idempotency key finds an issue whose change ID, approved tag, and full
SHA all match, record it as `published` without creating another issue. Any
mismatch becomes `failed` with a diff report and no tracker overwrite.

`to-spec retry` reuses the original payload and key for one attempt. It does
not start another automatic retry cycle and does not create a new issue.

## Failure report

```md
## 1. Result

Publication did not complete; include attempt count and classified diagnosis.

## 2. How to do

List read-only checks and the recommended human remedy.

## 3. Introduction

State direct evidence, inference, and that no OpenSpec, tag, tracker, or issue
was modified. Redact tokens, complete HTTP headers, and other sensitive data.
```
