## ADDED Requirements

### Requirement: Deterministic adaptive C-DRX A/B campaigns
The system SHALL execute each downlink or uplink C-DRX campaign with 330 scheduled arrivals, a recorded traffic-trace seed, and a recorded baseline profile. It SHALL score only arrivals 31 through 330 and SHALL keep traffic direction separate until both single-direction campaigns have completed.

#### Scenario: Reproducible baseline campaign
- **WHEN** an operator starts Arm A with a saved traffic trace and the fixed `drx-320-10` baseline
- **THEN** the runner applies the baseline once, records all 330 scheduled arrivals, and associates the same profile and policy version with all 300 scored arrivals

#### Scenario: Direction isolation
- **WHEN** an operator starts a downlink or uplink campaign
- **THEN** the runner stores direction-specific source timestamps and does not merge the results into a bidirectional claim

### Requirement: Versioned xApp prediction intent
The xApp SHALL consume only a committed set of 30 arrival intervals, calculate descriptive statistics and a z-score interval, and emit a versioned DRX policy intent for the next 30 arrivals. The intent SHALL include a prediction-quality result and a conservative fallback request when the selected candidate is not reliable.

#### Scenario: Bounded prediction
- **WHEN** the xApp receives 30 committed intervals whose predicted upper bound is within the configured experiment limit
- **THEN** it emits one policy intent containing the version, `mu`, `sigma`, lower and upper bounds, and candidate DRX values

#### Scenario: Unreliable prediction
- **WHEN** the prediction is outside configured bounds or fails a quality guard
- **THEN** the xApp emits a fallback-profile intent and records the reason without claiming a valid prediction

### Requirement: dApp-gNB DRX safety boundary
The dApp/gNB guard SHALL validate every DRX policy intent before runtime application and SHALL be the only component allowed to accept, reject, apply, or roll back a policy. It SHALL use an RRC configuration path for DRX-cycle or On Duration changes and SHALL treat a DRX Command MAC CE as a separately guarded early-active-state action.

#### Scenario: Accepted RRC DRX update
- **WHEN** a policy intent has a new version, legal enumerated values, a valid rollback profile, and passes the local state guard
- **THEN** the dApp applies the update through the selected gNB RRC surface and emits an applied-state marker with the policy version

#### Scenario: Rejected unsafe update
- **WHEN** a policy intent contains an unsupported value, stale version, failed cooldown check, or unavailable rollback profile
- **THEN** the dApp rejects it, preserves the sample evidence, and emits a reason-coded reject marker

#### Scenario: Guarded DRX Command
- **WHEN** the dApp evaluates an optional DRX Command action
- **THEN** it verifies the defined queue and outstanding-work guards and emits a distinct marker without changing the configured DRX-cycle or On Duration values

### Requirement: End-to-end evidence and window commit
The validation system SHALL correlate xApp request, E2 acknowledgement, dApp decision, gNB applied state, expected UE/RRC completion evidence, and scored traffic outcome by policy version. It SHALL clear a 30-sample history only after the policy version is committed or shall retain it with a failure record.

#### Scenario: Successful policy commit
- **WHEN** a requested policy receives all required control, gNB, and UE/RRC evidence
- **THEN** the system records the commit, starts the next 30-sample collection window, and associates subsequent scored arrivals with that policy version

#### Scenario: Incomplete control path
- **WHEN** the system receives an E2 acknowledgement but lacks the required gNB or UE/RRC evidence before timeout
- **THEN** it reports the policy as incomplete, retains the evidence window, and does not claim runtime application

### Requirement: Reproduction and source trace documentation
The project SHALL provide paired English and Traditional Chinese reproduction documents covering prerequisites, deterministic trace generation, build, run, validation, evidence interpretation, and rollback. The documentation SHALL end with a trace-code guide that maps the data and control flow across traffic generation, xApp, E2, dApp, gNB RRC/MAC, UE MAC, and validation markers.

#### Scenario: Trace-code guide use
- **WHEN** a reader opens the final trace-code guide
- **THEN** each trace step identifies the source file, symbol, input/output, expected marker, and next trace location needed to follow one DRX policy update end to end
