## MODIFIED Requirements

### Requirement: Stable workspace-private bridge interface
The bridge SHALL expose versioned `health`, `open`, `observe`, `act`, and
`close` operations over a workspace-private Unix-domain socket. Every request
and response MUST include protocol, request, session, and profile identity as
applicable. The runtime container MUST NOT receive a TCP control endpoint,
Docker socket, privileged capability, raw C pointer, or ASN.1 object.

`open` SHALL accept only `mode=control-once`; it SHALL create a session only
after the selected profile, qualification, target binding, recovery lock, and
exclusive lease gates succeed. `observe` SHALL remain a direct no-control
operation and SHALL NOT require an `open` or `close` session.

#### Scenario: Open a control-once session
- **WHEN** a runtime opens a valid selected profile in `control-once` mode
- **THEN** the bridge returns a session identifier through the private socket
  only after its control gates succeed and sends no E2SM-RC action during open

#### Scenario: Observe without a session
- **WHEN** an operator invokes a valid direct observation request for the
  selected profile
- **THEN** the bridge returns the observation result without creating a
  session, acquiring a lease, or sending an E2SM-RC action

#### Scenario: Removed observation-only open mode
- **WHEN** a runtime sends `open` with `mode=observation-only`
- **THEN** the bridge rejects the request as `INVALID_MODE` without native
  control activity

#### Scenario: Unknown protocol version
- **WHEN** a runtime sends an unsupported bridge protocol version
- **THEN** the bridge rejects the request without native control activity
