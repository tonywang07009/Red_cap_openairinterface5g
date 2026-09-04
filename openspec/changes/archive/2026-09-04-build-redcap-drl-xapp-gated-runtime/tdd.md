# TDD Contract Log

> Migration record (2026-09-01): the prior full `design.md` is retained here
> without deleting historical contracts or validation evidence. The current
> architecture and safety decisions now live in `design.md`; this file is the
> append-only TDD and execution-record source.

## Current contract index

| Area | Current record | Status |
| --- | --- | --- |
| Workflow | Workflow proportionality decision | Active process rule |
| Task 3.5 | Measurement-post and E2 provenance records | Control remains fail-closed until calibration freeze |
| Tasks 4.1–4.2 | Batch B records | Local transaction/recovery contract implemented |
| Task 4.3 | A3, D1, E2–E4, and model single-inference records | Local orchestration plus one bounded live fixed transaction; broader interoperability pending |
| Control Run correlation | Control Run evidence-correlation and Task 6.4 finalization records | Local seam plus one bounded live fixed transaction; host-clock/interoperability limits pending |
| Task 6.4 | Evidence package finalization contract and implementation record | 84/84 local tests, strict validation, and fixed-point review complete |

## Supersession index

| Earlier record | Replaced by | Current interpretation |
| --- | --- | --- |
| Batch C candidate-policy absence | Task 4.3 A3 and D1 | Fixed/greedy policy is approved and reaches the bounded transaction. |
| Task 4.3 A1 policy refusal | Task 4.3 A3 | `CANDIDATE_POLICY_REQUIRED` was a temporary fail-closed state before the user-approved candidate policy. |
| Task 4.3 E1 local marker reader | Task 4.3 E2–E4 | Marker matching is now used by the collector-backed native proof provider with later-KPM proof. |
| Task 4.3 model single-inference contract | Its implementation record | The current local model contract is implemented and validated; Tasks 6.2/6.3 remain live-evidence gates. |
| Task 4.3 A2 `--episodes` refusal | Task 4.3 `--episodes` removal contract | The temporary refusal syntax is removed; parser rejection is now required. |

## Control Run evidence-correlation contract (2026-09-01)

- Acceptance: `run --enable-control` creates one immutable `run_id` and its
  evidence package before its first execution preflight gate, after CLI input
  validation succeeds. All preflight, qualification, model input, model
  decision, collector, and UDS `open`/`act`/`close` records append to that
  package. Operators locate the complete attempt through
  `<workspace>/artifacts/runs/<run_id>/manifest.json`.
- CLI-input acceptance: missing, unknown, malformed, or syntactically invalid
  user input is rejected before Control Run creation and creates no package.
- Failure acceptance: a smoke, qualification, or model-input failure still
  retains that package, identifies the failed gate, and explicitly records
  `control_journal.json.control_attempted=false`. The field becomes `true`
  only when an UDS `open` request is attempted; it is not ACK or application
  proof. The Control Run creates no child evidence package.
- Finalization acceptance: either terminal outcome writes `finalized_at` to
  the manifest. Later append or repeat-control attempts with that `run_id`
  are refused; a new attempt has a new `run_id`. This evidence protection does
  not replace the native node lease for concurrent control.
- Interruption acceptance: a package without `finalized_at` after process
  termination remains interrupted evidence and is never resumed. A new
  Control Run uses a new `run_id` and must pass Bridge recovery before control.
- Operator acceptance: immediately after package creation and before any
  preflight request, the CLI emits exactly one `CONTROL_RUN_STARTED` JSON
  record with the `run_id` and evidence manifest path.
- Terminal-output acceptance: only after it writes `finalized_at`, the CLI
  emits exactly one `CONTROL_RUN_FINISHED` JSON record with the same `run_id`,
  gate status, finalization time, and manifest path.
- Output-seam acceptance: the same-file `emit_json(record)` helper emits both
  lifecycle records; no callback, generator, or class is added for output.
- Finalization-failure acceptance: if the terminal manifest write fails after
  control, report `EVIDENCE_FINALIZATION_FAILED`, emit no finished record, and
  never retry control.
- Pre-control evidence acceptance: if manifest, event-stream, or journal
  writes fail before UDS `open`, report `EVIDENCE_WRITE_REQUIRED`, retain
  `control_attempted=false`, and send no UDS request.
- Atomic-publication acceptance: manifest and model JSON write through a
  same-directory temporary file followed by standard-library atomic replace;
  `events.ndjson` remains append-only.
- Composition acceptance: standalone `qualify-kpm` retains its independent
  package. When an enabled Control Run invokes qualification, all
  qualification events and KPM evidence append to the Control Run package.
- Model-output acceptance: only strict valid output produces
  `model_decision.json`. Malformed, extra, or out-of-domain stdout records
  `MODEL_CANDIDATE_REQUIRED` in the event stream, creates no decision artifact,
  and sends no UDS request.
- Validation: see the implementation record below. Live proof remains outside
  this local contract.

### Control Run evidence-correlation implementation record (2026-09-01)

- Implementation: same-file `execute_control_run()` creates one package before
  preflight and reuses `bridge_operations()` for appended discovery and
  qualification. `control_once_in_run()` appends collector and UDS results to
  that package; `emit_json()` emits its lifecycle records after creation and
  after successful finalization. `qualified_model_observation()` now owns
  event-time pairing and the 30-sample summary in the bridge module. The
  runtime receives only read-only `<workspace>/runtime-input` at
  `/run/redcap-drl`; the bridge alone receives `<workspace>/run` and its UDS.
  The runtime image no longer ships the generic `redcap_drl.Client`.
- Validation: focused RED exposed the shared `run/` mount and generic runtime
  client; GREEN covers split mounts, runtime-client removal, one package,
  model observation/decision retention, finalization refusal, and bridge-owned
  pairing, and finalized-package append refusal. The full Python tracer passes
  71 tests:
  `test_log/compiler_logs/task51_architecture_full_green_final_2026-09-01_16-22-36.log`.
- Boundary: this is offline seam evidence. No Docker container, live E2
  subscription, E2SM-RC request, gNB application, or clock-equivalence claim
  was made; Tasks 6.2 and 6.3 remain **[Needs Verification]**.

## Archived design rationale

### Context

The existing RedCap/OAI/FlexRIC environment owns the gNB, UE, CN, RIC,
control contract, and native C xApp reference code. It does not provide a
reusable Python DRL development runtime that can attach safely to that
environment. The new environment must work for DQN, PPO, DDPG, and future
models without deciding their state, action, reward, reset, or episode policy.

The simulator topology is user supplied. RIC service, Docker network, gNB
service, ports, E2 node, KPM styles, and metric identities MUST be discovered
from the selected compose scenario or live RIC; they are not stable defaults.

## Goals / Non-Goals

**Goals:**

- Create isolated named workspaces from one command, using a shared local DRL
  release rather than copied Python environments.
- Provide CPU and GPU runtime variants and a separate native FlexRIC bridge.
- Let an IDE edit bind-mounted Python source and use a stable Python interface
  over a workspace-private Unix-domain socket (UDS).
- Prove one bounded, reversible real E2SM-RC action using E2SM-KPM evidence,
  contract validation, acknowledgement, gNB apply evidence, and a later
  observation.
- Preserve recovery state and concise evidence for every control run.

**Non-Goals:**

- Define or claim a production DQN/DPPG/PPO training method, reward, state,
  action space, reset semantics, baseline, episode count, or learning rate.
- Modify UE, CN, RIC compose services, their YAML, OAI image topology, or
  the existing control contract. This change permits only the scoped gNB KPM
  and FlexRIC SWIG changes defined below.
- Give xApp containers a Docker socket, privileged capability, writable
  simulator configuration, or a public control endpoint.
- Treat Docker reachability, an E2 acknowledgement, or a static configuration
  as proof that an action was applied.

## Decisions

### Shared release and workspace split

Build immutable local images once per release:

- `redcap-drl-runtime:<release>-cpu`
- `redcap-drl-runtime:<release>-gpu`
- `redcap-flexric-bridge:<release>`

Tags are never overwritten. A workspace lock records the requested tag and
the locally resolved image digest/ID. The workspace contains only its
bind-mounted editable source, generated overlay, lock, and run artifacts.
Changing PyTorch, Stable-Baselines3, CUDA, SWIG, or the native ABI creates a
new release; an existing workspace changes release only through an explicit
upgrade command.

This is smaller and more reproducible than per-workspace image builds. A
single multi-purpose container was rejected because it would expose native RIC
access and external network reachability to arbitrary model code.

### Container and bridge boundary

The runtime container runs the model and attaches only a workspace-private
volume containing `/run/redcap-drl/bridge.sock`. The bridge container owns:

- the selected external Docker network;
- the SWIG native extension and C ABI calls into FlexRIC;
- E2SM-KPM decoding, E2SM-RC encoding, the control journal, and lease state.

The stable protocol is versioned JSON messages carrying `protocol_version`,
`request_id`, `session_id`, and `profile_id`. Its V1 operations are `health`,
`open`, `observe`, `act`, and `close`. It exposes no C pointers, ASN.1
objects, RIC address, or raw Docker capability to model code.

UDS is selected over TCP because it has no public port, is scoped by the
workspace volume and Unix permissions, and directly matches the same-host IDE
and Docker development model. A Python reimplementation of FlexRIC was
rejected because the existing native owner seam and ASN.1 behavior must be
reused, not duplicated.

### Compose resolution and external mounts

`init` receives a compose path and derives the external network and relevant
service descriptors. It MUST stop if required data is absent or ambiguous.
The generated overlay adds only runtime and bridge services to that resolved
network; it never edits or restarts the base compose project. Existing control
contract and simulator configuration mounts are read-only. A host-side helper
may collect a short resolved gNB apply-marker excerpt, but containers do not
receive the Docker socket.

### Profile-gated observations and action

`profile=none` permits image, library, bridge-health, and offline Gym smoke
checks only. `profile=ul-prb-cap-v1` selects the first bounded live-control
profile. Its control input is constrained by the existing RedCap contract;
its observation source is live E2SM-KPM, not Docker logs.

Before control, the bridge MUST discover capabilities, resolve exactly one E2
node advertising both required KPM and RC support, qualify separate cell and
UE KPM observation streams, and obtain a verified target binding. The binding
records the KPM UE key, RC UE ID, RNTI, and source sequence. If an identity or
freshness condition cannot be proved, observation can continue but `act` is
refused.

This separates reusable infrastructure from research semantics. Future
profiles define their own observations, actions, evidence thresholds, and
reset/reward rules through a new OpenSpec change.

### Scoped native KPM capability extension

The live OAI agent currently advertises only the UE-level KPM report-style
tuple `(3,3,0,2)`, which maps to KPM Style 4 / Action Definition Format 4 /
Indication Message Format 3. `ul-prb-cap-v1` requires independently qualified
cell and UE streams, so the bridge cannot satisfy the profile by reinterpreting
that UE-only tuple.

This change therefore permits the smallest owner-local extension:

- `openair2/E2AP/RAN_FUNCTION/O-RAN/ran_func_kpm.c` MAY expose a cell-level
  KPM capability and report using the existing OAI KPM-agent path.
- `openair2/E2AP/flexric/src/sm/agent_if/read/sm_ag_if_rd.h` and
  `openair2/E2AP/flexric/src/sm/kpm_sm/kpm_sm_v03.00/kpm_sm_agent.c` MAY
  carry one subscription-owned cell baseline alongside the decoded action
  definition. The existing E2 agent already stores the RIC request identity
  in `ind_event_t` and invokes `free_act_def` on subscription deletion and
  agent teardown. The extension MUST reuse that ownership: the first sample
  initializes the baseline and the existing `free_act_def` path releases it.
  A new request-ID registry, cleanup callback, RAN cleanup operation, or
  shared process-wide delta baseline is not permitted.
- `openair2/E2AP/flexric/src/xApp/swig/` MAY project the existing native
  FlexRIC KPM subscription/callback API as Python-safe primitive observations.
- The existing bridge remains the only consumer that performs freshness,
  alignment, and target-binding qualification; it MUST refuse control until
  those gates pass.

This authorization does not add a parallel KPM implementation, change
E2SM-RC encoding, relax the cell-plus-UE requirement, alter compose files, or
make a Docker socket available to containers. Exact KPM action-definition,
indication-message, metric, and UE-identity mapping details remain
**[Needs Verification]** and must be source-traced before implementation.

