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
  - 5 MHz BWP profile: `ci-scripts/conf_files/gnb.sa.band78.fr1.106PRB.usrpb210.redcap.5mhz-bwp.yaml` keeps the 106 PRB RF carrier and configures BWP1 plus RedCap DL/UL initial BWP as 12 PRBs at 30 kHz SCS `[Needs Verification]`.
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
  - `test_log/build_logs/build_nr-softmodem_2026-07-06_17-28-49_gate-d-dci-bits.log`
  - `test_log/build_logs/build_nr-uesoftmodem_2026-07-06_17-29-03_gate-d-dci-bits.log`
- [Runtime Runner]:
  - `cd ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap`
  - `GNB_REDCAP_CONFIG=../../conf_files/gnb.sa.band78.fr1.106PRB.usrpb210.redcap.5mhz-bwp.yaml MMTC_N_RB_DL=106 OAI_REDCAP_DAPP_GATE_D_MARKER=1 docker compose -f docker-compose.yml -f docker-compose.mmtc.yml up -d oai-gnb oai-nr-ue2`
  - `python3 -B agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/gate_d_rfsim_marker_check.py --gnb-log <gNB-log-path> --ue-log <UE-log-path> --require-runtime --require-bwp-mhz 5`
- [Runtime Evidence 2026-07-06]:
  - gNB log: `test_log/runtime_logs/gate_d_5mhz_gnb_2026-07-06_17-16-57.log`.
  - UE2 log: `test_log/runtime_logs/gate_d_5mhz_ue2_2026-07-06_17-16-57.log`.
  - gNB observed `[RedCap RA][gNB Msg2 BWP selected]` with `dl_bwp_size 12` and `ul_bwp_size 12`.
  - gNB observed `[RedCap RA][gNB Msg2 DCI]` with `bwp_size 12`.
  - UE2 observed `SIB1 RedCap initial BWP decision` and applied DL/UL BWP size `12`.
  - Old-log root cause: gNB RedCap Msg2 DCI used `dci_bits 35`, while UE RedCap RA DCI config expected `dci_bits 39`.
  - Source fix: `openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_RA.c` and `openair2/LAYER2/NR_MAC_UE/nr_ue_dci_configuration.c` now use current DL BWP size for RedCap Case B RA common DCI sizing.
  - Gate D checker still exits non-zero because the log lacks `[RedCap dApp Gate D][gNB MAC UL]` and `[RedCap dApp Gate D][gNB MAC PUCCH]`.
- [Evidence]:
  - UE attach/PDU health.
  - xApp priority hint marker.
  - dApp PRB decision marker.
  - gNB-side apply marker: `[RedCap dApp Gate D][gNB MAC UL] gNB-side apply marker`
  - gNB-side PUCCH marker: `[RedCap dApp Gate D][gNB MAC PUCCH] gNB-side PUCCH marker`
  - PDCCH command path marker from ULSCH `config_uldci()` / `fill_dci_pdu_rel15()` mapping `[Needs Verification: TS 38.212 Section 7.3.1.1 / TS 38.214 Section 6.1]`.
- [Limitation]: current hooks prove ULSCH/PUSCH/PDCCH and PUCCH FAPI marker paths. They do not yet implement dApp policy rewrite of PUCCH/PUSCH allocation.
- [Runtime Blocker]: post-fix Docker image rebuild/RFsim recreate was rejected because workspace credits are unavailable. The old runtime remains useful only as failure evidence; it must not be treated as post-fix validation.
- [Status]: source hook readiness, 5 MHz BWP profile readiness, gNB/UE build PASS, and pre-fix 5 MHz RA/SIB1 failure evidence are present; post-fix Gate D dApp marker validation remains pending.

## Gate E: 56 UE / 5 MHz BWP Stress

- [Scope]: user-requested 56 RedCap UE scenario with 5 MHz BWP switching/profile validation.
- [Evidence]:
  - attach/PDU health summary.
  - dApp/xApp marker sequence.
  - no gNB restart.
  - bounded control latency.
- [Limitation]: PUCCH resource exhaustion is a scheduler/config failure until proven otherwise.
- [Status]: pending Gate D PASS.
