# RedCap dApp/xApp SDK Test Validation v1

## Project Metadata

- [Project Path]: `agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/project_plan.md`
- [OpenSpec Change]: `openspec/changes/redcap-dapp-xapp-sdk-test-validation/`
- [Primary References]: `dev_refer/`
- [Related Workflow]: `agent_doc/Project_management/projects/redcap_oran_sdk_workflow_v3/`
- [Objective]: validate the next RedCap dApp/xApp SDK slice through staged tests before claiming 56 UE / 5 MHz BWP runtime behavior.

## Reference Priority

- [MUST] Use `dev_refer/dapp_dev_need/libe3/` for E3 role, transport, encoding, and SWIG binding expectations.
- [MUST] Use `dev_refer/dapp_dev_need/E3Controller/` for I/Q pipeline, per-slot pipeline, `--num-prbs`, and timing-log expectations.
- [MUST] Use `dev_refer/dapp_dev_need/dApp-library/` for I/Q sample, PRB control, and visualization examples.
- [MUST] Use `dev_refer/dapp_dev_need/dApp-openairinterface5g/` only as a targeted implementation reference, not as a source tree to copy.
- [MUST] Use `dev_refer/xapp_dev_need/` and `openair2/E2AP/flexric/` for xApp design comparison.
- [MUST] Mark exact O-RAN and 3GPP clause mappings `[Needs Verification]` until locally extracted.

## Gate Index

| Gate | Purpose | Acceptance Evidence | Status |
|---|---|---|---|
| Gate A | SDK unit and API contract | Python self-test and C syntax checks | [~] static scaffold |
| Gate B | SWIG evidence boundary | SWIG interface files verified; generated module status reported | [~] definition check only |
| Gate C | E3 loopback | RAN-role and DAPP-role E3 agents exchange indication/control | [x] PASS with local expected shim |
| Gate D | small RFsim marker | 1-2 UE dApp/xApp markers plus gNB-side apply marker | [~] source/build ready; 5 MHz RA observed; dApp marker blocked |
| Gate E | 56 UE / 5 MHz BWP stress | attach/PDU health, dApp/xApp markers, no gNB restart, bounded latency | [ ] pending runtime |

## Current Boundary

- Current static work does not claim [56 UE / 5 MHz BWP runtime PASS].
- Current static work does not claim [PDCCH command path PASS].
- Current 5 MHz BWP runtime work only proves RA/SIB1 profile application, not dApp control effectiveness.
- Current SDK additions are test-facing helpers for priority hints and PRB allocation decisions.
- The dApp remains the local apply/reject boundary; xApp only emits UE priority hints.

## Validation Commands

```bash
python3 -B agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/check_dapp_xapp_sdk_test_validation.py
python3 -B agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/dapp_xapp_sdk_contract_selftest.py
python3 -B agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/gate_c_e3_loopback_check.py
python3 -B agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/gate_c_e3_loopback_check.py --try-configure
python3 -B agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/gate_c_e3_loopback_check.py --try-configure --allow-fetch
python3 -B agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/gate_d_rfsim_marker_check.py
openspec validate redcap-dapp-xapp-sdk-test-validation --strict
```

## Next Runtime Pull

- Replace the Gate C local `tl_expected` shim with official `tl_expected` cache/network access before treating the libe3 build as production dependency evidence.
- Use `ci-scripts/conf_files/gnb.sa.band78.fr1.106PRB.usrpb210.redcap.5mhz-bwp.yaml` for the 5 MHz BWP run. It keeps the 106 PRB RF carrier stable and makes BWP1 plus RedCap DL/UL initial BWP 12 PRBs at 30 kHz SCS `[Needs Verification]`.
- Latest Gate D 5 MHz RFsim run evidence:
  - gNB log: `test_log/runtime_logs/gate_d_5mhz_gnb_2026-07-06_17-16-57.log`.
  - UE2 log: `test_log/runtime_logs/gate_d_5mhz_ue2_2026-07-06_17-16-57.log`.
  - gNB observed `[RedCap RA][gNB Msg2 BWP selected]` with `dl_bwp_size 12` and `ul_bwp_size 12`.
  - UE2 observed `SIB1 RedCap initial BWP decision` and applied DL/UL BWP size `12`.
  - Root-cause evidence: old runtime logs show RedCap RA DCI bit-length mismatch, gNB `dci_bits 35` versus UE `dci_bits 39`.
  - Source fix: gNB and UE now align RedCap Case B RA common DCI size to the current 12 PRB DL BWP.
  - Build evidence: `test_log/build_logs/build_nr-softmodem_2026-07-06_17-28-49_gate-d-dci-bits.log` and `test_log/build_logs/build_nr-uesoftmodem_2026-07-06_17-29-03_gate-d-dci-bits.log`.
  - Remaining blocker: post-fix Docker image rebuild/RFsim recreate was rejected because workspace credits are unavailable; no post-fix Gate D runtime PASS is claimed.
- Next pull must rebuild local Docker images, recreate gNB + UE2 with the 5 MHz profile, confirm gNB/UE RedCap RA DCI bit-length alignment, then rerun the Gate D dApp marker checker.
- Treat the current ULSCH/PUCCH hooks as marker hooks only; dApp policy rewrite of PUCCH/PUSCH allocation remains a later implementation item.
- Run 56 UE / 5 MHz BWP only after Gate D passes.
