## ADDED Requirements

### Requirement: Approved tag is the only automatic publication trigger
The system SHALL start automatic GitHub Issue publication only for a pushed
annotated tag named `openspec/<change-id>/approved/<short-sha>`. Before any
GitHub API call, it SHALL verify the tag type, full target SHA, short-SHA
prefix, annotation fields, and the named change's `proposal.md` path.
This first publisher change is the bootstrap exception: its own approved tag
does not require publication before the workflow exists. After this publisher
is installed, every later valid approved tag uses this requirement.

#### Scenario: Valid approved tag starts publication
- **WHEN** GitHub receives a valid pushed approved annotated tag
- **THEN** the workflow prepares one mirror payload for its change and revision

#### Scenario: Invalid tag is rejected before publication
- **WHEN** a pushed tag is lightweight, malformed, or has inconsistent
  annotation metadata
- **THEN** the workflow fails without calling the GitHub Issues API

#### Scenario: Publisher bootstrap does not mirror itself
- **WHEN** this first publisher change is approved and installed before a
  repository-owned publisher exists
- **THEN** its local TDD and review complete without requiring a GitHub Issue,
  and later approved tags become eligible for automatic publication

### Requirement: Repository administration is a one-time deployment prerequisite
Before a live mirror, a repository administrator SHALL enable GitHub Actions
and grant only the publisher job `issues: write`. Every valid approved tag
after installation SHALL use the same trigger rule; no first-tag selection or
additional publication approval exists. The scheduled cleanup job SHALL have no
GitHub API access and SHALL NOT receive `issues: write`.

#### Scenario: A later approved tag needs no extra release approval
- **WHEN** GitHub Actions is enabled and a valid later approved tag is pushed
- **THEN** the publisher applies its normal validation and mirror flow without
  a separately selected bootstrap tag

### Requirement: Approval-gated local tag push removes manual Git steps
`to-spec add <change-id> --confirm-scope` SHALL create and push the approved
annotated tag for the exact committed OpenSpec revision using the caller's
existing Git identity. Its annotation SHALL record human scope confirmation,
parent task, full revision SHA, and proposal path. It SHALL NOT push a branch
or store a credential. Without `--confirm-scope`, it SHALL refuse before tag
creation. The resulting tag push is the sole automatic-publication trigger;
after explicit human approval in the current task, the agent SHALL invoke this
underlying operation automatically. The user SHALL NOT need a separate
`to-spec add`, `git tag`, or `git push` step.

The first implementation of `to-spec add` is a self-hosting exception: after
explicit human approval and commit, the agent MAY use `rtk git` once to create
and push exactly two fixed-format tags in one bootstrap action: the pipeline
parent tag and publisher-child tag, because `to-spec add` does not yet exist.
It SHALL record that bootstrap action in change evidence. No later change may
use this raw-Git exception.

Before tag creation, it SHALL inspect only
`openspec/changes/<change-id>/` for modified, deleted, or untracked content.
It SHALL refuse when that scoped directory is not committed and SHALL allow
unrelated dirty worktree paths.

It SHALL use only the `origin` remote. Before tag creation it SHALL verify that
`origin` exists and is reachable; otherwise it SHALL exit one without creating
a tag. A remote uncertainty after local tag creation follows the retained-local-
tag rule.

The annotation SHALL be exactly:

```text
OpenSpec approved revision
Human scope confirmation: confirmed
Change: <change-id>
Parent: <parent-change-id|none>
Parent tag: <parent-approved-tag|none>
Commit: <full-sha>
Proposal: openspec/changes/<change-id>/proposal.md
```

For a child annotation, `Parent tag` SHALL resolve before any GitHub API call
to an annotated approved tag whose `Change` field equals `Parent`; the resolved
parent tag target and its declared `Commit` SHALL match. A missing, lightweight,
or mismatched parent tag is a refusal before API access. A root annotation uses
both `Parent: none` and `Parent tag: none`.

