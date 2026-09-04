## Context

The RedCap/OAI/FlexRIC simulator owns the gNB, UE, CN, RIC, control contract,
and native C xApp reference code. This change supplies a reproducible Python
DRL workspace that can use that existing control path without giving model code
native RIC, Docker, or public-network authority.

The selected simulator topology is input, not a default. RIC/gNB service names,
network, E2 node, KPM styles, metric identities, and target binding must be
discovered from the supplied compose scenario and live E2 evidence.

Detailed TDD contracts, RED/GREEN traces, and superseded implementation records
are in [tdd.md](tdd.md). Task state is in [tasks.md](tasks.md).

## Goals and non-goals

### Goals

- Build immutable shared CPU/GPU runtime images and a separate native bridge.
- Create isolated named workspaces with editable model source.
- Expose a versioned workspace-private UDS bridge for observations and one
  bounded, reversible E2SM-RC transaction.
- Retain truthful evidence for every gate and control attempt.

### Non-goals

- Define a production DQN, PPO, DDPG, reward, reset, episode, or training-rate
  method.
- Change UE, CN, base compose topology, or the existing RedCap control contract.
- Expose a Docker socket, privileged capability, public control endpoint, raw C
  pointer, or ASN.1 object to model code.
- Treat Docker reachability, E2 acknowledgement, or static configuration as
  gNB-application proof.

## Current architecture decisions

### Immutable release and workspace split

The release owns immutable images:

- `redcap-drl-runtime:<release>-cpu`
- `redcap-drl-runtime:<release>-gpu`
- `redcap-flexric-bridge:<release>`

Each workspace records the selected tag and locally resolved image identity.
Dependencies change only through a newly built release and explicit upgrade;
workspace initialization must not rebuild or retag a shared release.

### Runtime, bridge, and compose isolation

The runtime container runs editable model code from `/workspace/src`, has no
network, and sees `/run/redcap-drl` read-only. The bridge container owns the
FlexRIC SWIG/native C ABI, E2SM-KPM decoding, E2SM-RC encoding, lease, journal,
and evidence collection. The generated overlay adds only those two services to
the resolved external network. Simulator configuration mounts are read-only.

The stable UDS protocol is JSON with protocol, request, session, and profile
identity. V1 operations are `health`, `open`, `observe`, `act`, and `close`.

### Profile and observation gates

`profile=none` permits only smoke/offline checks. `ul-prb-cap-v1` requires all
of the following before control:

1. Exactly one E2 node that advertises the required KPM and RC capabilities.
2. Separate cell and UE KPM observations.
3. Freshness, alignment, and measurement-post policy approved for the profile.
4. A verified `KPM UE key ↔ RC UE ID ↔ RNTI` binding from
   `source_seq_origin=e2_indication`, never `ue_id=rnti` or callback order.
5. An exclusive node lease.

Before a human freezes this profile's measurement-post policy, an
observation-only cadence probe records each cell/UE subscription acceptance,
first-callback latency, callback count, `RICindicationSN`, and event time.
The bridge keeps a successful pair of KPM subscriptions for its own session.
Requalification waits for a fresh pair from that retained stream; a control
phase proves later KPM only from a pair received after its native send time.
It must not unsubscribe and resubscribe after the control send.

The native KPM extension remains owner-local: a subscription-owned cell baseline
uses the existing action-definition free lifecycle. No request-ID registry,
global subscription table, new unsubscribe operation, or process-wide baseline
is permitted.

### One-candidate transaction and apply proof

For `ul-prb-cap-v1`, a control-once session has exactly this sequence:

```text
proved baseline → proved candidate → proved baseline restore
```

Every baseline, candidate, restore, or recovery phase needs native ACK, a
matching gNB apply marker, and a later qualified KPM observation within that
phase's one-second window. Uncertain rollback records
`ROLLBACK_UNCONFIRMED` and locks the target until explicit recovery.

The native KPM reporting period used for this proof must be strictly shorter
than the one-second proof window. Its actual cadence remains live evidence;
the CPU observation-only probe is required before any Task 6.3 attempt.

### Controller and model-profile contract

The fixed controller selects `16`. The greedy controller consumes the latest
qualified cell `RRU.PrbTotUl`: `<55% → 16`, `55..80% → 32`, `>80% → 64`.

The model controller is one inference per enabled run:

```text
30 valid paired E2 samples
  → RRU.PrbTotUl {latest, mean, min, max}
  → immutable /run/redcap-drl observation JSON
  → module:callable once
  → one stdout JSON line {"max_ul_prb": N}
  → N must be strict integer 1..51
  → existing one-candidate transaction
```

`0` is reserved for baseline/restore. The generic native contract remains
`0..275`. A model without `--enable-control`, malformed output, a boolean,
float, string, missing value, `0`, or `52+` refuses before UDS `open`.
The CLI exposes no generic `--episodes` option. A future multi-episode profile
requires a separate OpenSpec change defining state, action, reward, reset, and
rate semantics.

