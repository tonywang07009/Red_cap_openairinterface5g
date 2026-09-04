## ADDED Requirements

### Requirement: Stable workspace-private bridge interface
The bridge SHALL expose versioned `health`, `open`, `observe`, `act`, and
`close` operations over a workspace-private Unix-domain socket. Every request
and response MUST include protocol, request, session, and profile identity as
applicable. The runtime container MUST NOT receive a TCP control endpoint,
Docker socket, privileged capability, raw C pointer, or ASN.1 object.

#### Scenario: Open an observation session
- **WHEN** a runtime opens a valid selected profile in observation-only mode
- **THEN** the bridge returns a session identifier through the private socket
  and no E2SM-RC action is sent

#### Scenario: Unknown protocol version
- **WHEN** a runtime sends an unsupported bridge protocol version
- **THEN** the bridge rejects the request without native control activity

### Requirement: Capability discovery and qualification
The bridge SHALL provide standalone `discover-kpm` that records live E2 node,
KPM, and RC capability facts without sending control. It SHALL require
`qualify-kpm --profile` before live control and MUST qualify separate cell and
UE KPM observation streams for profile freshness and alignment. Static
configuration, Docker logs, and network reachability MUST NOT substitute for
live KPM qualification.

#### Scenario: Discover live capabilities
- **WHEN** the operator runs `discover-kpm` against a reachable RIC
- **THEN** the bridge writes a capability manifest and reports discovered
  facts or their absence without issuing E2SM-RC control

#### Scenario: Missing UE observation proof
- **WHEN** the cell stream is available but the required UE stream is absent,
  stale, or unaligned
- **THEN** qualification fails and the bridge refuses control while allowing
further observation diagnostics

#### Scenario: Observation-only cadence probe
- **WHEN** the operator runs the KPM cadence probe against a node with the
  required cell and UE styles
- **THEN** the bridge records, for each stream, subscription acceptance time,
  first-callback latency, callback count, latest `RICindicationSN`, and event
  time without sending E2SM-RC control

### Requirement: Scoped native KPM stream capability
For `ul-prb-cap-v1`, the implementation SHALL use the existing gNB KPM-agent
owner seam to expose a cell-level KPM capability/report in addition to the
existing UE-level capability/report, and SHALL use the existing FlexRIC SWIG
owner seam to project both streams as Python-safe primitive observations. It
MUST preserve existing UE Style-4 behavior, MUST NOT expose raw C pointers or
ASN.1 objects to Python, and MUST NOT treat a UE-only stream as cell evidence.

#### Scenario: UE-only live capability
- **WHEN** discovery finds only the existing UE-level KPM capability
- **THEN** qualification returns `CELL_KPM_STREAM_REQUIRED`, records the
  capability evidence, and sends no KPM subscription or E2SM-RC control

#### Scenario: Cell and UE streams are available
- **WHEN** discovery finds distinct supported cell and UE KPM capabilities and
  the SWIG callback projects valid primitive observations for both
- **THEN** the bridge may proceed to freshness, alignment, and verified-target
  binding gates without treating capability discovery as action proof

### Requirement: Verified target binding and exclusive lease
Before action, the bridge SHALL resolve exactly one E2 node advertising the
profile's KPM and RC support and construct a VerifiedTargetBinding from live
UE-level evidence. The binding MUST include a KPM UE key, RC UE ID, RNTI, and
source sequence. The bridge SHALL grant one node-level exclusive software
lease; a concurrent requester MUST receive `TARGET_BUSY` and MUST NOT act.

#### Scenario: Verified target binding exists
- **WHEN** live KPM evidence proves the KPM UE identity, RC UE ID, and RNTI
  mapping for one eligible node
- **THEN** the bridge permits a control-once session to request its lease

#### Scenario: Identity mapping cannot be proved
- **WHEN** live observations cannot prove the required target binding
- **THEN** the bridge denies action and records the failed gate without
  guessing an identifier or using a legacy `ue_id=rnti` fallback

#### Scenario: Target is leased by another workspace
- **WHEN** another workspace holds the eligible node's control lease
- **THEN** the new request returns `TARGET_BUSY`, sends no control, and does
  not reuse the holder's observations

### Requirement: Profile-limited reversible control transaction
`profile=none` SHALL permit no E2SM-RC action. For `ul-prb-cap-v1`, a
control-once session SHALL validate the existing control contract and execute
at most one candidate action in this order: proved baseline, candidate,
proved baseline restore. The candidate action MUST remain within the contract
limits and each irreversible transition MUST be journaled before it is sent.

