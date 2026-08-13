## Purpose

Define the authoritative fallback route for unqualified OAI requests and the
human-confirmed escalation path for research-wiki conclusions.

## Requirements

### Requirement: Fallback OAI workflow routing

When a user has not directly selected a skill, `ask-matt` SHALL classify an
OAI request and return one active primary skill, or no primary skill if no
active route matches, any necessary companion skill, a route reason, the next
human decision, and an authoritative tool-routing packet. A directly selected
skill SHALL not be rerouted by `ask-matt`; its explicit tool instructions
SHALL be retained, and the toolbox MAY fill only an omitted necessary tool
step. The router SHALL select only active skills; incubator skills SHALL
remain unloaded until formally promoted.

#### Scenario: User selects a skill directly
- **WHEN** a user invokes a named skill
- **THEN** the router preserves that selection, retains its explicit tool
  instructions, and uses the toolbox only for an omitted necessary tool step

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
- **THEN** it returns the task signal, primary skill, ordered tool steps, stop
  condition, and fallback from `redcap_toolbox.md` before any selected skill
  runs

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
