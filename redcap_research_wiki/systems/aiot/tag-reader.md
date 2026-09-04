---
status: review-required
source_refs:
  - radio/rfsimulator/stored_node.c
  - radio/rfsimulator/simulator.cpp
  - openair1/PHY/NR_UE_TRANSPORT/nr_ue_rf_helpers.c
  - executables/nr-ue.c
  - redcap_doc/manuals/aiot_tag_aiotf_architecture.en.md
evidence_tier: mixed
last_reviewed: 2026-07-31
related_pages:
  - agent_doc/Project_management/redcap_research_wiki/systems/aiot/overview.md
  - agent_doc/Project_management/redcap_research_wiki/systems/aiot/aiotf.md
---

# A-IoT Tag and UE Reader

## Role

Own the experimental Topology-2 CW/Tag behavior, R2D/D2R relay and codec, UE
wake gate, and 40-byte diagnostic report producer.

## Inputs and Outputs

- Inputs: `aiot_t2` profile, Tag identity/payload, reader handle, frame/slot,
  R2D command, and external CW.
- Outputs: CRC-qualified D2R payload and a 40-byte UE report sent through the
  UE's PDU session on the diagnostic N6 path.

## Owner and Source Trace

[Source Trace] `stored_node.c` owns Tag/CW behavior; `simulator.cpp` owns the
control relay; `nr_ue_rf_helpers.c` owns UE codec helpers;
`aiot_t2_role_process_slot` in `nr-ue.c` owns the UE Reader slot flow.

## Implementation Status

`implemented-called` for the disabled-by-default experimental profile. This is
not the complete standard path.

## Evidence and Markers

- Tag/reader frame, slot, handle, payload length, and CRC state are bounded by
  the diagnostic record.
- [Needs Verification] Manchester/SFS behavior is experimental and is not
  presented as current TS 38.291 conformance.

## Failure Propagation

Wrong Tag binding, frame/slot, reader eligibility, payload length, or CRC state
causes AIOTF context rejection or timeout. Missing external CW prevents the
selected Topology-2 energy path before AIOTF.

## Repair Inventory

- Existing owners: RFsim stored node/relay, UE PHY helper, and UE executable.
- Boundaries: Tag 1/60, reader 1/2, payload 1/16, frame 0/1023, slot 0/159,
  invalid CRC, missing CW, duplicate reader report, and ambiguous context.
- Do not create a second Tag/Reader implementation outside these owners.

## Research Reading Card

- Question: did the selected Tag/Reader exchange produce one report acceptable
  to the AIOTF input contract?
- Source types: Topology-2 study/spec, RFsim relay, UE codec/producer, and exact
  diagnostic marker.
- Competing explanations: radio/codec report was invalid; report was valid but
  AIOTF correlation/binding rejected it.
- Falsifier: validate CRC and report fields, then match exactly one pending
  AIOTF context for the same Tag/frame/slot.
- Strongest claim: deterministic experimental RFsim/diagnostic behavior.

## Course Route

Prerequisite: [A-IoT overview](overview.md). Next: [AIOTF](aiotf.md).

## Claim Boundary

No physical-RF, continuous-CW-from-UE, AMF/RAN, or standards-conformance claim
is made.

## Open Questions

- A standards-aligned Topology-2 UE Reader Stage-3 endpoint remains
  `[Needs Verification]`.
