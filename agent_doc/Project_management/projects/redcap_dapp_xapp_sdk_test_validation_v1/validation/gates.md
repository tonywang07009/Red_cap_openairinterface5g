# dApp/xApp SDK Validation Gates

## Gate A: SDK Unit And API Contract

- [Scope]: xApp priority hint and dApp PRB allocation decision.
- [Evidence]:
  - Python contract self-test PASS.
  - C syntax check for changed SDK files.
- [Expected Markers]:
  - `RedCap xApp priority hint`
  - `RedCap dApp PRB decision`

## Gate B: SWIG Evidence Boundary

- [Scope]: prove whether Python is backed by C/C++ binding.
- [Evidence]:
  - `dev_refer/dapp_dev_need/libe3/swig/libe3.i`
  - `dev_refer/dapp_dev_need/libe3/cmake/libe3SWIG.cmake`
  - `dev_refer/dapp_dev_need/dApp-library/libiqsaver/swig/iqsaver.i`
  - generated/importable modules only when built locally.
- [Limitation]: if generated modules are absent, status is definition-only, not SWIG runtime PASS.

## Gate C: E3 Loopback

- [Scope]: local RAN-role and DAPP-role E3 agents exchange data.
- [Reference Source]:
  - `dev_refer/dapp_dev_need/libe3/tests/integration/test_role_pair_posix.cpp`
  - `dev_refer/dapp_dev_need/libe3/tests/integration/bench_full_loop_latency.cpp`
- [Runner]:
  - `python3 -B agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/gate_c_e3_loopback_check.py`
- [Evidence]:
  - E3 setup success.
  - dApp indication receive marker.
  - dApp control/report send marker.
  - Optional latency table from `test_bench_full_loop_latency`.
- [Build Preconditions]:
  - `cmake`
  - C++17 compiler
  - `asn1c` (`/opt/asn1c/bin/asn1c` was detected in the current workspace)
  - cached or network-accessible `tl_expected` FetchContent source
- [Configure Evidence]:
  - `test_log/compiler_logs/gate_c_libe3_configure_2026-07-05_18-43-41.log`
  - `test_log/compiler_logs/gate_c_libe3_configure_fetch_2026-07-05_18-46-35.log`
  - `test_log/compiler_logs/gate_c_libe3_configure_local_expected_2026-07-06_11-56-12.log`
- [Build Evidence]:
  - `test_log/compiler_logs/gate_c_libe3_build_2026-07-06_11-56-12.log`
- [Runtime Evidence]:
  - `test_log/compiler_logs/gate_c_libe3_runtime_test_role_pair_posix_2026-07-06_11-58-08.log`
  - `test_log/compiler_logs/gate_c_libe3_runtime_test_bench_full_loop_latency_2026-07-06_11-58-23.log`
- [Latency Result]: POSIX IPC ASN.1 APER full-loop total round-trip p99 `183 us`, max `260 us`.
- [Caveat]: official `tl_expected` FetchContent remains unavailable; this Gate C PASS used the project-local `tl_expected` test shim.
- [Status]: PASS for local E3 POSIX loopback and latency evidence.

## Gate D: Small RFsim Marker

- [Scope]: 1-2 UE RFsim dApp/xApp marker validation.
- [Source Hook]:
  - gNB path: `openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_ulsch.c`
  - PUCCH path: `openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_uci.c`
  - Build path: `CMakeLists.txt` compiles `openair2/E3AP/sdk/redcap_dapp_sdk.c` into `MAC_NR_SRC`.
  - Runtime switch: `OAI_REDCAP_DAPP_GATE_D_MARKER=1`
  - Runtime env passthrough: `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/docker-compose.mmtc.yml` and `scripts/generate_mmtc_overlay.sh` expose `OAI_REDCAP_DAPP_GATE_D_MARKER` to the gNB container with default `0`.
  - ULSCH hook point: `post_process_ulsch()` calls the dApp PRB guard after `config_uldci()` and before `fill_dci_pdu_rel15()`.
  - PUCCH hook point: `nr_fill_nfapi_pucch()` calls the dApp PRB guard after `nr_configure_pucch()`.
- [dev_refer References]:
  - `dev_refer/dapp_dev_need/E3Controller/README.md` for `--num-prbs`, link layer, transport, and timing log shape.
  - `dev_refer/dapp_dev_need/E3Controller/src/e3sm/iq_pipeline.h` for per-section I/Q sample input.
  - `dev_refer/dapp_dev_need/E3Controller/src/e3sm/slot_iq_pipeline.h` for per-slot I/Q sample input.
  - `dev_refer/dapp_dev_need/dApp-library/README.md` for OpenRAN Gym dApp usage, `--num-prbs`, control, and visualization flags.
- [Source Readiness Runner]:
  - `python3 -B agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/gate_d_rfsim_marker_check.py`
- [Build Evidence]:
  - `test_log/build_logs/build_nr-softmodem_2026-07-06_gate-d-pucch-marker.log`
- [Runtime Runner]:
  - `python3 -B agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/gate_d_rfsim_marker_check.py --gnb-log <gNB-log-path> --require-runtime --require-bwp-prbs 5`
- [Evidence]:
  - UE attach/PDU health.
  - xApp priority hint marker.
  - dApp PRB decision marker.
  - gNB-side apply marker: `[RedCap dApp Gate D][gNB MAC UL] gNB-side apply marker`
  - gNB-side PUCCH marker: `[RedCap dApp Gate D][gNB MAC PUCCH] gNB-side PUCCH marker`
  - PDCCH command path marker from ULSCH `config_uldci()` / `fill_dci_pdu_rel15()` mapping `[Needs Verification: TS 38.212 Section 7.3.1.1 / TS 38.214 Section 6.1]`.
- [Limitation]: current hooks prove ULSCH/PUSCH/PDCCH and PUCCH FAPI marker paths. They do not yet implement dApp policy rewrite of PUCCH/PUSCH allocation.
- [Runtime Blocker]: local RedCap RFsim configs inspected in this pass expose 106/51 PRB carriers and RedCap initial BWP size 51; no ready 5 PRB BWP gNB config was found. Gate D runtime cannot pass the `--require-bwp-prbs 5` check until that config exists and the gNB image/container is rebuilt/recreated with `OAI_REDCAP_DAPP_GATE_D_MARKER=1`.
- [Status]: source hook readiness and `nr-softmodem` build PASS; RFsim runtime pending.

## Gate E: 56 UE / 5 PRB BWP Stress

- [Scope]: user-requested 56 RedCap UE scenario with 5 PRB BWP.
- [Evidence]:
  - attach/PDU health summary.
  - dApp/xApp marker sequence.
  - no gNB restart.
  - bounded control latency.
- [Limitation]: PUCCH resource exhaustion is a scheduler/config failure until proven otherwise.
- [Status]: pending Gate D PASS.
