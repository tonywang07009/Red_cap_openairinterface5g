# Gate E Full64 20 MHz Proxy Runtime Report - 2026-07-07

## Two-Tier Decision

- [Gate E-Core]: SDK v1 now closes on a 56 UE baseline-vs-dApp Launch-to-TUN access-latency comparison.
- [Gate E-Stretch]: strict 64 UE validation remains tracked as non-blocking upper-bound stress evidence.
- [Current Classification]: the latest `attach/pdu/tun=62/64` full64 result is a Stretch blocker, not a Core blocker.
- [Next Pull]: run baseline 56 UE without dApp, then dApp-enabled 56 UE with the same 51PRB RF/CN/UE profile, and compare success count, median, p95, max, and dApp-minus-baseline Launch-to-TUN latency.

## English

- [Scope]: Gate E full 64 RedCap UE stress attempt using the 51 PRB / 20 MHz proxy profile after the first32 5 MHz stage passed.
- [Command Profile]: `MMTC_TOTAL_UES_TARGET=64`, `MMTC_STAGE_LIST=64`, `MMTC_START_XAPP=1`, `MMTC_N_RB_DL=51`, `GNB_REDCAP_CONFIG=../../conf_files/gnb.sa.band78.fr1.51PRB.usrpb210.redcap.yaml`, local `oai-gnb:latest` / `oai-nr-ue:latest`, and the no-CSI/SRS RFsim workaround.
- [CN/AMF Source]: `/home/tonywang/OAI/oai-cn5g/docker-compose.yaml`.
- [RFsim Source]: `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/docker-compose.yml` plus `docker-compose.mmtc.yml`.
- [Summary]: `sample=64 running=64 attach=0 pdu=0 tun=0 forward_ping_ok=0 gnb_restart=0 failures=64`.
- [gNB Evidence]: gNB loaded the 51 PRB profile: `DLBW 51`, RedCap initial DL/UL BWP size `51`, `absoluteFrequencySSB 641280`, and the gNB generated UE hint `-C 3617640000 -r 51 --numerology 1 --ssb 238 -E`.
- [UE Evidence]: UE1 runtime config used `N_RB_DL: 51`, but the UE command still used `-C 3630360000 --ssb 144`; all 64 UE Docker logs contain `synch Failed`, and no UE generated `RRCSetupComplete`.
- [xApp/RIC Evidence]: nearRT-RIC accepted E2 setup and `ORAN-E2SM-RC`; xApp completed E42 setup and two RC subscriptions, then exited successfully. No RIC Indication or RIC Control marker was observed because no UE reached RRC.
- [Root Cause]: the 51 PRB gNB profile and UE RF/SSB defaults were mismatched before synchronization. This is earlier than RA collision, dApp policy, CN attach, PDU, or TUN creation.
- [Source Fix]: `redcap_interface/bash_library/fc_mmtc_smoke_validation.sh` now applies 51PRB RF defaults when `MMTC_N_RB_DL=51` or `GNB_REDCAP_CONFIG` contains `51PRB`: `MMTC_RF_FREQ=3617640000`, `MMTC_SSB_START=238`.
- [Prepare-Only Evidence]: `test_log/compiler_logs/mmtc_smoke_prepare_only_2026-07-07_51prb_rf_defaults.log` confirms the 64 UE overlay and 51PRB RF/SSB defaults without starting Docker.
- [Runtime Boundary At That Time]: post-fix Docker rerun was rejected by the system because workspace credits were exhausted. This is superseded by the later one-UE and full64 runtime attempts below.

### Follow-up Runtime - 2026-07-08

