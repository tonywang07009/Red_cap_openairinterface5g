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
- [x] 2.5 Add the dApp access-pressure policy helper in C and Python using the existing PRB allocation guard.

## 3. Documentation

- [x] 3.1 Add English API and usage documentation.
- [x] 3.2 Add Traditional Chinese API and usage documentation.
- [x] 3.3 Document Gate A-E acceptance evidence and runtime limitations.

## 4. Validation

- [x] 4.1 Run the new static checker.
- [x] 4.2 Run the new SDK contract self-test.
- [x] 4.3 Run OpenSpec validation for `redcap-dapp-xapp-sdk-test-validation`.
- [x] 4.4 Run targeted diff hygiene checks for the new artifacts.
- [x] 4.5 Run the dApp access-pressure policy self-tests and C syntax check.

## 5. Runtime Gates

- [x] 5.1 Run Gate C E3 loopback after the local E3 runtime is selected.
  - Runner selected: `agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/gate_c_e3_loopback_check.py`.
  - Configure evidence: `test_log/compiler_logs/gate_c_libe3_configure_2026-07-05_18-43-41.log`.
  - Fetch configure evidence: `test_log/compiler_logs/gate_c_libe3_configure_fetch_2026-07-05_18-46-35.log`.
  - Local-shim configure evidence: `test_log/compiler_logs/gate_c_libe3_configure_local_expected_2026-07-06_11-56-12.log`.
  - Build evidence: `test_log/compiler_logs/gate_c_libe3_build_2026-07-06_11-56-12.log`.
  - Runtime evidence: `test_log/compiler_logs/gate_c_libe3_runtime_test_role_pair_posix_2026-07-06_11-58-08.log`.
  - Latency evidence: `test_log/compiler_logs/gate_c_libe3_runtime_test_bench_full_loop_latency_2026-07-06_11-58-23.log`.
- [x] 5.2 Run Gate D small RFsim marker validation after dApp/xApp runtime hooks exist.
  - Source hook ready: `openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_ulsch.c`.
  - PUCCH marker hook ready: `openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_uci.c`.
  - Build wiring ready: `CMakeLists.txt` includes `openair2/E3AP/sdk/redcap_dapp_sdk.c` in `MAC_NR_SRC`.
  - Marker switch: `OAI_REDCAP_DAPP_GATE_D_MARKER=1`.
  - Compose env passthrough ready: `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/docker-compose.mmtc.yml` and `scripts/generate_mmtc_overlay.sh`.
  - 5 MHz BWP profile ready: `ci-scripts/conf_files/gnb.sa.band78.fr1.106PRB.usrpb210.redcap.5mhz-bwp.yaml`.
  - Readiness runner: `agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/gate_d_rfsim_marker_check.py`.
  - Build evidence: `test_log/build_logs/build_nr-softmodem_2026-07-06_gate-d-pucch-marker.log`.
  - DCI alignment build evidence: `test_log/build_logs/build_nr-softmodem_2026-07-06_17-28-49_gate-d-dci-bits.log` and `test_log/build_logs/build_nr-uesoftmodem_2026-07-06_17-29-03_gate-d-dci-bits.log`.
  - Runtime evidence: `test_log/runtime_logs/gate_d_5mhz_gnb_2026-07-06_17-16-57.log` and `test_log/runtime_logs/gate_d_5mhz_ue2_2026-07-06_17-16-57.log`.
  - Runtime observation: gNB and UE2 both show 12 PRB 5 MHz BWP profile application during RA/SIB1.
  - Root-cause observation: pre-fix runtime logs show gNB `dci_bits 35` and UE `dci_bits 39` for RedCap RA DCI.
  - Source fix: gNB and UE DCI sizing now use current 12 PRB DL BWP for RedCap Case B RA common DCI.
  - Local rebuild evidence: `test_log/build_logs/rebuild_local_oai_images_2026-07-07_00-35-33_dapp_access_pressure_policy.log`.
  - Post-rebuild local-image runtime evidence: `test_log/runtime_logs/gate_d_access_pressure_gnb_2026-07-07_00-47_local_no_csirs_srs.log` and `test_log/runtime_logs/gate_d_access_pressure_ue2_2026-07-07_00-47_local_no_csirs_srs.log`.
  - Runtime command used local images with `REGISTRY= TAG=latest GNB_IMG=oai-gnb NRUE_IMG=oai-nr-ue`.
  - Runtime workaround: `MMTC_GNB_EXTRA_OPTIONS="--gNBs.[0].do_CSIRS 0 --gNBs.[0].do_SRS 0"`.
  - Gate D checker PASS: `gate_d_rfsim_marker_check.py --require-runtime --require-bwp-mhz 5`.
  - gNB log contains both PUCCH Gate D marker and `RedCap dApp PRB decision` marker on the 12 PRB BWP.
  - Limitation: the same post-rebuild run with CSI-RS/SRS enabled hit `encode_cellGroupConfig()` on `nzp-CSI-RS-ResourceToAddModList`; this remains a separate follow-up before Gate E production-style stress claims.
