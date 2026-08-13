## ADDED Requirements

### Requirement: Approved OpenSpec pipeline routing
The formal workflow SHALL follow `grill-with-docs → OpenSpec → human approval
tag → to-spec mirror → TDD → implement → code-review → archive`. A directly
selected skill SHALL remain primary. For RedCap planning,
`redcap-plan-collbation` SHALL first identify risks; `grill-with-docs` SHALL
enter only when behavior/non-goals, owner, acceptance/evidence, or rollback/
stop decisions are missing.

#### Scenario: RedCap plan has all required decisions
- **WHEN** a RedCap plan identifies risks and already states behavior, owner,
  acceptance/evidence, and rollback/stop decisions
- **THEN** it proceeds without a second grilling interview

#### Scenario: RedCap plan lacks an acceptance decision
- **WHEN** a RedCap plan lacks behavior/non-goals, owner, acceptance/evidence,
  or rollback/stop information
- **THEN** the route invokes `grill-with-docs` to obtain the missing decision
