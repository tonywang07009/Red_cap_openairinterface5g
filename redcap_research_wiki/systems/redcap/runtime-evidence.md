---
status: review-required
source_refs:
  - agent_doc/Project_management/projects/redcap_mmtc_priority_execution_v1/project_plan.md
  - agent_doc/Project_management/projects/redcap_mmtc_priority_execution_v1/validation/runtime_checklist.md
  - redcap_library/library_reports_summary/m5_caseb_56ue_static_cn_pass_report.md
  - redcap_library/library_reports_summary/m5_caseb_64ue_static_cn_threshold_report.md
evidence_tier: runtime
last_reviewed: 2026-07-31
related_pages:
  - redcap_research_wiki/systems/redcap/overview.md
  - redcap_research_wiki/systems/rfsim-performance-evaluation.md
---

# RedCap Runtime Evidence

## Role

Route retained RedCap/mMTC runtime evidence and prevent a bounded RFsim result
from becoming a general capacity or physical-network claim.

## Inputs and Outputs

- Inputs: frozen configuration, validation ID, required gNB/UE/CN markers,
  retained report, and failure classification.
- Outputs: accepted, partial, blocked, or failed project result with an explicit
  claim boundary.

## Owner and Source Trace

[Source Trace] The project plan owns acceptance. The runtime checklist owns
required markers. Curated reports under `redcap_library/` retain reusable
56-UE and 64-UE conclusions.

## Implementation Status

`implemented-called` as a project evidence workflow. It is not a runtime code
component.

## Evidence and Markers

[Runtime Evidence] The accepted result is 56/56 attach, PDU/tunnel, and forward
ping for the frozen Case B/static-CN setup. The 64-UE report is a classified
upper-bound failure, not a partial capacity acceptance.

## Failure Propagation

A missing CN, RAN, or UE marker invalidates only the corresponding evidence
step. Aggregating attach counts cannot replace tunnel, ping, apply, or feature-
specific markers.

## Repair Inventory

- Existing owners: project plan, validation checklist, scenario, and curated
  reports.
- Boundaries: zero UEs, accepted maximum, maximum+1, first/last UE, restart,
  partial registration, missing tunnel, and stale/non-frozen configuration.
- New runtime is L4 and remains outside this approval.

## Research Reading Card

- Question: what is the strongest conclusion supported by the retained run?
- Source types: frozen config, required marker contract, raw/retained evidence,
  and acceptance record.
- Competing explanations: a component failed; the measurement/retention path
  failed while the component result is unknown.
- Falsifier: reproduce every required marker from the retained evidence under
  the frozen configuration.
- Strongest claim: the exact accepted RFsim/project boundary only.

## Course Route

Prerequisite: all earlier [RedCap components](overview.md). Next:
[A-IoT Topology 2](../aiot/overview.md).

## Claim Boundary

No general capacity, real-network latency, standards conformance, or physical-
power conclusion is supported.

## Open Questions

- Further threshold tuning and fresh runtime remain `[Needs Verification]` and
  require separate L4 approval.
