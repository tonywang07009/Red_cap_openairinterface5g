---
status: review-required
source_refs:
  - agent_doc/Project_management/projects/redcap_oran_sdk_workflow_v3/report/G4_rfsim_case_b_ul_prb_2026-07-04.md
  - agent_doc/Project_management/projects/redcap_oran_sdk_workflow_v3/project_plan.md
  - agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/Doc/sdk_development_guide.en.md
evidence_tier: mixed
last_reviewed: 2026-07-31
related_pages:
  - redcap_research_wiki/systems/xapp-dapp/overview.md
  - redcap_research_wiki/systems/xapp-dapp/gnb-apply-rollback.md
---

# xApp/dApp Outcome Evidence

## Role

Classify the strongest completed control evidence and prevent readiness,
transport, ACK, or apply from being reported as an unmeasured outcome.

## Inputs and Outputs

- Inputs: request identity, static/self-test result, transport trace, ACK,
  guard decision, apply snapshot/marker, UE completion, owning metric, and
  retained report.
- Outputs: strongest completed evidence step, bounded conclusion, missing next
  step, and next owner.

## Owner and Source Trace

[Source Trace] The G4 report owns the bounded UL-PRB control conclusion. Each
separate experiment/report owns its outcome metrics; the wiki does not merge
them into a product-level SDK result.

## Implementation Status

`implemented-called` as an evidence-classification workflow, not as runtime
code.

## Evidence and Markers

[Runtime Evidence] G4 retains `[Contract][PASS]`, `CONTROL ACK rx`, and the gNB
UL-PRB apply marker for one selected RNTI/cap. It does not establish latency,
access-rate, or resource-allocation improvement.

## Failure Propagation

If any evidence step is missing, the conclusion stops at the prior step. A
missing retention path also limits reviewability even when an ephemeral marker
was observed.

## Repair Inventory

- Existing owners: parameter-specific Gate report, verifier, metric producer,
  and retained evidence route.
- Boundaries: no request, ACK-only, reject, apply-only, missing UE completion,
  missing metric, baseline mismatch, empty sample, first/last sample, and stale
  report.
- Runtime reruns remain excluded L4 work.

## Research Reading Card

- Question: what is the strongest outcome claim supported for this exact
  request and experiment?
- Source types: contract, transport/ACK, guard, apply, UE completion, metric,
  and retained report.
- Competing explanations: control did not progress; control progressed but the
  chosen metric or experiment cannot measure the claimed effect.
- Falsifier: reproduce the claimed metric difference from the owning retained
  baseline/treatment evidence under equivalent conditions.
- Strongest claim: the final completed and retained ladder step only.

## Course Route

Prerequisite: [gNB apply and rollback](gnb-apply-rollback.md). Return to
[xApp/dApp overview](overview.md) with the bounded result.

## Claim Boundary

The accepted G4 slice is not a complete SDK, mitigation, latency improvement,
or general scheduler-effect claim.

## Open Questions

- Any new outcome comparison requires an owning metric contract and separate
  L4 approval; otherwise it remains `[Needs Verification]`.
