---
status: review-required
source_refs:
  - openair2/E2AP/RAN_FUNCTION/O-RAN/ran_func_rc.c
  - openair2/LAYER2/NR_MAC_gNB/config.c
  - openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_primitives.c
  - openair2/RRC/NR/rrc_gNB.c
  - agent_doc/Project_management/projects/redcap_oran_sdk_workflow_v3/report/G4_rfsim_case_b_ul_prb_2026-07-04.md
evidence_tier: mixed
last_reviewed: 2026-07-31
related_pages:
  - redcap_research_wiki/systems/xapp-dapp/dapp-guard.md
  - redcap_research_wiki/systems/xapp-dapp/outcome-evidence.md
---

# gNB Apply, Snapshot, and Rollback

## Role

Own parameter-specific mutation of gNB MAC/RRC state after decoding and guard
acceptance, plus the state needed to reject or roll back safely.

## Inputs and Outputs

- Inputs: decoded request, verified UE context, current snapshot, guard result,
  and policy/request identity.
- Outputs: applied state/marker, rejection reason, previous snapshot, rollback
  state, and RRC reconfiguration when required.

## Owner and Source Trace

[Source Trace] `apply_redcap_ul_prb_control` writes bounded UL-PRB state in the
gNB UE context. The DRX path gates `nr_mac_apply_drx_policy` and continues to
RRC reconfiguration.

## Implementation Status

`implemented-called` for selected UL-PRB and live DRX paths. Rollback semantics
are parameter-specific; no generic rollback claim is made.

## Evidence and Markers

- UL PRB: `RedCap UL PRB control RNTI ... requested ... effective ...`.
- DRX: dApp accept/reject, MAC apply/snapshot state, and RRC completion when the
  UE configuration changes.
- [Needs Verification] a marker does not prove every subsequent grant or
  performance outcome used the new state.

## Failure Propagation

Missing UE context, invalid snapshot, apply failure, or absent RRC completion
stops the evidence ladder before outcome measurement.

## Repair Inventory

- Existing owners: RC handler, MAC config/primitives, scheduler state, and gNB
  RRC reconfiguration.
- Boundaries: unknown UE, requested 0/min/max/max+1, stale policy, concurrent
  request, apply failure, rollback failure, and UE release during apply.
- Add tests at the nearest existing owner; do not duplicate state.

## Research Reading Card

- Question: did the accepted request mutate the intended gNB/UE state and
  retain sufficient prior state for failure handling?
- Source types: guard result, apply caller/callee, snapshot, marker, and RRC
  completion where applicable.
- Competing explanations: apply never occurred; apply occurred but later
  scheduler/RRC/outcome observation did not consume or reflect it.
- Falsifier: read back the owner state under the same request identity and
  correlate the next UE/scheduler consumer.
- Strongest claim: parameter-specific apply/snapshot evidence.

## Course Route

Prerequisite: [dApp guard](dapp-guard.md). Next:
[Outcome evidence](outcome-evidence.md).

## Claim Boundary

Apply evidence does not prove UE-visible completion for RRC-changing controls
or performance improvement for any control.

## Open Questions

- Parameter-independent rollback behavior and per-grant UL-cap consumption
  remain `[Needs Verification]` beyond retained evidence.
