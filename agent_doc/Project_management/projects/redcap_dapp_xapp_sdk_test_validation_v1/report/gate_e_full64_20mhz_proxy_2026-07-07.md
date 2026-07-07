# Gate E Full64 20 MHz Proxy Runtime Report - 2026-07-07

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
- [Runtime Boundary]: post-fix Docker rerun was rejected by the system because workspace credits were exhausted. Gate E remains open until a one-UE 51PRB smoke and then the full 64 UE / 20 MHz proxy stage pass with runtime logs.

## Traditional Chinese

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
- [Runtime Boundary]：post-fix Docker rerun 被系統拒絕，原因是 workspace credits 用完。Gate E 必須等一個 UE 的 51PRB smoke 與 full 64 UE / 20 MHz proxy stage 都有 runtime logs 後才能關閉。
