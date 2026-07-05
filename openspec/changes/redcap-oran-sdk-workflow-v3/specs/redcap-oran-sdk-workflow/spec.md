## ADDED Requirements

### Requirement: Workflow 3.0 shall define a minimal RedCap O-RAN SDK project route
The system SHALL provide a project route for RedCap O-RAN SDK work that keeps project planning, agent rules, milestones, validation templates, and reports in separate files.

#### Scenario: Project route is present
- **WHEN** a future agent enters the RedCap O-RAN SDK workflow
- **THEN** it can find `project_plan.md` and `agent_rules.md` under `agent_doc/Project_management/projects/redcap_oran_sdk_workflow_v3/`

#### Scenario: Root guidance stays short
- **WHEN** root `AGENTS.md` lists the workflow project
- **THEN** it points to the project plan and agent rules without embedding milestone details

### Requirement: SDK v1 shall separate rApp, xApp, and dApp/gNB guard ownership
The system SHALL document SDK v1 ownership so that rApp policy, xApp control decisions, and dApp/gNB runtime guards do not write the same runtime state directly.

#### Scenario: rApp policy remains declarative
- **WHEN** an rApp policy is defined
- **THEN** it emits policy/configuration intent and does not directly mutate OAI runtime state

#### Scenario: KPM remains observation only
- **WHEN** an xApp consumes KPM data
- **THEN** the workflow describes KPM as observation input and uses E2SM-RC, a custom SM, or a dApp local API for control output

#### Scenario: dApp/gNB guard owns apply safety
- **WHEN** a runtime update is requested
- **THEN** the dApp/gNB guard validates the control contract, bounds, ownership, ACK/NACK, rollback, and applied-parameter markers before claiming success

### Requirement: Pull workflow shall limit active work
The system SHALL define pull-based execution criteria before each SDK or validation task is started.

#### Scenario: Work item is ready
- **WHEN** an SDK work item is pulled
- **THEN** it has checked source/spec context, expected marker, validation command, and report target

#### Scenario: WIP is bounded
- **WHEN** multiple tasks are available
- **THEN** the workflow allows at most one C-code Gate and one docs/CI Gate to be active at the same time

### Requirement: Reference maps shall guide SDK placement before implementation
The system SHALL document how the updated `dev_refer/` library maps to xApp, dApp, and rApp SDK planning before new SDK source trees are created.

#### Scenario: Reference map is present
- **WHEN** a future agent pulls an SDK planning task
- **THEN** it can find a `dev_refer/` overview and an O-RAN spec usage map under the Workflow 3.0 project docs

#### Scenario: OAI-style channel layout is present
- **WHEN** a future agent pulls an SDK implementation task
- **THEN** the workflow identifies `openair2/E2AP/REDCAP_SDK/` as the RedCap xApp wrapper target, `openair2/E3AP/` as the dApp target, and rApp as docs-first only

### Requirement: SDK scaffold shall provide minimal xApp, dApp, and rApp entry points
The system SHALL provide a first SDK scaffold slice that is small enough to validate without RFsim runtime.

#### Scenario: xApp SDK builder is reusable
- **WHEN** the RedCap UL PRB control helper is built
- **THEN** it uses a reusable xApp SDK builder for the E2SM-RC control request

#### Scenario: dApp guard SDK is present
- **WHEN** a dApp/gNB guard checks a RedCap UL PRB cap request
- **THEN** the SDK can ACK in-contract requests and NACK missing, invalid, or out-of-range requests

#### Scenario: rApp policy package remains declarative
- **WHEN** an rApp policy package is defined
- **THEN** it contains policy intent and allowed runtime parameters without directly mutating OAI runtime state

### Requirement: SDK scaffold shall provide C and Python SDK entry points
The system SHALL provide C and Python SDK entry points for xApp, dApp, and rApp-facing policy packaging.

#### Scenario: xApp Python SDK mirrors the C request builder
- **WHEN** a RedCap UL PRB cap request is built in Python
- **THEN** it uses the same RedCap RC action ID and RAN parameter IDs as the C SDK

#### Scenario: dApp Python SDK mirrors the C guard decision
- **WHEN** a RedCap UL PRB cap request is checked in Python
- **THEN** it ACKs in-contract requests and NACKs missing, invalid, or out-of-range requests

#### Scenario: rApp Python SDK keeps policy declarative
- **WHEN** a RedCap rApp policy package is built in Python
- **THEN** it validates the same required fields as the policy schema and does not define a runtime apply path

#### Scenario: rApp C SDK keeps policy declarative
- **WHEN** a RedCap rApp policy package is built in C
- **THEN** it validates policy metadata and allowed runtime parameters without defining a runtime apply path
