---
status: review-required
source_refs:
  - agent_doc/Project_management/projects/redcap_oran_sdk_workflow_v3/project_plan.md
  - agent_doc/Project_management/projects/redcap_oran_sdk_workflow_v3/agent_rules.md
  - agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/Doc/sdk_development_guide.en.md
evidence_tier: mixed
last_reviewed: 2026-07-31
related_pages:
  - redcap_research_wiki/sources/active-redcap-projects.md
  - redcap_research_wiki/cases/CASE-2026-001-oran-g4-report-index-drift.md
  - redcap_research_wiki/systems/aiot/overview.md
---

# xApp and dApp Control System Map

## Scope

This map separates policy/observation, E2 transport, dApp guard, gNB
apply/rollback, and outcome evidence for the current RedCap SDK surfaces.

## System Flow

```mermaid
flowchart LR
  P[rApp or policy intent] --> X[xApp observation and control]
  X --> E[E2 transport and ACK]
  E --> D[dApp guard and accept or reject]
  D --> G[gNB apply, snapshot, and rollback]
  G --> O[UE-visible and outcome evidence]
```

## Component Index

| Component | Current state | Strongest evidence | Page |
|---|---|---|---|
| xApp observation/control | Mixed integrated and dormant helpers | Source plus bounded runtime | [Open](xapp-observation-control.md) |
| E2 transport | Implemented-called for selected control | Transport/ACK | [Open](e2-transport.md) |
| dApp guard | Mixed integrated and dormant guards | Guard decision/marker | [Open](dapp-guard.md) |
| gNB apply/rollback | Parameter-specific implemented paths | Apply/snapshot; rollback varies | [Open](gnb-apply-rollback.md) |
| Outcome evidence | Retained, parameter-specific | Stops at strongest completed step | [Open](outcome-evidence.md) |

## Current State

[Runtime Evidence] The project records one bounded live Case B
`redcap_ul_prb_cap` path with contract, control ACK, and gNB apply marker. It
does not establish a complete xApp/dApp/rApp SDK or a performance improvement.

## Evidence Ladder

1. Request identity and schema.
2. xApp decision/builder output.
3. E2 transport and ACK.
4. dApp/local accept or reject.
5. gNB apply marker and snapshot/rollback state.
6. UE/RRC completion when required.
7. Outcome metric from its owner.

## Repair Order

1. Correlate one request identity/version.
2. Find the last completed evidence step.
3. Inspect only the next owner.
4. Reuse the existing SDK/transport/apply module and nearest self-test.
5. Stop before source/runtime work unless separately approved.

## Course Route

Prerequisite: [A-IoT/AIOTF](../aiot/overview.md). Read Component Index in order,
reusing existing APIs before proposing a minimal in-place extension.

## Claim Boundary

Static, transport, ACK, guard, apply, UE-visible, and outcome evidence are
independent. No earlier step implies a later step. Exact O-RAN clause mappings
remain `[Needs Verification]`.

## Open Questions

- Production callers for several priority/policy helpers remain
  `[Needs Verification]`.
- Generic rollback and parameter-independent performance effects are not
  established.
