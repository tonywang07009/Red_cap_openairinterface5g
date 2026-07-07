## Why

The RedCap O-RAN SDK scaffold now has C and Python entry points, but the next pull item needs a test plan that proves dApp/xApp behavior instead of only proving file existence. The user specifically wants the validation to follow local `dev_refer/` material, cover a 64 UE staged scenario with the first 32 UE on 5 MHz BWP and later expansion to 20 MHz, verify SWIG-backed Python/C boundaries, and produce bilingual API documentation.

## What Changes

- Add a staged dApp/xApp SDK validation workflow: SDK unit checks, SWIG checks, E3 loopback, small RFsim marker validation, and 64 UE / 5 MHz-to-20 MHz stress validation.
- Define a test-facing dApp API contract for I/Q observation input, UE priority hints, PUCCH/PUSCH PRB ratio intent, and apply/reject decisions.
- Define a test-facing dApp access-pressure policy that maps RA/PUCCH collision proxy counters into bounded PUCCH/PUSCH ratio intent.
- Define a test-facing xApp API contract for weighted UE priority computation and E3-facing delivery to dApp.
- Add local `dev_refer/` reference requirements so dApp/xApp tests cite `libe3`, `dApp-library`, `dApp-openairinterface5g`, and xApp reference material before implementation claims.
- Add SWIG verification requirements for Python bindings rather than treating pure Python helper files as Python-to-C evidence.
- Add bilingual documentation requirements aligned with `redcap_docs_interface_reorg_v1`.
- Record failures or missing runtime work as follow-up items for `redcap_oran_sdk_workflow_v3` instead of reopening completed Workflow v3 tasks.

## Capabilities

### New Capabilities

- `redcap-dapp-xapp-sdk-test-validation`: staged validation requirements for RedCap dApp/xApp SDK tests, SWIG checks, E3 loopback, RFsim gates, and bilingual API documentation.

### Modified Capabilities

- None.

## Impact

- Affected OpenSpec artifacts: `openspec/changes/redcap-dapp-xapp-sdk-test-validation/`.
- Affected project docs: new project area under `agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/`.
- Affected SDK validation scripts: new Python test helpers under the new project area, with read-only checks against `openair2/E2AP/REDCAP_SDK/`, `openair2/E3AP/`, and `dev_refer/`.
- Affected runtime scope: no immediate Docker/RFsim execution is required for the first static implementation; RFsim gates remain explicit later-stage acceptance targets.