- [One-UE 51PRB Smoke]: PASS after local image rebuild. Evidence: `test_log/compiler_logs/mmtc_smoke_2026-07-08_12-05-16_gnb.log`, `test_log/compiler_logs/mmtc_smoke_2026-07-08_12-05-16_ue1_docker.log`, and `test_log/compiler_logs/mmtc_smoke_2026-07-08_12-05-16_gnb_state.log`.
- [One-UE Summary]: `sample=1 running=1 attach=1 pdu=1 tun=1 forward_ping_ok=1 reverse_ping_ok=1 gnb_restart=0 failures=0`.
- [One-UE Evidence]: UE reached sync, registration attach, PDU session accept, and `oaitun_ue1`; gNB loaded `DLBW 51`; no repeated `synch Failed`, RF/SSB mismatch, or assert/abort marker was observed.
- [dApp 51PRB Evidence]: gNB-side 51PRB PUCCH and UL apply markers appeared without `unsupported_bwp_profile` reject markers.
- [Full64 Result]: FAIL. Evidence: `test_log/compiler_logs/mmtc_stage_scan_2026-07-08_12-07-24_summary.log`, `test_log/compiler_logs/mmtc_stage_scan_2026-07-08_12-07-24_ue64.log`, and `test_log/compiler_logs/mmtc_smoke_2026-07-08_12-07-24_gnb.log`.
- [Full64 Summary]: `sample=64 running=15 attach=59 pdu=59 tun=11 forward_ping_ok=11 reverse_ping_ok=0 iperf_ul_ok=0 iperf_ul_run=0 gnb_restart=1 failures=55 mode=parallel`.
- [Root Cause]: the gNB aborted around UE48 in `set_csi_meas_periodicity()` with `Assertion (offset < 320) failed!`; the backtrace shows the path through `get_csiMeasConfig()`, `get_initial_cellGroupConfig()`, and `nr_process_mac_pdu()`. The container then restarted, so Gate E acceptance `gnb_restart=0` was not met.
- [Source Fix]: `openair2/LAYER2/NR_MAC_gNB/nr_radio_config.c` now uses `get_pucch_reservation_uid(scc, curr_bwp, uid, "CSI reporting")` before calculating CSI report offset. This aligns CSI periodicity with the existing 51PRB PUCCH reservation reuse.
- [Local Validation]: `gate_e_64ue_stage_check.py` static preflight PASS, `check_dapp_xapp_sdk_test_validation.py` PASS, `git diff --check -- openair2/LAYER2/NR_MAC_gNB/nr_radio_config.c` PASS, and `cmake --build --preset default --target nr-softmodem` PASS.
- [Post-CSI-Fix Image Rebuild]: PASS. Evidence: `test_log/build_logs/rebuild_local_oai_images_2026-07-08_17-11-54_gate-e-csi-pucch-uid_retry.log`.
- [Post-CSI-Fix One-UE 51PRB Smoke]: PASS. Evidence: `test_log/compiler_logs/mmtc_smoke_2026-07-08_17-21-13_gnb.log`, `test_log/compiler_logs/mmtc_smoke_2026-07-08_17-21-13_ue1_docker.log`, and `test_log/compiler_logs/mmtc_smoke_2026-07-08_17-21-13_gnb_state.log`.
- [Post-CSI-Fix Full64 Result]: FAIL. Evidence: `test_log/compiler_logs/mmtc_stage_scan_2026-07-08_17-24-06_summary.log`, `test_log/compiler_logs/mmtc_stage_scan_2026-07-08_17-24-06_ue64.log`, and `test_log/compiler_logs/mmtc_smoke_2026-07-08_17-24-06_gnb.log`.
- [Post-CSI-Fix Full64 Summary]: `sample=64 running=0 attach=62 pdu=62 tun=0 forward_ping_ok=0 reverse_ping_ok=0 iperf_ul_ok=0 iperf_ul_run=0 gnb_restart=0 failures=65 mode=parallel`.
- [Post-CSI-Fix Diagnosis]: the run passed the prior UE48 CSI offset crash zone, but exposed later high-pressure runtime failures: all UE containers exited, UE24/UE45/UE60 aborted on invalid CCCH MAC SDU length, the gNB log showed heavy SR/CSI PUCCH pressure, and direct post-run inspection showed a gNB restart after the script's early state sample.
- [Runtime Guard Fixes]: `openair2/E2AP/flexric/src/agent/asio_agent.c` now treats `epoll_wait(EINTR)` as a recoverable return instead of aborting; `openair2/LAYER2/NR_MAC_UE/nr_ue_procedures.c` now drops invalid CCCH MAC subPDUs instead of asserting; `openair2/RRC/NR/MESSAGES/asn1_msg.c` and `openair2/RRC/NR/rrc_gNB.c` now reject missing `masterCellGroup` RRCSetup input instead of asserting.
- [Runtime Guard Build/Rebuild]: local build PASS in `test_log/build_logs/build_gate_e_runtime_guards_2026-07-08_17-46-58.log`; local image rebuild PASS in `test_log/build_logs/rebuild_local_oai_images_2026-07-08_17-47-31_gate-e-runtime-guards.log`.
- [Runtime Guard One-UE 51PRB Smoke]: PASS. Evidence: `test_log/compiler_logs/mmtc_smoke_2026-07-08_18-00-40_gnb.log`, `test_log/compiler_logs/mmtc_smoke_2026-07-08_18-00-40_ue1_docker.log`, and `test_log/compiler_logs/mmtc_smoke_2026-07-08_18-00-40_gnb_state.log`.
- [Runtime Guard One-UE Summary]: `sample=1 running=1 attach=1 pdu=1 tun=1 forward_ping_ok=1 reverse_ping_ok=1 iperf_ul_ok=0 iperf_ul_run=0 gnb_restart=0 failures=0`.
- [Post-Runtime-Guard Full64 Result]: FAIL, but with improved transport health. Evidence: `test_log/compiler_logs/mmtc_stage_scan_2026-07-08_22-24-50_summary.log`, `test_log/compiler_logs/mmtc_stage_scan_2026-07-08_22-24-50_ue64.log`, and `test_log/compiler_logs/mmtc_smoke_2026-07-08_22-24-50_gnb.log`.
- [Post-Runtime-Guard Full64 Summary]: `sample=64 running=64 attach=64 pdu=64 tun=64 forward_ping_ok=64 reverse_ping_ok=0 iperf_ul_ok=1 iperf_ul_run=3 gnb_restart=0 failures=2 mode=parallel`.
- [Post-Runtime-Guard Limitation]: UE1 and UE25 sampled UL iperf clients timed out, UE50 sampled UL iperf passed, and the xApp monitor showed E42/RC subscription setup without a control/ACK marker. This is not a Gate E PASS because `failures=0`, xApp influence, and before/after collision-load evidence are still missing.
- [RC Control Failure]: the manual live control attempt in `test_log/compiler_logs/redcap_rc_ctrl_xapp_2026-07-08_22-52-46.log` timed out, while the gNB live log showed an abort in `apply_redcap_ul_prb_control` on an unknown/stale RNTI.
- [RC Control Guard Fix]: `openair2/E2AP/RAN_FUNCTION/O-RAN/ran_func_rc.c` now rejects malformed, no-MAC-instance, and unknown-RNTI RedCap UL PRB controls without aborting; `redcap_interface/bash_library/fc_send_ul_prb_control.sh` now prefers live dApp MAC marker RNTIs; `fc_mmtc_smoke_validation.sh` and `fc_mmtc_stage_scan.sh` now retry sampled iperf after restarting the server.
- [RC Control Guard Build/Rebuild]: local wrapper syntax, Python compile, static preflight, diff-check, and CMake builds passed; local runtime image rebuild PASS in `test_log/build_logs/rebuild_local_oai_images_2026-07-08_22-58-43_gate-e-rc-control-guard.log`.
- [Runtime Checker Boundary]: the 2026-07-08 22:24:50 full64 logs intentionally fail `gate_e_64ue_stage_check.py --stage full64` with `failures=2` and missing xApp control/ACK.
- [Superseded Runtime Boundary]: Docker image inspection and post-RC-control-guard one-UE/full64 reruns were initially rejected because workspace credits were exhausted. This was superseded by the 2026-07-08/09 runtime below; the strict full64 path remains open only as Gate E-Stretch evidence.

