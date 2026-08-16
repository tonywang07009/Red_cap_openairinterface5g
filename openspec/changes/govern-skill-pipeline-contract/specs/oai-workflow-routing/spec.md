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

## MODIFIED Requirements

### Requirement: Fallback OAI workflow routing

The router SHALL derive required tool steps and fallback from root `AGENTS.md`.
It SHALL use only the applicable `redcap_toolbox.md` task packet for task-
specific stop conditions and command references.

#### Scenario: User selects a skill directly
- **WHEN** a user invokes a named skill
- **THEN** the router preserves that selection, derives any omitted required
  tool step from root `AGENTS.md`, and uses the toolbox only for the applicable
  task packet's stop condition or command reference

#### Scenario: Router returns a tool packet
- **WHEN** the router has selected a primary skill or determined that no
  active route matches
- **THEN** it returns root `AGENTS.md` tool steps and fallback, plus the
  applicable toolbox packet's stop condition and command references, before
  any selected skill runs
