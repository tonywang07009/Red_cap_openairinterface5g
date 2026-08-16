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

`to-spec add <change-id> --confirm-scope` is the local approval-gated tag
operation. After an explicit human approval in the current task, the agent
automatically invokes this underlying operation. The explicit confirmation flag
records the human's already-decided scope in the immutable annotated tag for the
exact committed revision, then pushes only that tag with the caller's existing
Git identity. It never pushes a branch or stores a credential. Without the
flag it MUST refuse before creating or pushing a tag; the user does not
separately run `to-spec add`, `git tag`, or `git push`.

The sole self-hosting exception is the first implementation of `to-spec add`
itself. After explicit human approval and commit, the agent may use `rtk git`
in one bootstrap action to create and push exactly two fixed-format tags: the
pipeline parent tag and its publisher-child tag. Record that action in the
change evidence. Once `to-spec add` is implemented, no later change may use
this raw-Git exception.

Before tag creation, inspect only `openspec/changes/<change-id>/`. Refuse when
that directory has modified, deleted, or untracked content, because the tag
would otherwise identify an older revision than the approved OpenSpec. Do not
refuse solely for unrelated dirty worktree paths.

Use only the `origin` remote. Before creating a tag, verify that `origin`
exists and is reachable; otherwise exit `1` without creating a tag. If `origin`
becomes uncertain only after local tag creation, retain the local tag and apply
the uncertain-push rule below.

On success, output only the change ID, annotated tag, full SHA, `tag pushed`,
and this Chinese summary:

```text
摘要：已推送批准標籤；GitHub Issue mirror 由 GitHub Actions 後續處理。
```

This does not claim that a GitHub Issue exists. On a pre-tag refusal, report
the cause, emit exit code `1`, and state in Chinese that no tag was created or
pushed.
If the remote has the exact approved tag with matching target SHA and
annotation, report success as `tag pushed: already-present`; do not recreate,
overwrite, or push it again. A local tag alone is not success. When local tag
creation succeeded but remote status is absent or unverified, retain the local
tag and safely retry pushing that same immutable tag. A push result that remains
unknown exits `1` and states in Chinese that the local tag was retained for
verification; it does not claim that no tag exists. Any mismatch MUST refuse
with exit code `1`.

Only accept an immutable annotated tag matching:

```text
openspec/<change-id>/approved/<short-sha>
```

Its annotation MUST identify human scope confirmation, the parent task, full
revision SHA, and the OpenSpec `proposal.md` path. Verify that the tag points
to that full SHA, the short SHA is its prefix, and `proposal.md` resolves below
the matching change directory. The proposal is the reader entry point and links
to its design, specifications, and tasks.

Use this exact annotation format; a root change writes `Parent: none`:

```text
OpenSpec approved revision
Human scope confirmation: confirmed
Change: <change-id>
Parent: <parent-change-id|none>
Parent tag: <parent-approved-tag|none>
Commit: <full-sha>
Proposal: openspec/changes/<change-id>/proposal.md
```

For a child change, resolve `Parent tag` before any GitHub API call. It MUST be
an annotated approved tag whose `Change` field equals `Parent`, and its target
and declared `Commit` MUST match. Otherwise refuse before API access. A root
change writes both `Parent: none` and `Parent tag: none`.

Before a human confirms scope for that tag, show the request in this form:

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

## Repository administrator prerequisite

Before the first live mirror, a repository administrator enables GitHub Actions
once and grants only the publisher job `issues: write`. The tag publisher is
then uniform: every valid later approved tag is eligible, with no separately
selected or re-approved first tag. The daily cleanup job has no GitHub API
access and SHALL NOT receive `issues: write`.

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

## GitHub Issue mirror format

Use one stable title for the lifetime of a change:

```text
[OpenSpec] <change-id>
```

The body is a read-only reader entry point. It SHALL state that OpenSpec is
canonical, then contain only the approved mirror facts:

```md
OpenSpec is canonical; this Issue is a read-only mirror.

- Change: `<change-id>`
- Approved revision: `<annotated-tag>`
- Commit: `<full-sha>`
- Parent task: [<parent-change-id>](<parent-proposal-permalink>)  # only when present
- OpenSpec: [proposal](<proposal-permalink>)
- Acceptance summary: <from approved OpenSpec>

<!-- openspec-mirror: change=<change-id>; tag=<tag>; sha=<full-sha> -->
```

Apply exactly these labels:

```text
openspec-mirror
state:<draft|approved|publishing|published|diagnosing|failed>
```

Do not add priority, owner, schedule, or any tracker-originated requirement.
The marker is for reconciliation only and is not reader-facing content.
Each proposal permalink SHALL be a GitHub blob URL derived from the `origin`
repository, approved full SHA, and repository-relative proposal path:
`https://github.com/<owner>/<repo>/blob/<full-sha>/<proposal-path>`. Relative
Markdown links are not valid in an Issue body. For a parent link, resolve
`Parent tag` first and derive that parent's full SHA and proposal path from its
immutable annotation.

## Generated-state schema and retention

Store generated state only at:

```text
openspec/.to-spec/<change-id>/state.json
```

The state object contains only `state`, `approved_tag`, `commit_sha`,
`idempotency_key`, `attempt`, `issue_number`, `issue_url`, `diagnosis`, and
`updated_at`. It SHALL NOT duplicate requirements, owner, schedule, or
acceptance text. The implementation SHALL provide
`openspec/.to-spec/README.md` as the field memo: every key's meaning, value
domain, update condition, and nullability. Keep `state.json` valid JSON; do
not insert comments into it.

Keep `state.json` for status traceability. Remove only regenerable staging
payloads, payload diffs, and redacted diagnostic responses after 30 days in a
terminal `published` or `failed` state. Never remove data for `publishing` or
`diagnosing` revisions. A daily GitHub Actions cleanup job runs only on a
self-hosted runner with persistent staging; a GitHub-hosted fresh checkout
MUST reject the configuration rather than claim a successful no-op cleanup. It
does not call the GitHub API and must not delete OpenSpec artifacts, approved
tags, or GitHub Issues.

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
