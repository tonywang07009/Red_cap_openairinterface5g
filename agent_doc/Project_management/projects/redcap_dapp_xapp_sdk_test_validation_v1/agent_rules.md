# RedCap dApp/xApp SDK Test Validation Agent Rules

## Context Pack

- [MUST] Read this project `project_plan.md`.
- [MUST] Read `openspec/changes/redcap-dapp-xapp-sdk-test-validation/` before changing tasks.
- [MUST] Read only targeted `Apps_dev/` files needed for the active gate.
- [MUST] Use `symdex` first for OAI/FlexRIC source or symbol lookup.
- [MUST] Use normal shell commands in stable user-facing docs; keep `rtk` for Codex-side validation notes only.

## SDK Rules

- [xApp] computes and emits UE priority hints.
- [dApp] owns I/Q observation handling, PRB ratio decision, apply/reject, and marker evidence.
- [KPM] remains observation only; do not describe KPM as a control path.
- [E3] is the expected dApp channel, using `Apps_dev/dapp_dev_need/libe3/` as the reference.
- [SWIG] must be proven by interface files plus generated/importable module evidence before claiming Python-to-C/C++ binding.

## Reporting Rules

- [MUST] Keep Gate A/B static evidence separate from Gate C/D/E runtime evidence.
- [MUST NOT] claim [64 UE / 5 MHz-to-20 MHz BWP runtime PASS] from static checks.
- [MUST] Record missing hooks, failed markers, and runtime blockers in `followups/workflow_v3_followups.md`.
- [MUST] Keep English and Traditional Chinese docs paired.

## Validation Rules

- Static checker:
  - `python3 agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/check_dapp_xapp_sdk_test_validation.py`
- SDK contract self-test:
  - `python3 agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/dapp_xapp_sdk_contract_selftest.py`
- OpenSpec:
  - `openspec validate redcap-dapp-xapp-sdk-test-validation --strict`
