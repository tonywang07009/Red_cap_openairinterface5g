# RedCap O-RAN SDK Workflow 3.0

## Project Metadata

- [Project Path]: `agent_doc/Project_management/projects/redcap_oran_sdk_workflow_v3/project_plan.md`
- [Agent Rules]: `agent_doc/Project_management/projects/redcap_oran_sdk_workflow_v3/agent_rules.md`
- [OpenSpec Change]: `openspec/changes/redcap-oran-sdk-workflow-v3/`
- [O-RAN References]: `dev_refer/`
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
- `sdk_channel_layout.md`: OAI-style placement rule for future xApp, dApp, and rApp SDK work.
- `milestones/`: one execution contract per Gate.
- `spec_refs/`: targeted O-RAN/3GPP reference maps and clause extracts used by SDK tasks.
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
| G4 | `milestones/G4_rfsim_case_b_marker_validation.md` | First RFsim Case B SDK marker validation | [x] live marker PASS |

## Pull Queue

| Pull Item | Phase | Ready Criteria | Output | Status |
|---|---|---|---|---|
| WF3-G0 | Plan/Design | English plan accepted, SLM removed | OpenSpec + project scaffold | [x] |
| WF3-G1 | Design | Existing control contract and xApp seed inspected | SDK ownership contract | [x] |
| WF3-G1A | Design | Updated `dev_refer/` library inspected | Reference map + SDK channel layout | [x] |
| WF3-G1B | Build | SDK channel layout selected | xApp/dApp/rApp scaffold slice | [x] syntax PASS |
| WF3-G1C | Build | C SDK scaffold exists | Python SDK pair for xApp/dApp/rApp | [x] self-check PASS |
| WF3-G2 | Build | First runtime parameter selected and validation marker defined | Minimal SDK runtime path | [~] build/dry-run PASS |
| WF3-G3 | Test | Static checker runnable from repo root | CI Stage 1 evidence | [x] |
| WF3-G4 | Test | SDK runtime path builds and Case B policy selected | RFsim marker evidence | [x] gNB marker PASS |

## Current Boundary

- This project does not claim a complete xApp/dApp/rApp SDK yet.
- Existing `ci-scripts/redcap_ul_prb_ctrl_xapp.c` is a seed for C/C++ xApp work, not the full SDK.
- xApp SDK wrapper now lives under `openair2/E2AP/REDCAP_SDK/` and uses FlexRIC headers/libraries without modifying the dirty `openair2/E2AP/flexric` submodule.
- dApp SDK guard skeleton now lives under `openair2/E3AP/`.
- rApp SDK remains docs-first under this project until a concrete OAI runtime boundary is selected.
- Each SDK family now has both C and Python entry points; rApp remains declarative and does not expose a runtime apply path.
- First live Case B runtime validation passed for the narrow `redcap_ul_prb_cap` slice only: contract validation, xApp ACK, and gNB-side `RedCap UL PRB control` marker.
- Existing Case A protocol validation remains the baseline; Case B control must not mutate Case A policy files.
- Exact O-RAN clause mappings from the reference library remain `[Needs Verification]` until extracted locally.

## Next Action

- Use `openair2/E2AP/REDCAP_SDK/`, `openair2/E3AP/`, and `sdk/rapp/` as the first SDK scaffold slice before pulling larger SDK implementation items.
- Pull the next SDK item only after selecting whether the next runtime surface is broader xApp API coverage, dApp local apply service, or rApp policy packaging.
- Do not generalize the G4 PASS beyond `redcap_ul_prb_cap` until additional parameters have their own contract, control request, and gNB marker evidence.

## Follow-up From dApp/xApp SDK Test Validation

- [Pending Gates]: `agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/followups/workflow_v3_followups.md`.
- [Completed Follow-up]: Gate C E3 POSIX loopback and latency check passed with a project-local `tl_expected` shim.
- [Next Pull Item]: rebuild local OAI images after the Gate D RedCap RA DCI bit-length source fix, recreate gNB + UE2 with `GNB_REDCAP_CONFIG=../../conf_files/gnb.sa.band78.fr1.106PRB.usrpb210.redcap.5mhz-bwp.yaml` and `OAI_REDCAP_DAPP_GATE_D_MARKER=1`, then rerun Gate D small RFsim marker validation with both gNB and UE logs.
- [Stress Gate]: Gate E 56 UE / 5 MHz BWP stress validation stays blocked until Gate D produces both ULSCH/PUSCH and PUCCH markers that pass `--require-bwp-mhz 5`.
- [Boundary]: Workflow v3 remains complete for the narrow `redcap_ul_prb_cap` slice; the dApp/xApp validation project owns the new test gates.