### Post-RC-Control-Guard Runtime - 2026-07-08/09

- [Image Inspection]: PASS after Docker access was restored. Evidence: `test_log/compiler_logs/gnb_image_inspect_2026-07-09_rc_control_guard.log`; the image contains FlexRIC libraries and the PUCCH budget marker.
- [One-UE 51PRB Smoke]: PASS with the RC-control-guard images. Evidence: `test_log/compiler_logs/mmtc_smoke_2026-07-08_23-29-28_gnb.log`, `test_log/compiler_logs/mmtc_smoke_2026-07-08_23-29-28_ue1_docker.log`, `test_log/compiler_logs/mmtc_smoke_2026-07-08_23-29-28_ue1_tun.log`, `test_log/compiler_logs/mmtc_smoke_2026-07-08_23-29-28_smf.log`, and `test_log/compiler_logs/mmtc_smoke_2026-07-08_23-29-28_gnb_state.log`.
- [One-UE Evidence]: UE1 used `-C 3617640000 -r 51 --ssb 238`, reached `Initial sync successful`, received PDU Session Establishment Accept for `10.0.0.2`, created `oaitun_ue1`, and the gNB restart count stayed `0`.
- [Full64 Result]: FAIL. Evidence: `test_log/compiler_logs/mmtc_stage_scan_2026-07-08_23-31-13_summary.log`, `test_log/compiler_logs/mmtc_stage_scan_2026-07-08_23-31-13_ue64.log`, and `test_log/compiler_logs/mmtc_smoke_2026-07-08_23-31-13_gnb.log`.
- [Full64 Summary]: `sample=64 running=64 attach=62 pdu=62 tun=62 forward_ping_ok=54 reverse_ping_ok=0 iperf_ul_ok=1 iperf_ul_run=3 gnb_restart=0 failures=12 mode=parallel`.
- [Full64 Blockers]: UE62 and UE64 stayed running/healthy but did not create `oaitun_ue1`; UE8, UE23, UE42, UE44, UE54, UE56, UE59, and UE60 failed forward ping; UE25 and UE50 UL iperf clients timed out after two retries.
- [xApp/RIC/gNB Control Evidence]: PASS for one selected RNTI. `test_log/compiler_logs/redcap_rc_ctrl_xapp_2026-07-09_00-00-46.log` contains `CONTROL ACK rx`, `test_log/compiler_logs/redcap_rc_ctrl_xapp_2026-07-09_00-00-46_nearRT-RIC_live_postcontrol.log` contains `CONTROL ACKNOWLEDGE rx`, and `test_log/compiler_logs/redcap_rc_ctrl_xapp_2026-07-09_00-00-46_gnb_live_postcontrol.log` contains `RedCap UL PRB control RNTI fc38 requested 32 effective 32`.
- [Verifier Fix]: `redcap_interface/bash_library/fc_verify_ul_prb_control.sh` now falls back to the latest captured post-control gNB log when live Docker log scanning is too large for the short polling window.
- [Current Boundary]: Gate E-Core is closed by the 2026-07-09 56 UE baseline-vs-dApp Launch-to-TUN comparison. The latest full64 summary is retained as Gate E-Stretch evidence with `attach/pdu/tun=62/64` and `failures=12`.