#### Task 3.3 scope-reduction record (2026-08-27)

Source tracing showed that `msg_handler_agent.c` already copies the RIC
identity into `ind_event_t`, while subscription deletion and agent teardown
already invoke the KPM adapter's `free_act_def`. The earlier design therefore
overstated the need for explicit request-identity retention and a separate
unsubscribe lifecycle.

Task 3.3 now has one remaining implementation slice: produce valid
second-and-later cell PRB samples from a subscription-owned baseline, return
no value for the first sample and invalid counter deltas, keep independent
subscriptions isolated by object ownership, and release the baseline through
the existing action-definition free path. One frozen tracer SHALL cover this
slice. No identity table, global subscription registry, new unsubscribe API,
or separate identity/unsubscribe test suite is in scope. The exact
`RRU.PrbTotDl`/`RRU.PrbTotUl` value type and percentage mapping remain
**[Needs Verification]**.

### Exclusive control and bounded transaction

The bridge holds one node-level software lease per resolved E2 node. A second
workspace attempting control receives `TARGET_BUSY`; it neither waits nor
uses another workspace's observations. If waiting is added later, the new
holder MUST repeat qualification and binding.

V1 control is exactly one reversible transaction:

1. apply the contract baseline and prove acknowledgement plus gNB marker;
2. apply one candidate action and prove acknowledgement, gNB marker, and a
   later KPM observation;
3. restore baseline and prove acknowledgement plus gNB marker.

The bridge persists the control journal before each irreversible transition.
On uncertain candidate or rollback state it makes one best-effort baseline
attempt, reports `ROLLBACK_UNCONFIRMED` if proof remains missing, and locks
the target until explicit recovery. This is deliberately not a multi-episode
training loop.

### Evidence and operator surface

Each run stores a manifest, journal, event stream, qualified KPM summaries,
and a short gNB apply excerpt under the workspace artifact directory. The
generated overlay and resolved compose descriptor are separate runtime
configuration evidence. Artifacts are retained by `down` and `remove` unless
a future explicit purge operation is approved.

The CLI provides Traditional-Chinese read-only `--help` for each command and
emits `gate_status`, `evidence_manifest_path`, workspace/run identifiers, and
a safe next command. `run --enable-control` orchestrates `up`, verification,
qualification, model entrypoint, and the one transaction. It keeps containers
up by default; `--teardown` is explicit.

A model-invoked `redcap-drl-xapp-gates` guide begins every instruction with a
Gate, routes model developers separately from profile maintainers, and treats
the evidence package as an experiment access record plus flight recorder.

## Risks / Trade-offs

- [Live KPM may not expose a usable UE-to-RC identity mapping] →
  `discover-kpm` records the actual capability; control is refused until a
  `VerifiedTargetBinding` is proved.
- [Docker network reachability can be mistaken for E2 readiness] → require
  live E2 capability, KPM qualification, acknowledgement, gNB marker, and
  post-action observation as separate gates.
- [GPU host runtime is unavailable] → fail GPU workspace creation or startup
  before launching a run; CPU remains independent.
- [Bridge crash during action] → durable journal, target lock, and explicit
  `recover` path; never infer rollback from container exit.
- [A shared image becomes stale] → immutable releases and explicit workspace
  upgrade; no in-place dependency mutation.
- [Full DRL training is requested before methods are defined] → preserve the
  generic bridge but require a profile-specific OpenSpec before enabling a
  multi-action or multi-episode runner.

## Migration Plan

1. Build and smoke-test a named CPU/GPU release and bridge release locally.
2. Initialize a new workspace against a running user-selected compose
   scenario; do not alter that compose project.
3. Run offline smoke checks, bridge health, capability discovery, and KPM
   qualification before attempting control.
4. Run only the fixed/greedy single-decision validation transaction.
5. To roll back runtime dependencies, select the prior immutable workspace
   release. To recover an interrupted control transaction, use the bridge
   journal and `recover`; do not restart the simulator as a recovery method.

## Open Questions

- Live capability discovery found raw KPM report-style enum value `3` and RC
  control styles 1/2 on node `2:1:1:3584`. Metric identities and proof that UE
  KPM can derive RC UE ID/RNTI remain **[Needs Verification]**.
- The numeric KPM style value `3` is the zero-based enum value for Style 4,
  not semantic Style 3. The current OAI KPM agent advertises and implements
  only UE-level Format 4; it does not provide the separately required cell
  stream. This change authorizes a scoped gNB KPM capability extension; the
  exact compatible cell format remains **[Needs Verification]**.
- Source tracing confirms that the existing FlexRIC KPM model already defines
  the cell report tuple as Style 1 / Action Definition Format 1 / Indication
  Header Format 1 / Indication Message Format 1. The nearest existing xApp
  example requests `RRU.PrbTotDl` and `RRU.PrbTotUl`; runtime interoperability
  with this OAI agent remains **[Needs Verification]** until the native tracer
  and live qualification pass.
- The E2 agent already owns subscription identity and action-definition
  cleanup. `kpm_rd_ind_data_t` therefore needs at most a non-owning reference
  to the subscription-owned cell baseline while producing a report. A shared
  delta baseline remains invalid because concurrent cell subscriptions would
  corrupt one another.
- Per-profile freshness window, sequence count, pair skew, control timeout,
  and post-action observation window remain profile data to measure and
  freeze; this design does not invent values.
- The bridge build is aligned with the live stack's `E2AP_V3` and
  `KPM_V3_00` profile. The SWIG discovery surface projects primitive node and
  RAN-function identity while retaining the native IDs for later control.
- A future profile-switch command is deferred. V1 locks the selected profile
  at workspace initialization so an unreviewed profile cannot be selected
  during a live run.

## Implementation Inventory

| Concern | Existing owner seam | Implementation boundary |
| --- | --- | --- |
| Contract limits and apply marker | `redcap_interface/control/redcap_control_contract.yaml` | Read-only input; `redcap_ul_prb_cap` is runtime-mutable with range 0..275 and marker `RedCap UL PRB control`. |
| RC request construction | `openair2/E2AP/REDCAP_SDK/xapp/redcap_xapp_sdk.c` | Reuse `redcap_xapp_make_ul_prb_ctrl_req(ue_id, rnti, max_ul_prb)`; never equate `ue_id` with `rnti`. |
| Native FlexRIC session/control | `openair2/E2AP/flexric/src/xApp/e42_xapp_api.*` | Use the established `init_xapp_api` and `control_sm_xapp_api` owner seam through a minimal adapter. |
| gNB KPM cell capability | `openair2/E2AP/RAN_FUNCTION/O-RAN/ran_func_kpm.c`, `openair2/E2AP/flexric/src/sm/agent_if/read/sm_ag_if_rd.h`, and `openair2/E2AP/flexric/src/sm/kpm_sm/kpm_sm_v03.00/kpm_sm_agent.c` | Keep one cell baseline in the existing subscription-owned action object and release it through `free_act_def`; add no identity registry or cleanup API, preserve UE Style-4 behavior, and prove a distinct cell stream. |
| FlexRIC KPM callback projection | `openair2/E2AP/flexric/src/xApp/swig/` | Project the existing native KPM subscription callback as Python-safe primitives; do not expose raw C or ASN.1 objects. |
| Existing Python helper | `openair2/E2AP/REDCAP_SDK/xapp/redcap_xapp_sdk.py` | Reuse only after its callable surface is inspected; it is not evidence of live transport. |
| Compose/control mount precedent | `redcap_interface/bash_library/generate_mmtc_overlay.sh` and control scripts | Generate an external overlay only; all simulator inputs stay read-only. |

Live E2SM-KPM styles, metric identities, and a KPM-to-RC UE/RNTI mapping are
still **[Needs Verification]**. They are runtime gates, not defaults.

## TDD contract

### Workflow proportionality decision (2026-08-28)

- The user chooses the model. A model switch is an explicit cost or quality
  decision, not a TDD phase.
- Ordinary tests use normal version control and CI. Fixed hashes and read-only
  files remain for high-risk control or refusal evidence only.
- Task manifests cover Docker, live E2/control, and very long builds. Ordinary
  unit tests retain logs only.
- Registry entries are required only for reusable, external, or side-effecting
  scripts. Skills may run narrow diagnostics directly.
- Task checkboxes show progress. Update design only when scope or safety
  changes, and run strict OpenSpec validation at milestones or completion.
- `qualify-kpm` performs discovery and emits the same combined result;
  `discover-kpm` remains available for diagnostics.
- Symdex is required for symbols/callers. Ordinary reads are direct and do not
  require a fallback narrative.
- Earlier SHA-256 and `0444` entries below are historical tracer evidence, not
  standing workflow requirements. The three ordinary Task 3.3 KPM cell tests
  were restored to mode `0644` on 2026-08-28 and now rely on normal Git/CI.

### Workflow simplification validation (2026-08-28)

- Test boundary: `bridge_gate(qualify-kpm)` sends discovery then qualification
  through the existing UDS seam and emits one evidence manifest.
- Acceptance: a failed discovery stops before qualification; a successful
  discovery and qualification appear in the same manifest and no control
  operation is sent.
- Irreversible side effects: none. The unit tracer replaces UDS with a local
  callable and writes only a temporary workspace.

- Model / effort: GPT-5.6 Sol / high
- Active model confirmation: user confirmed GPT-5.6 Sol / high on 2026-08-27.
- Fallback: none
- Test boundary: `redcap_drl_xapp.sh` public CLI exit code, diagnostic output,
  generated workspace/evidence, and absence of Docker/native-control effects
  on refusal paths; bridge requests use the public versioned JSON protocol.
- Acceptance links: `drl-xapp-workspace-lifecycle` named initialization and
  isolation scenarios; `drl-xapp-bridge-gates` protocol, binding, lease,
  profile, and recovery refusal scenarios.
- Irreversible side effects: Docker image builds, workspace/container
  creation/removal, E2 subscriptions, and E2SM-RC control. Refusal tests MUST
  prove these are not reached; live control requires the explicit Gate chain.
- Boundary gate: clear; user confirmed the V1 controller, target, locked
  profile, and `module:callable` decisions on 2026-08-18.
- Test files: `redcap_library/bash_tool/scripts/test_redcap_drl_xapp.py`
- Frozen SHA-256: `b0cec19775842455befdf119d4ae08617cbad01ece10464df383de48d2b4d2f0`
- Frozen test-diff baseline: `?? redcap_library/bash_tool/scripts/test_redcap_drl_xapp.py`;
  the untracked test path is protected after each accepted tracer update and
  production implementation MUST NOT modify it.
- Qualification tracer: `test_qualification_refuses_missing_cell_stream_without_control`
  is red against `KPM_STREAM_BINDING_UNIMPLEMENTED` and requires the public
  bridge response `CELL_KPM_STREAM_REQUIRED` with `control_attempted=false`.
- Native capability tracer: `test_native_qualification_refuses_node_without_cell_kpm_style`
  is red because `NativeFlexric.qualify` is absent and requires a capability-stage
  refusal before any KPM subscription or E2SM-RC control.
- Proposed native gNB public seam: exercise the existing
  `read_kpm_setup_sm()` and `read_kpm_sm()` entry points; do not add a
  test-only production API. The first tracer freezes only the setup result:
  gNB/DU advertise the existing UE Style-4 tuple plus a distinct cell Style-1
  tuple, while CU-only nodes do not advertise unsupported cell reporting.
  The user confirmed this seam on 2026-08-27.
- Frozen native setup test:
  `/home/tonywang/OAI/Red_cap_openairinterface5g_exp/openair2/E2AP/RAN_FUNCTION/O-RAN/test_ran_func_kpm_cell_setup.c`
- Native setup test SHA-256:
  `cfe9b3d9ac0034c42f7c41df34acf4bd4074cd255b5be747513f1c540102b546`
- Native setup frozen baseline: Git status `M` for the protected test path;
  filesystem mode `0444`. Production implementation MUST NOT modify it.
