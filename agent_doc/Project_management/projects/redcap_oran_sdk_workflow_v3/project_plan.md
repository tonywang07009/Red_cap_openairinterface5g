# RedCap O-RAN SDK Workflow 3.0

## Project Metadata

- [Project Path]: `agent_doc/Project_management/projects/redcap_oran_sdk_workflow_v3/project_plan.md`
- [Agent Rules]: `agent_doc/Project_management/projects/redcap_oran_sdk_workflow_v3/agent_rules.md`
- [OpenSpec Change]: `openspec/changes/redcap-oran-sdk-workflow-v3/`
- [O-RAN References]: `../dev_refer/develop_refer_doc/`
- [Runtime Source of Truth]: `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/`
- [Control Contract]: `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/control/redcap_control_contract.yaml`
- [Created Date]: 2026-07-04
- [Objective]: Use a pull-based workflow to develop RedCap xApp/dApp/rApp SDK capability without weakening validated Case A protocol behavior.

## Workflow Summary

- [Default Route]: `OpenSpec -> symdex -> rtk -> Ponytail review -> marker validation -> report`.
- [Ponytail Level]: Full; remove unnecessary abstractions after source and spec context are understood.
- [Reporting Model]: Daily Report for progress, Gate Report for validation evidence.
- [SLM Status]: out of scope until the local SLM environment is ready.
- [Runtime Claim Rule]: attach, session, tunnel, or ping evidence alone is not enough for RedCap/O-RAN PASS.

## Document Model

- `project_plan.md`: short project index, current status, and pull queue.
- `agent_rules.md`: context pack, tool route, and Case A/B safety boundaries.
- `milestones/`: one execution contract per Gate.
- `spec_refs/`: targeted O-RAN/3GPP clause extracts used by SDK tasks.
- `validation/`: report templates, static CI checklist, and validation rules.
- `scripts/`: local checks that support the workflow.
- `report/`: final Gate reports only; do not store raw logs here.

## Gate Index

| Gate | File | Purpose | Status |
|---|---|---|---|
| G0 | `milestones/G0_workflow_scaffold.md` | OpenSpec, project docs, templates, and static checker | [x] |
| G1 | `milestones/G1_sdk_contract.md` | SDK ownership and contract boundary | [x] |
| G2 | `milestones/G2_sdk_runtime_v1.md` | First runnable xApp/dApp/rApp SDK slice | [~] build/dry-run PASS |
| G3 | `milestones/G3_reporting_static_ci.md` | Static CI plus reporting quality gates | [x] static only |
| G4 | `milestones/G4_rfsim_case_b_marker_validation.md` | First RFsim Case B SDK marker validation | [!] UE exit 139 before live control |

## Pull Queue

| Pull Item | Phase | Ready Criteria | Output | Status |
|---|---|---|---|---|
| WF3-G0 | Plan/Design | English plan accepted, SLM removed | OpenSpec + project scaffold | [x] |
| WF3-G1 | Design | Existing control contract and xApp seed inspected | SDK ownership contract | [x] |
| WF3-G2 | Build | First runtime parameter selected and validation marker defined | Minimal SDK runtime path | [~] build/dry-run PASS |
| WF3-G3 | Test | Static checker runnable from repo root | CI Stage 1 evidence | [x] |
| WF3-G4 | Test | SDK runtime path builds and Case B policy selected | RFsim marker evidence | [!] UE exit 139 before live control |

## Current Boundary

- This project does not claim a complete xApp/dApp/rApp SDK yet.
- Existing `ci-scripts/redcap_ul_prb_ctrl_xapp.c` is a seed for C/C++ xApp work, not the full SDK.
- Existing Case A protocol validation remains the baseline; Case B control must not mutate Case A policy files.
- Exact O-RAN clause mappings from the reference library remain `[Needs Verification]` until extracted locally.

## Next Action

- Run [G4] RFsim Case B marker validation for `redcap_ul_prb_cap`.
- Current G4 blocker: UE1 exits 139 before attach, so live RC control is intentionally not sent.
- Do not claim runtime PASS until live logs show contract validation, control request, and gNB-side `RedCap UL PRB control` marker.