#### Scenario: One valid candidate action
- **WHEN** qualification, binding, lease, and contract validation succeed
- **THEN** the bridge sends one baseline, one valid candidate, and one
  baseline restore, and rejects any second candidate in the same session

#### Scenario: Profile none attempts action
- **WHEN** a runtime opens or calls action with `profile=none`
- **THEN** the bridge refuses before native control encoding or transmission

### Requirement: Apply proof and recovery lock
The bridge SHALL require a control acknowledgement, a resolved gNB apply
marker, and a later qualified KPM observation for every baseline, candidate,
restore, or recovery transition. On uncertain candidate or rollback state it
MUST make at most one best-effort baseline restore, persist
`ROLLBACK_UNCONFIRMED` when proof remains absent, and lock the target until an
explicit `recover` operation completes.

#### Scenario: Control phase apply is proved
- **WHEN** a baseline, candidate, restore, or recovery acknowledgement and gNB
  apply marker are found and a later qualified KPM observation is captured
- **THEN** that phase is proved; a candidate proof permits the baseline restore

#### Scenario: Rollback proof is absent
- **WHEN** the bridge cannot prove the baseline restore after its one
  best-effort attempt
- **THEN** it records `ROLLBACK_UNCONFIRMED`, retains the journal, blocks new
  control on the target, and requires explicit recovery

### Requirement: Model runner boundary
`run --enable-control` SHALL orchestrate workspace startup when needed,
runtime smoke verification, KPM qualification, the supplied Python model
entrypoint, and one control-once transaction. It SHALL retain containers by
default and only tear them down when explicitly requested. It MUST NOT expose
a generic multi-episode training command or claim that a model decision is a
validated DRL experiment.

#### Scenario: Greedy validation controller
- **WHEN** the operator invokes the supported greedy controller with an
  eligible live profile
- **THEN** the runner performs at most the one bounded transaction and emits
  its gates and evidence location

#### Scenario: Approved fixed and greedy candidates
- **WHEN** the fixed controller is selected
- **THEN** it selects `max_ul_prb=16`
- **WHEN** the greedy controller is selected with the latest qualified cell
  `RRU.PrbTotUl` utilization percentage
- **THEN** it selects `16` below 55%, `32` from 55% through 80%, and `64`
  above 80%; a missing, nonnumeric, or out-of-range utilization value refuses
  action

#### Scenario: Model single-inference candidate
- **WHEN** the model controller is enabled after qualification has supplied at
  least 30 valid paired E2-indication samples
- **THEN** the CLI writes the latest 30 cell `RRU.PrbTotUl` samples as a
  runtime-readable summary containing only `latest`, `mean`, `min`, and `max`,
  invokes the model entrypoint exactly once, and accepts only its single JSON
  `max_ul_prb` integer in the profile range `1..51`
- **AND WHEN** the summary, entrypoint result, JSON shape, or candidate range
  is invalid
- **THEN** the CLI refuses before opening a UDS control session
- **AND THEN** `0` remains reserved for baseline/restore while the native
  control contract remains `0..275`

#### Scenario: Model without qualified control input
- **WHEN** the model controller is invoked without `--enable-control`
- **THEN** the CLI returns `MODEL_OBSERVATION_REQUIRED` before runtime startup,
  because no approved model observation exists

#### Scenario: One-second apply proof window
- **WHEN** a baseline, candidate, or restore control request is sent
- **THEN** its required xApp acknowledgement and gNB apply marker MUST be
  observed within one second; its later qualified KPM observation MUST also be
  observed within one second, otherwise the transaction fails
  closed under the recovery-lock requirement

#### Scenario: Later KPM uses an active subscription
- **WHEN** a qualified control-once session sends a baseline, candidate, or
  restore request
- **THEN** the later KPM proof waits for a pair received after that native send
  on the session's existing cell/UE subscriptions
- **AND THEN** it MUST NOT unsubscribe and resubscribe after the control send

#### Scenario: Generic episode syntax is unavailable
- **WHEN** an operator supplies `--episodes` to `run`
- **THEN** the CLI parser rejects the unknown option before `run_model()`,
  workspace access, evidence creation, runtime startup, or UDS control
- **AND THEN** a future multi-episode profile requires a separate OpenSpec
  change defining state, action, reward, reset, and rate semantics
