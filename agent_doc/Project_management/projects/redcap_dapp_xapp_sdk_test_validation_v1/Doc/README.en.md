# RedCap dApp/xApp SDK Test Validation

## Scope

- This page explains how to test the RedCap dApp/xApp SDK slice.
- Primary references are under `dev_refer/`.
- Static checks do not claim 56 UE / 5 PRB BWP runtime PASS.

## API / config behavior

| API | Language | Purpose | Current evidence |
|---|---|---|---|
| `redcap_xapp_make_priority_hint` | C | Build one UE priority hint from UL buffer and weights | syntax check target |
| `redcap_xapp_select_top_priority_hint` | C | Select the highest-priority UE; ties use lower RNTI | syntax check target |
| `make_priority_hint` | Python | Python equivalent of the C priority hint builder | self-test |
| `select_top_priority_hint` | Python | Python equivalent of top-UE selection | self-test |
| `redcap_dapp_guard_prb_allocation` | C | Validate 5 PRB BWP, I/Q presence, and PUCCH/PUSCH ratio intent | syntax check target |
| `redcap_dapp_guard_prb_allocation` | Python | Python equivalent of the dApp allocation guard | self-test |

Key fields:

- [RNTI]: UE identifier; must be non-zero.
- [priority_weight]: xApp output used by dApp metadata.
- [bwp_prbs]: must be `5` for this test scenario.
- [pucch_ratio_permille] / [pusch_ratio_permille]: ratio in permille; sum must be at most `1000`.
- [has_iq_samples]: dApp requires I/Q observation evidence before apply.

## Command usage

Run static validation:

```bash
python3 agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/check_dapp_xapp_sdk_test_validation.py
```

Run SDK contract validation:

```bash
python3 agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/dapp_xapp_sdk_contract_selftest.py
```

Run OpenSpec validation:

```bash
openspec validate redcap-dapp-xapp-sdk-test-validation --strict
```

Run Gate C E3 loopback dependency/runtime check:

```bash
python3 -B agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/gate_c_e3_loopback_check.py
```

Gate C returns `blocked` when `dev_refer/dapp_dev_need/libe3` has no existing loopback binary or required local build dependencies are absent.

Capture Gate C configure evidence:

```bash
python3 -B agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/gate_c_e3_loopback_check.py --try-configure
```

Current configure evidence is saved at `test_log/compiler_logs/gate_c_libe3_configure_2026-07-05_18-43-41.log`; the current blocker is missing offline `tl::expected` target/cache, not `asn1c`.

If network FetchContent is allowed, use a clean build directory:

```bash
python3 -B agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/gate_c_e3_loopback_check.py --try-configure --allow-fetch --build-dir dev_refer/dapp_dev_need/libe3/build/redcap-gate-c-fetch
```

Current fetch evidence is saved at `test_log/compiler_logs/gate_c_libe3_configure_fetch_2026-07-05_18-46-35.log`; sandbox DNS could not resolve `github.com`, and escalation was rejected because workspace credits are unavailable.

## Step-by-step recap

1. Confirm local `dev_refer/` references exist.
2. Confirm xApp priority hint APIs exist in C and Python.
3. Confirm dApp PRB allocation APIs exist in C and Python.
4. Confirm SWIG definition files exist for `libe3` and I/Q saver.
5. Run the SDK contract self-test.
6. Run the Gate C E3 loopback checker.
7. Treat Gate C-E as pending until runtime evidence exists.

## Example logic

- xApp receives UE metrics.
- xApp computes priority hints.
- dApp receives the selected hint.
- dApp checks I/Q observation availability.
- dApp validates 5 PRB BWP and PUCCH/PUSCH ratios.
- dApp emits an apply/reject result.

## Visualization

- Use `dev_refer/dapp_dev_need/dApp-library/examples/spectrum_dapp.py` as the reference for visualization mode.
- Relevant options from that reference include:
  - `--demo-gui`
  - `--iq-plotter-gui`
  - `--energy-gui`
  - `--num-prbs 5`
- Visualization is not a PASS gate until the dApp runtime path is connected.

## Expected markers

- `RedCap xApp priority hint`
- `RedCap dApp PRB decision`
- Gate C source path: `dev_refer/dapp_dev_need/libe3/tests/integration/test_role_pair_posix.cpp`
- Future runtime marker: PDCCH command path `[Needs Verification]`

## Limitations

- Gate B currently verifies SWIG definitions, not generated SWIG module runtime.
- Gate C E3 loopback has a dependency-aware runner, but runtime PASS requires a built `libe3` loopback binary.
- Gate C configure currently blocks at `tl::expected`; `asn1c` was detected at `/opt/asn1c/bin/asn1c`.
- Gate C network fetch currently blocks on workspace network/credits; provide local `tl_expected` cache or restore network access.
- Gate D small RFsim marker validation is pending.
- Gate E 56 UE / 5 PRB BWP stress validation is pending.
- Exact O-RAN and 3GPP clause mapping remains `[Needs Verification]`.
