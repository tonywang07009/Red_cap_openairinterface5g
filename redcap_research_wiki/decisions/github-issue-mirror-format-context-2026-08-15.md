---
status: confirmed
source_refs:
  - openspec/changes/implement-github-issue-mirror-publisher/proposal.md
  - openspec/changes/implement-github-issue-mirror-publisher/design.md
  - openspec/changes/implement-github-issue-mirror-publisher/specs/github-issue-mirror-publication/spec.md
  - .agents/skills/to-spec/SKILL.md
evidence_tier: human-decision
last_reviewed: 2026-08-15
related_pages:
  - redcap_research_wiki/governance.md
  - redcap_research_wiki/CONTEXT.md
---

# GitHub Issue Mirror Format Context

- question: What fixed GitHub Issue format, generated-state boundary, and
  retention rule shall the OpenSpec mirror publisher use?
- operation: decide
- goal: G7 Capture triage.
- system_scope: `implement-github-issue-mirror-publisher`, its `to-spec`
  contract, and generated state under `openspec/.to-spec/`.
- required_pages: `governance.md`, `CONTEXT.md`, `agent_goals.md`, and
  `ASK_MATT_ROUTING_MEMO.md`.
- authoritative_sources: the active publisher OpenSpec artifacts, the
  `to-spec` skill, and the human decisions recorded in this discussion.
- evidence_required: human decision and matching OpenSpec contract.
- claim_boundary: design and local-contract scope only; no claim that GitHub
  Actions is enabled, permissions exist, or a live Issue has been created.
- autonomy_level: L3.
- completion_evidence: the skill and active publisher OpenSpec state the same
  fixed title, body, labels, key memo, and retention boundary.
- stop_conditions: a proposed field makes the Issue canonical, stores a token,
  changes OpenSpec requirements from the tracker, or deletes active or
  canonical evidence.
- capture_route: decision-contract.
- next_action: decide administrator preconditions, cleanup trigger, and the
  workflow implementation boundary for automatic tag push.
- critical_check:
  - counter explanation: per-state labels or body revisions could be mistaken
    for tracker-owned workflow state.
  - discriminating evidence: every displayed value derives from the approved
    OpenSpec revision or generated mirror state; no owner, schedule, or
    tracker-authored requirement is present.
  - falsifier: the publisher needs a second Issue, a tracker-only decision, or
    an unrecoverable field absent from OpenSpec and generated state.

## Current Human Direction

One mirror uses the stable title `[OpenSpec] <change-id>`. Its body identifies
the approved revision, full commit SHA, proposal link, acceptance summary, and
machine marker. A child change includes a clickable parent-proposal link. Its
only labels are `openspec-mirror` and projected `state:<mirror-state>`.

Generated state remains valid JSON at
`openspec/.to-spec/<change-id>/state.json`. It may contain only state,
approved tag, commit SHA, idempotency key, attempt, Issue number and URL,
diagnosis, and update time. `openspec/.to-spec/README.md` will document each
key's meaning, value domain, update condition, and nullability; it replaces
invalid inline JSON comments.

Keep `state.json` indefinitely for traceability. After 30 days in a terminal
`published` or `failed` state, cleanup may remove only regenerable staging
payloads, payload diffs, and redacted diagnostic responses. It must never
remove active state, OpenSpec, approved tags, or GitHub Issues.

The cleanup runs once daily from GitHub Actions and makes no GitHub API call.

Before the first live mirror, a repository administrator enables GitHub Actions
once and grants only the publisher job `issues: write`. The cleanup job receives
no Issue permission. There is no separately selected or additionally approved
first tag: every later valid approved tag uses the same automatic mirror flow.

Archive requires a valid approved tag, completed canonical tasks, and the
applicable validation plus review evidence. A code change needs frozen TDD and
code review; documentation/governance needs its validation contract and review.
An absent or `failed` GitHub Issue mirror remains diagnosable external evidence,
not an archive blocker.

After human scope confirmation, local
`to-spec add <change-id> --confirm-scope` automatically creates and pushes the
approved annotated tag with the caller's existing Git identity. It does not
push a branch or store a credential. Without the explicit confirmation flag it
refuses before tag creation. The immutable annotation is the sole durable
confirmation record and identifies scope confirmation, parent task, full SHA,
and proposal path. The user does not run this command: after an explicit human
approval in the current task, the agent invokes the underlying operation.

Approval aligns the confirmed OpenSpec with its tag revision. `to-spec add`
checks only `openspec/changes/<change-id>/`: modified, deleted, or untracked
content there blocks tag creation because it would tag an older revision.
Unrelated dirty worktree paths do not block approval.

`to-spec add` uses only `origin`. It checks that `origin` exists and is
reachable before creating a tag; a missing or unreachable preflight exits `1`
without a new tag. An uncertainty after local creation retains the local tag for
safe verification and retry.

Approved tag annotations use this fixed parseable format; a root writes
`Parent: none`:

```text
OpenSpec approved revision
Human scope confirmation: confirmed
Change: <change-id>
Parent: <parent-change-id|none>
Parent tag: <parent-approved-tag|none>
Commit: <full-sha>
Proposal: openspec/changes/<change-id>/proposal.md
```

The first `to-spec add` implementation is the sole self-hosting exception.
After explicit human approval and commit, the agent may use `rtk git` in one
action to create and push exactly the parent and child fixed-format tags, then
records the bootstrap evidence. The child records the parent tag so its link
remains immutable. No later change may bypass automatic `to-spec add` this way.

`to-spec add` TDD uses only a random local worktree and bare remote beneath
`redcap_library/.test_tmp/to_spec_add.<random>/`. A cleanup trap removes only
its own random fixture. The test does not use GitHub, network, credentials, the
real repository Git metadata, or generated mirror state.

GPT-5.6 Sol/high designs and writes `to-spec add` TDD. GPT-5.6 Terra/high is a
fallback only when Sol is unavailable and its reason is recorded. GPT-5.6
Luna/max implements production code after TDD is frozen.

Successful `to-spec add` output shows only the change ID, annotated tag, full
SHA, and tag-push result, followed by `摘要：已推送批准標籤；GitHub Issue mirror
由 GitHub Actions 後續處理。`. Refusal reports the reason, uses exit code `1`,
and states that no tag was created or pushed. A local tag push is not evidence
that a GitHub Issue exists.

Repeated approval is safe only when the remote has an existing tag with matching
target SHA and annotation. It reports `tag pushed: already-present` without
rewriting or re-pushing that tag. A local tag alone is not success: when remote
push status is unknown, retain the local tag, exit `1`, report the uncertainty,
and safely retry the same immutable push later. A mismatch refuses with exit
code `1`.