On success it SHALL display only the change ID, annotated tag, full SHA, tag
push result, and `摘要：已推送批准標籤；GitHub Issue mirror 由 GitHub Actions
後續處理。`. It SHALL NOT claim that an Issue exists. On a pre-tag refusal it
SHALL report the cause, use exit code `1`, and state that no tag was created or
pushed. The retained-local-tag uncertain-push scenario is reported separately
and SHALL state that the local tag remains.

#### Scenario: Explicit human confirmation creates one pushed tag
- **WHEN** `to-spec add <change-id> --confirm-scope` is run for an exact
  committed revision after human scope confirmation
- **THEN** it creates and pushes that revision's one valid approved annotated
  tag and the normal publisher may receive the tag-push event

#### Scenario: Missing confirmation blocks tag creation
- **WHEN** `to-spec add` lacks `--confirm-scope`
- **THEN** it refuses before creating or pushing a tag

#### Scenario: Uncommitted change content blocks an outdated approval tag
- **WHEN** the requested change's OpenSpec directory has modified, deleted, or
  untracked content
- **THEN** `to-spec add` exits one before tag creation

#### Scenario: Unrelated worktree content does not block approval
- **WHEN** only paths outside the requested change's OpenSpec directory are
  dirty
- **THEN** `to-spec add` may proceed with the committed change revision

#### Scenario: Missing or unreachable origin blocks tag creation
- **WHEN** `origin` is missing or unreachable before a tag is created
- **THEN** `to-spec add` exits one without creating a tag

#### Scenario: Root and child tags use one parseable annotation format
- **WHEN** `to-spec add` creates an approved tag
- **THEN** its annotation uses the fixed fields and writes both `Parent: none`
  and `Parent tag: none` only for a root change

#### Scenario: First tag-helper implementation bootstraps once
- **WHEN** the approved `to-spec add` implementation has no available
  `to-spec add` command
- **THEN** the agent may use `rtk git` in one action after commit to create the
  two named tags, records the bootstrap evidence, and later changes return to
  the automatic operation

#### Scenario: Successful tag push reports its evidence boundary
- **WHEN** `to-spec add --confirm-scope` pushes a valid approved tag
- **THEN** its Chinese summary states that GitHub Actions processes the later
  mirror and does not claim that an Issue already exists

#### Scenario: Repeated approval operation preserves an immutable tag
- **WHEN** `to-spec add --confirm-scope` verifies that the remote has the exact
  tag with matching target SHA and annotation
- **THEN** it succeeds as `tag pushed: already-present` without recreating,
  overwriting, or pushing the tag

#### Scenario: Local tag is retained when remote push is uncertain
- **WHEN** the operation created a matching local tag but cannot verify whether
  the remote received it
- **THEN** it retains that local tag, exits one, and reports that retry may push
  the same immutable tag without claiming that no tag exists

#### Scenario: Existing tag mismatch is rejected
- **WHEN** a local or remote approved tag differs in target SHA or annotation
- **THEN** `to-spec add` exits one without overwriting the tag

### Requirement: GitHub Issue mirrors an approved OpenSpec revision
The system SHALL create or reconcile one GitHub Issue whose body identifies the
change ID, approved tag, full target SHA, immutable proposal link, acceptance
summary, and a
deterministic idempotency marker. The Issue SHALL be a read-only mirror and
SHALL NOT add requirements, scheduling, approval, or ownership decisions.
Its first body line SHALL state `OpenSpec is canonical; this Issue is a
read-only mirror.`
Its title SHALL be `[OpenSpec] <change-id>`. Its only labels SHALL be
`openspec-mirror` and `state:<mirror-state>`. When the change has a parent
task, the body SHALL link to the parent's OpenSpec proposal.

#### Scenario: Parent-aware mirror remains a reader entry point
- **WHEN** an approved child change has a parent task
- **THEN** its one GitHub Issue uses the stable title, links to the parent and
  child proposals, and contains no priority, owner, or schedule label

#### Scenario: Issue links remain valid from an Issue page
- **WHEN** the publisher renders a proposal or parent-proposal link
- **THEN** it uses a GitHub blob permalink derived from `origin`, the approved
  full SHA, and the repository-relative proposal path; for a parent it first
  resolves the immutable `Parent tag`

