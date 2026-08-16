## Purpose

Define the authoritative fallback route for unqualified OAI requests and the
human-confirmed escalation path for research-wiki conclusions.

## Requirements

### Requirement: Fallback OAI workflow routing

When a user has not directly selected a skill, `ask-matt` SHALL classify an
OAI request and return one active primary skill, or no primary skill if no
active route matches, any necessary companion skill, a route reason, the next
human decision, and a root-`AGENTS.md` tool-routing packet. A directly selected
skill SHALL not be rerouted by `ask-matt`; its explicit tool instructions
SHALL be retained, root `AGENTS.md` SHALL supply any omitted required tool
step, and the toolbox SHALL supply only the applicable task packet's stop
condition or command reference. The router SHALL select only active skills;
incubator skills SHALL remain unloaded until formally promoted.

#### Scenario: User selects a skill directly
- **WHEN** a user invokes a named skill
- **THEN** the router preserves that selection, retains its explicit tool
  instructions, derives any omitted required tool step from root `AGENTS.md`,
  and uses the toolbox only for the applicable task packet's stop condition or
  command reference

#### Scenario: User submits an unqualified OAI behavior change
- **WHEN** the request changes observable behavior, a public contract,
  architectural responsibility, or a traceable decision
- **THEN** the router selects `openspec-explore` as the primary route and
  identifies the OpenSpec lifecycle as the formal path

#### Scenario: No active route matches
- **WHEN** no active skill matches an unqualified request
- **THEN** the router does not inspect or select an incubator skill, returns
  no primary skill, and asks the human to clarify the request or approve
  formal promotion

#### Scenario: Router returns a tool packet
- **WHEN** the router has selected a primary skill or determined that no
  active route matches
- **THEN** it returns root `AGENTS.md` tool steps and fallback, plus the
  applicable toolbox packet's stop condition and command references, before
  any selected skill runs

### Requirement: Research-wiki escalation routing

The router SHALL route a new source-backed reading card or case to the
research-wiki capture route unless the result changes an existing conclusion,
an evidence threshold, or a governance rule. For those three changes, it
SHALL present an OpenSpec change candidate and require human confirmation
before creating or applying the change.

#### Scenario: New source-backed case preserves current governance
- **WHEN** a new reading card or case adds traceable evidence without changing
  an existing conclusion, evidence threshold, or governance rule
- **THEN** the router selects the research-wiki capture route without OpenSpec

#### Scenario: Evidence result changes a conclusion
- **WHEN** evidence would change an existing conclusion, evidence threshold,
  or governance rule
- **THEN** the router selects an OpenSpec candidate route and requests human
  confirmation before proposal creation or implementation

### Requirement: Retained routing memo

The research wiki SHALL contain an indexed memo that defines the router's
OpenSpec trigger criteria, research-wiki escalation rule, retained skill
routes, and human-confirmation boundary.

#### Scenario: User consults the routing reference
- **WHEN** a user needs to recall `ask-matt` routing criteria or retained
  skills
- **THEN** the wiki index links to a memo containing those criteria and routes

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
