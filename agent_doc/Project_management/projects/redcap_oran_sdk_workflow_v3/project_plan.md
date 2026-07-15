# RedCap O-RAN SDK Workflow 3.0

## Project Metadata

- [Project Path]: `agent_doc/Project_management/projects/redcap_oran_sdk_workflow_v3/project_plan.md`
- [Agent Rules]: `agent_doc/Project_management/projects/redcap_oran_sdk_workflow_v3/agent_rules.md`
- [OpenSpec Change]: `openspec/changes/redcap-oran-sdk-workflow-v3/`
- [O-RAN References]: `Apps_dev/`
- [Runtime Source of Truth]: `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/`
- [Control Contract]: `redcap_interface/control/redcap_control_contract.yaml`
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
| WF3-G1A | Design | Updated `Apps_dev/` library inspected | Reference map + SDK channel layout | [x] |
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
- [Completed Follow-up]: Gate D small RFsim marker validation passed with local rebuilt images, 5 MHz BWP, and the no-CSI/SRS runtime workaround; evidence is in `test_log/runtime_logs/gate_d_access_pressure_gnb_2026-07-07_00-47_local_no_csirs_srs.log`.
- [Prepared Follow-up]: Gate E static preflight is ready: 64 UE mMTC overlay, 64 UE CN DB overlay, 5 MHz/12 PRB first-stage profile, and 51 PRB 20 MHz proxy profile `[Needs Verification]` are checked by `gate_e_64ue_stage_check.py`.
- [Runtime Follow-up]: Gate E first32 post-DCI-BWP rerun passed the 5 MHz stage with `sample=32`, `running=32`, `attach=32`, `pdu=32`, `tun=32`, `forward_ping_ok=32`, `gnb_restart=0`, and `failures=0`.
- [Runtime Follow-up]: gNB evidence includes `128` `[RedCap RA][gNB DCI BWP]` markers, `32` `Received RRCSetupComplete`, `32` `Received RRCReconfigurationComplete`, and `32` `PDU Session Setup: ID=10`; UE logs no longer contain `TDA index from DCI 12`.
- [Runtime Follow-up]: xApp/RIC Docker logs for the 23:18 rerun show E42 setup, two RC subscriptions, `5` RC Indications, and E2 setup with RAN function 3 `ORAN-E2SM-RC`; no RIC Control request/ACK marker was observed.
- [Runtime Follow-up]: Gate E full64 20 MHz proxy attempt at 2026-07-07 23:39 failed before synchronization: summary `sample=64 running=64 attach=0 pdu=0 tun=0 gnb_restart=0 failures=64`; gNB expected UE `-C 3617640000 -r 51 --ssb 238`, but UE used `-C 3630360000 --ssb 144`.
- [Source Follow-up]: `redcap_interface/bash_library/fc_mmtc_smoke_validation.sh` now auto-applies 51PRB RF/SSB defaults when `MMTC_N_RB_DL=51` or `GNB_REDCAP_CONFIG` contains `51PRB`; prepare-only evidence is `test_log/compiler_logs/mmtc_smoke_prepare_only_2026-07-07_51prb_rf_defaults.log`.
- [Next Pull Item]: after Docker escalation is available, run one-UE 51PRB RF/SSB alignment smoke first; if it reaches sync/attach/PDU/TUN, run the full 64 UE / 20 MHz proxy stage and collect expansion/control evidence plus collision-load before/after access-pressure evidence.
- [Stress Gate]: Gate E 64 UE staged 5 MHz-to-20 MHz BWP stress validation remains pending until full 64 UE attach/control evidence and collision-load access-pressure evidence exist.
- [Boundary]: Workflow v3 remains complete for the narrow `redcap_ul_prb_cap` slice; the dApp/xApp validation project owns the new test gates.
