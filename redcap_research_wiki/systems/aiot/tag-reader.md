---
status: review-required
source_refs:
  - radio/rfsimulator/stored_node.c
  - radio/rfsimulator/simulator.cpp
  - openair1/PHY/NR_UE_TRANSPORT/nr_ue_rf_helpers.c
  - executables/nr-ue.c
  - openair3/AIOTF/aiotf_inventory.h
  - openspec/changes/archive/2026-09-18-add-aiot-cfa-rfsim-ber-measurement/code.md
  - openspec/specs/aiot-cfa-rfsim-ber-measurement/spec.md
  - openspec/changes/archive/2026-09-18-add-aiot-cfa-rfsim-ber-measurement/validation.txt
  - redcap_doc/manuals/aiot_tag_aiotf_architecture.en.md
evidence_tier: mixed
last_reviewed: 2026-09-19
related_pages:
  - redcap_research_wiki/systems/aiot/overview.md
  - redcap_research_wiki/systems/aiot/aiotf.md
---

# A-IoT Tag and UE Reader

## Role

Own the experimental Topology-2 CW/Tag behavior, R2D/D2R relay and codec, UE
Reader slot flow, 40-byte diagnostic report producer, and the fixed measurement
observation export used by the CFA RFsim experiment.

## Inputs and Outputs

- Inputs: `aiot_t2` profile, Tag identity/payload, reader handle, frame/slot,
  R2D command, and external CW.
- Outputs: CRC-qualified or CRC-failed D2R payload, a 40-byte delivery report
  sent through the UE's PDU session on the diagnostic N6 path, and a fixed
  80-byte observation report for TX/RX comparison.

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

## CFA RFsim BER measurement (review-required)

[Source Trace] The accepted measurement slice keeps the existing 16-byte
inventory payload and adds a separate 80-byte, network-order observation
report. `stored_node.c` emits TX truth, `simulator.cpp` routes by Reader handle
and applies independent duration-specific two-leg 3 dB Rician/noise samples to
D2R, and `nr-ue.c` compares the decoded payload against the truth before
exporting status, bit counters, sample-tick timestamps, and channel provenance.

[Runtime Evidence] The isolated RFsim/UE build, nearest codec test, RFsim
self-test, seventeen Python unit tests, corrected 40-job three-Reader RFsim
matrix, fixed 4,000-row RFsim aggregate, independent numerical reference, and
run13 one-Reader RFsim UDP ingest passed. Run13 captured CW relay, TX truth,
K=3 dB/noise=0.1 D2R relay, CRC failure with 2/128 errors, and JSON
`ber=0.015625`, `packet_loss_rate=0.0`, and provenance `10491263`. The v3
aggregate contains `complete=6745`, `crc_failure=5199`, `undetected=45`, and
`unaligned=11`; the eight-duration reference comparison stays within
exploratory absolute BER tolerance 0.02 (maximum absolute difference
0.0185627926). A separate no-D2R run emitted one
`undetected` report and JSON `packet_loss_rate=1.0` in the TX-attempt window.
This evidence is simulator/model evidence and does not establish real-Reader
equivalence.

[Needs Verification] Real-Reader equivalence remains open. The legacy AIOTF
60-Tag/two-Reader profile remains a separate owner; the opt-in CFA visibility
adapter supports 100 Tags and three Readers without changing that legacy
profile.

## Failure Propagation

Wrong Tag binding, frame/slot, reader eligibility, payload length, or CRC state
causes AIOTF context rejection or timeout. Missing external CW prevents the
selected Topology-2 energy path before AIOTF.

## Repair Inventory

- Existing owners: RFsim stored node/relay, UE PHY helper, and UE executable.
- Boundaries: Tag 1/100 in the CFA profile (legacy inventory remains 1/60),
  Reader 1/3 in the CFA profile, payload 1/16, frame 0/1023, slot 0/159,
  invalid CRC, missing CW, undetected timeout, duplicate reader report, and
  ambiguous context.
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
