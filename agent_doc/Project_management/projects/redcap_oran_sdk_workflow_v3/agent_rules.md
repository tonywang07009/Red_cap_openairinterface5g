# RedCap O-RAN SDK Workflow 3.0 Agent Rules

## Project Entry

- [Project Plan]: `agent_doc/Project_management/projects/redcap_oran_sdk_workflow_v3/project_plan.md`
- [OpenSpec Change]: `openspec/changes/redcap-oran-sdk-workflow-v3/`
- [SDK Channel Layout]: `agent_doc/Project_management/projects/redcap_oran_sdk_workflow_v3/sdk_channel_layout.md`
- [Reference Maps]: `agent_doc/Project_management/projects/redcap_oran_sdk_workflow_v3/spec_refs/`
- [Milestones]: `agent_doc/Project_management/projects/redcap_oran_sdk_workflow_v3/milestones/`
- [Validation]: `agent_doc/Project_management/projects/redcap_oran_sdk_workflow_v3/validation/`
- [Runtime Source of Truth]: `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/`

## Context Pack

- [MUST] For planning/docs/static checks, read only:
  - root `AGENTS.md`
  - this project `project_plan.md`
  - this `agent_rules.md`
  - `sdk_channel_layout.md` when SDK placement is discussed
  - `spec_refs/dev_refer_reference_overview.md` and `spec_refs/oran_spec_usage_map.md` when reference usage is discussed
  - target milestone
  - relevant validation template/checklist
- [MUST] For code lookup, use `symdex` before raw source reads.
- [MUST] Use `rtk` for normal shell commands unless the wrapper does not support the command shape.
- [MUST NOT] bulk-read O-RAN PDFs/DOCX files. Extract only the target clause or interface section when needed.

## Tool Route

- [OpenSpec]: formal requirements, scope, and task status.
- [dev_refer]: local O-RAN reference library and external SDK design inputs.
- [symdex]: source/symbol/marker navigation in OAI/FlexRIC code.
- [rtk]: shell commands, static checks, and validation commands.
- [Ponytail Full]: design/review gate to remove unnecessary abstraction.
- [Marker validation]: only RedCap/O-RAN-specific markers can support runtime PASS.

## SDK Ownership Rules

- [rApp] may write policy intent but must not directly mutate OAI runtime state.
- [xApp] may observe KPM and request control through E2SM-RC, custom SM, or dApp local API.
- [KPM] is observation only; do not describe KPM as applying control.
- [dApp/gNB guard] owns local safety checks, apply/reject decisions, rollback, and applied snapshots.
- [xApp channel] RedCap-specific SDK code should follow `openair2/E2AP/REDCAP_SDK/` and compile against `openair2/E2AP/flexric/`.
- [dApp channel] SDK code should follow `openair2/E3AP/`.
- [rApp channel] remains docs-first only; do not create an `openair2` rApp channel until the runtime boundary is selected.
- [SDK language rule] xApp, dApp, and rApp SDK slices must keep C and Python entry points in sync.
- [Case A] remains the fixed protocol baseline.
- [Case B] owns dynamic policy/control validation and must not overwrite Case A files.

## Reporting Rules

- [Daily Report] is for progress and next pull item only.
- [Gate Report] is for validation evidence, spec mapping, limitations, and learning summary.
- [MUST] Mark uncertain O-RAN or 3GPP clause mappings as `[Needs Verification]`.
- [MUST NOT] claim PASS from attach/session/tunnel/ping without RedCap/O-RAN markers.

## Static CI Rules

- Run `rtk python agent_doc/Project_management/projects/redcap_oran_sdk_workflow_v3/scripts/check_workflow_v3_static.py`.
- Run `rtk python -m py_compile agent_doc/Project_management/projects/redcap_oran_sdk_workflow_v3/scripts/check_workflow_v3_static.py`.
- Run `rtk openspec validate redcap-oran-sdk-workflow-v3 --strict`.
- Static CI Stage 1 does not replace build/CTest or RFsim validation.
