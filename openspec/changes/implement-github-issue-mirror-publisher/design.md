## Context

The governance change defines an approved OpenSpec tag and a generic mirror
contract, but no publisher exists. The remote is GitHub; the confirmed tracker
and CI runner are GitHub Issues and GitHub Actions. Existing Jenkinsfiles are
GitLab-oriented and are not reused.

## Goals / Non-Goals

**Goals:**

- Turn one pushed, valid approved annotated tag into at most one GitHub Issue.
- Make retry and lost-response recovery safe through one deterministic key and
  a body marker that can be queried from GitHub.
- Keep all diagnostics read-only and redact token-bearing HTTP details.
- Make the publisher testable without a GitHub credential.

**Non-Goals:**

- Migrate or change existing Jenkins CI.
- Synchronize edits from GitHub Issues back into OpenSpec.
- Store a credential in the repository, grant approval, or let the GitHub
  publisher workflow create tags. The local `to-spec add` approval helper is in scope.
- Implement retention timing beyond the already agreed protected history rule.

### Bootstrap boundary

This change is the first publisher and cannot publish its own tag before the
workflow exists. It remains subject to human approval, approved-tag evidence,
local fake-API TDD, and code review, but its own Issue mirror is intentionally
not an acceptance condition. After installation, the next approved tag starts
the normal GitHub Actions publication path.

## Decisions

### GitHub Actions is the sole automatic entry point

A workflow runs on pushes matching `openspec/<change-id>/approved/<short-sha>`.
It first validates that the ref is an annotated tag, resolves its full target
SHA, checks the annotation fields, and verifies that `proposal.md` belongs to
the named change. Invalid tags stop before GitHub API access.

GitHub Actions is selected over the existing Jenkinsfiles because those files
are parameterized for GitLab CI work and do not provide a safe tag publisher.
Before the first live mirror, a repository administrator enables Actions once
and grants `issues: write` only to the publisher job. The cleanup job has no
GitHub API access or Issue permission. No later approved tag needs an extra
release approval: valid tag push is sufficient.

### Local approval gate creates and pushes the annotated tag

`to-spec add <change-id> --confirm-scope` is invoked only after the human has
confirmed scope. It creates the annotated tag and pushes only that tag using
the caller's existing Git identity. Its annotation is the durable confirmation
record for the exact revision; it contains the confirmation, parent task, full
SHA, and proposal path. This removes the separate manual `git tag` and
`git push` steps without adding a GitHub App, PAT, repository secret, branch
push, or a self-referential approval file. The operation refuses before tag
creation when the explicit confirmation flag is absent. After an explicit
human approval in the current task, the agent invokes the underlying operation
automatically; the user does not run `to-spec add`. The tag-push publisher
trigger stays unchanged. Success reports only change ID, tag, full SHA, tag
push result, and `摘要：已推送批准標籤；GitHub Issue mirror 由 GitHub Actions
後續處理。`; this prevents a local tag-push result from overstating GitHub Issue
publication. Every refusal and local tag-push failure returns exit code `1`;
the reason remains in the human-readable error and Chinese summary.

Before creating a tag, the operation checks only the requested change's
`openspec/changes/<change-id>/` directory for modified, deleted, or untracked
content. A scoped dirty path would make an approved tag point to an older
revision, so it refuses. Unrelated worktree changes remain allowed.

The only permitted remote is `origin`. The operation verifies it exists and is
reachable before tag creation, so a preflight failure leaves no tag. If it
becomes uncertain after a local tag exists, the retained-local-tag rule applies.

Tag annotations use one parseable format. Root changes write `Parent: none`;
child changes use their parent change ID:

```text
OpenSpec approved revision
Human scope confirmation: confirmed
Change: <change-id>
Parent: <parent-change-id|none>
Parent tag: <parent-approved-tag|none>
Commit: <full-sha>
Proposal: openspec/changes/<change-id>/proposal.md
```

