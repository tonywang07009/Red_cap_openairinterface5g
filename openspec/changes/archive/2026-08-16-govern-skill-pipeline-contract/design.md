## Context

The accepted workflow is `grill-with-docs → OpenSpec → human approval tag →
to-spec mirror → TDD → implement → code-review → archive`. Existing skill
files predate it and use incompatible defaults.

## Goals / Non-Goals

**Goals:**

- Make OpenSpec canonical and prevent agents, CI, and `to-spec` from granting
  approval.
- Preserve a test contract across implementation and review.
- Route source, Git, and artifact inspection consistently.

**Non-Goals:**

- Implement tracker credentials, CI configuration, or remote publication.
- Rebuild the issue tracker or change RAN/runtime behavior.
- Require architecture scanning for every implementation.

## Decisions

### Approval and mirror

A human confirms scope, then the agent creates and pushes
`openspec/<change-id>/approved/<short-sha>` as an annotated tag. Its annotation
identifies the parent task, full revision SHA, and the change `proposal.md`. A
tag-push CI job is the future publisher. It
creates one staging payload and idempotency key, attempts publication once plus
three retries at one-minute intervals, then performs read-only diagnosis.

The issue tracker is a mirror. `to-spec add` is the approval-gated tag
operation; `to-spec status`, `to-spec diff`, and `to-spec retry` are the only
public mirror-state operations. Retry is a single human action after diagnosis;
it never starts another automatic retry loop or creates a second issue.

The governance parent and the first publisher child form one bootstrap bundle.
Their approved tags preserve the human decision, but neither requires an Issue
mirror before the publisher exists. The bootstrap still requires its local
validation/TDD and review. Once installed, the publisher handles every later
approved tag through the normal tag-push route.

### Test and implementation contract

For code changes, `design.md` contains the agreed seam, model/effort, test
paths, SHA-256 values, and acceptance links. Tests are made read-only before
Luna/max implementation; final acceptance compares their SHA-256 values and
frozen test-diff baseline. Terra/high is the approved TDD-design fallback when Sol/high is not
available, with the reason recorded. Before test authoring, TDD records the
test boundary, acceptance condition, and irreversible side effects. A clear
approved contract proceeds directly; any uncertainty stops authoring before a
test is created or changed and invokes `grill-with-docs`. Tests preserve
refactoring freedom by asserting observable business outcomes, not private
implementation structure.

Before implementation, a short design check finds the owner module and seam,
records why the smallest change has locality, and escalates only when the work
crosses major seams, requires a new adapter, or cannot be tested through the
existing interface.

### Review and documentation changes

Code review keeps independent Standards and Spec reports. It labels findings
through boundary, business-logic, and readability lenses; a branch changing
observable behavior, protocol state, or data decision must trace to an
approved requirement or acceptance criterion. Documentation/governance changes
use the same two reports but validate links, rules, boundaries, and approval
traceability instead of requiring program tests.

### Archive uses canonical evidence, not mirror availability

Archive requires a valid approved tag, complete implementation/validation/review
tasks, frozen TDD plus code review for code changes, or validation contract plus
documentation/governance review for non-code changes. GitHub Issue publication
is an external projection: an absent or failed mirror retains diagnosis for
recovery but does not block archive. This preserves OpenSpec as the canonical
record and avoids treating a one-time platform outage as unfinished code work.

The governance parent archives after its own contract, validation, and review
tasks complete. Publisher implementation is owned by its named child change;
that child remains independently traceable and does not keep the parent open.

## Risks / Trade-offs

- [Same user can defeat chmod] → SHA-256 and frozen test-diff baseline make the violation
  visible; review rejects it.
- [CI/tag automation is not implemented here] → Skill text is an executable
  contract only; no claim of publication behavior is made until CI exists.
- [Strict routes can block a lookup] → A named, recorded fallback is allowed
  only when the primary tool cannot perform it.
