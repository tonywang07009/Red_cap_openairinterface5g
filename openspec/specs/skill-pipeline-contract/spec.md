## Purpose

Define the canonical OpenSpec-to-archive pipeline, including approval, mirror,
TDD, implementation, review, and archive boundaries.

## Requirements

### Requirement: Human-approved OpenSpec is the canonical change record
The workflow SHALL treat OpenSpec as the canonical requirement, architecture,
task, acceptance, and scheduling record. A human scope-confirmed, agent-created
and pushed annotated approved tag SHALL be the only mirror-publication trigger.
An issue tracker MUST remain a synchronization mirror and MUST NOT add
requirements or schedule. The initial parent task that installs the publisher
and its named publisher child are a bootstrap exception: they SHALL still have
human approval, approved tags, TDD or validation, and review, but SHALL NOT
require their own Issue mirror before the publisher exists. Every later approved
tag SHALL use the normal publication route.

#### Scenario: Human approves a change
- **WHEN** a human confirms scope for an OpenSpec revision and the agent pushes
  its annotated approved tag
- **THEN** automation may mirror that exact revision and no agent, CI job, or
  `to-spec` operation may approve a revision itself

#### Scenario: Publisher bootstrap completes
- **WHEN** the approved parent task and its named publisher child install the
  first repository-owned publisher
- **THEN** they complete local validation and review without requiring their
  own Issue mirror, and the next approved tag uses the normal mirror route

### Requirement: Mirror publication is idempotent and diagnosable
The mirror workflow SHALL create one staging payload and idempotency key from
an approved revision, attempt publication once plus three one-minute retries,
and then run read-only diagnosis. `to-spec add` is the approval-gated tag
operation; its public mirror-state operations SHALL be `status`, `diff`, and
single-attempt `retry`. A retry MUST reuse the original payload and key and
MUST NOT start a retry loop or create a duplicate issue.

#### Scenario: Publication response is lost
- **WHEN** diagnosis finds an existing issue for the original idempotency key
  whose change ID, approved tag, and full SHA match the local payload
- **THEN** it records the existing issue as published without creating another
  issue

### Requirement: Code changes preserve an immutable TDD contract
A code change SHALL record its agreed seam, model/effort, test paths, frozen
SHA-256 values, and approved acceptance links in `design.md`. Implementation
MUST NOT modify protected TDD tests. Acceptance SHALL execute those tests and
reject a changed hash or test diff. TDD authoring SHALL use Sol/high when
available or record the approved Terra/high fallback and reason. Before writing
any test, TDD SHALL record the test boundary, acceptance condition, and
irreversible side effects. If any one is unclear, it SHALL create or modify no
test and SHALL invoke `grill-with-docs`; it may resume only after the resulting
human decision is recorded in the OpenSpec/TDD contract. Tests SHALL bind
observable business outcomes rather than private functions, internal data
structures, or incidental call order.

#### Scenario: Review detects a changed protected test
- **WHEN** final SHA-256 or Git diff differs from the frozen TDD contract
- **THEN** review rejects the implementation before archive

#### Scenario: TDD boundary is clear
- **WHEN** the approved revision makes the boundary, acceptance condition, and
  irreversible side effects clear
- **THEN** TDD records them in the contract and may write the first test

#### Scenario: TDD boundary is unclear
- **WHEN** the boundary, acceptance condition, or irreversible side effect is
  unclear
- **THEN** TDD writes no test and invokes `grill-with-docs` before resuming

### Requirement: Review separates standards from specified behavior
Every change SHALL receive separate Standards and Spec review reports. Review
SHALL assess boundaries, business logic, and readability without merging those
axes. A behavior, protocol-state, or data-decision branch MUST trace to an
approved requirement or TDD acceptance criterion. Documentation/governance
changes SHALL validate links, rule consistency, boundaries, and approval
traceability without inventing program tests.

#### Scenario: Review finds an untraced behavior branch
- **WHEN** a code branch changes observable behavior, protocol state, or a data
  decision without an approved requirement or acceptance reference
- **THEN** the Spec report records a finding

### Requirement: Archive is based on canonical completion evidence
An OpenSpec change SHALL archive only after it has a valid approved annotated
tag and all implementation, validation, and review tasks are complete. A code
change SHALL have frozen TDD evidence and code review; a documentation or
governance change SHALL have its validation contract and documentation/governance
review. A GitHub Issue mirror is external projection evidence and SHALL NOT
block archive when it is absent or `failed`.

A governance parent SHALL archive when its own contract, validation, and review
tasks are complete. A separately approved implementation child remains its own
OpenSpec change and SHALL NOT block that parent archive.

#### Scenario: External mirror failure does not block a completed change
- **WHEN** a change has complete canonical tasks and evidence but its Issue
  mirror is absent or diagnosed as `failed`
- **THEN** the change may archive while retaining the external diagnosis for
  later idempotent recovery

### Requirement: Implementation uses a minimal owner-aware design check
Before modifying production code, implementation SHALL identify the owner
module, existing reusable path, seam, locality of the change, and the smallest
accepted solution. It SHALL escalate to architecture review only when ownership
is unclear, major seams are crossed, a new adapter is required, or existing
interfaces cannot support the agreed test.

#### Scenario: A bug has multiple callers
- **WHEN** a proposed fix touches a function with multiple callers
- **THEN** implementation traces the callers and applies the smallest fix at
  the shared owner when that preserves the approved behavior
