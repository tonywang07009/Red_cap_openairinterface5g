# Static CI Checklist

## Stage 1 Static Checks

- [OpenSpec]: `rtk openspec validate redcap-oran-sdk-workflow-v3 --strict`
- [Workflow checker]: `rtk python agent_doc/Project_management/projects/redcap_oran_sdk_workflow_v3/scripts/check_workflow_v3_static.py`
- [Python syntax]: `rtk python -m py_compile agent_doc/Project_management/projects/redcap_oran_sdk_workflow_v3/scripts/check_workflow_v3_static.py`
- [Diff hygiene]: `rtk git diff --check -- AGENTS.md openspec/changes/redcap-oran-sdk-workflow-v3 agent_doc/Project_management/projects/redcap_oran_sdk_workflow_v3`

## Stage 1 Now Checks

- Required Workflow 3.0 docs, templates, OpenSpec artifacts, and control policy files.
- `dev_refer/` reference-map docs and legacy relative reference paths.
- SDK channel decisions:
  - xApp: `openair2/E2AP/flexric/`
  - dApp: `openair2/E3AP/`
  - rApp: docs-first only.
- SDK scaffold files:
  - xApp: `openair2/E2AP/REDCAP_SDK/xapp/redcap_xapp_sdk.*`
  - dApp: `openair2/E3AP/sdk/redcap_dapp_sdk.*`
  - rApp: `agent_doc/Project_management/projects/redcap_oran_sdk_workflow_v3/sdk/rapp/`

## Stage 1 SDK Syntax Checks

- [xApp SDK C syntax]: `rtk cc -DASN -DE2AP_V3 -DKPM_V3_00 '-DSERVICE_MODEL_DIR_PATH="/"' -DSQLITE3_XAPP -I. -Iopenair2/E2AP/flexric/src -W -Wall -Wextra -std=gnu11 -fsyntax-only openair2/E2AP/REDCAP_SDK/xapp/redcap_xapp_sdk.c ci-scripts/redcap_ul_prb_ctrl_xapp.c`
- [dApp SDK C syntax]: `rtk cc -Iopenair2/E3AP/sdk -W -Wall -Wextra -std=c11 -fsyntax-only openair2/E3AP/sdk/redcap_dapp_sdk.c`
- [rApp SDK C syntax]: `rtk cc -Iagent_doc/Project_management/projects/redcap_oran_sdk_workflow_v3/sdk/rapp -W -Wall -Wextra -std=c11 -fsyntax-only agent_doc/Project_management/projects/redcap_oran_sdk_workflow_v3/sdk/rapp/redcap_rapp_policy.c`
- [rApp schema JSON]: `rtk python -m json.tool agent_doc/Project_management/projects/redcap_oran_sdk_workflow_v3/sdk/rapp/redcap_rapp_policy.schema.json`
- [xApp Python SDK]: `rtk python openair2/E2AP/REDCAP_SDK/xapp/redcap_xapp_sdk.py`
- [dApp Python SDK]: `rtk python openair2/E3AP/sdk/redcap_dapp_sdk.py`
- [rApp Python SDK]: `rtk python agent_doc/Project_management/projects/redcap_oran_sdk_workflow_v3/sdk/rapp/redcap_rapp_policy.py`

## Stage 1 Does Not Prove

- SDK runtime behavior.
- E2SM-KPM/E2SM-RC clause conformance.
- RFsim Case B control success.
- RedCap protocol PASS.

## Stage 2 And Stage 3 Placeholders

- [Stage 2]: build the touched xApp/OAI target after runtime code exists.
- [Stage 3]: run RFsim Case B marker validation after runtime code exists.
