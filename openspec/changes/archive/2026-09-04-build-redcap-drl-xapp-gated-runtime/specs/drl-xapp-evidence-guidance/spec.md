## ADDED Requirements

### Requirement: Per-run evidence package
Every bridge run SHALL retain an evidence package containing a run manifest,
control journal, ordered event stream, qualified KPM summaries, and a short
resolved gNB apply-marker excerpt when control was attempted. The manifest
MUST identify workspace, run, runtime release identity, selected profile,
resolved node, gate status, and evidence paths. Generated overlay and resolved
compose descriptor evidence MUST be kept separately from mutable simulator
configuration.

`run_model()` SHALL reject missing, unknown, malformed, or otherwise
syntactically invalid user input before a Control Run exists. Such rejection
MUST NOT create an evidence package. An enabled Control Run with a valid
request SHALL create exactly one evidence package before its first execution
preflight gate. Its `run_id` SHALL name the package directory and appear in
its manifest and ordered events. Qualification, model observation, model
decision, collector, and UDS results SHALL append only to that package; they
MUST NOT create a child evidence package. An operator SHALL trace a Control
Run with `<workspace>/artifacts/runs/<run_id>/manifest.json`.
On either terminal outcome, the manifest SHALL record `finalized_at`; the
orchestration SHALL refuse any later append for that `run_id`. This protection
does not replace the Bridge's lease for concurrent control.
If a process stops before finalization, its package SHALL remain interrupted
evidence and MUST NOT be resumed. A later control attempt SHALL use a new
`run_id` and pass the Bridge recovery gate before control.
Immediately after creating the package and before the first preflight gate,
the CLI SHALL emit one JSON record with `event=CONTROL_RUN_STARTED`, `run_id`,
and `evidence_manifest_path`.
After successful manifest finalization, it SHALL emit one JSON record with
`event=CONTROL_RUN_FINISHED`, the same `run_id`, `gate_status`, `finalized_at`,
and `evidence_manifest_path`.
The same-file `emit_json(record)` helper SHALL be the Control Run output seam;
the implementation SHALL not introduce a callback, generator, or class solely
for this output.
If finalization fails after control, the orchestration SHALL report
`EVIDENCE_FINALIZATION_FAILED`, MUST NOT emit `CONTROL_RUN_FINISHED`, and
MUST NOT retry control.
Before any UDS `open`, the orchestration SHALL verify that its manifest, event
stream, and journal are writable. Failure SHALL report
`EVIDENCE_WRITE_REQUIRED` and MUST NOT send a UDS request.
The manifest and model JSON artifacts SHALL use same-directory temporary files
and atomic replacement with the Python standard library. The ordered event
stream SHALL remain append-only.
An operator-invoked `qualify-kpm` remains an independent run and retains its
own package; only qualification invoked by an enabled Control Run is required
to append to the Control Run package.

The package SHALL retain `model_decision.json` only after the model output
passes the profile's strict candidate validation. A malformed model output
SHALL be recorded as a fail-closed ordered event and MUST NOT be retained as a
trusted decision artifact.

#### Scenario: Successful control-once run
- **WHEN** a control-once transaction completes
- **THEN** its package identifies the baseline, candidate, restore, required
  acknowledgement/apply/observation gates, and final recovery state

#### Scenario: Invalid CLI input creates no package
- **WHEN** a user omits a required argument, supplies an unknown flag, or
  supplies a malformed argument value
- **THEN** `run_model()` reports the CLI error before Control Run creation and
  creates no evidence package

#### Scenario: Run fails before control
- **WHEN** discovery, qualification, binding, or lease acquisition fails
- **THEN** the package records the failed gate and safe next command without
  fabricating control acknowledgement or gNB apply evidence

#### Scenario: One run ID correlates a failed preflight
- **WHEN** a Control Run fails during smoke, qualification, or model-input
validation before any UDS request
- **THEN** its one package is addressable by its `run_id`, records that no UDS
  control was sent through `control_journal.json.control_attempted=false`, and
  contains no second qualification or model package

#### Scenario: Control Run qualification has no child package
- **WHEN** `run --enable-control` performs qualification
- **THEN** the qualification events and KPM evidence append to the Control
  Run package rather than creating the package used by standalone
  `qualify-kpm`