- Native setup boundaries frozen in one public-seam tracer:
  gNB and gNB-DU MUST advertise exactly one cell Style-1 tuple and preserve
  the existing UE Style-4 tuple; the cell tuple MUST use Action Definition
  Format 1, Indication Header Format 1, Indication Message Format 1, and the
  ordered metrics `RRU.PrbTotDl`, `RRU.PrbTotUl`; gNB-CU and gNB-CU-UP MUST
  preserve UE Style 4 without the unsupported cell style; gNB-CU-CP MUST
  advertise no report style while it has no supported measurement list.
- Native setup RED evidence:
  `test_log/compiler_logs/drl_xapp_kpm_cell_setup_red_2026-08-27_15-23-11.log`;
  the target builds, then fails at
  `sz_ric_report_style_list == 2` because current production advertises only
  one report style.
- Native setup GREEN evidence:
  `test_log/compiler_logs/drl_xapp_kpm_cell_setup_green_2026-08-27_20-22-00.log`;
  GPT-5.6 Luna changed only `ran_func_kpm.c` production behavior to advertise
  the confirmed cell Style-1 tuple for gNB/gNB-DU while preserving UE Style 4.
  The frozen setup tracer passes with
  `ASAN_OPTIONS=detect_leaks=0`; LeakSanitizer is disabled only because it is
  unsupported under the active ptrace environment. This proves setup
  capability construction, not cell report emission, subscription lifecycle,
  live interoperability, or runtime-effective KPM delivery.
- Native setup build/run:
  `cmake --preset tests -B /tmp/redcap-exp-kpm-tests -DE2_AGENT=ON`, then
  `cmake --build /tmp/redcap-exp-kpm-tests --target test_ran_func_kpm_cell_setup --parallel 4`,
  then `ctest --test-dir /tmp/redcap-exp-kpm-tests -R '^test_ran_func_kpm_cell_setup$' --output-on-failure`.
  The isolated build directory is required because the repository's existing
  `cmake_targets/ran_build/build_test` cache names the other checkout.
- Formatting check: **[Needs Verification]** because no `clang-format`
  executable is installed in the current environment; the test was checked
  manually against the repository's 2-space and 132-column rules.
- Luna implementation boundary: after the user switches models, record the
  actual GPT-5.6 Luna effort before production edits; make the frozen native
  setup test green by changing only
  `openair2/E2AP/RAN_FUNCTION/O-RAN/ran_func_kpm.c`. Do not modify the frozen
  test or reinterpret a linker/configuration failure as RED.
- One remaining native cell-delta tracer is approved for the existing KPM
  subscription and `read_kpm_sm()` public seams. It freezes first-sample and
  invalid-delta no-value behavior, valid later samples, independent baselines
  for two subscription-owned objects, and release through the existing
  action-definition free lifecycle. It does not require a RIC-ID registry,
  new unsubscribe operation, or test-only production API.
- Frozen native cell report tracer:
  `/home/tonywang/OAI/Red_cap_openairinterface5g_exp/openair2/E2AP/RAN_FUNCTION/O-RAN/test_ran_func_kpm_cell_report.c`
- Native cell report tracer SHA-256:
  `14fa39267380834511a1f92382330c53ec28a8b23196e7cdf61b9eef4c44f4a2`
- Native cell report frozen baseline: Git status `??` for the protected test
  path; filesystem mode `0444`. The associated CTest registration is in the
  already-modified `openair2/E2AP/RAN_FUNCTION/CMakeLists.txt` test block.
- Native cell report tracer boundary: a Style-1 action requesting the ordered
  metrics `RRU.PrbTotDl` and `RRU.PrbTotUl` through `read_kpm_sm()` MUST emit
  Indication Header Format 1 and Indication Message Format 1, retain the two
  measurement names in order, emit one two-record sample, and represent its
  initial delta sample as two `NO_VALUE_MEAS_VALUE` records. The cell path
  MUST NOT call the existing UE measurement helper. This tracer does not yet
  freeze later delta values or subscription-owned baseline release.
- Native cell report RED evidence:
  `test_log/compiler_logs/drl_xapp_kpm_cell_report_red_2026-08-27_22-14-20.log`;
  the isolated target builds and then aborts in `read_kpm_sm()` because Action
  Definition Format 1 is not implemented. The frozen setup tracer still
  passes after the new harness is registered.
- Native cell report build/run:
  `cmake --build /tmp/redcap-exp-kpm-tests --target test_ran_func_kpm_cell_report --parallel 4`,
  then `ASAN_OPTIONS=detect_leaks=0 ctest --test-dir /tmp/redcap-exp-kpm-tests
  -R '^test_ran_func_kpm_cell_report$' --output-on-failure`.
- Luna report-emission implementation boundary: make only this frozen tracer
  green through the existing `read_kpm_sm()` seam. Do not modify either
  frozen native test, do not route cell reports through the UE measurement
  helper, and do not add the later per-subscription delta lifecycle before its
  next tracer is frozen.
- Report-emission implementation record: the user confirmed the switch to
  GPT-5.6 Luna on 2026-08-27. The active Luna reasoning-effort value is not
  exposed in the session metadata **[Needs Verification]**; no fallback model
  was used. The implementation adds only the Format-1 cell report branch and
  its owner-local initial no-value record construction required by the frozen
  tracer. One subscription-owned delta-state slice remains; identity retention
  and unsubscribe cleanup are not separate implementation slices because the
  existing E2 event and `free_act_def` lifecycle already own them.
- Native cell report GREEN evidence:
  `test_log/compiler_logs/drl_xapp_kpm_cell_report_green_2026-08-27_22-56-34.log`;
  GPT-5.6 Luna changed only `ran_func_kpm.c` for this slice. The frozen report
  tracer and the existing frozen setup tracer each pass 1/1 under
  `ASAN_OPTIONS=detect_leaks=0`. This proves the public Format-1 report shape,
  ordered measurement names, one initial two-record no-value sample, and
  preservation of the setup capability path. It does not prove later delta
  values, subscription-owned baseline release, live E2 delivery, or
  runtime-effective KPM telemetry.
- Task 3.3 delta-state contract (2026-08-28): the user authorized completion
  with the active model. The exact model and reasoning effort are not exposed
  in this session metadata **[Needs Verification]**. The public seam is a
  non-owning `kpm_cell_delta_state_t *` in `kpm_rd_ind_data_t`; its concrete
  storage is embedded in the adapter's existing subscription action object.
  The tracer covers first, valid, and invalid counter deltas plus independent
  state objects. Existing `free_act_def` owns final release. This isolated
  CMake/CTest run has no Docker, E2 subscription, or E2SM-RC side effect.
- Task 3.3 implementation evidence (2026-08-28):
  `test_ran_func_kpm_cell_delta.c` is frozen at SHA-256
  `740bbdf315895398833dbdef5824a2bb9c5e50b0d594428ad0d8dbda2cd14ba0`
  and was initially mode `0444`. It first failed at the required valid-delta assertion, then
  passed with the existing setup and initial-report tracers. The report owner
  snapshots aggregate MAC counters under `sched_lock`, emits no-value for an
  absent state, first sample, non-advancing total, regressing counter, or used
  delta above the total delta, and re-baselines after every sample. The KPM
  v03.00 adapter embeds this state beside its decoded action definition and
  passes it through `kpm_rd_ind_data_t`; its existing `free_act_def` frees the
  enclosing action object. `kpm_sm_static` compiled under `KPM_V3_00`.
  Exact `RRU.PrbTotDl`/`RRU.PrbTotUl` percentage semantics and live E2SM-KPM
  interoperability remain **[Needs Verification]**.

### Batch A TDD contract (2026-08-28)

- Model / effort: GPT-5.6 Terra / high, user-authorized for Batch A test work.
- Test boundary: `NativeFlexric.qualify("ul-prb-cap-v1")` consumes the minimal
  SWIG callable `subscribe_kpm(node_id, stream, callback)`. `stream` is either
  `cell` or `ue`; each callback input is a Python primitive mapping, never a
  C pointer or ASN.1 object.
- Acceptance: a node exposing both supported KPM style tuples subscribes to
  both streams and preserves valid primitive observations in its fail-closed
  qualification result. A missing RC UE ID/RNTI binding returns
  `TARGET_BINDING_REQUIRED`; a malformed observation returns
  `KPM_CALLBACK_MALFORMED` at `failed_stage=callback`.
- Irreversible side effects: none. The tracer replaces the native extension
  with an in-memory callable and asserts `control_attempted=false`.
- Deferred evidence: freshness, cell/UE alignment thresholds, real SWIG ABI
  loading, and live E2 delivery remain **[Needs Verification]** and belong to
  the later implementation/live-validation gates.
- Test file: `redcap_library/bash_tool/scripts/test_redcap_drl_xapp.py`.
- Test evidence: `test_log/compiler_logs/drl_xapp_batch_a_red_2026-08-28.log`.

### Batch A implementation record (2026-08-28)

- Model / effort: GPT-5.6 Luna / high, user-confirmed switch; exact session
  effort metadata is not exposed **[Needs Verification]**.
- Python qualification now retains `subscribe_kpm` handles and director
  callback objects, projects both dictionary and SWIG object samples to
  primitive mappings, and refuses malformed callbacks before any control.
- The existing FlexRIC SWIG owner seam now exposes
  `subscribe_kpm(node_id, stream, callback)` and `unsubscribe_kpm(handle)`;
  native callbacks convert KPM Format 1 cell and Format 3 UE indications to
  primitive measurement records while preserving the existing generic report
  API and action-definition cleanup. `source_seq` is currently a callback
  ordinal because the decoded indication header exposes no source sequence;
  correlation with a live E2 source sequence remains **[Needs Verification]**.
- Validation: the full Python suite passes 21/21 in
  `test_log/compiler_logs/drl_xapp_batch_a_full_green_2026-08-28.log`; direct
  SWIG/native syntax validation passes in
  `test_log/compiler_logs/drl_xapp_batch_a_swig_syntax_green_2026-08-28.log`.
  The CMake SWIG build is **[Needs Verification]** because the host exposes
  SWIG 4.0.2 and the project requires version 4.1 or newer.
- Task 3.5 remains open: profile-specific freshness/alignment thresholds,
  live KPM delivery, and verified UE-to-RC/RNTI binding are not inferred from
  these mock or syntax checks.

### Batch B TDD contract (2026-08-28)

- Model / effort: GPT-5.6 Terra / high, user-confirmed before Batch B test
  work; exact session metadata is not exposed **[Needs Verification]**.
- Test boundary: the public UDS `Bridge.handle()` operations `open`, `act`,
  and `close`. The existing injected `native_control(action)` seam is the
  only test double. It receives primitive action fields `phase`, `node_id`,
  `rc_ue_id`, `rnti`, and `max_ul_prb`, and returns primitive proof fields
  `acknowledged`, `gnb_apply_marker`, and, for the candidate, `later_kpm`.
- Acceptance: `ul-prb-cap-v1` accepts the contract upper bound 275 and emits
  baseline 0, one candidate, then baseline restore only after the required
  proof gates. Value 276 is refused before native control. A missing rollback
  proof records `ROLLBACK_UNCONFIRMED` and later control-open returns
  `RECOVERY_REQUIRED`; an explicit `recover` with a proved baseline clears the
  lock and records `RECOVERED`.
- Journal scope: this batch freezes only state values needed for safety
  (`LEASE_ACQUIRED`, `COMPLETED`, `ROLLBACK_UNCONFIRMED`, and `RECOVERED`).
  Full journal, manifest, and event schemas remain Task 5.1.
- Irreversible side effects: none. Tests use an in-memory `native_control`;
  refusal asserts no call, and rollback asserts one best-effort restore only.
- Boundary gate: clear. The profile contract fixes the control range and the
  bridge-gates spec fixes the transaction/proof/recovery behavior.
- Test file: `redcap_library/bash_tool/scripts/test_redcap_drl_xapp.py`.
- Test evidence: `test_log/compiler_logs/drl_xapp_batch_b_red_2026-08-28.log`.
  The full suite runs 25 tests: the prior 21 pass, while the four Batch B
  tracers fail only because durable lease journaling, contract validation,
  bounded proof-gated transaction, and rollback lock behavior are not yet
  implemented.

### Batch B implementation record (2026-08-28)

- Model / effort: GPT-5.6 Luna / high, user-confirmed switch; exact session
  metadata is not exposed **[Needs Verification]**.