The runtime receives only the read-only `<workspace>/runtime-input` directory
at `/run/redcap-drl`; the bridge alone receives `<workspace>/run`, including
the UDS. The runtime image exposes the model entrypoint and does not ship a
generic UDS control client. The CLI remains the only orchestration caller of
the native bridge protocol.

### Evidence and operator surface

`run_model()` rejects missing, unknown, malformed, or otherwise syntactically
invalid user input before a Control Run exists; these errors create no package.
An enabled Control Run with a valid request creates exactly one package before
its first execution preflight gate. Its unique `run_id` names
`<workspace>/artifacts/runs/<run_id>/`; every gate, model input/decision,
collector result, and UDS result appends to that package. Operators trace a
run through that `run_id` and its `manifest.json`.
`control_journal.json.control_attempted` is `true` only after an UDS `open`
request has been attempted; it is `false` for all pre-UDS failures and is not
proof of acknowledgement or application.
On either terminal outcome, the manifest receives `finalized_at`; later
appends for that `run_id` are refused. This protects closed evidence from
repeat invocation and is separate from the Bridge's concurrent-control lease.
If the process stops before finalization, the package remains interrupted
evidence and is never resumed. A later attempt uses a new `run_id` and first
relies on the Bridge's existing recovery gate.
Immediately after package creation and before the first preflight gate, the
CLI emits one `CONTROL_RUN_STARTED` JSON record with `run_id` and the manifest
path, so an interrupted run remains directly discoverable.
After successful manifest finalization, it emits one `CONTROL_RUN_FINISHED`
JSON record with the same `run_id`, terminal gate status, `finalized_at`, and
manifest path.
The same-file `emit_json(record)` helper is the output seam used by the
Control Run; no callback, generator, or class is introduced for this output.
If that finalization write fails after control, the run reports
`EVIDENCE_FINALIZATION_FAILED`, emits no finished record, and never retries
control.
Before any UDS `open`, it verifies that the package manifest, event stream,
and journal are writable. Failure is `EVIDENCE_WRITE_REQUIRED` with no UDS
request.
The manifest and model JSON artifacts use same-directory temporary files plus
atomic replace from the Python standard library. The ordered event stream
remains append-only.
An operator-invoked `qualify-kpm` keeps its independent evidence package. A
Control Run invokes the same qualification logic only as an append operation
against its own `run_id`; it must not create a child package.
Only a strictly accepted model decision is retained as `model_decision.json`.
Malformed model stdout is represented by the ordered fail-closed event, not
preserved as trusted decision evidence.
Generated overlay and resolved compose evidence remain separate from mutable
simulator configuration. `down` and `remove` retain evidence.

CLI help is Traditional Chinese and read-only. It distinguishes runtime smoke,
network reachability, E2 capability, KPM qualification, ACK, gNB apply marker,
and later observation; earlier gates are not proof of later gates.

## Current unresolved facts

- Live KPM metric/interoperability and cell action-definition mappings remain
  **[Needs Verification]**.
- Measurement-post freshness, skew, and sample thresholds are profile-owned,
  human-approved calibration values; an unfrozen policy refuses control.
- Host marker receipt time is not an on-gNB execution timestamp. Host/container
  monotonic-clock comparability remains **[Needs Verification]**.
- A local test passing does not prove live E2SM-RC application. One approved
  fixed-candidate Task 6.3 transaction passed on 2026-09-02; its immutable
  package exposed a stale journal snapshot, and the finalization repair is
  covered by `tdd.md` for subsequent runs.

## Owner inventory

| Concern | Owner seam | Constraint |
| --- | --- | --- |
| PRB contract and marker | `redcap_interface/control/redcap_control_contract.yaml` | Read-only; generic limit `0..275`. |
| RC request | `openair2/E2AP/REDCAP_SDK/xapp/redcap_xapp_sdk.c` | Reuse `redcap_xapp_make_ul_prb_ctrl_req`; never map `ue_id=rnti`. |
| Native session/control | `openair2/E2AP/flexric/src/xApp/e42_xapp_api.*` | Reuse native owner through the adapter. |
| Cell KPM | `ran_func_kpm.c`, `sm_ag_if_rd.h`, KPM v03.00 adapter | Subscription-owned baseline only; preserve UE Style-4. |
| KPM projection | `openair2/E2AP/flexric/src/xApp/swig/` | Python primitives only. |
| Workspace CLI | `redcap_library/bash_tool/scripts/redcap_drl_xapp.py` | Owns orchestration and evidence projection, not native control encoding. |

## TDD and validation index

- Full contract/evidence history: [tdd.md](tdd.md).
- Current task progress: [tasks.md](tasks.md).
- Unit evidence proves local seams only; Docker/live E2/control operations use
  the task-manifest protocol and require separately approved execution.
- Strict OpenSpec validation is required after documentation restructuring and
  at change completion.
