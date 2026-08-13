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

### Requirement: GitHub Issue mirrors an approved OpenSpec revision
The system SHALL create or reconcile one GitHub Issue whose body identifies the
change ID, approved tag, full target SHA, proposal link, approval scope, and a
deterministic idempotency marker. The Issue SHALL be a read-only mirror and
SHALL NOT add requirements, scheduling, approval, or ownership decisions.

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
SHALL expose `to-spec status` and `to-spec diff` from this state or a
read-only GitHub marker query; the state SHALL NOT be treated as a source of
requirements.

#### Scenario: Status is requested without local state
- **WHEN** a user requests status on a clean runner with no generated state
- **THEN** the system performs only a read-only marker query and reports the
  result or its inability to query

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
