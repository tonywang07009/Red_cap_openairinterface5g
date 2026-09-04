---
status: review-required
source_refs:
  - openair2/E2AP/REDCAP_SDK/xapp/redcap_xapp_sdk.h
  - openair2/E2AP/REDCAP_SDK/xapp/redcap_xapp_sdk.c
  - openair2/E2AP/REDCAP_SDK/xapp/redcap_xapp_sdk.py
  - openair2/E2AP/flexric/src/xApp/swig/swig_wrapper.cpp
  - redcap_library/drl_xapp/bridge_daemon.py
  - redcap_library/bash_tool/scripts/test_redcap_drl_xapp.py
  - openspec/changes/build-redcap-drl-xapp-gated-runtime/design.md
  - ci-scripts/redcap_ul_prb_ctrl_xapp.c
  - agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/Doc/sdk_development_guide.en.md
evidence_tier: mixed
last_reviewed: 2026-08-31
related_pages:
  - agent_doc/Project_management/redcap_research_wiki/systems/xapp-dapp/overview.md
  - agent_doc/Project_management/redcap_research_wiki/systems/xapp-dapp/e2-transport.md
---

# xApp Observation and Control

## Role

Own RedCap xApp metric interpretation, candidate selection, RC function lookup,
and construction of bounded control requests.

## Inputs and Outputs

- Inputs: connected E2 node/RAN functions, UE identity/RNTI, metric or policy
  intent, and parameter bounds.
- Outputs: selected candidate, priority hint, or E2SM-RC request owned by the
  caller.

## Owner and Source Trace

[Source Trace] `redcap_xapp_sdk.*` owns reusable helpers;
`ci-scripts/redcap_ul_prb_ctrl_xapp.c` is the integrated caller for RC lookup
and UL-PRB request construction.

## Implementation Status

- UL-PRB RC lookup/builder: `implemented-called` and bounded runtime-evidenced.
- Priority-hint helpers: `dormant` or self-test-only until a production
  conversion caller is verified.
- DRX C builder: focused-test caller; the live path uses another route.

## Evidence and Markers

- Builder/source presence is not transport evidence.
- `CONTROL ACK rx` belongs to the next E2 step, not to xApp decision quality.
- [Needs Verification] exact O-RAN parameter mapping remains unconfirmed.

## Failure Propagation

Wrong RAN-function selection, UE identity, RNTI, cap, or validity can create an
invalid request or target the wrong downstream state.

## Repair Inventory

- Existing owner: the current xApp SDK and its real caller.
- Boundaries: null node, empty function list, UE/RNTI zero, cap min/max,
  validity zero/max, empty metrics, invalid candidates, and tie-break order.
- Extend the existing contract self-test; do not create another SDK.

## Research Reading Card

- Question: did the xApp select and encode the intended request for the live
  UE and RAN function?
- Source types: SDK contract, actual caller, request dump, and E2 correlation.
- Competing explanations: decision/builder output was wrong; it was correct but
  transport or downstream guard failed.
- Falsifier: inspect the request identity/parameters at the transport decoder.
- Strongest claim: per-helper caller and request-construction state.

## Course Route

Prerequisite: [xApp/dApp overview](overview.md). Next:
[E2 transport](e2-transport.md).

## Claim Boundary

An xApp helper result is not an ACK, gNB apply, UE completion, or performance
outcome.

## Task 3.5 KPM Provenance Safety Capture

### Context Packet

- question: Can a locally incremented SWIG KPM callback counter establish the
  source sequence required for a control target binding?
- operation: `capture-triage`.
- goal: G2 source-to-runtime safety boundary.
- system_scope: FlexRIC SWIG KPM projection and RedCap DRL xApp qualification.
- authoritative_sources: the SWIG producer, bridge qualification owner,
  OpenSpec Task 3.5 contract, and retained RED/GREEN test logs.
- evidence_required: source trace plus a read-only refusal-path test.
- claim_boundary: prove the local provenance label and refusal contract only;
  do not claim a live E2 indication sequence or qualified control path.
- autonomy_level: L2; editorial status remains `review-required`.
- completion_evidence: the native producer is fail-closed and the focused plus
  full unit tests pass.
- stop_conditions: no decoded E2 field or live trace proving sequence
  provenance; retain `[Needs Verification]` and stop before control.
- capture_route: `update-page`.
- next_action: trace a real E2 indication sequence only in a separately
  approved native/profile change.

### Finding

[Source Trace] `sm_cb_kpm()` increments `kpm_source_seq` locally. On
2026-08-31 its cell Format 1 and UE Format 3 projections were changed from
`source_seq_origin="e2_indication"` to
`source_seq_origin="bridge_callback_counter"`. This prevents the producer
from claiming a sequence it cannot prove.

[Source Trace] `NativeFlexric.qualify()` accepts target-binding sequence
provenance only when `source_seq_origin="e2_indication"`; a callback-counter
sample therefore returns `SOURCE_SEQUENCE_UNVERIFIED` before any E2SM-RC
control. The focused tracer first failed against the old native claim, then
passed; the full suite passed 42 tests. Evidence:
`test_log/compiler_logs/task35_native_callback_provenance_red_2026-08-31.log`,
`test_log/compiler_logs/task35_native_callback_provenance_green_2026-08-31.log`,
and
`test_log/compiler_logs/task35_native_callback_provenance_full_green_2026-08-31.log`.

### Live Qualification Update (2026-08-31)

[Source Trace] A periodic `ind_event_t` owns a non-zero `RICindicationSN`.
`generate_indication()` allocates it for E2AP, the xApp copies an available
received SN to KPM read data, and `sm_cb_kpm()` labels only that field as
`e2_indication`. An absent SN is `e2_indication_unavailable`, preserving the
existing `SOURCE_SEQUENCE_UNVERIFIED` refusal path.

[Runtime Evidence] Release `1.0.14` qualification at node `2:1:1:3584`
captured one cell/UE pair with `source_seq=1`, `source_seq_origin=e2_indication`,
0 ms cell/UE skew, and UE binding `gnb-ran:1` to RC UE ID `1` and RNTI
`12064`. The run returned `MEASUREMENT_POST_UNFROZEN`,
`failed_stage=qualification`, and `control_attempted=false`. This proves that
measured observations are not promoted to control before human threshold
freezing; it does not prove an E2SM-RC apply transaction.

Evidence: `test_log/compiler_logs/task35_e2_indication_sn_{red,green,full_green}_2026-08-31.log`,
`test_log/build_logs/task35_e2_indication_sn_release_1.0.14_2026-08-31.log`,
and `/tmp/task35-e2-sn-live/task35-e2-sn-live/artifacts/runs/20260831T112450Z-137662c5/manifest.json`.

## Open Questions

- Production conversion callers for priority-hint helpers remain
  `[Needs Verification]`.
