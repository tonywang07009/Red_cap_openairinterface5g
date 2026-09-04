---
status: review-required
source_refs:
  - openair2/E3AP/sdk/redcap_dapp_sdk.h
  - openair2/E3AP/sdk/redcap_dapp_sdk.c
  - openair2/E3AP/sdk/redcap_dapp_sdk.py
  - openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_uci.c
  - openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_ulsch.c
  - agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/Doc/sdk_development_guide.en.md
evidence_tier: mixed
last_reviewed: 2026-07-31
related_pages:
  - agent_doc/Project_management/redcap_research_wiki/systems/xapp-dapp/e2-transport.md
  - agent_doc/Project_management/redcap_research_wiki/systems/xapp-dapp/gnb-apply-rollback.md
---

# dApp Guard and Local Policy

## Role

Own local safety validation and parameter-specific accept/reject decisions
before a request may reach a gNB apply owner.

## Inputs and Outputs

- Inputs: RNTI, BWP/IQ state, requested cap/ratios, access counters, DRX policy
  version/current state, cooldown, and rollback config.
- Outputs: bounded result, reason/marker, selected intent, and allow-apply gate.

## Owner and Source Trace

[Source Trace] `openair2/E3AP/sdk/redcap_dapp_sdk.*` owns guard/policy helpers.
PUCCH/UL hooks call the allocation guard; `ran_func_rc.c` calls the live E2 DRX
guard before MAC/RRC apply.

## Implementation Status

- PRB allocation guard and live E2 DRX guard: `implemented-called` with bounded
  marker evidence.
- Access-pressure policy, RA selector C path, and prediction guard: mixed
  self-test/experimental or `dormant` states.

## Evidence and Markers

- `RedCap dApp PRB decision` supports the local guard result; allocation
  mutation remains `[Needs Verification]` where the hook only observes.
- `[RedCap DRX][dApp ACCEPT/REJECT]` supports the live DRX guard decision.
- A self-test proves contract logic, not production invocation.

## Failure Propagation

A guard rejection must stop apply. A dormant policy can produce correct output
without affecting the scheduler. Mislabeling either case creates false outcome
claims.

## Repair Inventory

- Existing owner: the current dApp SDK and its actual callers.
- Boundaries: null, empty, zero RNTI, min/max and boundary-1/+1, ratio sum 1000,
  missing IQ, unsupported BWP, stale version, cooldown edge, and rollback state.
- Update the existing SDK contract self-test for any logic change.

## Research Reading Card

- Question: did the production caller invoke the correct guard, and did it
  permit the exact apply?
- Source types: SDK contract, caller trace, accept/reject marker, and apply gate.
- Competing explanations: guard rejected correctly; guard passed but no apply
  owner consumed the result.
- Falsifier: correlate the same request with guard result and the immediately
  gated apply call.
- Strongest claim: the parameter-specific guard result and caller state.

## Course Route

Prerequisite: [E2 transport](e2-transport.md). Next:
[gNB apply and rollback](gnb-apply-rollback.md).

## Claim Boundary

Guard success is not scheduler mutation, UE completion, or outcome improvement.

## Open Questions

- Production application of several policy/selector helpers remains
  `[Needs Verification]`.