- [ ] 5.3 Run Gate E 64 UE staged 5 MHz-to-20 MHz BWP stress validation after Gate D passes.
  - Preflight evidence: `generate_mmtc_overlay.sh 64` regenerated the RFsim mMTC overlay with UE1..UE64, and compose config confirms 64 `oai-nr-ue*` services.
  - Preflight evidence: the RFsim test topology uses `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/docker-compose.yml` plus `docker-compose.mmtc.yml`, and the CN/AMF topology uses `/home/tonywang/OAI/oai-cn5g/docker-compose.yaml` with `oai-amf`.
  - Preflight evidence: `generate_mmtc_cn_db_overlay.sh 64` generated `test_log/runtime_configs/oai_db_mmtc_64.sql` and `test_log/runtime_configs/oai-cn5g_mmtc_64.override.yml`.
  - Preflight evidence: `gate_e_64ue_stage_check.py` PASS for 64 UE service/config coverage, 5 MHz / 12 PRB first-stage profile, 51 PRB 20 MHz proxy profile `[Needs Verification]`, CN DB overlay, and prior Gate D marker evidence.
  - Source mitigation: `openair2/LAYER2/NR_MAC_gNB/nr_radio_config.c` now reuses a bounded PUCCH reservation index for initial and active 12 PRB BWPs and emits `[RedCap dApp Gate E][PUCCH pressure]` instead of aborting on oversubscription.
  - Build evidence: `cmake --build --preset default --target nr-softmodem` PASS, then `redcap_interface/redcap_rebuild_local_oai_images.sh` rebuilt `oai-gnb:latest` / `oai-nr-ue:latest`.
  - Post-rebuild first32 runtime evidence: `test_log/compiler_logs/mmtc_stage_scan_2026-07-07_11-11-52_summary.log` reports `sample=32 running=32 attach=0 pdu=0 tun=0 gnb_restart=0 failures=32`.
  - gNB evidence: `test_log/compiler_logs/mmtc_smoke_2026-07-07_11-11-52_gnb.log` contains `260` PUCCH-pressure markers and no assert/abort/segfault marker.
  - xApp/RIC evidence: `test_log/compiler_logs/mmtc_smoke_2026-07-07_11-11-52_xapp-rc-moni.log` and `..._nearrt-ric.log` contain E42 setup, RC subscriptions, and four RC Indications; no RIC Control request/ACK marker was observed.
  - DL TDA source mitigation: `openair2/LAYER2/NR_MAC_gNB/nr_radio_config.c` rebuilds the RedCap initial DL BWP PDSCH TDA list for the 12 PRB BWP instead of cloning the 106 PRB initial BWP TDA list.
  - DL TDA build evidence: `test_log/build_logs/build_nr-softmodem_2026-07-07_11-38-37_gate-e-redcap-tda.log`.
  - DL TDA image rebuild evidence: `test_log/build_logs/rebuild_local_oai_images_2026-07-07_11-39-43_gate-e-redcap-tda.log`.
  - Post-DL-TDA first32 runtime evidence: `test_log/compiler_logs/mmtc_stage_scan_2026-07-07_12-14-11_summary.log` reports `sample=32 running=32 attach=0 pdu=0 tun=0 gnb_restart=0 failures=32`.
  - gNB evidence: `test_log/compiler_logs/mmtc_smoke_2026-07-07_12-14-11_gnb.log` contains `2` `[RedCap RA][gNB DL TDA]` markers with `first_start_symbol 2`, `0` `Msg4 vrb_map fail` markers, and `32` Msg4 ACK markers.
  - UE evidence: UE1..UE32 each generated `RRCSetupComplete` once, but no UE registration/PDU/TUN evidence was produced.
  - Connected DCI BWP source mitigation: `openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_primitives.c` preserves RedCap initial DL/UL BWP start/size for connected DCI through `apply_redcap_initial_bwp_if_needed()`.
  - Connected DCI BWP source build evidence: `test_log/build_logs/build_nr-softmodem_2026-07-07_12-42-09_gate-e-redcap-dci-bwp_retry.log`.
  - Connected DCI BWP Docker image rebuild boundary: `test_log/build_logs/rebuild_local_oai_images_2026-07-07_12-42-46_gate-e-redcap-dci-bwp.log` failed with Docker socket permission denial, and escalation was rejected because workspace credits were exhausted; this boundary is superseded by the retry2 rebuild evidence below.
  - Connected DCI BWP Docker image rebuild evidence: `test_log/build_logs/rebuild_local_oai_images_2026-07-07_23-05-19_gate-e-redcap-dci-bwp_retry2_escalated.log`.
  - Post-DCI-BWP first32 runtime evidence: `test_log/compiler_logs/mmtc_stage_scan_2026-07-07_23-18-49_summary.log` reports `sample=32 running=32 attach=32 pdu=32 tun=32 forward_ping_ok=32 gnb_restart=0 failures=0`.
  - gNB evidence: `test_log/compiler_logs/mmtc_smoke_2026-07-07_23-18-49_gnb.log` contains `128` `[RedCap RA][gNB DCI BWP]` markers, `32` `Received RRCSetupComplete`, `32` `Received RRCReconfigurationComplete`, and `32` `PDU Session Setup: ID=10`.
  - dApp evidence: the same gNB log contains `34291` `[RedCap dApp Gate D][gNB MAC UL]` apply markers and `28` `[RedCap dApp Gate E][PUCCH pressure]` markers.
  - UE evidence: UE1..UE32 each generated `RRCSetupComplete`; no UE Docker log contains `TDA index from DCI 12`.
  - xApp/RIC Docker evidence: `test_log/compiler_logs/mmtc_smoke_2026-07-07_23-18-49_xapp-rc-moni.log` contains E42 setup, two RC subscriptions, `5` RC Indications, and `Test xApp run SUCCESSFULLY`; `test_log/compiler_logs/mmtc_smoke_2026-07-07_23-18-49_nearRT-RIC.log` contains E2 setup and RAN function 3 `ORAN-E2SM-RC`.
  - Control boundary: no RIC Control request/ACK marker was observed in xApp or nearRT-RIC Docker logs.
  - First32 checker PASS: `gate_e_64ue_stage_check.py --stage first32 --gnb-log test_log/compiler_logs/mmtc_smoke_2026-07-07_23-18-49_gnb.log --summary-log test_log/compiler_logs/mmtc_stage_scan_2026-07-07_23-18-49_summary.log`.
  - Full64 20 MHz proxy attempt report: `agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/report/gate_e_full64_20mhz_proxy_2026-07-07.md`.
  - Full64 20 MHz proxy summary log: `test_log/compiler_logs/mmtc_stage_scan_2026-07-07_23-39-18_summary.log` reports `sample=64 running=64 attach=0 pdu=0 tun=0 forward_ping_ok=0 gnb_restart=0 failures=64`.
  - Full64 20 MHz proxy gNB evidence: `test_log/compiler_logs/mmtc_smoke_2026-07-07_23-39-18_gnb.log` loaded the 51 PRB profile and reported the matching UE hint `-C 3617640000 -r 51 --numerology 1 --ssb 238 -E`.
  - Full64 20 MHz proxy UE evidence: UE1 runtime config used `N_RB_DL: 51`, but the UE command used `-C 3630360000 --ssb 144`; all 64 UE Docker logs contain `synch Failed`, and no UE generated `RRCSetupComplete`.
  - Full64 20 MHz proxy xApp/RIC evidence: `test_log/compiler_logs/mmtc_smoke_2026-07-07_23-39-18_xapp-rc-moni.log` and `test_log/compiler_logs/mmtc_smoke_2026-07-07_23-39-18_nearRT-RIC.log` show E42/E2 setup and RC subscription readiness, but no RIC Indication or RIC Control marker because no UE reached RRC.
  - Source fix: `redcap_interface/bash_library/fc_mmtc_smoke_validation.sh` now defaults the 51PRB profile to `MMTC_RF_FREQ=3617640000` and `MMTC_SSB_START=238` unless explicitly overridden.
  - Prepare-only evidence: `test_log/compiler_logs/mmtc_smoke_prepare_only_2026-07-07_51prb_rf_defaults.log` confirms 51PRB RF/SSB defaults and 64 UE overlay generation without Docker.
  - Runtime rerun boundary: post-fix Docker rerun was rejected because workspace credits were exhausted.
  - Runtime boundary: task remains open because the 64 UE / 20 MHz proxy stage and collision-load access-pressure effectiveness have not produced runtime evidence.