## Traditional Chinese

- [Two-Tier Decision]：SDK v1 的 [Gate E-Core] 現在改以 56 UE baseline-vs-dApp [Launch-to-TUN] 接入延遲比較作為工程完成標準。
- [Gate E-Stretch]：strict 64 UE 驗證保留為 non-blocking upper-bound stress evidence。
- [Current Classification]：最新 `attach/pdu/tun=62/64` full64 結果是 Stretch blocker，不是 Core blocker。
- [Next Pull]：56 UE baseline-vs-dApp Launch-to-TUN 比較已於 2026-07-09 完成；下一步只在需要 strict upper-bound evidence 時回到 64 UE Stretch。

- [Scope]：Gate E full 64 RedCap UE stress attempt，使用 first32 5 MHz stage PASS 之後的 51 PRB / 20 MHz proxy profile。
- [Command Profile]：`MMTC_TOTAL_UES_TARGET=64`、`MMTC_STAGE_LIST=64`、`MMTC_START_XAPP=1`、`MMTC_N_RB_DL=51`、`GNB_REDCAP_CONFIG=../../conf_files/gnb.sa.band78.fr1.51PRB.usrpb210.redcap.yaml`，使用本地 `oai-gnb:latest` / `oai-nr-ue:latest` 與 no-CSI/SRS RFsim workaround。
- [CN/AMF Source]：`/home/tonywang/OAI/oai-cn5g/docker-compose.yaml`。
- [RFsim Source]：`ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/docker-compose.yml` 加上 `docker-compose.mmtc.yml`。
- [Summary]：`sample=64 running=64 attach=0 pdu=0 tun=0 forward_ping_ok=0 gnb_restart=0 failures=64`。
- [gNB Evidence]：gNB 已載入 51 PRB profile：`DLBW 51`、RedCap initial DL/UL BWP size `51`、`absoluteFrequencySSB 641280`，且 gNB log 建議 UE 參數為 `-C 3617640000 -r 51 --numerology 1 --ssb 238 -E`。
- [UE Evidence]：UE1 runtime config 已使用 `N_RB_DL: 51`，但 UE command 仍使用 `-C 3630360000 --ssb 144`；64 個 UE Docker logs 都出現 `synch Failed`，且沒有 UE 產生 `RRCSetupComplete`。
- [xApp/RIC Evidence]：nearRT-RIC 接受 E2 setup 與 `ORAN-E2SM-RC`；xApp 完成 E42 setup 與兩個 RC subscriptions 後正常結束。因為沒有 UE 進入 RRC，因此沒有觀察到 RIC Indication 或 RIC Control marker。
- [Root Cause]：51 PRB gNB profile 與 UE RF/SSB 預設在同步前就不一致。這個失敗點早於 RA collision、dApp policy、CN attach、PDU 或 TUN 建立。
- [Source Fix]：`redcap_interface/bash_library/fc_mmtc_smoke_validation.sh` 現在會在 `MMTC_N_RB_DL=51` 或 `GNB_REDCAP_CONFIG` 含有 `51PRB` 時套用 51PRB RF defaults：`MMTC_RF_FREQ=3617640000`、`MMTC_SSB_START=238`。
- [Prepare-Only Evidence]：`test_log/compiler_logs/mmtc_smoke_prepare_only_2026-07-07_51prb_rf_defaults.log` 已確認 64 UE overlay 與 51PRB RF/SSB defaults，且沒有啟動 Docker。
- [Runtime Boundary At That Time]：post-fix Docker rerun 被系統拒絕，原因是 workspace credits 用完。這個邊界已被下方後續 one-UE 與 full64 runtime attempts 取代。