For a child annotation, `Parent tag` must resolve before any GitHub API call to
an annotated approved tag whose `Change` equals `Parent`; its target and
declared `Commit` must match. A missing, lightweight, or mismatched parent tag
is a refusal before API access. Root annotations use `Parent: none` and
`Parent tag: none`.

Repeated `to-spec add --confirm-scope` is idempotent only when the remote tag
has the same target SHA and annotation. It then reports
`tag pushed: already-present` and does not rewrite or re-push the tag. A local
tag alone is not proof of remote publication: if a remote push result is
unknown, preserve the matching local tag and retry pushing it on the next run.
The uncertain result exits `1` and says that the local tag remains for
verification. Any local or remote mismatch is a refusal with exit code `1`.

The bootstrap bundle has one self-hosting action after the approved
pipeline-contract baseline commit: the agent uses `rtk git` to create exactly
two independent fixed-format parent and child tags. This is required because
`to-spec add` does not yet exist. It records that action in change evidence.
The child annotation carries the parent tag so its immutable proposal link can
be resolved. The tags approve the OpenSpec revision, not a later implementation
commit. No later change may use this raw-Git path.

### One stdlib publisher owns payload and reconciliation

A small Python standard-library publisher under the reusable RedCap tool
registry builds the payload, derives `sha256(change-id + full-sha + tag)`, and
uses the same marker in the Issue body and local staging record. It queries
GitHub for that marker before creating an Issue and after any ambiguous error.
No custom service, database, or third-party SDK is introduced.

The publisher writes generated, redacted state beneath `openspec/.to-spec/`.
The directory name supplies the change ID and `idempotency_key` is the payload
digest; its state record contains the tag, full SHA, GitHub Issue URL or
number, attempt count, terminal state, and diagnostic summary. It never
contains a token. The path is ignored by Git and is a regenerable staging area,
not a second source of requirements.

Each state is a valid JSON object at
`openspec/.to-spec/<change-id>/state.json`, with only `state`, `approved_tag`,
`commit_sha`, `idempotency_key`, `attempt`, `issue_number`, `issue_url`,
`diagnosis`, and `updated_at`. A sibling `.to-spec/README.md` is the durable
key memo; it documents every key's meaning, value domain, update condition,
and nullability without compromising JSON parsing.

The mirror title is `[OpenSpec] <change-id>`, so updates never produce a
second title convention. Its first line is `OpenSpec is canonical; this Issue
is a read-only mirror.` The body then contains the revision facts, OpenSpec
proposal link, acceptance summary, and deterministic marker. A child also links
its parent proposal. The only labels are `openspec-mirror` and the projected
`state:<mirror-state>` label.

`state.json` remains for traceability. A later cleanup implementation may
delete only regenerable payload, payload-diff, and redacted diagnosis files
older than 30 days after `published` or `failed`; active `publishing` and
`diagnosing` entries are protected. It must not delete state records, approved
tags, OpenSpec artifacts, or Issues. A daily GitHub Actions cleanup job runs
only on a self-hosted runner with the persistent staging workspace mounted;
a GitHub-hosted runner has no prior ignored staging to clean and SHALL fail
configuration rather than report a no-op cleanup as successful. The cleanup
job never calls the GitHub API.

### Retry is bounded by workflow input

The tag-triggered workflow performs one attempt plus three retries, with a
one-minute wait before each retry. On exhaustion it performs read-only
diagnosis and records `failed`. A `workflow_dispatch` retry requires the same
tag plus an explicit human-remedy acknowledgement; it loads the stored key and
payload, performs exactly one send, and never schedules automatic retries.

### Status is a planned read-only Bash entry point

`redcap_library/bash_tool/scripts/to_spec_status.sh <change-id>` will be the
first registered public-operation implementation. It reads
`openspec/.to-spec/<change-id>/state.json`; when absent, it uses a valid local
annotated approved tag to distinguish `approved` from `draft`. It prints the
state, relevant Issue or diagnosis information, and next action. Known states
exit zero; missing changes exit two; invalid state data exits three. It does
not contact GitHub or create the generated-state directory.

## Status TDD contract (pending)

