# RedCap dApp/xApp SDK Test Validation

## Scope

- This page explains how to test the RedCap dApp/xApp SDK slice.
- Primary references are under `dev_refer/`.
- Static checks do not claim 56 UE / 5 MHz BWP runtime PASS.

## API / config behavior

| API | Language | Purpose | Current evidence |
|---|---|---|---|
| `redcap_xapp_make_priority_hint` | C | Build one UE priority hint from UL buffer and weights | syntax check target |
| `redcap_xapp_select_top_priority_hint` | C | Select the highest-priority UE; ties use lower RNTI | syntax check target |
| `make_priority_hint` | Python | Python equivalent of the C priority hint builder | self-test |
| `select_top_priority_hint` | Python | Python equivalent of top-UE selection | self-test |
| `redcap_dapp_guard_prb_allocation` | C | Validate a 5 MHz BWP profile, I/Q presence, and PUCCH/PUSCH ratio intent | syntax check target |
| `redcap_dapp_guard_prb_allocation` | Python | Python equivalent of the dApp allocation guard | self-test |

Key fields:

- [RNTI]: UE identifier; must be non-zero.
- [priority_weight]: xApp output used by dApp metadata.
- [bwp_prbs]: runtime-derived BWP PRB marker; for the 5 MHz / 30 kHz SCS profile, local notes expect about `12` PRBs `[Needs Verification]`.
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

Run Gate C with the project-local expected shim:

```bash
python3 -B agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/gate_c_e3_loopback_check.py --try-configure --use-local-expected-stub --try-build --build-dir dev_refer/dapp_dev_need/libe3/build/redcap-gate-c-local-expected
```

Current Gate C runtime evidence:

- POSIX IPC/TCP loopback PASS: `test_log/compiler_logs/gate_c_libe3_runtime_test_role_pair_posix_2026-07-06_11-58-08.log`
- Full-loop latency PASS: `test_log/compiler_logs/gate_c_libe3_runtime_test_bench_full_loop_latency_2026-07-06_11-58-23.log`
- Total round-trip latency: p99 `183 us`, max `260 us`

Run Gate D source readiness check:

```bash
python3 -B agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/gate_d_rfsim_marker_check.py
```

Run Gate D RFsim marker scan after starting gNB with the marker environment enabled:

```bash
cd ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap
GNB_REDCAP_CONFIG=../../conf_files/gnb.sa.band78.fr1.106PRB.usrpb210.redcap.5mhz-bwp.yaml \
MMTC_N_RB_DL=106 \
OAI_REDCAP_DAPP_GATE_D_MARKER=1 <start gNB/UE RFsim command>
python3 -B agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/gate_d_rfsim_marker_check.py --gnb-log <gNB-log-path> --ue-log <UE-log-path> --require-runtime --require-bwp-mhz 5
```

Gate D source readiness plus `nr-softmodem` build evidence is saved at `test_log/build_logs/build_nr-softmodem_2026-07-06_gate-d-pucch-marker.log`. It proves that the gNB ULSCH/PUSCH/PDCCH path calls the dApp PRB guard after `config_uldci()`, that the PUCCH FAPI path calls the same guard after `nr_configure_pucch()`, and that the target still builds. It does not claim RFsim runtime PASS.

Current Gate D 5 MHz RFsim evidence:

- gNB log: `test_log/runtime_logs/gate_d_5mhz_gnb_2026-07-06_17-16-57.log`
- UE2 log: `test_log/runtime_logs/gate_d_5mhz_ue2_2026-07-06_17-16-57.log`
- gNB observed `[RedCap RA][gNB Msg2 BWP selected]` with `dl_bwp_size 12` and `ul_bwp_size 12`.
- UE2 observed `SIB1 RedCap initial BWP decision` and applied DL/UL BWP size `12`.
- The old logs also show a RedCap RA DCI bit-length mismatch: gNB `dci_bits 35`, UE `dci_bits 39`.
- The source fix aligns both sides to the current 12 PRB DL BWP for RedCap Case B RA common DCI sizing.
- Gate D still does not PASS because the run stops at RA/RAR/Msg3 before `[RedCap dApp Gate D][gNB MAC UL]` and `[RedCap dApp Gate D][gNB MAC PUCCH]` markers appear.