- `Bridge` now atomically persists journal state before each control step,
  validates `redcap_ul_prb_cap` at `0..275`, executes one
  baseline→candidate→restore transaction, and requires explicit ACK, gNB
  apply-marker, and later-KPM proof fields from the injected native-control
  owner seam.
- Candidate or restore proof failure performs at most one best-effort restore;
  missing restore proof persists `ROLLBACK_UNCONFIRMED` and blocks new control.
  The explicit `recover` operation sends one proved baseline restore before
  writing `RECOVERED` and releasing the lease.
- Validation: the full Python suite passes 26/26 in
  `test_log/compiler_logs/drl_xapp_batch_b_recovery_green_2026-08-28.log`;
  the recovery RED boundary is retained in
  `test_log/compiler_logs/drl_xapp_batch_b_recovery_red_2026-08-28.log`.
- This is a local proof-provider seam only. Native FlexRIC ACK delivery,
  runtime gNB apply-marker correlation, and later live KPM evidence remain
  **[Needs Verification]** and belong to Tasks 4.3/5.1/6.3.

### Batch C TDD contract (2026-08-28)

- Model / effort: GPT-5.6 Terra / high, user-confirmed before Batch C test
  work; exact session metadata is not exposed **[Needs Verification]**.
- Test boundary: public CLI helpers `run_model()` and `bridge_gate()` with
  temporary workspaces. `verify`, the UDS call, and runtime overlay are local
  test doubles; no Docker, E2 subscription, or E2SM-RC control is invoked.
- Acceptance: an enabled fixed/greedy control run stops before qualification
  if smoke fails; an invalid model entrypoint is refused before runtime start;
  a successful qualification projects its resolved node into the run manifest
  while the run journal remains `NOT_STARTED` with
  `control_attempted=false`.
- Candidate-policy boundary: the profile supplies a legal range (`0..275`),
  not a fixed/greedy PRB decision rule. This batch deliberately does not invent
  an actionable candidate or claim a live control transaction; binding and
  candidate policy remain **[Needs Verification]** for Tasks 3.5/4.3/6.3.
- Test file: `redcap_library/bash_tool/scripts/test_redcap_drl_xapp.py`.
- Test evidence: the full suite retains 26 prior PASS cases and has exactly
  three Batch C RED failures in
  `test_log/compiler_logs/drl_xapp_batch_c_red_refined_2026-08-28.log`:
  smoke gating before qualification, CLI-side `module:callable` refusal, and
  `resolved_node` manifest projection.

### Batch C implementation record (2026-08-28)

- Model / effort: GPT-5.6 Luna / high, user-confirmed switch; exact session
  metadata is not exposed **[Needs Verification]**.
- `run_model()` now validates dotted `module:callable` entrypoints before any
  runtime overlay command and runs the existing smoke/reachability gate before
  KPM qualification for enabled control. A failed smoke gate therefore sends
  no qualification or control request.
- `bridge_gate()` now records an explicit qualified `node_id` in the manifest;
  each package also points to the existing resolved compose and generated
  overlay descriptors. The control journal remains `NOT_STARTED` until a
  control operation is actually attempted.
- Validation: the full Python suite passes 29/29 in
  `test_log/compiler_logs/drl_xapp_batch_c_green_2026-08-28.log`; the three
  RED tracers remain recorded in the Batch C RED log above.
- Task boundary: this is preflight and evidence projection only. A live
  fixed/greedy transaction still requires profile-specific freshness and
  verified binding, a candidate-decision rule, and native ACK/apply/later-KPM
  evidence; those remain **[Needs Verification]** for Tasks 3.5, 4.3, 5.1,
  and 6.3.

### Task 3.5 source-sequence safety-boundary TDD contract (2026-08-28)

- Model / effort: active user-authorized model metadata is unavailable
  **[Needs Verification]**.
- Test boundary: `NativeFlexric.qualify("ul-prb-cap-v1")` with the existing
  primitive SWIG subscription seam.
- Acceptance: a UE observation that contains a callback ordinal but no proved
  E2 indication source-sequence provenance returns
  `SOURCE_SEQUENCE_UNVERIFIED` at `failed_stage=binding` and reports
  `control_attempted=false`.
- Irreversible side effects: none. The test supplies in-memory callbacks and
  sends no E2SM-RC control.
- Boundary gate: clear. The approved bridge-gates requirement prohibits
  guessing a target binding, while the current SWIG projection records its
  `source_seq` as a callback ordinal **[Needs Verification]**.
- Test file: `redcap_library/bash_tool/scripts/test_redcap_drl_xapp.py`.
- Test evidence: RED
  `test_log/compiler_logs/drl_xapp_task35_source_seq_red_2026-08-28.log`
  failed only because the old result was
  `KPM_QUALIFICATION_POLICY_REQUIRED`; GREEN
  `test_log/compiler_logs/drl_xapp_task35_source_seq_green_2026-08-28.log`
  passes 30/30 after the explicit refusal gate.

### Task 3.5 measurement-post policy decision (2026-08-30)

- Decision: the `ul-prb-cap-v1` profile owns `freshness_window_ms`,
  `cell_ue_max_skew_ms`, and `min_valid_paired_samples`; they are not global
  constants and have no CLI or model override.
- Initial state: `measurement_post.status=UNFROZEN` permits observation-only
  evidence capture but refuses every control attempt.
- Freeze boundary: a human must explicitly approve a live calibration record
  before the values become `FROZEN`. The record identifies the node, KPM
  capability/style and metric mapping, proven time origins, release/profile
  digest, and retained calibration evidence. A changed fingerprint invalidates
  the record and returns the profile to `UNFROZEN`.
- Semantics: freshness uses bridge monotonic receipt time. Cell/UE alignment
  requires comparable E2-indication event times from both streams; callback
  ordinals, raw unproven `timestamp_ms`, and local callback ordering do not
  prove alignment. A valid sample is a same-node cell/verified-target-UE pair.
- Recheck: qualification must repeat freshness, alignment, and target-binding
  checks after lease acquisition and before each baseline, candidate, and
  restore action. It must not reuse a pre-wait observation.
- Required refusal boundaries: `UNFROZEN`, stale at threshold plus one,
  skew at threshold plus one, valid-pair count at `N-1`, unproven time origin,
  and a changed calibration fingerprint each send no E2SM-RC control.

### Task 3.5 measurement-post TDD contract (2026-08-30)

- Model / effort: GPT-5.6 Terra / high.
- Test boundary: `NativeFlexric.qualify("ul-prb-cap-v1")`.
- Acceptance: one eligible node with supported cell/UE styles, primitive cell and UE observations, completed KPM-to-RC UE binding, and UE `source_seq_origin="e2_indication"`, but no human-approved frozen measurement-post policy, returns `MEASUREMENT_POST_UNFROZEN` at `failed_stage="qualification"` with `control_attempted=false`.
- Irreversible side effects: none; in-memory observation subscriptions only, no E2SM-RC control.
- Boundary gate: clear; the 2026-08-30 measurement-post decision requires human approval before a policy becomes `FROZEN`.
- Test file: `redcap_library/bash_tool/scripts/test_redcap_drl_xapp.py`.
- Test evidence: RED `test_log/compiler_logs/drl_xapp_task35_measurement_post_unfrozen_red_2026-08-30_11-06-08.log`.

### Task 3.5 E2 indication-sequence provenance TDD contract (2026-08-31)

- Test boundary: existing FlexRIC periodic indication event to `sm_cb_kpm` callback handoff.
- Acceptance: the agent assigns each periodic `RICindicationSN`; the xApp copies an available SN into KPM read data; the asynchronous copy preserves it; and the SWIG callback labels only that value as `e2_indication`.
- Refusal path: an absent SN remains absent/unavailable at the callback, so `NativeFlexric.qualify()` continues to return `SOURCE_SEQUENCE_UNVERIFIED` with `control_attempted=false`.
- Irreversible side effects: none. The source tracer creates no subscription and sends no control; live qualification remains the final interoperability proof.
- Test file: `redcap_library/bash_tool/scripts/test_redcap_drl_xapp.py`.

### Task 3.5 measurement-post GREEN implementation record (2026-08-30)

- Model / effort: GPT-5.6 Luna / max; user-confirmed model switch.
- Implementation: the existing terminal qualification refusal now returns
  `MEASUREMENT_POST_UNFROZEN`; it preserves `failed_stage=qualification`,
  the collected cell and UE observations, and `control_attempted=false`.
- Validation: the full Python suite passes 31/31 in
  `test_log/compiler_logs/drl_xapp_task35_measurement_post_unfrozen_green_2026-08-30_11-10-59.log`.
- Boundary: this slice adds no measurement policy loading or freeze path and
  does not prove live freshness, skew, sample count, fingerprint, KPM
  provenance, qualification, or E2SM-RC control. Task 3.5 remains open.

### Task 3.5 next RED slice design: workspace-locked policy delivery (2026-08-30)

- Model / effort: GPT-5.6 Terra / high; user-selected for the next TDD step.
- Test boundary: the public `redcap_drl_xapp.sh init` command and its generated
  `workspace.lock.json` plus `compose.overlay.json` artifacts, using the
  existing temporary workspace and fake-Docker fixture.
- Acceptance: initializing `ul-prb-cap-v1` writes an explicit
  `measurement_post.status=UNFROZEN` in the existing workspace lock. The
  generated bridge service receives that same lock by a read-only mount and a
  bridge-local file argument; the runtime service receives neither. The UDS
  request remains profile identity only and cannot supply or override policy.
- Irreversible side effects: a test-owned temporary workspace only. The fake
  Docker fixture may resolve compose/image metadata; it starts no container,
  subscribes to no KPM stream, and sends no E2SM-RC control.
- Boundary gate: clear. The 2026-08-30 decision makes policy profile-owned,
  human-approved, and non-overridable by CLI/model. The existing workspace
  lock is the smallest owner of the selected profile and release identity.
- Test file: `redcap_library/bash_tool/scripts/test_redcap_drl_xapp.py`.
- Planned tracer: `test_init_writes_unfrozen_measurement_post_for_bridge_only`.
- Stop condition: this slice establishes only the trusted `UNFROZEN` delivery
  source. It neither creates a human approval/freeze operation nor permits
  qualification success, freshness, skew, sample-count, or E2SM-RC control.

### Task 3.5 policy delivery TDD contract (2026-08-30)

- Model / effort: GPT-5.6 Terra / high; user-selected.
- Test boundary: public `redcap_drl_xapp.sh init` in the existing temporary
  workspace and fake-Docker fixture.
- Acceptance: `ul-prb-cap-v1` writes `measurement_post.status=UNFROZEN` to
  `workspace.lock.json`; `flexric-bridge` receives that lock through a
  read-only bind mount and a command argument containing the mount target;
  `drl-runtime` receives neither source nor target.
- Irreversible side effects: test-owned temporary workspace only; no Docker
  container, KPM subscription, or E2SM-RC control.
- Boundary gate: clear; the preceding workspace-locked policy-delivery design
  records the approved profile-owned, non-overridable policy source.
- Test file: `redcap_library/bash_tool/scripts/test_redcap_drl_xapp.py`.
- Test evidence: RED
  `test_log/compiler_logs/drl_xapp_task35_policy_delivery_red_2026-08-30_11-28-43.log`.

### Task 3.5 policy delivery GREEN implementation record (2026-08-30)

- Model / effort: GPT-5.6 Luna / max; user-confirmed switch.
- Implementation: `initialize()` writes
  `measurement_post.status=UNFROZEN` for `ul-prb-cap-v1`. The generated
  bridge overlay mounts the final workspace lock read-only at
  `/opt/redcap/workspace.lock.json` and passes that same target through
  `--workspace-lock`; `drl-runtime` receives neither lock source nor target.
  Temporary workspace construction and atomic rename remain unchanged.
- Validation: the full Python suite passes 32/32 in
  `test_log/compiler_logs/drl_xapp_task35_policy_delivery_green_2026-08-30_11-40-58.log`.
  `py_compile`, `git diff --check`, and strict OpenSpec validation pass.
- Boundary: this slice adds no policy thresholds, freeze or approval command,
  qualification logic, live KPM subscription, or E2SM-RC control. Task 3.5
  remains open pending runtime qualification and live evidence.

### Task 3.5 frozen-measurement policy TDD contract (2026-08-30)

