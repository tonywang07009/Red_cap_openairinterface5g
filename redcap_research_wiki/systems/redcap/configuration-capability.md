---
status: review-required
source_refs:
  - openair2/GNB_APP/gnb_config.c
  - openair2/GNB_APP/gnb_paramdef.h
  - openair2/RRC/NR_UE/rrc_ue_redcap.c
  - openair3/UICC/nr_redcap_config.c
  - redcap_doc/specs/function_reference/redcap_l1_l3_function_lookup.md
evidence_tier: source-trace
last_reviewed: 2026-07-31
related_pages:
  - redcap_research_wiki/systems/redcap/overview.md
  - redcap_research_wiki/systems/redcap/rrc-access.md
---

# RedCap Configuration and Capability

## Role

Own the gNB RedCap configuration, UE-local capability input, SIB1 RedCap fields,
and minimal UE capability container before access decisions.

## Inputs and Outputs

- Inputs: gNB config values, SCC, UE YAML capability, 1Rx/2Rx and HD-FDD state.
- Outputs: `nr_redcap_config_t`, SIB1 RedCap IEs, and UE capability flags used by
  later RRC/MAC owners.

## Owner and Source Trace

[Source Trace] `GNB_REDCAP_PARAMS_DESC` is consumed by `gnb_config.c`; the
runtime structure is passed into radio configuration. `rrc_ue_redcap.c` parses
SIB1 and builds UE capability; `nr_redcap_config.c` loads UE-local capability.

## Implementation Status

`implemented-called`. Exact field optionality and some TS 38.306/38.331 clause
mappings remain `[Needs Verification]`.

## Evidence and Markers

- Source owners: `get_redcap_config`, `get_redcap_initial_bwp_config`,
  `nr_rrc_parse_redcap_sib1`, and `nr_rrc_build_redcap_ue_capability`.
- A parsed field proves presence, not that a later access or scheduling branch
  consumed it.

## Failure Propagation

Missing or inconsistent gNB/UE capability state can appear downstream as SIB1
access rejection, a non-RedCap RA path, or a BWP mismatch.

## Repair Inventory

- Existing owners: `openair2/GNB_APP`, `openair2/RRC/NR_UE`, and
  `openair3/UICC`.
- Boundaries: absent config, null optional IE, 1Rx/2Rx combinations, unsupported
  SCS/PRB maximum, and conflicting HD-FDD state.
- Stop if the governing clause is unavailable; mark the mapping
  `[Needs Verification]` rather than changing policy.

## Research Reading Card

- Question: did the intended RedCap configuration become the capability state
  consumed by access?
- Source types: config descriptor, runtime structure, SIB1 encoder/parser, UE
  capability builder, and governing clause.
- Competing explanations: the config was not parsed; it was parsed but a later
  owner selected a different path.
- Falsifier: show the parsed value and the next consumer reading the same state.
- Strongest claim: current source ownership and field propagation only.

## Course Route

Prerequisite: [RedCap overview](overview.md). Next: [RRC and access](rrc-access.md).

## Claim Boundary

No configuration-field presence is treated as access permission, standards
conformance, or runtime success.

## Open Questions

- Optionality and access semantics of combined 1Rx/2Rx fields remain
  `[Needs Verification]` against the selected 3GPP release.