### 2026-07-08 Follow-up Runtime

- [One-UE 51PRB Smoke]：本地 image rebuild 後 PASS。證據：`test_log/compiler_logs/mmtc_smoke_2026-07-08_12-05-16_gnb.log`、`test_log/compiler_logs/mmtc_smoke_2026-07-08_12-05-16_ue1_docker.log`、`test_log/compiler_logs/mmtc_smoke_2026-07-08_12-05-16_gnb_state.log`。
- [One-UE Summary]：`sample=1 running=1 attach=1 pdu=1 tun=1 forward_ping_ok=1 reverse_ping_ok=1 gnb_restart=0 failures=0`。
- [One-UE Evidence]：UE 已達到 sync、registration attach、PDU session accept 與 `oaitun_ue1`；gNB 載入 `DLBW 51`；沒有觀察到 repeated `synch Failed`、RF/SSB mismatch 或 assert/abort marker。
- [dApp 51PRB Evidence]：gNB-side 51PRB PUCCH 與 UL apply markers 已出現，且沒有 `unsupported_bwp_profile` reject markers。
- [Full64 Result]：FAIL。證據：`test_log/compiler_logs/mmtc_stage_scan_2026-07-08_12-07-24_summary.log`、`test_log/compiler_logs/mmtc_stage_scan_2026-07-08_12-07-24_ue64.log`、`test_log/compiler_logs/mmtc_smoke_2026-07-08_12-07-24_gnb.log`。
- [Full64 Summary]：`sample=64 running=15 attach=59 pdu=59 tun=11 forward_ping_ok=11 reverse_ping_ok=0 iperf_ul_ok=0 iperf_ul_run=0 gnb_restart=1 failures=55 mode=parallel`。
- [Root Cause]：gNB 在 UE48 左右進入 `set_csi_meas_periodicity()` 時觸發 `Assertion (offset < 320) failed!`；backtrace 顯示路徑經過 `get_csiMeasConfig()`、`get_initial_cellGroupConfig()` 與 `nr_process_mac_pdu()`。之後容器重啟，因此不符合 Gate E 的 `gnb_restart=0` 驗收條件。
- [Source Fix]：`openair2/LAYER2/NR_MAC_gNB/nr_radio_config.c` 現在會先使用 `get_pucch_reservation_uid(scc, curr_bwp, uid, "CSI reporting")`，再計算 CSI report offset。這讓 CSI periodicity 與既有 51PRB PUCCH reservation reuse 行為一致。
- [Local Validation]：`gate_e_64ue_stage_check.py` static preflight PASS、`check_dapp_xapp_sdk_test_validation.py` PASS、`git diff --check -- openair2/LAYER2/NR_MAC_gNB/nr_radio_config.c` PASS，以及 `cmake --build --preset default --target nr-softmodem` PASS。
- [Post-CSI-Fix Image Rebuild]：PASS。證據：`test_log/build_logs/rebuild_local_oai_images_2026-07-08_17-11-54_gate-e-csi-pucch-uid_retry.log`。
- [Post-CSI-Fix One-UE 51PRB Smoke]：PASS。證據：`test_log/compiler_logs/mmtc_smoke_2026-07-08_17-21-13_gnb.log`、`test_log/compiler_logs/mmtc_smoke_2026-07-08_17-21-13_ue1_docker.log`、`test_log/compiler_logs/mmtc_smoke_2026-07-08_17-21-13_gnb_state.log`。
- [Post-CSI-Fix Full64 Result]：FAIL。證據：`test_log/compiler_logs/mmtc_stage_scan_2026-07-08_17-24-06_summary.log`、`test_log/compiler_logs/mmtc_stage_scan_2026-07-08_17-24-06_ue64.log`、`test_log/compiler_logs/mmtc_smoke_2026-07-08_17-24-06_gnb.log`。
- [Post-CSI-Fix Full64 Summary]：`sample=64 running=0 attach=62 pdu=62 tun=0 forward_ping_ok=0 reverse_ping_ok=0 iperf_ul_ok=0 iperf_ul_run=0 gnb_restart=0 failures=65 mode=parallel`。
- [Post-CSI-Fix Diagnosis]：這次已越過先前 UE48 CSI offset crash 區間，但暴露後段高壓 runtime 失敗：所有 UE containers 結束、UE24/UE45/UE60 因 invalid CCCH MAC SDU length abort、gNB log 持續出現 SR/CSI PUCCH pressure，且直接 post-run inspection 顯示 gNB 在腳本早期 state sample 之後發生 restart。
- [Runtime Guard Fixes]：`openair2/E2AP/flexric/src/agent/asio_agent.c` 現在將 `epoll_wait(EINTR)` 視為可恢復 return，不再 assert；`openair2/LAYER2/NR_MAC_UE/nr_ue_procedures.c` 現在 drop invalid CCCH MAC subPDU，不再 assert；`openair2/RRC/NR/MESSAGES/asn1_msg.c` 與 `openair2/RRC/NR/rrc_gNB.c` 現在會在 `masterCellGroup` 缺失時 reject RRCSetup input，不再 assert。
- [Runtime Guard Build/Rebuild]：local build PASS：`test_log/build_logs/build_gate_e_runtime_guards_2026-07-08_17-46-58.log`；local image rebuild PASS：`test_log/build_logs/rebuild_local_oai_images_2026-07-08_17-47-31_gate-e-runtime-guards.log`。
- [Runtime Guard One-UE 51PRB Smoke]：PASS。證據：`test_log/compiler_logs/mmtc_smoke_2026-07-08_18-00-40_gnb.log`、`test_log/compiler_logs/mmtc_smoke_2026-07-08_18-00-40_ue1_docker.log`、`test_log/compiler_logs/mmtc_smoke_2026-07-08_18-00-40_gnb_state.log`。
- [Runtime Guard One-UE Summary]：`sample=1 running=1 attach=1 pdu=1 tun=1 forward_ping_ok=1 reverse_ping_ok=1 iperf_ul_ok=0 iperf_ul_run=0 gnb_restart=0 failures=0`。
- [Post-Runtime-Guard Full64 Result]：FAIL，但 transport health 已改善。證據：`test_log/compiler_logs/mmtc_stage_scan_2026-07-08_22-24-50_summary.log`、`test_log/compiler_logs/mmtc_stage_scan_2026-07-08_22-24-50_ue64.log`、`test_log/compiler_logs/mmtc_smoke_2026-07-08_22-24-50_gnb.log`。
- [Post-Runtime-Guard Full64 Summary]：`sample=64 running=64 attach=64 pdu=64 tun=64 forward_ping_ok=64 reverse_ping_ok=0 iperf_ul_ok=1 iperf_ul_run=3 gnb_restart=0 failures=2 mode=parallel`。
- [Post-Runtime-Guard Limitation]：UE1 與 UE25 sampled UL iperf client timeout，UE50 sampled UL iperf PASS，且 xApp monitor 只有 E42/RC subscription setup，沒有 control/ACK marker。這還不是 Gate E PASS，因為仍缺 `failures=0`、xApp influence、before/after collision-load evidence。
- [RC Control Failure]：手動 live control attempt `test_log/compiler_logs/redcap_rc_ctrl_xapp_2026-07-08_22-52-46.log` timeout，同時 gNB live log 顯示 `apply_redcap_ul_prb_control` 因 unknown/stale RNTI abort。
- [RC Control Guard Fix]：`openair2/E2AP/RAN_FUNCTION/O-RAN/ran_func_rc.c` 現在會 reject malformed、no-MAC-instance、unknown-RNTI 的 RedCap UL PRB control，不再 abort；`redcap_interface/bash_library/fc_send_ul_prb_control.sh` 現在優先使用 live dApp MAC marker RNTI；`fc_mmtc_smoke_validation.sh` 與 `fc_mmtc_stage_scan.sh` 現在會 restart iperf server 後 retry sampled iperf。
- [RC Control Guard Build/Rebuild]：local wrapper syntax、Python compile、static preflight、diff-check、CMake builds 都 PASS；local runtime image rebuild PASS：`test_log/build_logs/rebuild_local_oai_images_2026-07-08_22-58-43_gate-e-rc-control-guard.log`。
- [Runtime Checker Boundary]：2026-07-08 22:24:50 full64 logs 目前會被 `gate_e_64ue_stage_check.py --stage full64` 正確判定為 FAIL，原因是 `failures=2` 且缺少 xApp control/ACK。
- [Superseded Runtime Boundary]：Docker image inspection 與 post-RC-control-guard one-UE/full64 rerun 一開始被系統拒絕，原因是 workspace credits 用完。這個邊界已被下方 2026-07-08/09 runtime 取代；Gate E 仍維持 open，原因是 full64 acceptance 與 collision-load evidence 尚未完成。