- Model / effort: active metadata unavailable **[Needs Verification]**.
- Test boundary: `NativeFlexric.qualify("ul-prb-cap-v1")` with an injected,
  profile-owned `measurement_post` record and primitive KPM callbacks.
- Acceptance links: Task 3.5 measurement-post policy decision and the
  `drl-xapp-bridge-gates` qualification requirement.
- Irreversible side effects: none. The tracer supplies in-memory callbacks
  and asserts `control_attempted=false`; it does not open an E2SM-RC session.
- Boundary gate: clear. The frozen policy, its fingerprint, and the required
  stale/skew/sample/provenance refusals are specified above. Human approval is
  still required before a live workspace lock changes from `UNFROZEN`.
- Test files: `redcap_library/bash_tool/scripts/test_redcap_drl_xapp.py`.
- Test evidence: pending red/green logs for the FROZEN qualification tracer.

### Task 3.5 frozen-measurement implementation record (2026-08-30)

- `NativeFlexric.qualify()` now accepts a profile-owned FROZEN policy only
  after independent cell/UE event-time provenance, freshness, skew, pair
  count, target binding, and node/style/metric fingerprint checks pass.
- `freeze-measurement-post` is the only host CLI operation that changes a
  stopped workspace lock to FROZEN. It requires an explicit matching
  `--approve-calibration` set, preserves the selected calibration run IDs,
  and binds the policy to the locked release and image IDs. It starts no
  container and sends no E2SM-RC control.
- Release upgrade resets a FROZEN policy to UNFROZEN because image identity is
  part of the calibration fingerprint. A bridge re-qualifies live KPM before
  opening every control-once session.
- Validation: the focused RED logs are
  `task35_frozen_measurement_post_red_2026-08-30_15-48-00.log`,
  `task35_frozen_skew_red_2026-08-30_15-51-00.log`, and
  `task35_freeze_command_red_2026-08-30_16-00-00.log`; the full 40-test GREEN
  suite is `test_log/compiler_logs/task35_freeze_full_green_2026-08-30_16-04-00.log`.
- Live freeze remains pending human approval of a calibration record. Until
  then the retained workspace lock remains `UNFROZEN` and no control is
  eligible.

### Task 3.5 native callback-sequence provenance TDD contract (2026-08-31)

- Model / effort: active user-authorized model metadata is unavailable
  **[Needs Verification]**.
- Test boundary: the existing native SWIG KPM producer source plus the existing
  public `NativeFlexric.qualify("ul-prb-cap-v1")` refusal boundary.
- Acceptance: a locally incremented callback counter is projected as
  `bridge_callback_counter`, never `e2_indication`; such a projected UE sample
  is refused as `SOURCE_SEQUENCE_UNVERIFIED` before control.
- Irreversible side effects: none. The tracer reads the owner source and the
  public qualification test uses in-memory callbacks; no Docker, E2SM-KPM, or
  E2SM-RC operation is invoked.
- Boundary gate: clear. `source_seq` is incremented locally in
  `sm_cb_kpm()`, so it cannot truthfully establish E2 indication provenance.
- Test file: `redcap_library/bash_tool/scripts/test_redcap_drl_xapp.py`.

### Task 3.5 native callback-sequence provenance implementation record (2026-08-31)

- Implementation: `sm_cb_kpm()` now labels its locally incremented
  `source_seq` as `bridge_callback_counter` for both cell Format 1 and UE
  Format 3 projections. It does not claim E2 indication sequencing.
- Validation: the new RED tracer failed against the old claim in
  `test_log/compiler_logs/task35_native_callback_provenance_red_2026-08-31.log`.
  The focused GREEN tracer and full 42-test suite pass in
  `test_log/compiler_logs/task35_native_callback_provenance_green_2026-08-31.log`
  and
  `test_log/compiler_logs/task35_native_callback_provenance_full_green_2026-08-31.log`.
- Boundary: this makes the existing qualification gate reject native callback
  ordinals with `SOURCE_SEQUENCE_UNVERIFIED`; it does not create a true E2
  source sequence, live cell/UE qualification, or E2SM-RC control proof.

### Task 4.3 Slice B1 TDD contract (2026-08-31)

- Model / effort: active metadata unavailable **[Needs Verification]**.
- Test boundary: public UDS `Bridge.handle()` operations `open` then `act`,
  using an injected native qualification source and the existing injected
  `native_control(action)` system-boundary seam.
- Acceptance: after `open` has acquired the node lease, a newly failed
  qualification immediately before the baseline phase returns that
  qualification error and sends no native control action.
- Irreversible side effects: none. The tracer uses an in-memory qualification
  source and native-control recorder; it creates no Docker resource, KPM
  subscription, or E2SM-RC control request.
- Boundary gate: clear. Task 4.3 Slice B requires a fresh qualification before
  every phase and must not reuse a pre-lease observation.
- Test file: `redcap_library/bash_tool/scripts/test_redcap_drl_xapp.py`.
- Test evidence: pending RED/GREEN logs.

### Task 6.2 workspace compose-name TDD contract (2026-09-01)

- Model / effort: active metadata unavailable **[Needs Verification]**.
- Test boundary: `overlay_command()` as the single Docker Compose invocation
  seam for a syntactically accepted workspace name containing `.`.
- Acceptance: the generated Compose project name is lowercase and contains
  only Compose-permitted characters, while the workspace directory and locked
  user-facing name remain unchanged.
- Irreversible side effects: mocked subprocess only; no Docker, KPM, or
  E2SM-RC activity.
- Boundary gate: clear. This repair restores the existing workspace-name
  contract; it does not broaden accepted workspace input.
- Test files: `redcap_library/bash_tool/scripts/test_redcap_drl_xapp.py`.
- Test evidence: pending RED/GREEN logs.

### Task 6.2 workspace-down socket-cleanup TDD contract (2026-09-01)

- Test boundary: public `down` lifecycle command with the Docker Compose seam
  mocked and a test-owned `bridge.sock` path under the workspace `run/` path.
- Acceptance: a successful Compose down unlinks only the stale bridge socket;
  a failed Compose down preserves it and returns failure.
- Irreversible side effects: test-owned socket only; no Docker, KPM, or
  E2SM-RC activity.
- Boundary gate: clear. `freeze-measurement-post` must continue to reject a
  socket path while a bridge could be active; cleanup occurs only after
  successful lifecycle shutdown.
- Test files: `redcap_library/bash_tool/scripts/test_redcap_drl_xapp.py`.
- Test evidence: pending RED/GREEN logs.

### Task 6.2 workspace-down socket-cleanup implementation record (2026-09-01)

- Implementation: after a successful existing `down` or `remove` Compose
  lifecycle operation, the CLI unlinks only `run/bridge.sock`. A failed
  Compose operation leaves the path unchanged; a cleanup error fails instead
  of reporting a false successful shutdown.
- Validation: RED preserves the stale path; GREEN proves it is removed only
  after the mocked Compose success. Evidence:
  `test_log/compiler_logs/task62_socket_cleanup_{red,green}_2026-09-01.log`.
  The full Python tracer passes 78/78 in
  `test_log/compiler_logs/task62_socket_cleanup_full_python_2026-09-01.log`.
  The stopped live workspace reported `WORKSPACE_DOWN` and removed its stale
  socket in `test_log/compiler_logs/task62_socket_cleanup_2026-09-01.log`.
- Boundary: this does not weaken the freeze guard; a socket that remains
  present after a failed shutdown still blocks policy mutation.

### Task 4.3 Slice B2 TDD contract (2026-08-31)

- Model / effort: active metadata unavailable **[Needs Verification]**.
- Test boundary: public UDS `Bridge.handle()` operations `open` then `act`,
  using an injected native qualification source and the existing injected
  `native_control(action)` system-boundary seam.
- Acceptance: after a proved baseline, a newly failed qualification immediately
  before the candidate phase returns that qualification error, sends no
  candidate or restore, and records `RECOVERED` because the proved baseline is
  already the safe terminal state.
- Irreversible side effects: none. The tracer uses an in-memory qualification
  source and native-control recorder; it creates no Docker resource, KPM
  subscription, or E2SM-RC control request.
- Boundary gate: clear. Task 4.3 Slice B requires a fresh qualification before
  every phase and must not reuse a pre-wait observation.
- Test file: `redcap_library/bash_tool/scripts/test_redcap_drl_xapp.py`.
- Test evidence: pending RED/GREEN logs.

### Task 4.3 Slice B3 TDD contract (2026-08-31)

- Model / effort: active metadata unavailable **[Needs Verification]**.
- Test boundary: public UDS `Bridge.handle()` operations `open` then `act`,
  using an injected native qualification source and the existing injected
  `native_control(action)` system-boundary seam.
- Acceptance: after a proved candidate, a newly failed qualification immediately
  before restore returns that qualification error, sends no restore with a stale
  binding, persists `ROLLBACK_UNCONFIRMED`, and retains the target lease for
  explicit recovery.
- Irreversible side effects: none. The tracer uses an in-memory qualification
  source and native-control recorder; it creates no Docker resource, KPM
  subscription, or E2SM-RC control request.
- Boundary gate: clear. Task 4.3 Slice B requires a fresh qualification before
  every phase and must not reuse a pre-wait observation; a failed restore gate
  cannot safely target a potentially changed UE.
- Test file: `redcap_library/bash_tool/scripts/test_redcap_drl_xapp.py`.
- Test evidence: pending RED/GREEN logs.

### Task 4.3 Slice C1 TDD contract (2026-08-31)

- Model / effort: active metadata unavailable **[Needs Verification]**.
- Test boundary: `NativeFlexric.control_ul_prb()` with an injected SWIG SDK
  surface exposing the existing `control_redcap_ul_prb_sm()` owner seam.
- Acceptance: a valid primitive action resolves the exact live-node object,
  calls the existing SWIG control function with the resolved node, RC UE ID,
  RNTI, and PRB cap, and records a nonzero RIC request ID as acknowledgement.
  It must not report a gNB apply marker or later KPM observation.
- Irreversible side effects: none. The tracer uses an in-memory SWIG SDK and
  does not connect to a RIC or issue E2SM-RC control.
- Boundary gate: clear. The existing SWIG control owner returns an ACK/request
  ID only; Task 5.1 owns gNB apply-marker and later-KPM proof correlation.
- Test file: `redcap_library/bash_tool/scripts/test_redcap_drl_xapp.py`.
- Test evidence: pending RED/GREEN logs.

### Task 4.3 Slice C2 TDD contract (2026-08-31)

- Model / effort: active metadata unavailable **[Needs Verification]**.
- Test boundary: `NativeFlexric.control_ul_prb()` with an injected SWIG SDK
  control recorder.
- Acceptance: boolean values for numeric RC UE ID, RNTI, or UL-PRB fields are
  invalid control input. The adapter returns `INVALID_CONTROL_ACTION` and does
  not invoke the native SWIG control owner seam.
- Irreversible side effects: none. The tracer uses an in-memory SWIG SDK and
  asserts its native control recorder remains empty.
- Boundary gate: clear. Python accepts `bool` as an integer subtype, whereas
  the existing RedCap control contract permits only numeric protocol values.
- Test file: `redcap_library/bash_tool/scripts/test_redcap_drl_xapp.py`.
- Test evidence: pending RED/GREEN logs.

### Task 4.3 Slice C2 implementation record (2026-08-31)

- Implementation: `NativeFlexric.control_ul_prb()` rejects booleans in RC UE
  ID, RNTI, and UL-PRB fields before integer conversion, so no native SWIG
  control call can turn `True` into protocol value `1`.
- Validation: the focused tracer first failed because `True` became request
  value `1`; it then passed after the guard. Evidence is retained in
  `test_log/compiler_logs/task43_c2_native_bool_{red,green}_2026-08-31_*.log`.
- Boundary: this validates Python input type safety only. It neither sends a
  real E2SM-RC action nor proves gNB apply-marker or later-KPM evidence.

### Task 4.3 Slice A1 TDD contract (2026-08-31)

- Model / effort: active metadata unavailable **[Needs Verification]**.
- Test boundary: public `run_model()` fixed-controller path after the existing
  runtime smoke and UDS discovery/qualification gates.
- Acceptance: while no approved fixed/greedy candidate rule exists, an enabled
  fixed run returns `CANDIDATE_POLICY_REQUIRED` and sends discovery plus
  qualification only; it never sends a UDS `act` request.
