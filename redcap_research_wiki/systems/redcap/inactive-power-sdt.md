---
status: review-required
source_refs:
  - openair2/LAYER2/NR_MAC_gNB/nr_mac_sdt_fsm.c
  - openair2/LAYER2/NR_MAC_UE/nr_ue_scheduler.c
  - openair2/RRC/NR_UE/rrc_ue_lowpower.c
  - openair3/NAS/NR_UE/nr_nas_msg.c
  - agent_doc/Project_management/projects/redcap_mmtc_priority_execution_v1/project_plan.md
evidence_tier: mixed
last_reviewed: 2026-07-31
related_pages:
  - redcap_research_wiki/systems/redcap/bwp-ra-scheduling.md
  - redcap_research_wiki/systems/redcap/runtime-evidence.md
---

# RedCap Inactive, Power, and SDT

## Role

Route RRC_INACTIVE/SDT state, configured-grant scheduling, DRX/eDRX allowance,
and NAS PSM timers without merging their evidence tiers.

## Inputs and Outputs

- Inputs: inactive enablement, SDT payload/path state, active BWP/configured
  grant, DRX profile, SIB1 eDRX allowances, and NAS PSM timers.
- Outputs: FSM transitions, CG-SDT scheduling or fallback, DRX apply state,
  eDRX readiness markers, and PSM readiness markers.

## Owner and Source Trace

[Source Trace] gNB SDT state lives in `nr_mac_sdt_fsm.c`; UE configured-grant
SDT lives in `nr_ue_scheduler.c`; eDRX SIB1 state lives in
`rrc_ue_lowpower.c`; NAS PSM timers live in `nr_nas_msg.c`.

## Implementation Status

`partial` by feature. The project records DRX at unit/flow level and eDRX/PSM
at runtime-log level. These tiers are not interchangeable.

## Evidence and Markers

- SDT: FSM transitions and RRC_INACTIVE Gate markers.
- DRX: dApp accept/reject, apply state, and RRC completion when required.
- eDRX/PSM: feature-specific allowance/timer readiness markers.
- [Needs Verification] None of these local markers measures physical power.

## Failure Propagation

Wrong active BWP or configured-grant state can look like SDT failure. Missing
SIB1 allowance or NAS timer state can look like low-power policy failure.

## Repair Inventory

- Existing owners: MAC SDT FSM/scheduler, UE RRC low-power parser, NAS timer
  parser, and selected DRX apply path.
- Boundaries: zero/max payload, timer min/max, window N-1/N/N+1, simultaneous
  expiry/occasion, missing CG config, inactive disabled, and rollback state.
- Keep SDT, DRX, eDRX, and PSM tests separate.

## Research Reading Card

- Question: which low-power or inactive owner last accepted state, and which
  next owner failed to consume it?
- Source types: RRC/NAS clause, FSM/scheduler trace, retained feature marker.
- Competing explanations: feature state was absent; state existed but active
  BWP/timer/scheduling context rejected it.
- Falsifier: correlate the feature's producer state with its next consumer at
  the exact frame/slot or timer boundary.
- Strongest claim: feature-specific local tier only; no energy conclusion.

## Course Route

Prerequisite: [BWP, RA, and scheduling](bwp-ra-scheduling.md). Next:
[Runtime evidence](runtime-evidence.md).

## Claim Boundary

Static, flow, and log readiness do not establish complete RRC_INACTIVE/SDT
interoperability or physical-power savings.

## Open Questions

- Full matched-clause and fresh end-to-end evidence remains `[Needs Verification]`
  for feature combinations not accepted by the owning project plan.
