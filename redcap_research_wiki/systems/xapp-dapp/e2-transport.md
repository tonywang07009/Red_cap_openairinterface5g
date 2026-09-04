---
status: review-required
source_refs:
  - openair2/E2AP/flexric
  - openair2/E2AP/RAN_FUNCTION/O-RAN/ran_func_rc_redcap.c
  - openair2/E2AP/RAN_FUNCTION/O-RAN/ran_func_rc.c
  - ci-scripts/redcap_ul_prb_ctrl_xapp.c
  - agent_doc/Project_management/projects/redcap_oran_sdk_workflow_v3/report/G4_rfsim_case_b_ul_prb_2026-07-04.md
evidence_tier: mixed
last_reviewed: 2026-07-31
related_pages:
  - redcap_research_wiki/systems/xapp-dapp/xapp-observation-control.md
  - redcap_research_wiki/systems/xapp-dapp/dapp-guard.md
---

# E2 Transport and Control Decode

## Role

Own delivery and decoding of selected xApp control requests into the gNB RC
handler and expose transport/ACK separately from apply.

## Inputs and Outputs

- Inputs: E2 node/RAN function, request identity, E2SM-RC payload, UE identity,
  and RedCap parameter.
- Outputs: decoded local control structure, ACK/failure, and handoff to guard or
  apply owner.

## Owner and Source Trace

[Source Trace] FlexRIC assets own the E2 integration route;
`ran_func_rc_redcap.c` owns RedCap parameter extraction/parse;
`ran_func_rc.c` owns the RC write dispatch.

## Implementation Status

`implemented-called` for the selected UL-PRB and DRX control surfaces. Other
service-model/parameter mappings are evaluated independently.

## Evidence and Markers

- Transport evidence: correlated request reaches the RC handler.
- ACK evidence: `CONTROL ACK rx` or matching protocol result.
- An ACK without `RedCap UL PRB control ... effective ...` or the parameter's
  owning apply marker stops at acknowledgement.

## Failure Propagation

Decode/schema/identity failure prevents guard/apply. ACK-only success can hide
a missing or rejected downstream apply if evidence steps are merged.

## Repair Inventory

- Existing owners: FlexRIC/E2 integration and RC parser/handler.
- Boundaries: unknown RAN function, missing parameter, invalid integer, UE/RNTI
  zero, stale request identity, reject/failure response, and duplicate request.
- Use existing parser and focused contract tests.

## Research Reading Card

- Question: did the exact xApp request reach and decode at the intended RC
  handler?
- Source types: request builder, E2 trace, decoder, handler, and correlated ACK.
- Competing explanations: transport/decode failed; transport passed but guard
  or apply rejected downstream.
- Falsifier: correlate request identity and decoded values at handler entry.
- Strongest claim: transport/ACK, unless later evidence is separately present.

## Course Route

Prerequisite: [xApp observation/control](xapp-observation-control.md). Next:
[dApp guard](dapp-guard.md).

## Claim Boundary

Transport or ACK does not prove dApp acceptance, gNB state mutation, UE-visible
completion, or outcome improvement.

## Open Questions

- Exact O-RAN clause and parameter mappings remain `[Needs Verification]`.