- Irreversible side effects: test-owned evidence files only. The UDS callable
  records requests and makes no E2SM-RC request.
- Boundary gate: clear. The profile fixes only the legal range `0..275`; it
  does not authorize the controller to invent a candidate action.
- Test file: `redcap_library/bash_tool/scripts/test_redcap_drl_xapp.py`.
- Test evidence: pending RED/GREEN logs.

### Task 4.3 Slice A1 implementation record (2026-08-31)

- Implementation: `run --controller fixed --enable-control` now reports
  `CANDIDATE_POLICY_REQUIRED` after its existing smoke and qualification
  gates, instead of misreporting absent candidate semantics as a binding
  failure. It sends no `act` request.
- Validation: the public CLI tracer records only `discover`, `qualify`, and
  the explicit policy refusal. Its RED/GREEN logs are
  `test_log/compiler_logs/task43_a1_policy_refusal_{red,green}_2026-08-31_*.log`.
- Boundary: this is a fail-closed policy-absence slice. It does not define the
  required fixed candidate or greedy rule, so it cannot enable control.

### Task 4.3 Slice C3 verification contract (2026-08-31)

- Test boundary: public UDS `Bridge.handle()` `open` then `act`, with a valid
  target binding but no injected apply-proof provider.
- Acceptance: `act` returns `APPLY_PROOF_PROVIDER_REQUIRED`; the durable
  journal remains at `LEASE_ACQUIRED`, proving no baseline/candidate/restore
  phase was entered.
- Irreversible side effects: test-owned lease and journal files only; no
  native provider exists, therefore no E2SM-RC request is possible.
- Boundary gate: clear. Task 4.3 C explicitly requires failure before control
  when the provider that can return all required proof fields is unavailable.
- Test file: `redcap_library/bash_tool/scripts/test_redcap_drl_xapp.py`.

### Task 4.3 Slice C3 verification record (2026-08-31)

- Validation: the public UDS tracer passes with a valid binding and no
  provider, returning `APPLY_PROOF_PROVIDER_REQUIRED` while the durable
  journal remains `LEASE_ACQUIRED`. Evidence:
  `test_log/compiler_logs/task43_c3_provider_refusal_green_2026-08-31_*.log`.
- Boundary: the native adapter's SWIG ACK/request-ID projection remains
  separate from apply proof. This verification does not make a live request.

### Task 4.3 Slice C4 TDD contract (2026-08-31)

- Model / effort: active metadata unavailable **[Needs Verification]**.
- Test boundary: `NativeFlexric.control_ul_prb()` with a SWIG provider that
  exposes the control method but raises while enumerating E2 nodes.
- Acceptance: the adapter returns `NATIVE_CONTROL_UNAVAILABLE` and invokes no
  SWIG control method.
- Irreversible side effects: none. The tracer uses an in-memory SDK whose
  control recorder must remain empty.
- Boundary gate: clear. A provider that cannot resolve the target is not an
  available native control provider and must fail before transmission.
- Test file: `redcap_library/bash_tool/scripts/test_redcap_drl_xapp.py`.
- Test evidence: pending RED/GREEN logs.

### Task 4.3 Slice C4 implementation record (2026-08-31)

- Implementation: `NativeFlexric.control_ul_prb()` materializes the existing
  node-provider result before target matching. An unavailable/malformed
  provider returns `NATIVE_CONTROL_UNAVAILABLE` before the SWIG control call.
- Validation: the tracer first raised `RuntimeError` from node enumeration;
  it passes after the fail-closed guard. Evidence:
  `test_log/compiler_logs/task43_c4_provider_unavailable_{red,green}_2026-08-31_*.log`.
- Boundary: this establishes provider availability only. ACK/request-ID are
  still not gNB apply or later-KPM proof.

### Task 4.3 Slice A2 TDD contract (2026-08-31)

- Model / effort: active metadata unavailable **[Needs Verification]**.
- Test boundary: public `run_model()` invocation with a generic
  `--episodes` request.
- Acceptance: any supplied generic episode count returns
  `PROFILE_SPECIFICATION_REQUIRED` before runtime smoke, qualification,
  runtime entrypoint, or UDS control activity.
- Irreversible side effects: none. The tracer records all existing external
  seams and asserts none is reached.
- Boundary gate: clear. The change's model-runner requirement prohibits
  generic multi-episode training until a separately approved profile defines
  state, action, reward, reset, and rate semantics.
- Test file: `redcap_library/bash_tool/scripts/test_redcap_drl_xapp.py`.
- Test evidence: pending RED/GREEN logs.

### Task 4.3 Slice A2 implementation record (2026-08-31)

- Implementation: the CLI accepts `--episodes` only to reject it with
  `PROFILE_SPECIFICATION_REQUIRED`; generic episode semantics cannot reach a
  runtime, qualification, model entrypoint, or control request.
- Validation: the tracer first reached the unrelated model-entrypoint
  refusal; it passes after the new profile-specification refusal. Evidence:
  `test_log/compiler_logs/task43_a2_multiepisode_refusal_{red,green}_2026-08-31_*.log`.
- Boundary: this is a refusal-only option. It does not define or enable any
  episode count, candidate policy, or live control transaction.

### Task 4.3 `--episodes` removal TDD contract (2026-09-01)

- Model / effort: active metadata unavailable **[Needs Verification]**.
- Test boundary: public `redcap_drl_xapp.sh run` parser invoked with the
  removed `--episodes` option.
- Acceptance: the parser returns its normal argument error (exit code `2`)
  before `run_model()`, workspace access, evidence creation, runtime startup,
  or UDS control.
- Irreversible side effects: none; the tracer invokes only the parser and
  asserts no Control Run package exists.
- Boundary gate: clear. `--episodes` was temporary test syntax, while generic
  multi-episode semantics remain outside the approved profile.
- Test file: `redcap_library/bash_tool/scripts/test_redcap_drl_xapp.py`.
- Test evidence: pending RED/GREEN logs.

### Task 4.3 `--episodes` removal implementation record (2026-09-01)

- Implementation: remove `--episodes` from the public `run` parser and delete
  the corresponding `run_model()` branch. The parser now rejects the option
  before workspace loading or Control Run creation.
- Validation: the parser-level tracer was RED while the temporary option
  existed; the public `redcap_drl_xapp.sh` tracer is GREEN after removal, and
  the full Python tracer passes 66 tests. Evidence:
  `test_log/compiler_logs/task43_remove_episodes_{red,public_green,public_full_green}_2026-09-01_*.log`.
- Boundary: this removes temporary syntax only. It defines no multi-episode
  policy, runtime loop, or live-control behavior.

### Task 4.3 approved validation-policy decision (2026-08-31)

- User-approved fixed controller candidate: `max_ul_prb=16`.
- User-approved greedy input: the latest qualified cell `RRU.PrbTotUl`
  percentage. The gNB owner emits it as `(ul_used * 100 / ul_total)` in
  `ran_func_kpm.c`; nonnumeric or out-of-range projections are refused.
- User-approved greedy thresholds: below 55% selects `16`; 55% through 80%
  selects `32`; above 80% selects `64`.
- User-approved proof window: xApp ACK, gNB apply marker, and candidate later
  qualified KPM evidence each have a one-second window after control send.

### Task 4.3 Slice A3 TDD contract (2026-08-31)

- Model / effort: active metadata unavailable **[Needs Verification]**.
- Test boundary: CLI validation-policy selector consumed by `run --enable-control`.
- Acceptance: fixed selects `16`; greedy selects `16`, `32`, and `64` at
  independent utilization examples 54%, 55%/80%, and 81%, respectively.
  Invalid/missing utilization refuses rather than producing an action.
- Irreversible side effects: none. The selector is pure and the tracer sends
  no UDS, Docker, or E2SM-RC request.
- Boundary gate: clear. The user approved the fixed value, KPM metric,
  threshold map, and one-second proof window above.
- Test file: `redcap_library/bash_tool/scripts/test_redcap_drl_xapp.py`.
- Test evidence: pending RED/GREEN logs.

### Task 4.3 Slice D1 TDD contract (2026-08-31)

- Model / effort: active metadata unavailable **[Needs Verification]**.
- Test boundary: public `run_model()` greedy-controller path with the existing
  UDS helper replaced by a local transport recorder.
- Acceptance: a qualified `RRU.PrbTotUl=55` selects candidate `32` and emits
  exactly `open`, `act`, and `close` UDS results in that order. When `act`
  returns `APPLY_PROOF_PROVIDER_REQUIRED`, `close` still occurs and the CLI
  reports control failure rather than success.
- Irreversible side effects: test-owned run evidence only. The recorder makes
  no Docker, E2 subscription, or E2SM-RC control request.
- Boundary gate: clear. The user approved the greedy thresholds; Task 4.3 D
  requires safe close after an act failure, while Task 4.3 E remains the only
  path that may turn an ACK into a proved apply result.
- Test file: `redcap_library/bash_tool/scripts/test_redcap_drl_xapp.py`.
- Test evidence: pending RED/GREEN logs.

### Task 4.3 Slice A3 implementation record (2026-08-31)

- Implementation: `validation_candidate()` selects fixed `16`; its greedy
  path reads the latest qualified cell `RRU.PrbTotUl` percentage and maps
  `<55` to `16`, `55..80` to `32`, and `>80` to `64`. Missing, boolean,
  nonnumeric, or out-of-range values return `UL_PRB_UTILIZATION_REQUIRED`.
- Validation: the RED tracer failed because the selector was absent. The
  focused GREEN tests cover 54, 55, 80, and 81 percent plus invalid input;
  evidence is `test_log/compiler_logs/task43_a3_candidate_policy_{red,green}_2026-08-31_*.log`.
- Boundary: selection remains data-only. It does not itself establish apply
  proof or send an E2SM-RC request.

### Task 4.3 Slice D1 implementation record (2026-08-31)

- Implementation: the enabled fixed/greedy runner captures qualification,
  selects one candidate, and uses the existing UDS helper for `open`, `act`,
  then `close`. The one-second policy applies to each native phase's proof,
  not to the enclosing three-phase UDS transaction. The run manifest and
  ordered event stream retain the three result objects; `close` occurs after
  an `act` failure when `open` produced a session.
- Validation: the D1 RED tracer failed at the pre-existing qualification
  return boundary; GREEN records `open`, `act`, `close`, candidate `32` at
  55%, and a safe close after `APPLY_PROOF_PROVIDER_REQUIRED`. Full-suite
  evidence is `test_log/compiler_logs/task43_a3_d1_full_green_2026-08-31_*.log`.
- Boundary: this is orchestration and fail-closed evidence. The bridge does
  not yet receive a real marker/KPM proof provider, so a live `act` remains
  unable to report success.

### Task 4.3 Slice E1 TDD contract (2026-08-31)

- Model / effort: active metadata unavailable **[Needs Verification]**.
- Test boundary: the bridge marker-proof reader consumes a host-written JSONL
  record with the actual gNB marker fields `rnti`, `requested`, `effective`,
  and `observed_monotonic_ms`.
- Acceptance: only a record matching the action RNTI and requested PRB within
  one second after the send timestamp proves marker application. A stale or
  mismatched record is not proof.
- Irreversible side effects: test-owned proof file only; no Docker, E2
  subscription, or E2SM-RC request.
- Boundary gate: clear. The gNB owner marker contains RNTI, requested, and
  effective PRBs but no RIC request ID. The exclusive lease and sequential
  phases make these fields plus the approved time window the available
  correlation key.
- Test file: `redcap_library/bash_tool/scripts/test_redcap_drl_xapp.py`.
- Test evidence: pending RED/GREEN logs.

### Task 4.3 Slice E1 implementation record (2026-08-31)

- Implementation: `marker_proof()` reads the host-mounted JSONL evidence with
  the standard library and accepts only records whose RNTI and requested PRB
  equal the current action and whose monotonic observation timestamp falls in
  the inclusive `0..1000 ms` proof window. Missing files, malformed records,
  booleans, and out-of-contract action fields fail closed.
- Validation: the RED tracer failed because no reader existed; GREEN covers a
  matching record plus stale and mismatched records. Evidence:
  `test_log/compiler_logs/task43_e1_marker_proof_{red,green}_2026-08-31.log`.
- Boundary: this is a local evidence reader, not a collector or a native proof
  provider. It cannot yet prove a live gNB apply without a host process that
  writes the actual marker records and a subsequent qualified KPM observation.