#### Scenario: No matching Issue exists
- **WHEN** the publisher finds no Issue with the revision's idempotency marker
- **THEN** it creates exactly one Issue using the prepared payload

#### Scenario: Matching Issue exists after ambiguous response
- **WHEN** creation response is unavailable and a later query finds the same
  change ID, tag, full SHA, and marker
- **THEN** the publisher records `published` without creating another Issue

#### Scenario: Mirror fields conflict
- **WHEN** a found Issue has the idempotency marker but conflicts on change ID,
  tag, or full SHA
- **THEN** the publisher records `failed`, reports the mismatch, and does not
  overwrite the Issue

### Requirement: Publication retries and diagnosis are bounded
The system SHALL attempt automatic publication once and retry the unchanged
payload at most three times, at one-minute intervals. If all four attempts do
not publish, it SHALL diagnose read-only and record `failed`; diagnosis SHALL
not mutate OpenSpec, the approved tag, or any GitHub Issue.

#### Scenario: Transient publication failure recovers
- **WHEN** an automatic attempt fails and a later permitted attempt succeeds
- **THEN** the system records `published` with the same payload digest and
  idempotency marker

#### Scenario: All automatic attempts fail
- **WHEN** the first attempt and three retries fail
- **THEN** the system performs read-only diagnosis and records `failed`

### Requirement: Manual retry is one human-remedied send
The system SHALL permit `to-spec retry` only when the local state is `failed`,
diagnosis is complete, and the human records that the reported cause was
remedied. It SHALL reuse the stored payload and idempotency key, issue exactly
one send, and SHALL NOT start another automatic retry loop.

#### Scenario: Human performs an eligible retry
- **WHEN** a failed revision has completed diagnosis and a human confirms the
  remedy
- **THEN** the manual workflow dispatch sends the unchanged mirror once

#### Scenario: Retry precondition is absent
- **WHEN** state is not `failed`, diagnosis is incomplete, or no remedy is
  confirmed
- **THEN** `to-spec retry` refuses without calling GitHub

#### Scenario: Retry behavior is verified through its public outcome
- **WHEN** an eligible manual retry succeeds or fails against the fake API
- **THEN** the test observes exactly one send and `published` or retained
  `failed` state without asserting how staging payload is loaded or stored

### Requirement: Generated publication evidence is redacted and regenerable
The system SHALL store generated staging and status information under
`openspec/.to-spec/`, excluding credentials and authorization headers. It
SHALL expose `to-spec status` and `to-spec diff` from this local state and
local approved-tag metadata; the state SHALL NOT be treated as a source of
requirements.

When state is absent after archive or on a new runner, reconstruction SHALL read
the proposal from the approved tag target commit and annotation proposal path,
not from the pre-archive working-tree path. Archive SHALL NOT rewrite a tag or
Issue in order to support recovery.

Each change state SHALL be a valid JSON object at
`openspec/.to-spec/<change-id>/state.json` containing only `state`,
`approved_tag`, `commit_sha`, `idempotency_key`, `attempt`, `issue_number`,
`issue_url`, `diagnosis`, and `updated_at`. The implementation SHALL provide
`openspec/.to-spec/README.md` that explains every key's meaning, permitted
values, update condition, and nullability. Comments SHALL NOT be inserted into
`state.json`.

The system SHALL retain `state.json` for traceability. It SHALL remove only
regenerable staging payloads, payload diffs, and redacted diagnostic responses
after 30 days in terminal `published` or `failed` state. It SHALL NOT clean
`publishing` or `diagnosing` data, OpenSpec artifacts, approved tags, or
GitHub Issues. A daily GitHub Actions cleanup job SHALL run only on a
self-hosted runner with the persistent staging workspace mounted. It SHALL
fail configuration on a GitHub-hosted runner rather than treat its empty fresh
checkout as successful cleanup; it never calls the GitHub API.

#### Scenario: Status is requested without local state
- **WHEN** a user requests status on a clean runner with no generated state
- **THEN** the system reports `approved` for a valid local approved tag,
  otherwise `draft`, without contacting GitHub

