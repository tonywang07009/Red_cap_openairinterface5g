## Purpose

Define the authoritative, evidence-bounded tool route for OAI repository work
and the governance boundary for changing that route.

## Requirements

### Requirement: Authoritative OAI tool routing

`redcap_toolbox.md` SHALL define the authoritative route from an OAI task
signal to the smallest appropriate tool sequence, its stop condition, and its
fallback. It SHALL use `symdex` for code symbols, callers, callees, and module
ownership; filesystem MCP for local document, specification, and log content;
and `rtk` for text search, Git state, build, test, and runtime commands. It
SHALL link research-wiki work to the existing context gate and routing memo.

#### Scenario: Router handles a source-navigation question
- **WHEN** an OAI request needs a symbol, caller, callee, or module owner
- **THEN** the toolbox route selects `symdex` first and gives its documented
  fallback and stop condition

#### Scenario: Router handles repository evidence
- **WHEN** an OAI request needs local documents, specifications, logs, text
  search, build, test, or runtime evidence
- **THEN** the toolbox route selects the documented filesystem MCP or `rtk`
  path and stops once the route's required evidence is captured

#### Scenario: Router handles research-wiki work
- **WHEN** an OAI request queries or updates the research wiki
- **THEN** the toolbox links to `CONTEXT.md` and `ASK_MATT_ROUTING_MEMO.md`
  without restating their rules

### Requirement: Tool-route governance boundary

`redcap_toolbox.md` SHALL treat tool availability, command examples, and
fallback corrections as direct maintenance. A change to a default route, stop
condition, or evidence threshold SHALL be an OpenSpec candidate requiring
human confirmation before application.

#### Scenario: A command example becomes stale
- **WHEN** an existing example or tool-health entry needs correction without
  changing a default route, stop condition, or evidence threshold
- **THEN** the toolbox can be updated directly

#### Scenario: A default route changes
- **WHEN** a proposed toolbox update changes a default tool route, stop
  condition, or evidence threshold
- **THEN** the router presents an OpenSpec candidate and waits for human
  confirmation before applying the change
