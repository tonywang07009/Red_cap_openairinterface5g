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