#### Scenario: Terminal regenerable data expires safely
- **WHEN** a published or failed revision has retained regenerable staging data
  for more than 30 days
- **THEN** cleanup may remove only that regenerable data and preserves the
  state record and all canonical OpenSpec and GitHub evidence

#### Scenario: Scheduled cleanup does not access the tracker
- **WHEN** the daily cleanup workflow runs on its persistent self-hosted
  staging workspace
- **THEN** it inspects only local generated staging files and makes no GitHub
  API request

#### Scenario: Stateless runner rejects cleanup configuration
- **WHEN** scheduled cleanup is configured on a GitHub-hosted runner without
  persistent staging
- **THEN** it fails configuration rather than reporting a no-op cleanup

### Requirement: Status reports every known mirror state read-only
`to-spec status <change-id>` SHALL read only
`openspec/.to-spec/<change-id>/state.json` and local approved-tag metadata. It
SHALL report `draft`, `approved`, `publishing`, `published`, `diagnosing`, or
`failed` in a human-readable form with the next permitted action. A missing
state file SHALL report `approved` when a valid local approved annotated tag
exists, otherwise `draft`. Every known state SHALL exit zero. An unknown change
SHALL exit two; unreadable or invalid state data SHALL exit three.

#### Scenario: Status reports failed as a known business state
- **WHEN** generated state reports `failed` after completed diagnosis
- **THEN** status exits zero and displays the diagnosis and guarded retry as
  the next action

#### Scenario: Status reports a pre-publication change
- **WHEN** no generated state exists
- **THEN** status reports `approved` for a valid local approved tag, otherwise
  `draft`, without writing state or contacting GitHub

#### Scenario: Status cannot identify a change
- **WHEN** the requested change has no OpenSpec proposal
- **THEN** status exits two and identifies the missing change

#### Scenario: Status finds malformed generated data
- **WHEN** the state file cannot be parsed or names an unsupported state
- **THEN** status exits three and identifies invalid mirror state

### Requirement: TDD verifies observable outcomes without live GitHub access
The TDD contract SHALL verify observable business outcomes through a local fake
GitHub API. It SHALL NOT bind private functions, internal data structures, or
incidental call order. It SHALL verify that a matching marker creates no second
Issue, diagnosis performs no Issue mutation, and output does not reveal a token
or authorization header. A live GitHub Issue SHALL require separate repository
administrator authorization and SHALL NOT be a TDD prerequisite.

#### Scenario: Duplicate recovery uses a fake GitHub API
- **WHEN** the fake API reports an existing matching Issue after a create
  response is lost
- **THEN** the test observes one Issue, `published` state, and the existing
  Issue URL without asserting a private implementation detail

#### Scenario: Diagnosis preserves fake API state
- **WHEN** four automatic publication attempts fail against the fake API
- **THEN** diagnosis leaves its Issue collection unchanged and records a
  redacted `failed` result

#### Scenario: Live publication is not a TDD dependency
- **WHEN** the frozen TDD suite runs without GitHub credentials or network
  access
- **THEN** it completes using only the local fake API

#### Scenario: TDD uses the tag boundary rather than a private publisher
- **WHEN** TDD simulates a valid approved-tag workflow event against the fake
  GitHub API
- **THEN** it asserts the resulting mirror state and Issue outcome without
  requiring a public publish command or a private-module assertion

### Requirement: Local tag-push TDD fixture is isolated
The `to-spec add` TDD SHALL use only a temporary worktree and bare remote under
`redcap_library/.test_tmp/to_spec_add.<random>/`. Its cleanup SHALL remove only
the random directory created by that run. It SHALL NOT use GitHub, network,
credentials, the repository's real Git metadata, or generated mirror state.

#### Scenario: Interrupted test leaves only an owned fixture
- **WHEN** a local tag-push fixture test is interrupted before cleanup
- **THEN** any leftover is confined below `.test_tmp/to_spec_add.*` and no
  repository or remote GitHub state changed
