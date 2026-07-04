# Static CI Checklist

## Stage 1 Static Checks

- [OpenSpec]: `rtk openspec validate redcap-oran-sdk-workflow-v3 --strict`
- [Workflow checker]: `rtk python agent_doc/Project_management/projects/redcap_oran_sdk_workflow_v3/scripts/check_workflow_v3_static.py`
- [Python syntax]: `rtk python -m py_compile agent_doc/Project_management/projects/redcap_oran_sdk_workflow_v3/scripts/check_workflow_v3_static.py`
- [Diff hygiene]: `rtk git diff --check -- AGENTS.md openspec/changes/redcap-oran-sdk-workflow-v3 agent_doc/Project_management/projects/redcap_oran_sdk_workflow_v3`

## Stage 1 Does Not Prove

- SDK runtime behavior.
- E2SM-KPM/E2SM-RC clause conformance.
- RFsim Case B control success.
- RedCap protocol PASS.

## Stage 2 And Stage 3 Placeholders

- [Stage 2]: build the touched xApp/OAI target after runtime code exists.
- [Stage 3]: run RFsim Case B marker validation after runtime code exists.
