## 1. OpenSpec And Project Scaffold

- [x] 1.1 Create the OpenSpec change scaffold.
- [x] 1.2 Add proposal, design, and delta spec artifacts.
- [x] 1.3 Add the project documentation root for dApp/xApp SDK test validation.
- [x] 1.4 Add a follow-up ledger for Workflow v3 missing or failed gates.

## 2. Static SDK Test Helpers

- [x] 2.1 Extend the existing xApp and dApp SDKs with minimal priority-hint and PRB-allocation test APIs.
- [x] 2.2 Add a Python static checker for `dev_refer/`, SDK files, docs, and marker wording.
- [x] 2.3 Add a Python SDK contract self-test for xApp priority hints and dApp PRB allocation decisions.
- [x] 2.4 Add SWIG evidence checks for `libe3` and I/Q saver references without requiring a full external build.

## 3. Documentation

- [x] 3.1 Add English API and usage documentation.
- [x] 3.2 Add Traditional Chinese API and usage documentation.
- [x] 3.3 Document Gate A-E acceptance evidence and runtime limitations.

## 4. Validation

- [x] 4.1 Run the new static checker.
- [x] 4.2 Run the new SDK contract self-test.
- [x] 4.3 Run OpenSpec validation for `redcap-dapp-xapp-sdk-test-validation`.
- [x] 4.4 Run targeted diff hygiene checks for the new artifacts.

## 5. Runtime Gates

- [ ] 5.1 Run Gate C E3 loopback after the local E3 runtime is selected.
  - Runner selected: `agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/gate_c_e3_loopback_check.py`.
  - Configure evidence: `test_log/compiler_logs/gate_c_libe3_configure_2026-07-05_18-43-41.log`.
  - Fetch configure evidence: `test_log/compiler_logs/gate_c_libe3_configure_fetch_2026-07-05_18-46-35.log`.
  - Runtime PASS remains pending until `tl_expected` is available and `dev_refer/dapp_dev_need/libe3` has a runnable loopback binary.
- [ ] 5.2 Run Gate D small RFsim marker validation after dApp/xApp runtime hooks exist.
- [ ] 5.3 Run Gate E 56 UE / 5 PRB BWP stress validation after Gate D passes.
