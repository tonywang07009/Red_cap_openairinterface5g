## MODIFIED Requirements

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