### Task 4.3 Slice E2-E4 implementation record (2026-09-01)

- Decision applied: every baseline, candidate, restore, and recovery control
  phase requires native ACK, matching gNB marker, and a later qualified KPM
  observation. All three must complete within the phase's one-second window.
- Implementation: `NativeFlexric.prove_ul_prb()` timestamps the native send,
  accepts a marker only for the action's RNTI/requested PRB in that window,
  and spends the remaining time on a new qualified KPM observation whose
  target binding matches the action. `serve()` injects this as the one native
  provider. The host CLI starts a read-only gNB log collector before UDS open,
  projects only the existing apply marker into the bridge-mounted JSONL and
  run excerpt, and refuses before UDS when the collector cannot start.
- Validation: focused RED/GREEN logs cover the all-phase proof requirement,
  native proof composition, marker projection, and pre-UDS collector refusal.
  Full tracer passes 60 tests:
  `test_log/compiler_logs/task43_e4_full_green_2026-09-01.log`.
- Evidence boundary: the marker timestamp is the host collector receipt time,
  not an on-gNB execution timestamp. Host/container monotonic-clock namespace
  equivalence and live E2SM-RC/KPM interoperability remain **[Needs
  Verification]**; a live 6.3 transaction is still required before claiming
  control success.

### Task 4.3 model single-inference TDD contract (2026-09-01)

- Model / effort: active metadata unavailable **[Needs Verification]**.
- Test boundary: public `run_model()` model-controller path and the existing
  `redcap-drl-run-entrypoint` executable, using a temporary workspace,
  qualified primitive observations, and local transport/runtime recorders.
- Acceptance: after smoke and qualification, exactly 30 latest valid paired
  E2-indication observations produce one immutable runtime-readable JSON
  observation with only `RRU.PrbTotUl` `latest`, `mean`, `min`, and `max`
  percentages. The entrypoint receives that observation, emits exactly one JSON
  decision line, and the CLI accepts only the strict integer candidate range
  `1..51` before the existing one-candidate transaction. A model error,
  malformed/extra output, boolean, float, string, missing value, `0`, or `52+`
  candidate sends no UDS control request. The generic native contract remains
  `0..275`; `0` is reserved for baseline/restore, never model output.
  A model controller without `--enable-control` is refused because it has no
  approved observation input.
- Irreversible side effects: test-owned temporary observation/evidence files
  only. Docker, KPM subscription, and E2SM-RC control are replaced by local
  seams.
- Boundary gate: clear. The user approved the 30-sample summary, metric,
  single inference, and model candidate domain. Live collection cadence and
  the human-frozen measurement-post policy remain **[Needs Verification]**;
  Task 6.3 remains the first live-control proof.
- Test files: `redcap_library/bash_tool/scripts/test_redcap_drl_xapp.py`.
- Test evidence: pending RED/GREEN logs.

### Task 4.3 model single-inference implementation record (2026-09-01)

- Implementation: `run_model()` now derives the latest 30 valid paired
  E2-indication samples into an immutable `/run/redcap-drl` observation file
  containing only `RRU.PrbTotUl` `latest`, `mean`, `min`, and `max` values.
  It invokes `module:callable` exactly once through the existing runtime
  wrapper. The wrapper passes the decoded observation mapping to the callable,
  redirects model diagnostics to stderr, and emits one JSON decision line.
  The profile parser accepts only a single strict integer `max_ul_prb` in
  `1..51`; invalid output refuses before UDS `open`. The existing generic
  native `0..275` contract is unchanged, and `0` remains baseline/restore
  only. The runtime image adds `/workspace/src` to its existing `PYTHONPATH`
  so the workspace's editable model module is importable.
- Validation: the focused model-contract tracers pass 6/6 in
  `test_log/compiler_logs/task43_model_contract_green_2026-09-01.log`; the
  full Python suite passes 66/66 in
  `test_log/compiler_logs/task43_model_full_green_2026-09-01.log`. The
  boundary tracer exposed a missing-output `KeyError`; it now returns
  `MODEL_CANDIDATE_REQUIRED` before any UDS request. Initial contract RED
  evidence is `test_log/compiler_logs/task43_model_single_inference_red_2026-09-01.log`.
- Evidence boundary: this is local, mocked orchestration. It does not prove
  that a live system can collect 30 samples at its measured cadence, freeze
  measurement-post calibration, establish host/container clock equivalence,
  or complete real E2SM-RC/KPM proof; those remain **[Needs Verification]**
  for Tasks 6.2 and 6.3.

### Task 6.2/6.3 live validation record (2026-09-01)

- Implementation: built immutable release `1.0.15`, initialized separate CPU
  and GPU workspaces, and exercised the existing CN5G/FlexRIC/gNB/UE compose
  without modifying its source. The CLI ran read-only runtime/bridge smoke,
  E2 capability discovery, and profile qualification; it did not invoke
  `run --enable-control`.
- Validation: release and workspace evidence is in
  `test_log/compiler_logs/task62_live_qualification_2026-09-01.log`,
  `test_log/runtime_configs/drl_releases/1.0.15.json`, and the two workspace
  `artifacts/runs/` trees. Discovery passed for node `2:1:1:3584`. CPU
  qualification recorded one valid paired E2-indication sample but stopped at
  `MEASUREMENT_POST_UNFROZEN`; GPU retries included `KPM_STREAM_EMPTY`.
  The local Python tracer passes 72/72. The UDS client now handles workspace
  paths over the Linux AF_UNIX limit with a temporary short symlink.
- Boundary: Task 6.2 is not complete because the profile's human-approved
  measurement-post policy and stable live KPM callback cadence are not proven.
  Task 6.3 remains unexecuted by design: no E2SM-RC request, gNB marker, or
  later-KPM control proof exists. These live facts remain **[Needs
  Verification]** until an operator freezes measured thresholds and the
  qualification gate passes.

### Task 6.2 cadence and retained-stream TDD contract (2026-09-01)

- Model / effort: active metadata unavailable **[Needs Verification]**.
- Test boundary: the public observation-only `probe-kpm` CLI/UDS `observe`
  path, and `NativeFlexric.prove_ul_prb()` with an in-process SWIG seam.
- Acceptance: a successful probe records, separately for `cell` and `ue`, the
  accepted subscription time, first callback latency, callback count, latest
  `RICindicationSN`, and latest E2 event time; it sends no E2SM-RC control.
  Once a session has subscribed, qualification waits for a fresh paired sample
  without replacing those subscriptions. A later-KPM proof accepts only a
  pair received after the native send timestamp and does not subscribe again.
- Irreversible side effects: test-owned evidence only. The native control
  seam is a local recorder; Docker, live KPM subscription, and E2SM-RC are
  not used by tests.
- Boundary gate: clear. The user approved the observation-only CPU-first
  repair sequence. Measurement-post thresholds remain human-approved and
  Task 6.3 remains closed until a fresh live qualification passes.
- Test files: `redcap_library/bash_tool/scripts/test_redcap_drl_xapp.py`.
- Test evidence: pending RED/GREEN logs.

### Task 6.2 workspace compose-name implementation record (2026-09-01)

- Implementation: the single `overlay_command()` seam lowercases the locked
  workspace name and replaces `.` with `-` only for Docker Compose's project
  argument. The workspace directory and lock name are unchanged.
- Validation: the RED tracer captured Compose rejecting
  `redcap-drl-task62-cpu-1.0.16`; GREEN accepts
  `redcap-drl-task62-cpu-1-0-16`. Evidence:
  `test_log/compiler_logs/task62_compose_project_name_{red,green}_2026-09-01.log`.
  The full Python tracer passes 77/77 in
  `test_log/compiler_logs/task62_cadence_full_python_final_2026-09-01.log`.
- Boundary: this fixes an input-contract inconsistency before Docker starts;
  it does not change control policy.

### Task 6.2 cadence and retained-stream implementation record (2026-09-01)

- Implementation: the native KPM report period is 100 ms. `probe-kpm` records
  separate cell/UE subscription acceptance, first callback latency, count,
  E2 indication sequence, and event time without control. A bridge session
  retains successful subscriptions; later-KPM proof passes the native send
  timestamp to qualification and accepts only a fresh post-send pair.
- Validation: focused RED/GREEN evidence is
  `test_log/compiler_logs/task62_{cadence_probe,probe_cli,retained_stream}_{red,green}_2026-09-01_*.log`.
  Release `1.0.16` passed runtime and bridge smoke in
  `test_log/compiler_logs/task62_cadence_repair_2026-09-01.log`. CPU run
  `20260901T094918Z-2840effd` passed observation-only probe on
  `2:1:1:3584`: both streams received 3 callbacks, first callback latency
  103 ms, and `RICindicationSN` 3. Thirty subsequent unfrozen
  qualifications kept the same node/RNTI `9419`, advanced sequence 476 to
  1171, produced 30 valid pairs with maximum freshness 1 ms and skew 0 ms,
  and recorded `control_attempted=false` throughout.
- Load calibration: the initial 10 Mbit/s, 12-second UE-to-external-DN UDP
  flow carried 10.5 Mbit/s with 0% loss but was below the cell metric's integer
  percentage resolution. A second 50 Mbit/s flow carried 52.4 Mbit/s with 0%
  loss. Its 30 fail-closed qualification runs retained a single node/RNTI,
  recorded maximum freshness 2 ms and skew 1 ms, and produced cell
  `RRU.PrbTotUl` values `0..37` (mean 7.2; 6 nonzero values). The immutable
  summary and exact run IDs are
  `test_log/runtime_configs/task62_cadence_workspaces/task62-cpu-1.0.16/load_calibration_summary_20260901.json`.
- Boundary: this is representative low-load evidence for candidate `16`; it
  does not validate the 55%/80% greedy boundaries. The human must approve the
  freshness/skew/sample thresholds before `freeze-measurement-post`. Live
  native ACK, gNB marker, and post-send KPM proof remain **[Needs
  Verification]** for Task 6.3; no E2SM-RC control was sent.

### Task 6.2 frozen qualification implementation record (2026-09-02)

- Decision: the approved measurement-post policy is `freshness_window_ms=200`,
  `cell_ue_max_skew_ms=20`, and `min_valid_paired_samples=30`. The policy is
  frozen against release `1.0.17`, node `2:1:1:3584`, both cell metrics, and
  the existing UE metric set. Qualification retains 30 paired samples, while
  freshness is evaluated from the latest pair; a later native phase uses one
  fresh post-send pair inside its one-second proof window.
- Implementation: the CPU workspace lock was upgraded to immutable bridge
  `redcap-flexric-bridge:1.0.17` and runtime
  `redcap-drl-runtime:1.0.17-cpu`. A clean CN5G/FlexRIC/gNB/UE restart was
  performed before `verify`, `probe-kpm`, and frozen `qualify-kpm`.
- Validation: `probe-kpm` passed at run
  `20260902T014627Z-af59fb39`; frozen qualification passed at run
  `20260902T014636Z-2051229b` with 30 valid paired samples, latest freshness
  `1 ms`, maximum cell/UE skew `0 ms`, and
  `source_seq_origin=e2_indication`. Evidence is retained under
  `test_log/runtime_configs/task62_cadence_workspaces/task62-cpu-1.0.16/artifacts/runs/`
  and the transcript is
  `test_log/compiler_logs/task62_frozen_requalification_final_2026-09-02.log`.
- Boundary: the CPU Task 6.2 gate is proven. The parent 6.2 checkbox remains
  open because a fresh GPU live qualification was not repeated after the
  release restart; GPU release smoke remains passed. No E2SM-RC control was
  sent during this qualification record.

### Task 6.3 bounded control validation record (2026-09-02)

- Implementation: after the fresh frozen CPU qualification, the fixed
  controller selected candidate `16` and started the read-only gNB marker
  collector before UDS `open`. The single attempted transaction used the
  existing baseline → candidate → restore orchestration.
