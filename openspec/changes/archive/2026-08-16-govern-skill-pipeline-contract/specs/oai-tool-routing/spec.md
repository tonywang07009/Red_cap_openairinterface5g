## MODIFIED Requirements

### Requirement: Authoritative OAI tool routing

Root `AGENTS.md` SHALL define the authoritative required-first tool route and
fallback for an OAI task signal. The applicable `redcap_toolbox.md` task packet
SHALL define task-specific stop conditions and command references. Skills and
`redcap_toolbox.md` SHALL link to the root rule rather than duplicate it.
Source code, symbols, callers, callees, and repository structure SHALL use
Symdex first; Git status, diff, log, blame, branch, and commit lookup SHALL use
rtk first; Markdown, PDF, configuration, logs, generated artifacts, and file
content SHALL use filesystem MCP first. A fallback SHALL be reported with its
reason and MUST NOT replace a required Symdex lookup with `rg`.

#### Scenario: Router handles a source-navigation question
- **WHEN** an OAI request needs a symbol, caller, callee, or module owner
- **THEN** the route selects Symdex first and records a fallback only when
  Symdex cannot perform the lookup

#### Scenario: Router handles Git state
- **WHEN** an OAI request needs Git status, diff, history, blame, branch, or
  commit information
- **THEN** the route selects rtk first and records a fallback only when rtk
  cannot perform the operation

#### Scenario: Router handles repository evidence
- **WHEN** an OAI request needs Markdown, PDF, configuration, logs, generated
  artifacts, or ordinary file content
- **THEN** the route selects filesystem MCP first and records a fallback only
  when filesystem MCP cannot access the required path

#### Scenario: Router handles research-wiki work
- **WHEN** an OAI request queries or updates the research wiki
- **THEN** the route links to `CONTEXT.md` and `ASK_MATT_ROUTING_MEMO.md`
  without restating their rules