#### Scenario: UDS request attempt is not application proof
- **WHEN** a Control Run attempts its first UDS `open` request
- **THEN** `control_journal.json.control_attempted` becomes `true` without
  claiming acknowledgement, marker proof, or gNB application

#### Scenario: A finalized run cannot be polluted
- **WHEN** a Control Run records a terminal pass or failure and writes
  `finalized_at`
- **THEN** a later attempt to append events or repeat control with the same
  `run_id` is refused and a new Control Run requires a new `run_id`

#### Scenario: An interrupted run cannot be resumed
- **WHEN** the orchestration process stops after an UDS request but before
  recording `finalized_at`
- **THEN** that package remains interrupted evidence, the same `run_id` is
  never resumed, and the next control attempt obtains a new `run_id` and
  passes Bridge recovery first

#### Scenario: Operator receives the run ID before preflight
- **WHEN** an enabled Control Run creates its evidence package
- **THEN** before any smoke or qualification request, the CLI emits exactly
  one `CONTROL_RUN_STARTED` JSON record containing its `run_id` and manifest
  path

#### Scenario: Operator receives a finalized terminal record
- **WHEN** a Control Run has successfully written `finalized_at` to its
  manifest
- **THEN** the CLI emits exactly one `CONTROL_RUN_FINISHED` JSON record with
  the same `run_id`, terminal gate status, finalization time, and manifest path

#### Scenario: Final evidence write fails after control
- **WHEN** control has completed but the manifest cannot record `finalized_at`
- **THEN** the run reports `EVIDENCE_FINALIZATION_FAILED`, emits no
  `CONTROL_RUN_FINISHED` record, and does not retry control

#### Scenario: Evidence cannot be written before control
- **WHEN** the Control Run cannot write its manifest, event stream, or journal
  before UDS `open`
- **THEN** it reports `EVIDENCE_WRITE_REQUIRED`, records no UDS request, and
  leaves `control_journal.json.control_attempted=false`

#### Scenario: JSON evidence is never partially published
- **WHEN** a manifest or model JSON artifact is updated
- **THEN** the orchestration writes a same-directory temporary file and
  atomically replaces the target; `events.ndjson` remains append-only

#### Scenario: Malformed model output remains untrusted
- **WHEN** model stdout is malformed, has extra output, or has an invalid
  candidate
- **THEN** the Control Run records `MODEL_CANDIDATE_REQUIRED` in its event
  stream, creates no `model_decision.json`, and sends no UDS control request

### Requirement: Evidence retention and truthful claims
`down` and `remove` SHALL retain run evidence unless a future separately
specified explicit purge operation removes it. CLI status and guides MUST
distinguish runtime smoke, Docker/hostname reachability, E2 capability,
KPM qualification, xApp acknowledgement, gNB apply marker, and later
observation. They MUST NOT describe any earlier gate as proof of a later gate.

#### Scenario: Network-only result
- **WHEN** the bridge can resolve or reach the RIC but no E2 setup evidence is
  available
- **THEN** status labels network reachability as passed and E2/KPM/control as
  unproved

### Requirement: Gate-oriented developer guidance
The project SHALL provide a model-invoked `redcap-drl-xapp-gates` guide whose
instructional steps begin with a Gate. The guide MUST route model developers
to the stable Python interface and profile maintainers to the native C/SWIG,
E2SM, and OpenSpec path. It MUST explain, in plain language, the distinction
between discovery and qualification, exclusive target leases, and the evidence
package as an experiment access record plus flight recorder.

#### Scenario: Model developer changes a policy
- **WHEN** a developer changes DQN, PPO, DDPG, or another Python policy
- **THEN** the guide directs the developer to workspace source, bridge API,
  evidence gates, and profile limits without asking them to edit C, ASN.1, or
  simulator compose assets

#### Scenario: Profile maintainer changes native semantics
- **WHEN** a maintainer needs a new KPM/RC profile or changes native
  C/SWIG/E2SM semantics
- **THEN** the guide requires a new OpenSpec change before implementation and
  does not route the change through a model workspace alone
