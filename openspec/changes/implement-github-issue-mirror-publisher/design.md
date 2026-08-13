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
- Store a credential in the repository, create tags, or grant approval.
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

### One stdlib publisher owns payload and reconciliation

A small Python standard-library publisher under the reusable RedCap tool
registry builds the payload, derives `sha256(change-id + full-sha + tag)`, and
uses the same marker in the Issue body and local staging record. It queries
GitHub for that marker before creating an Issue and after any ambiguous error.
No custom service, database, or third-party SDK is introduced.

The publisher writes generated, redacted state beneath `openspec/.to-spec/`.
It contains the change ID, tag, full SHA, payload digest, GitHub Issue URL or
number, attempt count, terminal state, and diagnostic summary; it never
contains a token. The path is ignored by Git and is a regenerable staging
area, not a second source of requirements.

### Retry is bounded by workflow input

The tag-triggered workflow performs one attempt plus three retries, with a
one-minute wait before each retry. On exhaustion it performs read-only
diagnosis and records `failed`. A `workflow_dispatch` retry requires the same
tag plus an explicit human-remedy acknowledgement; it loads the stored key and
payload, performs exactly one send, and never schedules automatic retries.

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
contract. `status`, `diff`, and guarded `retry` remain the only public
`to-spec` operations. Retry tests verify precondition refusal, exactly one
send, and terminal outcome; they do not bind staging payload persistence.

## Risks / Trade-offs

- [GitHub token lacks Issue permission] → fail before mutation, redact the
  response, and enter read-only diagnosis.
- [Create response is lost] → query the body marker; a matching Issue becomes
  `published`, while a mismatching mirror remains `failed` without overwrite.
- [Same user can bypass chmod] → final review compares frozen SHA-256 and the
  frozen test-diff baseline.
- [Local generated state is absent on a new runner] → rebuild staging from the
  approved tag and GitHub marker before creating anything.

## Migration Plan

1. Add the publisher, registry entry, frozen tests, and GitHub Actions workflow.
2. Run dry-run fixtures and workflow syntax checks without a credential.
3. Human approves the OpenSpec revision and creates the annotated tag.
4. Push that tag; the workflow performs the first real publication.
5. Roll back by disabling the workflow. Existing GitHub Issues remain read-only
   mirrors and approved tags remain immutable history.

## Open Questions

None for the implementation contract. Repository administrators must enable
GitHub Actions and permit `issues: write` for the workflow before a live run.