- Validation: `open` returned a session. The native bridge log recorded three
  E2SM-RC ACKs and the gNB excerpt recorded requested/effective PRBs `0`,
  `16`, and `0` for RNTI `0x0f33`. The client-side `act` result timed out at
  the pre-repair five-second UDS timeout; `close` then saw a reset connection,
  so the run gate is FAIL. The bridge had completed its durable journal at
  `COMPLETED`, but the evidence run's UDS result object remained unavailable.
  Evidence: run `20260902T014841Z-c3433b77`, manifest
  `test_log/runtime_configs/task62_cadence_workspaces/task62-cpu-1.0.16/artifacts/runs/20260902T014841Z-c3433b77/manifest.json`,
  event stream and marker excerpt in that directory, and transcript
  `test_log/compiler_logs/task63_bounded_control_2026-09-02.log`.
- Boundary: native application/restore markers and ACKs are not an end-to-end
  control PASS when the UDS result cannot be delivered. Task 6.3 remains
  unchecked; no second live control is authorized by this record.

### Task 6.3 UDS budget and teardown repair TDD record (2026-09-02)

- Decision: the enclosing three-phase UDS request needs a 20-second client
  timeout; the one-second limit remains on each native proof phase. The
  existing `--teardown` flag must call the workspace `down` lifecycle after
  finalization, including after a failed control run.
- RED: the timeout assertion failed with `[5, 5, 5]` instead of the required
  budget, and the teardown test observed zero `down` calls. Evidence:
  `test_log/compiler_logs/task63_uds_timeout_red_2026-09-02.log` and
  `test_log/compiler_logs/task63_teardown_red_2026-09-02.log`.
- GREEN: `CONTROL_UDS_TIMEOUT_SECONDS` is now `20`, and `run_model()` invokes
  `lifecycle(command=down)` when `--teardown` is set. Focused tests and the
  full 81-test Python suite pass; evidence:
  `test_log/compiler_logs/task63_uds_timeout_green_2026-09-02.log`,
  `test_log/compiler_logs/task63_teardown_green_2026-09-02.log`, and
  `test_log/compiler_logs/task63_orchestration_repairs_full_green_2026-09-02.log`.
- Boundary: these are local orchestration repairs only. They do not convert
  the already attempted live run into success and do not justify a new
  E2SM-RC transaction without explicit approval.

### Task 6.2 GPU live qualification implementation record (2026-09-02)

- Decision: the GPU workspace uses immutable release `1.0.17` and the same
  human-approved measurement-post policy as CPU:
  `freshness_window_ms=200`, `cell_ue_max_skew_ms=20`, and
  `min_valid_paired_samples=30`. The qualification remains observation-only;
  no model inference or E2SM-RC control is part of this record.
- Implementation: the existing GPU workspace was upgraded, the selected
  CN5G/FlexRIC/gNB/UE topology was restarted, and `verify`, `probe-kpm`, and
  `qualify-kpm` were run through the public CLI. Thirty one-pair GPU
  calibration runs were retained before freezing the policy. A transient
  nearRT-RIC exit (`139`) after subscription cleanup was recovered by
  restarting only that service; the final smoke ran in the permitted UDS
  execution environment. The GPU workspace, target stack, and CN5G services
  were removed after evidence capture.
- Validation: frozen `qualify-kpm` passed at run
  `20260902T063402Z-c24ac755` for node `2:1:1:3584`, verified target RNTI
  `45242`, 30 valid paired `e2_indication` samples, latest freshness `1 ms`,
  and maximum cell/UE skew `0 ms`; `control_attempted=false`. The transcript
  and all calibration outputs are in
  `test_log/compiler_logs/task62_gpu_live_qualification_2026-09-02.log`, and
  the final manifest is
  `test_log/runtime_configs/task62_workspaces/task62-gpu/artifacts/runs/20260902T063402Z-c24ac755/manifest.json`.
- Boundary at that record time: this proved GPU observation-only discovery,
  cadence, target binding, and frozen measurement-post qualification. It did
  not prove a post-send KPM pair, native ACK, gNB marker, or a bounded
  E2SM-RC transaction; the later 6.2.2/6.3 live record is below.
  Host/container monotonic-clock equivalence and live E2SM-RC/KPM
  interoperability remain **[Needs Verification]**.

### Task 6.2.2 retained-stream contract recheck (2026-09-02)

- Test boundary: the public native proof seam with an in-process SWIG
  recorder; no Docker, E2 subscription, or E2SM-RC request.
- Validation: 4/4 focused tracers pass in
  `test_log/compiler_logs/task62_2_retained_stream_recheck_2026-09-02.log`.
  The tracers cover ACK/marker/fresh-KPM composition within one second, a
  one-pair post-send proof while the pre-control policy requires 30 samples,
  retained subscriptions without resubscription after send, and the 100 ms
  native report period.
- Boundary: this recheck proves the local retained-stream contract only. A
  live native phase with real ACK, gNB marker, and later KPM remains required
  before 6.2.2 and Task 6.3 can be marked complete; no control was sent.

### Task 6.3 evidence journal finalization TDD contract (2026-09-02)

- Test boundary: the public `run --enable-control` orchestration with local
  UDS and marker seams, plus a workspace-mounted durable journal updated by
  the simulated bridge after `act`.
- Acceptance: when control was attempted, the single finalized run package's
  `control_journal.json` projects the latest valid workspace journal,
  including the final recovery state, while retaining
  `control_attempted=true`. A preflight refusal that never writes
  `control_attempted=true` keeps the package's `NOT_STARTED` journal. No
  finalized event or manifest may be written before this synchronization.
- Irreversible side effects: test-owned temporary workspace and evidence files
  only; no Docker, E2 subscription, or E2SM-RC request.
- Boundary gate: clear. The fix closes an evidence-copy race/ordering defect;
  it does not add another control attempt or change the native proof contract.
- Test file: `redcap_library/bash_tool/scripts/test_redcap_drl_xapp.py`.
- Test evidence: `test_log/compiler_logs/task63_journal_finalization_{red,green,full_green}_2026-09-02.log`.

### Task 6.2.2 / 6.3 live native proof record (2026-09-02)

- Implementation: after the frozen CPU qualification passed, the explicitly
  approved runner executed one fixed candidate `16` control-once transaction.
  The bridge used the retained cell/UE KPM subscriptions for each later pair;
  `NativeFlexric.prove_ul_prb()` enforced native ACK, matching marker, and
  later qualified KPM before the inclusive one-second deadline for baseline,
  candidate, and restore.
- Validation: run `20260902T071437Z-b5133c57` returned `open`, `act`, and
  `close` with `ok=true`; `act` reported
  `baseline-candidate-restore`. The marker excerpt recorded requested and
  effective PRBs `0`, `16`, `0` for RNTI `7651`; qualification recorded 30
  paired `e2_indication` samples with latest freshness `0 ms` and maximum
  cell/UE skew `1 ms`. The run emitted exactly one start and one finish event,
  and teardown removed the selected workspace. Evidence is retained at
  `test_log/runtime_configs/task62_cadence_workspaces/task62-cpu-1.0.16/artifacts/runs/20260902T071437Z-b5133c57/`
  with transcript
  `test_log/compiler_logs/task63_bounded_control_approved_2026-09-02.log`.
- Boundary: this proves one live fixed transaction and the retained-stream
  native proof path. The gNB marker time is the host collector receipt time;
  host/container monotonic-clock equivalence and broader E2SM-RC/KPM
  interoperability remain **[Needs Verification]**. No model training or
  second live control was performed.

### Task 6.3 evidence journal finalization implementation record (2026-09-02)

- Implementation: `finalize_control_run()` now reads the workspace durable
  journal after a control attempt, merges its final state into the run package
  journal while retaining `control_attempted=true`, and only then appends
  `CONTROL_RUN_FINISHED` and writes the finalized manifest. Preflight failures
  that never set `control_attempted=true` keep the initial `NOT_STARTED`
  journal; malformed package or workspace JSON fails closed as
  `EVIDENCE_FINALIZATION_FAILED`.
- Validation: the RED tracer reproduced the stale `OPEN_PENDING` package
  journal; GREEN and the full 82-test Python tracer pass after the repair.
  Evidence:
  `test_log/compiler_logs/task63_journal_finalization_{red,green,full_green}_2026-09-02.log`.
- Boundary: the already finalized live package is immutable and was not
  rewritten. Its workspace journal is retained as the final-state companion
  (`state=COMPLETED`); the repair applies to subsequent packages. No second
  live control was sent.

### Task 6.4 evidence package finalization TDD contract (2026-09-02)

- Test boundary: standalone `discover-kpm`, `probe-kpm`, `qualify-kpm`, and
  `recover` evidence paths plus enabled control finalization, using temporary
  local UDS/marker seams only.
- Acceptance: every terminal standalone package writes `finalized_at` and
  refuses later event append. A control package must fail closed when a
  control attempt has no valid terminal workspace durable journal (`COMPLETED`,
  `RECOVERED`, or `ROLLBACK_UNCONFIRMED`; a successful run requires
  `COMPLETED`). The finalized
  manifest is written before the terminal event is appended; if that manifest
  write fails, no `CONTROL_RUN_FINISHED` event is retained or emitted. Fixed
  and greedy manifests omit model artifact paths; model observation is listed
  only when created and model decision only after strict candidate validation.
- Irreversible side effects: test-owned temporary workspaces and evidence
  files only; no Docker, E2 subscription, or E2SM-RC request.
- Boundary gate: clear. This closes evidence truthfulness and lifecycle
  ordering; it does not add control attempts or change native proof policy.
- Test file: `redcap_library/bash_tool/scripts/test_redcap_drl_xapp.py`.
- Test evidence: RED `test_log/compiler_logs/task64_evidence_finalization_red_2026-09-02.log`,
  GREEN `test_log/compiler_logs/task64_evidence_finalization_green_2026-09-02.log`,
  nonterminal-journal boundary `test_log/compiler_logs/task64_nonterminal_journal_green_2026-09-02.log`,
  and full GREEN `test_log/compiler_logs/task64_evidence_finalization_full_green_2026-09-02.log`.

### Task 6.4 evidence package finalization implementation record (2026-09-02)

- RED: the focused tracer reproduced missing `finalized_at`, post-finalization
  event append, stale model artifact paths, missing-journal acceptance, and a
  terminal event surviving manifest-write failure.
- Implementation: standalone bridge gates now finalize their own manifest;
  `record_event()` refuses later appends; control finalization requires a valid
  workspace journal after an attempted control, writes the manifest before the
  terminal event, and lists model artifacts only when they exist and are
  trusted. The change uses only the Python standard library.
- GREEN: the focused 8-test slice, the nonterminal-journal boundary test, and
  the full 84-test tracer pass. Evidence:
  `test_log/compiler_logs/task64_evidence_finalization_green_2026-09-02.log`,
  `test_log/compiler_logs/task64_nonterminal_journal_green_2026-09-02.log`,
  and `test_log/compiler_logs/task64_evidence_finalization_full_green_2026-09-02.log`.
- Boundary: the historical one-line Task 6.3 commit metadata and unrelated
  submodule dirt remain unchanged; no history rewrite was requested. No Docker,
  E2 subscription, or live control was added by this slice.

## Validation snapshot (2026-08-18)

| Gate | Result | Evidence boundary |
| --- | --- | --- |
| Narrow refusal and isolation tests | PASS, 15 tests | Frozen test SHA-256 above. |
| Shared release `1.0.7` | PASS | `test_log/runtime_configs/drl_releases/1.0.7.json`; CPU runtime, RTX 5060 Ti CUDA tensor, SWIG import, and Python iteration of node/KPM/RC capability projections passed. |
| Isolated GPU overlay | PARTIAL PASS | `test_log/compiler_logs/drl_xapp_1.0.1_gpu_overlay_2026-08-18_14-10-38.log`; runtime and bridge passed, and only workspace services were removed. |
| Live E2 discovery | PASS | `test_log/compiler_logs/drl_xapp_live_e2_discovery_override_2026-08-18_14-46-18.log`; E42 setup succeeded and node `2:1:1:3584` advertised KPM/RC capabilities. The approved temporary gNB image override and all targeted containers were removed afterward. |
| KPM qualification | FAIL-CLOSED | `test_log/compiler_logs/drl_xapp_live_kpm_qualification_preflight_2026-08-18_15-33-15.log`; release `1.0.8` rejected the Style-4-only node with `CELL_KPM_STREAM_REQUIRED` before subscription. |
| RC control | UNPROVED | No E2SM-RC request was sent. Separate cell/UE streams, identity binding, and ACK-versus-failure propagation remain **[Needs Verification]**. |
