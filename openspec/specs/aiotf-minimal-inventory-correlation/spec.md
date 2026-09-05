## Purpose

Define the minimal AIOTF correlation, network-owned reader binding, session
roles, deterministic scheduling, failover, and report arbitration boundary.

## Requirements

### Requirement: Minimal inventory correlation
The minimal AIOTF boundary SHALL create one Correlation ID per accepted Inventory Request and associate all resulting UE Reader reports with that ID.

#### Scenario: Accepted request receives report
- **WHEN** AIOTF accepts an Inventory Request and receives a valid UE Reader Inventory Report before timeout
- **THEN** it returns the report with the request Correlation ID and a completed result.

### Requirement: Rejection and timeout distinction
The minimal AIOTF boundary SHALL distinguish rejected requests from accepted requests that time out without an accepted Inventory Report.

#### Scenario: No accepted UE Reader report
- **WHEN** an accepted Inventory Request reaches its configured timeout without a valid UE Reader report
- **THEN** AIOTF returns a timeout result with the original Correlation ID.

### Requirement: Network-owned reader binding
AIOTF SHALL own the Tag-to-reader binding table. Each binding SHALL contain a stable Tag ID, eligible reader handles, default primary reader, binding epoch, and resource policy. A Tag SHALL NOT receive or store the eligible-reader list.

#### Scenario: Bounded 60-tag binding
- **WHEN** the bounded two-reader profile is loaded
- **THEN** Tags 1-20 are eligible only for UE1, Tags 21-40 are eligible for UE1 and UE2, and Tags 41-60 are eligible only for UE2.

#### Scenario: Balanced default primary assignment
- **WHEN** AIOTF creates normal-mode sessions for all 60 tags
- **THEN** UE1 is primary for Tags 1-30 and UE2 is primary for Tags 31-60.

### Requirement: Per-session reader roles
AIOTF SHALL select exactly one primary R2D sender for each tag transaction. Normal mode SHALL activate only that reader. Diversity mode MAY activate both eligible readers for Tags 21-40, but non-primary readers SHALL receive D2R only and SHALL NOT transmit R2D.

#### Scenario: Shared tag in diversity mode
- **WHEN** a diversity session targets Tag 25 with UE1 selected as primary
- **THEN** UE1 sends R2D and both UE1 and UE2 may report independently decoded D2R results.

#### Scenario: Exclusive reader unavailable
- **WHEN** the only eligible reader for a tag is unavailable
- **THEN** AIOTF returns an unavailable or timeout outcome and does not silently activate an ineligible reader.

### Requirement: Binding epoch and failover
AIOTF SHALL increment the binding epoch when the primary reader changes. It SHALL reject an epoch-mismatched report as a result candidate while retaining it as stale measurement evidence.

#### Scenario: Shared-tag primary failover
- **WHEN** the primary reader for a Tag in 21-40 becomes unavailable before R2D transmission
- **THEN** AIOTF selects the other eligible reader, increments the binding epoch, and starts a new tag transaction.

### Requirement: Deterministic multi-tag scheduling
AIOTF SHALL decompose the bounded 60-tag inventory into single-tag radio transactions and SHALL assign no more than one Tag to the same initial response slot. The profile SHALL NOT claim concurrent-tag anti-collision support.

#### Scenario: Full bounded inventory
- **WHEN** an accepted request targets Tags 1-60
- **THEN** AIOTF creates 60 correlated tag transactions with deterministic ordering and a separate result state for each Tag.

### Requirement: First-valid report arbitration
AIOTF SHALL accept a report as a result candidate only when its Correlation ID, session ID, Tag ID, binding epoch, active reader, deadline, and CRC outcome are valid. The first valid report SHALL complete the Tag result. Other reports SHALL be retained as measurement evidence without MRC, soft combining, or IQ combining.

#### Scenario: Identical valid reports
- **WHEN** two active readers return the same valid payload for the same Tag transaction
- **THEN** AIOTF keeps the first report as the result and marks the other report as duplicate evidence.

#### Scenario: Conflicting valid reports
- **WHEN** two active readers return different valid payloads for the same Tag transaction
- **THEN** AIOTF keeps the first report as the provisional result and records a conflicting-valid-reports outcome for review.