- Model / effort: GPT-5.6 Sol / high; Terra / high is permitted only when Sol
  is unavailable and the recorded fallback reason precedes test writing.
- Test boundary: `to_spec_status.sh <change-id>` output and exit code against a
  temporary local OpenSpec/Git fixture root.
- Acceptance links: `Status reports every known mirror state read-only`.
- Irreversible side effects: no write beneath fixture `openspec/`, no Git tag
  mutation, no GitHub request, and no credential output.
- Boundary gate: clear; human confirmation on 2026-08-15.
- Test files: `redcap_library/bash_tool/scripts/test_to_spec_status.sh`.
- Frozen SHA-256: pending test creation.
- Frozen test-diff baseline: pending test creation.

### Tests freeze the public seam before implementation

The TDD contract in this change will define fixture-driven checks for tag
validation, deterministic key generation, duplicate recovery, mismatch
rejection, four-attempt exhaustion, and one-shot manual retry. The tests and
registry entry live in `redcap_library/`, become read-only before implementation,
and record SHA-256 plus a frozen test-diff baseline in this design.

The contract binds externally observable business outcomes, not private
functions, data structures, or incidental call order. It additionally tests
three irreversible or security-relevant outcomes: a matching marker cannot
create a second Issue; diagnosis cannot mutate an Issue; and logs or generated
state cannot reveal a token or authorization header. Tests use a local fake
GitHub API only. A live GitHub Issue is separate administrator-authorized
acceptance evidence, not a TDD prerequisite.

TDD enters through the approved-tag/workflow boundary and asserts the resulting
mirror state, Issue count, Issue URL, and redacted report. It does not expose a
public `to-spec publish` command or treat a publisher-private module as a
contract. `to-spec add` remains approval-gated; `status`, `diff`, and guarded
`retry` remain the only public mirror-state operations. Retry tests verify
precondition refusal, exactly one send, and terminal outcome; they do not bind
staging payload persistence.

### Planned `to-spec add` TDD environment

The public seam is `to-spec add <change-id> --confirm-scope`. Its test program
will be `redcap_library/bash_tool/scripts/test_to_spec_add.sh`. Each run creates
an isolated worktree and bare remote only beneath a random
`redcap_library/.test_tmp/to_spec_add.<random>/` directory. A cleanup trap may
remove only that run's own random directory. The test never uses GitHub,
network, credentials, the repository's real `.git`, or `openspec/.to-spec/`.
Interrupted leftovers are confined to `.test_tmp/to_spec_add.*` for a later
safe owned-fixture cleanup.

The TDD authoring model is GPT-5.6 Sol / high. GPT-5.6 Terra / high is allowed
only when Sol is unavailable and the specific reason is recorded before a test
is written. GPT-5.6 Luna / max is reserved for production implementation after
the test hash and permissions are frozen.

## Risks / Trade-offs

- [GitHub token lacks Issue permission] → fail before mutation, redact the
  response, and enter read-only diagnosis.
- [Create response is lost] → query the body marker; a matching Issue becomes
  `published`, while a mismatching mirror remains `failed` without overwrite.
- [Same user can bypass chmod] → final review compares frozen SHA-256 and the
  frozen test-diff baseline.
- [Local generated state is absent after archive or on a new runner] → rebuild
  staging from the approved tag target commit, annotation proposal path, and
  GitHub marker before creating anything.

## Migration Plan

1. Add the publisher, registry entry, frozen tests, and GitHub Actions workflow.
2. Run dry-run fixtures and workflow syntax checks without a credential.
3. Human approves scope; the agent creates and pushes the annotated tag.
4. Push event triggers the workflow; the first later valid approved tag performs
   the first real publication.
5. Roll back by disabling the workflow. Existing GitHub Issues remain read-only
   mirrors and approved tags remain immutable history.

## Open Questions

Repository administrators must enable GitHub Actions and permit `issues: write`
for the publisher job before a live run. No separately selected first tag is
needed: the first later valid approved tag is normal live-mirror acceptance
evidence.
