---
status: review-required
source_refs:
  - openair3/AIOTF/aiotf_inventory.c
  - openair3/AIOTF/aiotf_service.c
  - redcap_doc/manuals/aiot_tag_aiotf_architecture.en.md
  - redcap_doc/specs/function_reference/aiot_tag_aiotf_function_trace.md
evidence_tier: mixed
last_reviewed: 2026-07-31
related_pages:
  - agent_doc/Project_management/redcap_research_wiki/systems/aiot/tag-reader.md
  - agent_doc/Project_management/redcap_research_wiki/systems/aiot/standard-path.md
---

# AIOTF

## Role

Own Tag-to-reader binding, scheduling, correlation, failover, first-valid
arbitration, evidence retention, service health, and bounded NRF/Naiotf
Inventory surfaces.

## Inputs and Outputs

- Inputs: Inventory request, Tag set, reader bindings, pending context,
  diagnostic UE report, deadline, and callback URI.
- Outputs: transaction/correlation state, accepted/duplicate/conflict/timeout
  evidence, NRF lifecycle, and bounded Inventory notification.

## Owner and Source Trace

[Source Trace] `aiotf_inventory.c` owns binding and arbitration;
`aiotf_service.c` owns process/health, diagnostic listener, NRF client, Naiotf
request, and callback handling.

## Implementation Status

`implemented-called` for 60 Tags, two reader handles, `experimental_n6`, NRF
registration/discovery, and the bounded Naiotf Inventory surface. Complete SBI
readiness is blocked.

## Evidence and Markers

- Context acceptance requires matching Tag, frame, slot, reader eligibility,
  deadline, and CRC state.
- Bounded NRF and Naiotf evidence does not prove AMF/RAN or NEF communication.
- [Needs Verification] permanent-ID mapping and local authorization are
  experimental contracts, not conformance evidence.

## Failure Propagation

Zero/multiple pending contexts reject before arbitration. NRF unavailability
affects discovery/lifecycle. Callback failure affects notification but does not
retroactively prove the radio path failed.

## Repair Inventory

- Existing owners: `aiotf_inventory.c` and `aiotf_service.c`.
- Boundaries: zero/61 Tags, duplicate Tag, reader 0/3, zero/multiple context,
  deadline edge, callback non-204, NRF unavailable, restart, and deregistration.
- Preserve bounded state and do not introduce another service owner.

## Research Reading Card

- Question: which AIOTF boundary rejected or stopped a valid Inventory flow?
- Source types: API/schema, binding/arbitration source, service route, and
  retained request/callback marker.
- Competing explanations: input correlation/binding failed; service/NRF/Naiotf
  transport failed after valid arbitration.
- Falsifier: prove one accepted pending context, then follow the same
  transaction ID to the next service response/callback.
- Strongest claim: the exact bounded Inventory/NRF/Naiotf surface reached.

## Course Route

Prerequisite: [Tag and UE Reader](tag-reader.md). Next:
[Blocked standard path](standard-path.md).

## Claim Boundary

AIOTF health, NRF registration, or Naiotf success does not establish AMF/RAN
round trip, complete SBI, NEF availability, or 3GPP conformance.

## Open Questions

- Naiotf service-list mapping and full generated API parity remain
  `[Needs Verification]`.
