## ADDED Requirements

### Requirement: BWP trigger0 reconfiguration shall not crash the gNB
The system SHALL complete a telnet-triggered BWP switch from additional BWP 1 to initial BWP 0 without terminating the gNB process.

#### Scenario: Trigger BWP 0 after UE is on BWP 1
- **WHEN** a connected UE has active DL and UL BWP ID 1 and the operator issues `ci trigger_bwp_switch 0`
- **THEN** the gNB process remains running and no `Segmentation fault` is emitted in the runtime logs

#### Scenario: BWP 0 candidate is applied after reconfiguration ACK
- **WHEN** the UE acknowledges the BWP 0 RRC reconfiguration
- **THEN** the gNB applies the pending cell group and emits evidence that DL and UL BWP state switched to BWP 0

### Requirement: BWP reconfiguration shall not mutate live cell-group state before candidate success
The system MUST build BWP reconfiguration data as a candidate before replacing live UE cell-group state.

#### Scenario: Candidate creation fails
- **WHEN** BWP reconfiguration candidate creation fails
- **THEN** the live `UE->CellGroup` remains unchanged and no pending `UE->reconfigCellGroup` is submitted

#### Scenario: Candidate encoding fails
- **WHEN** ASN.1 encoding of the candidate cell group fails
- **THEN** the live `UE->CellGroup` and `UE->local_bwp_id` remain at their pre-trigger values

### Requirement: BWP reconfiguration shall use encode-before-submit semantics
The system MUST encode the candidate cell group successfully before assigning it to pending UE state or sending a UE context modification request.

#### Scenario: Encoded candidate is submitted
- **WHEN** BWP candidate creation and ASN.1 encoding both succeed
- **THEN** the encoded cell group is sent through the existing UE context modification path and the candidate is stored as pending UE reconfiguration state

### Requirement: Gate 5 status shall be based on post-fix runtime evidence
The validation project SHALL distinguish crash-reproduction evidence from post-fix Gate 5 evidence.

#### Scenario: Fixed matrix produces BWP metrics
- **WHEN** the BWP matrix is rerun after the crash fix
- **THEN** `BWP_results.csv`, plots, and summary text are updated only from the new runtime evidence

#### Scenario: Runtime hooks remain label-only
- **WHEN** traffic load, BWP inactivity timer, or switch-delay behavior is still represented only by wrapper or manifest labels
- **THEN** the project records keep those fields marked as label-only or `[Needs Verification]` and do not claim paper-comparable Gate 5 PASS

### Requirement: Project implementation shall receive a code-review gate
The validation project SHALL include a code-review gate for all current project implementation changes before final Gate 7 reporting.

#### Scenario: Review gate covers active project changes
- **WHEN** the review gate is executed
- **THEN** the review covers BWP/SDT wrappers, runtime helper scripts, extractors, aggregators, CSV merge behavior, runtime evidence updates, and report/plot alignment