## Step-by-step recap

1. Confirm local `dev_refer/` references exist.
2. Confirm xApp priority hint APIs exist in C and Python.
3. Confirm dApp PRB allocation APIs exist in C and Python.
4. Confirm SWIG definition files exist for `libe3` and I/Q saver.
5. Run the SDK contract self-test.
6. Run the Gate C E3 loopback checker.
7. Run the Gate D source readiness checker.
8. Treat Gate D-E as pending until RFsim runtime evidence exists.

## Example logic

- xApp receives UE metrics.
- xApp computes priority hints.
- dApp receives the selected hint.
- dApp checks I/Q observation availability.
- dApp validates the 5 MHz BWP profile and PUCCH/PUSCH ratios.
- dApp emits an apply/reject result.

## Visualization

- Use `dev_refer/dapp_dev_need/dApp-library/examples/spectrum_dapp.py` as the reference for visualization mode.
- Relevant options from that reference include:
  - `--demo-gui`
  - `--iq-plotter-gui`
  - `--energy-gui`
  - `--num-prbs <derived 5 MHz PRB count>`
- Visualization is not a PASS gate until the dApp runtime path is connected.

## Expected markers

- `RedCap xApp priority hint`
- `RedCap dApp PRB decision`
- `[RedCap dApp Gate D][gNB MAC UL] gNB-side apply marker`
- `[RedCap dApp Gate D][gNB MAC PUCCH] gNB-side PUCCH marker`
- Gate C source path: `dev_refer/dapp_dev_need/libe3/tests/integration/test_role_pair_posix.cpp`
- Gate D source path: `openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_ulsch.c`
- Gate D PUCCH source path: `openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_uci.c`
- Gate D 5 MHz BWP profile: `ci-scripts/conf_files/gnb.sa.band78.fr1.106PRB.usrpb210.redcap.5mhz-bwp.yaml`
- Gate D runtime env passthrough: `OAI_REDCAP_DAPP_GATE_D_MARKER` in `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/docker-compose.mmtc.yml`
- Gate D I/Q reference: `dev_refer/dapp_dev_need/E3Controller/src/e3sm/iq_pipeline.h` and `slot_iq_pipeline.h`
- PDCCH command path: `config_uldci()` followed by `fill_dci_pdu_rel15()` in the ULSCH path `[Needs Verification: TS 38.212 Section 7.3.1.1 / TS 38.214 Section 6.1]`

## Limitations

- Gate B currently verifies SWIG definitions, not generated SWIG module runtime.
- Gate C E3 loopback passed with the project-local `tl_expected` test shim.
- Official `tl_expected` FetchContent remains unavailable; do not use the local shim as production dependency evidence.
- Gate D source hook readiness and `nr-softmodem` build PASS are present; small RFsim marker validation has run but is not PASS.
- The DCI bit-length source fix builds for both `nr-softmodem` and `nr-uesoftmodem`.
- Gate D runtime env passthrough is present in the compose overlay, and the 5 MHz BWP profile was mounted in the gNB container for the latest run.
- The 5 MHz profile keeps the RF carrier at 106 PRBs while BWP1 and RedCap DL/UL initial BWP are 12 PRBs at 30 kHz SCS `[Needs Verification]`; runtime logs confirm RA/SIB1 uses size `12`, but dApp markers are blocked before connected scheduling.
- Current Gate D runtime blocker: post-fix Docker image rebuild/RFsim recreate was rejected because workspace credits are unavailable.
- Gate D currently covers the ULSCH/PUSCH/PDCCH and PUCCH marker paths. It does not yet implement dApp policy rewrite of PUCCH/PUSCH allocation.
- Gate E 56 UE / 5 MHz BWP stress validation is pending.
- Exact O-RAN and 3GPP clause mapping remains `[Needs Verification]`.
