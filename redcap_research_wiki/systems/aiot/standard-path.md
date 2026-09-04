---
status: review-required
source_refs:
  - redcap_doc/manuals/aiot_tag_aiotf_architecture.en.md
  - redcap_doc/specs/A_IoT/README.md
  - redcap_doc/specs/function_reference/aiot_tag_aiotf_function_trace.md
evidence_tier: source-trace
last_reviewed: 2026-07-31
related_pages:
  - redcap_research_wiki/systems/aiot/overview.md
  - redcap_research_wiki/systems/aiot/aiotf.md
---

# A-IoT Standard-Path Boundary

## Role

Preserve the exact missing AMF/RAN/NEF owners and prevent experimental N6,
container health, NRF registration, or Naiotf success from substituting for the
standard path.

## Inputs and Outputs

- Expected inputs: AIOTF-to-AMF transfer, matched Topology-2 NGAP/RRC UE Reader
  contract, and third-party AF/NEF request.
- Expected outputs: AMF/RAN round trip and `Nnef_AIoT_*` authorization/callback.

## Owner and Source Trace

[Source Trace] The selected AMF returns HTTP 404 for the expected transfer
route; the RAN checkout has no matched Topology-2 NGAP/RRC UE Reader endpoint;
the selected NEF has no `Nnef_AIoT_*` owner.

## Implementation Status

`missing` or `blocked` at the listed endpoints. Published topology-1 material
must not be imported as a Topology-2 UE Reader implementation.

## Evidence and Markers

- Expected consumer route/model/handler is absent for `Namf_AIoT`.
- Expected topology-2 encoder/decoder/RRC owner is absent.
- Expected NEF route/model/auth/callback owner is absent.
- All three remain `[Needs Verification]` against a future matched Stage-3
  baseline.

## Failure Propagation

The flow stops before a standard end-to-end transaction. Sharing a Docker
network or receiving an NRF/Naiotf response cannot advance this evidence step.

## Repair Inventory

- Needed owners: AMF service, matched Topology-2 NGAP/RRC contract, and NEF API.
- Prerequisite: one consistent release/baseline across service model, ASN.1,
  RRC, and callbacks.
- Stop before source change or runtime: both are excluded L4 work.

## Research Reading Card

- Question: is there an implementable, release-matched owner for each standard
  endpoint?
- Source types: published/local clause, API/ASN.1 model, route/handler, caller,
  and retained endpoint response.
- Competing explanations: endpoint exists under another verified release/name;
  endpoint is genuinely absent in the selected checkout.
- Falsifier: locate the exact route/model/handler and one caller for the same
  release and Topology-2 contract.
- Strongest claim: negative source trace for the selected baselines.

## Course Route

Prerequisite: [AIOTF](aiotf.md). Stop here until the missing owners are
verified; then continue conceptually to [xApp/dApp](../xapp-dapp/overview.md).

## Claim Boundary

This page records blockers. It does not propose or authorize the missing
implementation, documentation synchronization, or runtime validation.

## Open Questions

- Matched Topology-2 Stage-3 NGAP/RRC and `Nnef_AIoT_*` ownership remains
  `[Needs Verification]`.
