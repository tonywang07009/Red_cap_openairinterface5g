## ADDED Requirements

### Requirement: Daily reports shall use a fixed progress template
The system SHALL provide a Daily Report template with the fields `[Today Done]`, `[Evidence Path]`, `[Blocked]`, `[Needs Verification]`, `[Next Pull Item]`, and `[Status]`.

#### Scenario: Daily report can be checked
- **WHEN** a daily report is written for the workflow
- **THEN** the required fields are present and `[Status]` is one of `PASS`, `PARTIAL`, `FAIL`, or `BLOCKED`

### Requirement: Gate reports shall preserve validation evidence
The system SHALL provide a Gate Report template that records scope, spec mapping, modification points, validation evidence, limitations, and next action.

#### Scenario: Gate report blocks overclaiming
- **WHEN** a Gate report claims protocol or O-RAN control success
- **THEN** it includes RedCap/O-RAN-specific markers and does not treat attach, session, tunnel, or ping evidence alone as PASS

### Requirement: Static CI shall validate planning and report structure
The system SHALL provide a local static checker for workflow files, OpenSpec artifacts, control contract structure, report templates, and overclaim guard text.

#### Scenario: Static checker passes
- **WHEN** the checker is run from the repository root
- **THEN** it verifies required workflow files, OpenSpec delta specs, control-contract parameter fields, and report-template fields without requiring RFsim runtime

#### Scenario: Runtime checks remain separate
- **WHEN** static CI passes
- **THEN** the workflow still requires build/CTest or RFsim marker validation before runtime PASS is claimed
