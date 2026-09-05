## ADDED Requirements

### Requirement: CW-dependent D2R acceptance
The UE Reader SHALL accept a D2R Inventory Report only when the configured CW source is present and the D2R payload passes Manchester and CRC validation.

#### Scenario: CW-present valid D2R
- **WHEN** CW is present and a tag emits a valid experimental D2R Inventory Report
- **THEN** the UE Reader decodes the report and emits a UE-to-gNB report marker.

#### Scenario: CW-absent D2R
- **WHEN** CW is absent and the same tag response is attempted
- **THEN** the UE Reader does not accept the Inventory Report and records a CW-absent outcome.

### Requirement: Deterministic validation faults
The tag simulator SHALL support deterministic valid, CRC-corrupt, invalid-Manchester, and CW-absent cases.

#### Scenario: CRC corruption
- **WHEN** the tag simulator emits a CRC-corrupt D2R response with CW present
- **THEN** the UE Reader rejects the report as CRC-invalid.

### Requirement: Evidence boundary
The validation report SHALL distinguish protocol simulation, baseband proof, and RFsim runtime evidence.

#### Scenario: Protocol-only result
- **WHEN** only the tag simulator round-trip has passed
- **THEN** the report marks RF/backscatter validation as not yet proven.

### Requirement: Independent multi-reader evidence
When diversity mode activates two readers, each UE Reader SHALL independently decode Manchester, validate CRC, and emit its own measurement report. The validation path SHALL NOT combine IQ samples, soft bits, or decoded payloads across readers.

#### Scenario: One valid and one invalid reader report
- **WHEN** one active reader reports a valid payload and the other reports a CRC or line-code failure
- **THEN** the valid report completes the Tag result and both reader outcomes remain in the evidence record.
