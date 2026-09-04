---
status: review-required
source_refs:
  - openair2/GNB_APP/gnb_config.c
  - openair2/LAYER2/NR_MAC_gNB/nr_radio_config.c
  - openair2/LAYER2/NR_MAC_gNB/nr_mac_redcap_bwp.c
  - openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_RA.c
  - redcap_doc/specs/function_reference/redcap_l1_l3_function_lookup.md
evidence_tier: mixed
last_reviewed: 2026-07-31
related_pages:
  - redcap_research_wiki/systems/redcap/rrc-access.md
  - redcap_research_wiki/systems/redcap/runtime-evidence.md
---

# RedCap BWP, RA, and Scheduling

## Role

Own RedCap initial BWP construction, CORESET#0 compatibility, RACH feature
preambles, Msg2 BWP view, and scheduler consumption of RedCap constraints.

## Inputs and Outputs

- Inputs: RedCap config/SCC, SCS, carrier/BWP geometry, CORESET mode, Msg1
  preamble, and RA state.
- Outputs: DL/UL initial BWP, search-space/CORESET binding, RedCap RA partition,
  Msg2 scheduling view, and bounded grants.

## Owner and Source Trace

[Source Trace] `get_redcap_initial_bwp_config` feeds `nr_radio_config.c` and
`nr_mac_redcap_bwp.c`; `configure_redcap_msg2_bwp` owns the Msg2 view in
`gNB_scheduler_RA.c`.

## Implementation Status

`implemented-called` for the local Case A/B and RA helpers. Clause mappings in
the function lookup remain `[Needs Verification]` where marked.

## Evidence and Markers

- Source helpers cover RIV, edge alignment, CORESET/search-space rebinding,
  RACH partition, and Msg2 BWP selection.
- Retained project evidence supports bounded Case A/B behavior, not all carrier
  geometries or every scheduler path.

## Failure Propagation

A wrong BWP/CORESET view can suppress Msg2/PDCCH, select the wrong search space,
or later surface as active-BWP/SR/grant mismatch.

## Repair Inventory

- Existing owners: GNB config, MAC radio config, RedCap BWP helpers, and RA
  scheduler.
- Boundaries: PRB limit, RIV min/max, edge/non-edge BWP, Case A/B, first/last
  feature preamble, Msg2 window N-1/N/N+1, and shared scheduler state.
- Use the nearest BWP/RA unit or RFsim gate; do not invent a parallel module.

## Research Reading Card

- Question: did the same RedCap BWP/CORESET/RACH state reach the Msg2 and grant
  owners?
- Source types: config, BWP helper, RA scheduler, spec trace, and retained Case
  A/B evidence.
- Competing explanations: invalid BWP/CORESET construction; correct construction
  but wrong active view at scheduling time.
- Falsifier: compare the configured BWP with the exact Msg2/scheduler consumer
  state for the failed frame/slot.
- Strongest claim: bounded local source and retained Case A/B coverage.

## Course Route

Prerequisite: [RRC and access](rrc-access.md). Next:
[Inactive, power, and SDT](inactive-power-sdt.md).

## Claim Boundary

Case A/B evidence does not establish universal bandwidth support, capacity, or
exact standards conformance.

## Open Questions

- Some TS 38.213/38.321/38.331 mappings remain `[Needs Verification]` in the
  local traceability records.
