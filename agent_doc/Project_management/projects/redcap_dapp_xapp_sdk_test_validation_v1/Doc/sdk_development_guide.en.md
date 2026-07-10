# RedCap dApp/xApp SDK Development Guide

## Scope

- This guide is for engineers adding or changing RedCap dApp/xApp SDK algorithms.
- It explains the current SDK contract, not a fully productized O-RAN SDK.
- Runtime claims must still point to Gate reports and logs.

## Code Locations

| Area | Path | Current role |
|---|---|---|
| xApp C SDK | `openair2/E2AP/REDCAP_SDK/xapp/redcap_xapp_sdk.h` / `.c` | Priority-hint data model and selection helper |
| xApp Python helper | `openair2/E2AP/REDCAP_SDK/xapp/redcap_xapp_sdk.py` | Fast parity helper for priority-hint logic |
| dApp C SDK | `openair2/E3AP/sdk/redcap_dapp_sdk.h` / `.c` | PRB allocation guard, access-pressure policy, and RA-pressure selector |
| dApp Python helper | `openair2/E3AP/sdk/redcap_dapp_sdk.py` | Fast parity helper for dApp policy and selector logic |
| E2/FlexRIC assets | `openair2/E2AP/flexric` | xApp / nearRT-RIC integration route |
| E3 references | `dev_refer/dapp_dev_need/libe3` | dApp-side E3 loopback and SWIG reference route |

## Algorithm Contract

- [xApp input]: per-UE metric such as RNTI, UL buffer, QoS weight, and RedCap weight.
- [xApp output]: `priority_weight`, packaged as a RedCap priority hint.
- [dApp input]: RA retry count, Msg3 failure count, PUCCH resource reject count, CRC/discard count, previous pressure EWMA, BWP PRB marker, I/Q availability, and optional xApp priority hint.
- [dApp output]: bounded PUCCH/PUSCH ratio intent, RA-pressure priority selection, and PRB allocation metadata.
- [Guard boundary]: dApp policy output must pass `redcap_dapp_guard_prb_allocation` before it can be treated as applyable.
- [I/Q boundary]: `has_iq_samples` must be true for apply; otherwise the result must stay reject/diagnostic.

## Current Policy Shape

- [Pressure score]: `100 * ra_retry + 120 * msg3_failure + 160 * pucch_resource_reject + 40 * crc_discard`, clamped to `1000`.
- [Priority selector]: `redcap_dapp_select_ra_pressure_priority` picks the UE with the highest [RA retry count] first, then pressure score, priority weight, and lower RNTI.
- [EWMA]: integer approximation of `0.7 * previous + 0.3 * current`.
- [Low pressure]: PUCCH `200`, PUSCH `600`.
- [Medium pressure]: PUCCH `300`, PUSCH `500`.
- [High pressure]: PUCCH `400`, PUSCH `400`.
- [51 PRB proxy]: Gate E-Core uses `MMTC_N_RB_DL=51`; exact 20 MHz terminology remains `[Needs Verification]`.

## E2 / E3 Boundary

- [E2]: xApp uses FlexRIC / nearRT-RIC for RC subscription and control-path experiments.
- [Current xApp control proof]: one selected RNTI has xApp/RIC/gNB ACK/apply evidence.
- [Gate E-Core boundary]: the 56 UE A/B run proves dApp marker and access-latency comparison; it does not prove per-UE xApp influence.
- [E3]: `dev_refer/dapp_dev_need/libe3` is the reference route for dApp-side RAN-role / DAPP-role communication.
- [SWIG status]: definitions exist; generated/importable SWIG runtime modules are not a required PASS for Gate E-Core.

## Development Workflow

1. Update the Python helper first for fast intent checking.
2. Mirror the same field semantics in the C SDK.
3. Keep the guard boundary intact; do not bypass `redcap_dapp_guard_prb_allocation`.
4. Run the SDK contract self-test:

```bash
python3 agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/dapp_xapp_sdk_contract_selftest.py
```

5. Run the project static checker:

```bash
python3 -B agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/check_dapp_xapp_sdk_test_validation.py
```

6. Run OpenSpec validation:

```bash
openspec validate redcap-dapp-xapp-sdk-test-validation --strict
```

7. For 36 UE pressure evidence, run baseline first, derive `MMTC_DAPP_PRIORITY_UES` with `select_core36_pressure_priority.py`, then validate with `gate_e_64ue_stage_check.py --stage core36-pressure`.
8. For 56 UE runtime evidence, follow [Gate E-Core manual reproduction](./gate_e_core56_manual_reproduction.en.md).

## Reporting Rules

- Do not report static checker PASS as runtime PASS.
- Do not describe KPM as the control path.
- Do not describe Python helpers as SWIG runtime bindings unless a generated/importable module has been verified.
- Do not claim dApp latency improvement from the accepted Gate E-Core run; it is a valid A/B comparison only.
- Every runtime claim must include summary metrics, gNB marker evidence, and the log/report path.
