---
status: review-required
source_refs:
  - openair2/RRC/NR_UE/rrc_ue_redcap.c
  - openair2/RRC/NR/rrc_gNB.c
  - openair2/LAYER2/NR_MAC_UE/nr_ra_procedures.c
  - agent_doc/Project_management/projects/redcap_mmtc_priority_execution_v1/validation/test_matrix.md
  - redcap_doc/specs/function_reference/redcap_l1_l3_function_lookup.md
evidence_tier: mixed
last_reviewed: 2026-07-31
related_pages:
  - redcap_research_wiki/systems/redcap/configuration-capability.md
  - redcap_research_wiki/systems/redcap/bwp-ra-scheduling.md
---

# RedCap RRC and Access

## Role

Own SIB1 RedCap access evaluation, UE capability exchange, gNB capability state,
and selection of the RedCap random-access inputs.

## Inputs and Outputs

- Inputs: parsed SIB1 RedCap fields, UE antenna/HD-FDD capability, RA state, and
  feature-preamble configuration.
- Outputs: access allow/bar decision, UE capability flags, and RedCap RA
  preamble/LCID choices for MAC.

## Owner and Source Trace

[Source Trace] `nr_rrc_redcap_sib1_access_allowed` owns the UE SIB1 access gate;
`handle_ueCapabilityInformation` stores gNB-side capability; UE RA helpers own
RedCap preamble partition and Msg3 CCCH LCID selection.

## Implementation Status

`implemented-called` for the listed local paths. Exact standards mappings and
complete negative-path runtime coverage remain `[Needs Verification]`.

## Evidence and Markers

- Source endpoints are indexed in the L1-L3 function lookup.
- Runtime success must include the owning RRC/RA markers; attach alone does not
  prove that every RedCap-specific branch executed.

## Failure Propagation

An access-bar decision stops before RA. Incorrect capability state can select a
non-RedCap preamble/LCID or propagate into BWP/Msg2 handling.

## Repair Inventory

- Existing owners: UE RRC, gNB RRC, and UE MAC RA procedure.
- Boundaries: missing SIB1 extension, 1Rx/2Rx mismatch, barred value, no feature
  preamble partition, first/last preamble, and Msg3 LCID choice.
- Nearest verification: existing mMTC M2/M3 validation IDs.

## Research Reading Card

- Question: where did a RedCap UE stop between SIB1 evaluation and completed
  access?
- Source types: SIB1 clause/decoder, UE capability trace, RA state, and retained
  RRC/RA markers.
- Competing explanations: RRC access was barred; access passed but BWP/RA
  scheduling failed.
- Falsifier: observe access-allowed state followed by the expected RedCap Msg1
  preamble and next Msg2 consumer.
- Strongest claim: ownership of the local access path, not fresh runtime proof.

## Course Route

Prerequisite: [Configuration and capability](configuration-capability.md).
Next: [BWP, RA, and scheduling](bwp-ra-scheduling.md).

## Claim Boundary

RRC access success is not PDU-session, throughput, capacity, or standards-
conformance evidence.

## Open Questions

- Release-specific interpretation of feature-preamble and CCCH LCID behavior
  remains `[Needs Verification]` where the local traceability matrix says so.