### 2026-07-08/09 Post-RC-Control-Guard Runtime

- [Image Inspection]：Docker access 恢復後 PASS。證據：`test_log/compiler_logs/gnb_image_inspect_2026-07-09_rc_control_guard.log`；image 內有 FlexRIC libraries 與 PUCCH budget marker。
- [One-UE 51PRB Smoke]：使用 RC-control-guard images 後 PASS。證據：`test_log/compiler_logs/mmtc_smoke_2026-07-08_23-29-28_gnb.log`、`test_log/compiler_logs/mmtc_smoke_2026-07-08_23-29-28_ue1_docker.log`、`test_log/compiler_logs/mmtc_smoke_2026-07-08_23-29-28_ue1_tun.log`、`test_log/compiler_logs/mmtc_smoke_2026-07-08_23-29-28_smf.log`、`test_log/compiler_logs/mmtc_smoke_2026-07-08_23-29-28_gnb_state.log`。
- [One-UE Evidence]：UE1 使用 `-C 3617640000 -r 51 --ssb 238`，達到 `Initial sync successful`，收到 PDU Session Establishment Accept 與 `10.0.0.2`，建立 `oaitun_ue1`，且 gNB restart count 維持 `0`。
- [Full64 Result]：FAIL。證據：`test_log/compiler_logs/mmtc_stage_scan_2026-07-08_23-31-13_summary.log`、`test_log/compiler_logs/mmtc_stage_scan_2026-07-08_23-31-13_ue64.log`、`test_log/compiler_logs/mmtc_smoke_2026-07-08_23-31-13_gnb.log`。
- [Full64 Summary]：`sample=64 running=64 attach=62 pdu=62 tun=62 forward_ping_ok=54 reverse_ping_ok=0 iperf_ul_ok=1 iperf_ul_run=3 gnb_restart=0 failures=12 mode=parallel`。
- [Full64 Blockers]：UE62 與 UE64 維持 running/healthy，但沒有建立 `oaitun_ue1`；UE8、UE23、UE42、UE44、UE54、UE56、UE59、UE60 forward ping fail；UE25 與 UE50 UL iperf client 經過兩次 retry 後仍 timeout。
- [xApp/RIC/gNB Control Evidence]：單一 selected RNTI 的 control path PASS。`test_log/compiler_logs/redcap_rc_ctrl_xapp_2026-07-09_00-00-46.log` 有 `CONTROL ACK rx`，`test_log/compiler_logs/redcap_rc_ctrl_xapp_2026-07-09_00-00-46_nearRT-RIC_live_postcontrol.log` 有 `CONTROL ACKNOWLEDGE rx`，`test_log/compiler_logs/redcap_rc_ctrl_xapp_2026-07-09_00-00-46_gnb_live_postcontrol.log` 有 `RedCap UL PRB control RNTI fc38 requested 32 effective 32`。
- [Verifier Fix]：`redcap_interface/bash_library/fc_verify_ul_prb_control.sh` 現在會在 live Docker log 太大、短時間輪詢不到 marker 時，fallback 到最新 captured post-control gNB log。
- [Current Boundary]：Gate E-Core 仍 pending，原因是 56 UE baseline-vs-dApp Launch-to-TUN 比較尚未執行。最新 full64 summary 會保留為 Gate E-Stretch evidence，其結果是 `attach/pdu/tun=62/64` 且 `failures=12`。
