---
status: review-required
case_id: CASE-2026-001
case_type: doc-drift
system_scope: RedCap O-RAN SDK Workflow 3.0 G4 report index
source_refs:
  - agent_doc/Project_management/projects/redcap_oran_sdk_workflow_v3/report/README.md
  - agent_doc/Project_management/projects/redcap_oran_sdk_workflow_v3/project_plan.md
evidence_refs:
  - agent_doc/Project_management/projects/redcap_oran_sdk_workflow_v3/report/G4_rfsim_case_b_ul_prb_2026-07-04.md
evidence_tier: mixed
last_reviewed: 2026-07-31
related_pages:
  - redcap_research_wiki/systems/xapp-dapp/overview.md
---

# CASE-2026-001: O-RAN G4 Report-Index Drift

## Question

Should the Workflow 3.0 Gate-report index list the G4 RFsim Case B report and
its bounded PASS after the project plan and Gate report record that result?

## Context and Reproduction

The [Gate-report index](../../agent_doc/Project_management/projects/redcap_oran_sdk_workflow_v3/report/README.md)
owns navigation to final Gate reports, while the
[project plan](../../agent_doc/Project_management/projects/redcap_oran_sdk_workflow_v3/project_plan.md) owns
overall Gate status. Inspect the report-index correction with:

```bash
git diff -- agent_doc/Project_management/projects/redcap_oran_sdk_workflow_v3/report/README.md
```

The tracked baseline said that no runtime Gate report existed and listed only
G0 scaffold evidence. The current project plan and
[G4 Gate report](../../agent_doc/Project_management/projects/redcap_oran_sdk_workflow_v3/report/G4_rfsim_case_b_ul_prb_2026-07-04.md)
already record the bounded G4 result.

## Expected versus Observed

- Expected: the report index links each final Gate report, takes overall Gate
  status from the project plan, and preserves the report's claim boundary.
- Observed baseline: the index said no runtime Gate report existed even though
  the G4 report and project-plan G4 status existed.
- Observed correction: the index now links the G4 report as PASS only for the
  live `redcap_ul_prb_cap` control slice and keeps UE1 exit 139 unresolved.

## Evidence

[Source Trace] The project plan marks G4 `live marker PASS`; the Gate report
requires `[Contract][PASS]`, `CONTROL ACK rx`, and the gNB-side
`RedCap UL PRB control RNTI 7d05 requested 32 effective 32` marker. The corrected
index links that report and repeats its narrow claim boundary.

[Runtime Evidence] The linked Gate report records the accepted G4 markers and
also records the missing short Docker evidence-log persistence as `BLOCKED`.
This case does not re-run or independently validate those markers.

## Competing Explanations

1. G4 should remain absent because short Docker evidence-log persistence was
   blocked. This does not match the project plan or Gate report, which accept
   the marker result while recording the persistence limitation.
2. G4 may be indexed as a complete SDK PASS. This conflicts with both canonical
   records, which limit PASS to `redcap_ul_prb_cap`.
3. The xApp acknowledgement alone establishes G4. The Gate report explicitly
   requires the gNB apply marker and rejects ACK-only overclaiming.

## Resolution or Next Owner

Keep the current report-index correction because it restores navigation and
matches the project plan and Gate report. A human reviewer must confirm this
case before changing `status` to `confirmed` or synchronizing its conclusion
elsewhere.

## Claim Boundary

This case establishes document alignment among the report index, project plan,
and existing Gate report. It does not create new runtime evidence, establish a
complete xApp/dApp/rApp SDK, resolve UE1 exit 139, validate other parameters,
or confirm exact O-RAN clause mappings.

## Documentation Impact

Retain the current bounded G4 entry in the project-local report index. Do not
edit public READMEs or stable manuals until a human confirms this case and
explicitly approves a documentation-sync route.
