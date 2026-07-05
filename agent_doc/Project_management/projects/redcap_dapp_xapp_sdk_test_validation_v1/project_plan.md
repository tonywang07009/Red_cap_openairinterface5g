# RedCap dApp/xApp SDK Test Validation v1

## Project Metadata

- [Project Path]: `agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/project_plan.md`
- [OpenSpec Change]: `openspec/changes/redcap-dapp-xapp-sdk-test-validation/`
- [Primary References]: `dev_refer/`
- [Related Workflow]: `agent_doc/Project_management/projects/redcap_oran_sdk_workflow_v3/`
- [Objective]: validate the next RedCap dApp/xApp SDK slice through staged tests before claiming 56 UE / 5 PRB BWP runtime behavior.

## Reference Priority

- [MUST] Use `dev_refer/dapp_dev_need/libe3/` for E3 role, transport, encoding, and SWIG binding expectations.
- [MUST] Use `dev_refer/dapp_dev_need/dApp-library/` for I/Q sample, PRB control, and visualization examples.
- [MUST] Use `dev_refer/dapp_dev_need/dApp-openairinterface5g/` only as a targeted implementation reference, not as a source tree to copy.
- [MUST] Use `dev_refer/xapp_dev_need/` and `openair2/E2AP/flexric/` for xApp design comparison.
- [MUST] Mark exact O-RAN and 3GPP clause mappings `[Needs Verification]` until locally extracted.

## Gate Index

| Gate | Purpose | Acceptance Evidence | Status |
|---|---|---|---|
| Gate A | SDK unit and API contract | Python self-test and C syntax checks | [~] static scaffold |
| Gate B | SWIG evidence boundary | SWIG interface files verified; generated module status reported | [~] definition check only |
| Gate C | E3 loopback | RAN-role and DAPP-role E3 agents exchange indication/control | [blocked-external-dependency] `tl::expected` unavailable |
| Gate D | small RFsim marker | 1-2 UE dApp/xApp markers plus gNB-side apply marker | [ ] pending runtime |
| Gate E | 56 UE / 5 PRB BWP stress | attach/PDU health, dApp/xApp markers, no gNB restart, bounded latency | [ ] pending runtime |

## Current Boundary

- Current static work does not claim [56 UE / 5 PRB BWP runtime PASS].
- Current static work does not claim [PDCCH command path PASS].
- Current SDK additions are test-facing helpers for priority hints and PRB allocation decisions.
- The dApp remains the local apply/reject boundary; xApp only emits UE priority hints.

## Validation Commands

```bash
python3 -B agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/check_dapp_xapp_sdk_test_validation.py
python3 -B agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/dapp_xapp_sdk_contract_selftest.py
python3 -B agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/gate_c_e3_loopback_check.py
python3 -B agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/gate_c_e3_loopback_check.py --try-configure
python3 -B agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/gate_c_e3_loopback_check.py --try-configure --allow-fetch
openspec validate redcap-dapp-xapp-sdk-test-validation --strict
```

## Next Runtime Pull

- Resolve Gate C dependency: provide local `tl_expected` cache or restore workspace credits/network access for FetchContent; `asn1c` was found at `/opt/asn1c/bin/asn1c` during configure.
- Build `test_role_pair_posix` under `dev_refer/dapp_dev_need/libe3` after configure succeeds.
- Select the exact OAI dApp/gNB marker before Gate D.
- Run 56 UE / 5 PRB BWP only after Gate D passes.
