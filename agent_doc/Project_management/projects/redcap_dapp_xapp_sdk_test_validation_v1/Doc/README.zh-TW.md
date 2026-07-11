# RedCap dApp/xApp SDK 測試驗證

## Scope

- 本頁說明 RedCap dApp/xApp SDK slice 的測試方式。
- 主要參考來源是 `dev_refer/`。
- 靜態檢查不代表 64 UE / staged 5 MHz-to-20 MHz BWP runtime PASS。

## SDK routes

| 需求 | 檔案 |
|---|---|
| 場景、API 行為、開發注意事項與目前證據 | [README.zh-TW.md](./README.zh-TW.md) |
| SDK 開發流程 | [sdk_development_guide.zh-TW.md](./sdk_development_guide.zh-TW.md) |
| 36 UE zero-gap pressure gate | `MMTC_STAGE_PROFILE=core36_pressure` 搭配 `gate_e_64ue_stage_check.py --stage core36-pressure` |
| 56 UE Gate E-Core 手動復現 | [gate_e_core56_manual_reproduction.zh-TW.md](./gate_e_core56_manual_reproduction.zh-TW.md) |
| 最終 Gate E-Core accepted report | [gate_e_core56_ab_latency_2026-07-09.md](../report/gate_e_core56_ab_latency_2026-07-09.md) |
| Adaptive C-DRX A/B 手動重建 | [adaptive_drx_ab_manual_reproduction.zh-TW.md](./adaptive_drx_ab_manual_reproduction.zh-TW.md) |
| Adaptive C-DRX 實驗文件 | [drx_exprment/README.zh-TW.md](../drx_exprment/README.zh-TW.md) |
| Adaptive C-DRX API 與控制合約 | [adaptive_drx_api_contract.zh-TW.md](./adaptive_drx_api_contract.zh-TW.md) |
| Adaptive C-DRX 原始碼 Trace Code Guide | [adaptive_drx_trace_code_guide.zh-TW.md](./adaptive_drx_trace_code_guide.zh-TW.md) |
| Adaptive C-DRX 證據 Gate 報告 | [adaptive_drx_ab_gate_2026-07-11.zh-TW.md](../report/adaptive_drx_ab_gate_2026-07-11.zh-TW.md) |

## API / config behavior

| API | 語言 | 功能 | 目前證據 |
|---|---|---|---|
| `redcap_xapp_make_priority_hint` | C | 依 UL buffer 與權重建立單一 UE priority hint | 語法檢查目標 |
| `redcap_xapp_select_top_priority_hint` | C | 選出最高優先 UE；同分時使用較小 RNTI | 語法檢查目標 |
| `make_priority_hint` | Python | C priority hint builder 的 Python 對應版本 | self-test |
| `select_top_priority_hint` | Python | top UE 選擇的 Python 對應版本 | self-test |
| `redcap_dapp_guard_prb_allocation` | C | 驗證 5 MHz BWP profile、I/Q presence、PUCCH/PUSCH ratio intent | 語法檢查目標 |
| `redcap_dapp_guard_prb_allocation` | Python | dApp allocation guard 的 Python 對應版本 | self-test |
| `redcap_dapp_access_pressure_policy` | C | 將 RA/PUCCH collision proxy counter 轉成受限的 PUCCH/PUSCH ratio intent，並呼叫 dApp allocation guard | 語法檢查目標 |
| `redcap_dapp_access_pressure_policy` | Python | access-pressure policy 的 Python 對應版本 | self-test |
| `redcap_dapp_select_ra_pressure_priority` | C / Python | 先選出 RA retry count 最高的 UE，再用 pressure/priority/RNTI tie-break | self-test |

重要欄位：

- [RNTI]：UE 識別碼，不能為 0。
- [priority_weight]：xApp 輸出，dApp 會放進 decision metadata。
- [bwp_prbs]：runtime 推導出的 BWP PRB marker；在 5 MHz / 30 kHz SCS profile 下，本地 notes 預期約 `12` PRBs `[Needs Verification]`。
- [pucch_ratio_permille] / [pusch_ratio_permille]：permille 比例，總和不得超過 `1000`。
- [has_iq_samples]：dApp 必須有 I/Q observation 證據才允許 apply。

## Access-pressure policy

- [Purpose]：先針對 32 UE / 5 MHz BWP 接入壓力做緩解，再讓 xApp 引導後續 UE 擴充到 20 MHz。
- [Inputs]：RA retry count、Msg3 failure count、PUCCH resource reject count、CRC/discard count、previous pressure EWMA、BWP PRB marker、priority weight、I/Q availability。
- [Pressure score]：`100 * ra_retry + 120 * msg3_failure + 160 * pucch_resource_reject + 40 * crc_discard`，上限 clamp 到 `1000`。
- [Priority selector]：`redcap_dapp_select_ra_pressure_priority` 先選 [RA retry count] 最高的 UE；同分再看 pressure score、priority weight、較小 RNTI。
- [EWMA]：`0.7 * previous + 0.3 * current`，目前用整數運算實作。
- [Ratio mapping]：
  - low pressure：PUCCH `200`，PUSCH `600`。
  - medium pressure：PUCCH `300`，PUSCH `500`。
  - high pressure：PUCCH `400`，PUSCH `400`。
- [Guard boundary]：只有 `redcap_dapp_guard_prb_allocation` 回傳 ACK 時，policy result 才能視為可 apply。
- [Current evidence]：Python SDK self-check、dApp/xApp contract self-test、C syntax check、Gate D marker runtime，以及 Gate E-Core 56 UE A/B Launch-to-TUN 比較皆已通過。Core36 true batch-start A/B evidence 已取得，但沒有顯示 mitigation improvement。

## Command usage

執行靜態驗證：

```bash
python3 agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/check_dapp_xapp_sdk_test_validation.py
```

執行 SDK contract 驗證：

```bash
python3 agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/dapp_xapp_sdk_contract_selftest.py
```

執行 OpenSpec 驗證：

```bash
openspec validate redcap-dapp-xapp-sdk-test-validation --strict
```

執行 Gate C E3 loopback dependency/runtime 檢查：

```bash
python3 -B agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/gate_c_e3_loopback_check.py
```

當 `dev_refer/dapp_dev_need/libe3` 沒有既有 loopback binary，或本機缺少必要 build 依賴時，Gate C 會回報 `blocked`；這不等於失敗，也不等於 PASS。

保存 Gate C configure 證據：

```bash
python3 -B agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/gate_c_e3_loopback_check.py --try-configure
```

目前 configure 證據位於 `test_log/compiler_logs/gate_c_libe3_configure_2026-07-05_18-43-41.log`；目前 blocker 是離線 `tl::expected` target/cache 不可用，不是 `asn1c`。

若允許 network FetchContent，請使用乾淨 build directory：

```bash
python3 -B agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/gate_c_e3_loopback_check.py --try-configure --allow-fetch --build-dir dev_refer/dapp_dev_need/libe3/build/redcap-gate-c-fetch
```

目前 fetch 證據位於 `test_log/compiler_logs/gate_c_libe3_configure_fetch_2026-07-05_18-46-35.log`；sandbox DNS 無法解析 `github.com`，且 escalation 因 workspace credits 不足被拒絕。

使用 project-local expected shim 執行 Gate C：

```bash
python3 -B agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/gate_c_e3_loopback_check.py --try-configure --use-local-expected-stub --try-build --build-dir dev_refer/dapp_dev_need/libe3/build/redcap-gate-c-local-expected
```

目前 Gate C runtime 證據：

- POSIX IPC/TCP loopback PASS：`test_log/compiler_logs/gate_c_libe3_runtime_test_role_pair_posix_2026-07-06_11-58-08.log`
- Full-loop latency PASS：`test_log/compiler_logs/gate_c_libe3_runtime_test_bench_full_loop_latency_2026-07-06_11-58-23.log`
- Total round-trip latency：p99 `183 us`，max `260 us`

執行 Gate D source readiness 檢查：

```bash
python3 -B agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/gate_d_rfsim_marker_check.py
```

啟用 marker 環境變數後，執行 Gate D RFsim marker 掃描：

```bash
cd ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap
REGISTRY= \
TAG=latest \
GNB_IMG=oai-gnb \
NRUE_IMG=oai-nr-ue \
GNB_REDCAP_CONFIG=../../conf_files/gnb.sa.band78.fr1.106PRB.usrpb210.redcap.5mhz-bwp.yaml \
MMTC_N_RB_DL=106 \
OAI_REDCAP_DAPP_GATE_D_MARKER=1 \
MMTC_GNB_EXTRA_OPTIONS="--gNBs.[0].do_CSIRS 0 --gNBs.[0].do_SRS 0" \
docker compose -f docker-compose.yml -f docker-compose.mmtc.yml up -d --force-recreate oai-gnb oai-nr-ue2
python3 -B agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/gate_d_rfsim_marker_check.py --gnb-log <gNB-log-path> --ue-log <UE-log-path> --require-runtime --require-bwp-mhz 5
```

Gate D source readiness 與 `nr-softmodem` build 證據位於 `test_log/build_logs/build_nr-softmodem_2026-07-06_gate-d-pucch-marker.log`。這代表 gNB ULSCH/PUSCH/PDCCH 路徑已在 `config_uldci()` 之後呼叫 dApp PRB guard，PUCCH FAPI 路徑也已在 `nr_configure_pucch()` 之後呼叫同一個 guard，且目前仍可 build。

目前 Gate D 5 MHz RFsim 證據：

- gNB log：`test_log/runtime_logs/gate_d_5mhz_gnb_2026-07-06_17-16-57.log`
- UE2 log：`test_log/runtime_logs/gate_d_5mhz_ue2_2026-07-06_17-16-57.log`
- gNB 已觀察到 `[RedCap RA][gNB Msg2 BWP selected]`，其中 `dl_bwp_size 12`、`ul_bwp_size 12`。
- UE2 已觀察到 `SIB1 RedCap initial BWP decision`，並套用 DL/UL BWP size `12`。
- 舊 log 也顯示 RedCap RA DCI bit-length 不一致：gNB `dci_bits 35`，UE `dci_bits 39`。
- source fix 已讓兩端在 RedCap Case B RA common DCI sizing 使用目前的 12 PRB DL BWP。
- local rebuilt image 證據：`test_log/build_logs/rebuild_local_oai_images_2026-07-07_00-35-33_dapp_access_pressure_policy.log`。
- CSI-RS/SRS 啟用時的 post-rebuild 失敗證據：`test_log/runtime_logs/gate_d_access_pressure_gnb_2026-07-07_00-45_local.log`。
- 失敗原因：gNB 已走到 RA/RAR/Msg3，但在 `encode_cellGroupConfig()` 對 `nzp-CSI-RS-ResourceToAddModList` assert。
- Gate D PASS gNB log：`test_log/runtime_logs/gate_d_access_pressure_gnb_2026-07-07_00-47_local_no_csirs_srs.log`。
- Gate D PASS UE2 log：`test_log/runtime_logs/gate_d_access_pressure_ue2_2026-07-07_00-47_local_no_csirs_srs.log`。
- PASS run 使用 local images 與 `MMTC_GNB_EXTRA_OPTIONS="--gNBs.[0].do_CSIRS 0 --gNBs.[0].do_SRS 0"`。
- gNB log 確認 `CSI-RS 0, SRS 0`、12 PRB RedCap RA DCI、`[RedCap dApp Gate D][gNB MAC PUCCH]` 與 `[RedCap dApp Gate D][gNB MAC UL]` marker `"RedCap dApp PRB decision"`。
- Gate D checker PASS：`gate_d_rfsim_marker_check.py --require-runtime --require-bwp-mhz 5`。
- 這不代表 64 UE runtime PASS，也不代表 access-pressure mitigation 已在碰撞負載下有效。

執行 36 UE zero-gap pressure profile：

```bash
MMTC_STAGE_PROFILE=core36_pressure \
MMTC_START_XAPP=0 \
MMTC_USE_EXISTING_CN_DB=0 \
MMTC_N_RB_DL=51 \
GNB_REDCAP_CONFIG=../../conf_files/gnb.sa.band78.fr1.51PRB.usrpb210.redcap.yaml \
MMTC_GNB_EXTRA_OPTIONS="--gNBs.[0].do_CSIRS 0 --gNBs.[0].do_SRS 0" \
bash redcap_interface/redcap_mmtc_stage_scan.sh
```

從 baseline 證據選出 dApp priority UE list：

```bash
python3 -B agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/select_core36_pressure_priority.py \
  --summary-log test_log/compiler_logs/mmtc_stage_scan_<baseline>_summary.log
```

使用選出的 list 執行 dApp profile：

```bash
PRIORITY_UES=$(python3 -B agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/select_core36_pressure_priority.py \
  --summary-log test_log/compiler_logs/mmtc_stage_scan_<baseline>_summary.log \
  --emit-env-only)

MMTC_STAGE_PROFILE=core36_pressure \
MMTC_START_XAPP=1 \
MMTC_USE_EXISTING_CN_DB=0 \
MMTC_N_RB_DL=51 \
GNB_REDCAP_CONFIG=../../conf_files/gnb.sa.band78.fr1.51PRB.usrpb210.redcap.yaml \
OAI_REDCAP_DAPP_GATE_D_MARKER=1 \
MMTC_DAPP_STOP_NON_PRIORITY=1 \
MMTC_DAPP_PRIORITY_UES="${PRIORITY_UES}" \
MMTC_GNB_EXTRA_OPTIONS="--gNBs.[0].do_CSIRS 0 --gNBs.[0].do_SRS 0" \
bash redcap_interface/redcap_mmtc_stage_scan.sh
```

驗證 36 UE pressure comparison：

```bash
python3 -B agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/gate_e_64ue_stage_check.py \
  --stage core36-pressure \
  --baseline-summary-log test_log/compiler_logs/mmtc_stage_scan_<baseline>_summary.log \
  --dapp-summary-log test_log/compiler_logs/mmtc_stage_scan_<dapp>_summary.log \
  --baseline-latency-log test_log/compiler_logs/mmtc_smoke_<baseline>_access_latency.csv \
  --dapp-latency-log test_log/compiler_logs/mmtc_smoke_<dapp>_access_latency.csv \
  --dapp-gnb-log test_log/compiler_logs/mmtc_smoke_<dapp>_gnb.log
```

準備 Gate E 64 UE preflight：

```bash
bash ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/scripts/generate_mmtc_overlay.sh 64
bash redcap_interface/generate_mmtc_cn_db_overlay.sh 64
python3 -B agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/gate_e_64ue_stage_check.py
```

目前 Gate E preflight 證據：

- RFsim overlay：`ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/docker-compose.mmtc.yml` 已包含 UE1..UE64。
- RFsim base compose：`ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/docker-compose.yml`。
- CN/AMF 來源：`redcap_interface/redcap_mmtc_smoke_validation.sh` 預設將 `CN_COMPOSE` 指到 `/home/tonywang/OAI/oai-cn5g/docker-compose.yaml`，該 compose service list 包含 `oai-amf`、`mysql`、`oai-smf` 與 `oai-upf`。
- CN DB overlay：`test_log/runtime_configs/oai_db_mmtc_64.sql` 與 `test_log/runtime_configs/oai-cn5g_mmtc_64.override.yml`。
- Config merge 證據：`docker compose -f /home/tonywang/OAI/oai-cn5g/docker-compose.yaml -f test_log/runtime_configs/oai-cn5g_mmtc_64.override.yml config --services` 會列出 `oai-amf`；在 RFsim RedCap 目錄執行 `docker compose -f docker-compose.yml -f docker-compose.mmtc.yml config --services` 會列出 64 個 `oai-nr-ue*` service。
- 第一階段 profile：`gnb.sa.band78.fr1.106PRB.usrpb210.redcap.5mhz-bwp.yaml` 保留 106 PRB RF carrier，並將 RedCap active/initial BWP 設為 12 PRBs。
- 第二階段 proxy profile：`gnb.sa.band78.fr1.51PRB.usrpb210.redcap.yaml` 作為 51 PRB 的 20 MHz proxy `[Needs Verification]`。
- checker 結果：`gate_e_64ue_stage_check.py` 回報 `[PASS] Gate E static preflight is ready for 64 UE staged RFsim`。
- Runtime evidence checker 格式：

```bash
python3 -B agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/gate_e_64ue_stage_check.py \
  --stage first32 \
  --gnb-log test_log/compiler_logs/mmtc_smoke_<timestamp>_gnb.log \
  --summary-log test_log/compiler_logs/mmtc_stage_scan_<timestamp>_summary.log
```

2026-07-07 Gate E first32 runtime 嘗試：

- Summary log：`test_log/compiler_logs/mmtc_stage_scan_2026-07-07_11-11-52_summary.log`。
- gNB log：`test_log/compiler_logs/mmtc_smoke_2026-07-07_11-11-52_gnb.log`。
- 結果：`sample=32 running=32 attach=0 pdu=0 tun=0 gnb_restart=0 failures=32`。
- 正向證據：重建後的 gNB 沒有重啟，且 log 有 `260` 筆 `[RedCap dApp Gate E][PUCCH pressure]` marker。
- 負向證據：gNB log 沒有 `Assertion`、`assert`、`Not enough resources`、`event_asio_agent`、`Aborted` 或 `Segmentation` marker。
- xApp/RIC 證據：`mmtc_smoke_2026-07-07_11-11-52_xapp-rc-moni.log` 與 `..._nearrt-ric.log` 有 E42 setup、兩個 RC subscription、四筆 RC Indication。
- 控制邊界：xApp 與 nearRT-RIC Docker logs 尚未看到 RIC Control request/ACK marker。
- 目前 blocker：12 PRB BWP run 持續出現 Msg4/RRC Setup failure，尚未進入 UE registration/PDU session。
- Gate E runtime PASS 仍然 pending；目前尚未產生 64 UE attach/control/collision-load runtime 證據。

2026-07-07 Gate E first32 DL TDA fix 嘗試：

- Build log：`test_log/build_logs/build_nr-softmodem_2026-07-07_11-38-37_gate-e-redcap-tda.log`。
- Local image rebuild log：`test_log/build_logs/rebuild_local_oai_images_2026-07-07_11-39-43_gate-e-redcap-tda.log`。
- Summary log：`test_log/compiler_logs/mmtc_stage_scan_2026-07-07_12-14-11_summary.log`。
- gNB log：`test_log/compiler_logs/mmtc_smoke_2026-07-07_12-14-11_gnb.log`。
- 結果：`sample=32 running=32 attach=0 pdu=0 tun=0 gnb_restart=0 failures=32`。
- 正向證據：`nr_radio_config.c` 會依 12 PRB BWP 重建 RedCap initial DL BWP PDSCH TDA list，且 gNB log 有 `2` 筆 `[RedCap RA][gNB DL TDA]` marker，`first_start_symbol 2`。
- 正向證據：舊的 `Msg4 vrb_map fail` marker 已不再出現；gNB log 有 `32` 筆 Msg4 ACK marker 與 `32` 筆 `Send RRC Setup` marker。
- 剩餘失敗證據：gNB log 仍有 `85` 筆 `[RedCap RA][gNB Msg4 compact fallback]` marker，以及 `1` 筆 `[RedCap RA][gNB Msg2 vrb_map fail]` marker。
- UE-side 證據：UE1..UE32 的 Docker log 各有一次 `Generating RRCSetupComplete`。
- Core-network 邊界：gNB/AMF logs 尚未看到 UE registration 或 PDU-session progress，stage summary 仍回報沒有 TUN interface。
- xApp/RIC 邊界：stage script 沒有保存 12:14 的 xApp/RIC log 檔；live Docker logs 有 E42 setup、兩個 RC subscription、RC Indication，但沒有 RIC Control request/ACK marker。
- Gate E runtime PASS 仍然 pending；下一個 blocker 是 12 PRB BWP 上的 SRB1/UL-DCCH 或 post-RRCSetupComplete handling。

2026-07-07 Gate E first32 connected DCI BWP runtime rerun：

- Root cause 已由 log 證據縮小：Msg4 ACK 後，gNB connected common-search-space UL DCI 使用一般 51 PRB initial UL BWP 的 RIV 寬度，但 UE 已套用 12 PRB RedCap SIB1 initial UL BWP。
- Failure signature：gNB 對 5 PRB grant 記錄 `dci_freq 204`，這是 51 PRB RIV 值；UE 端接著把位移後的低位元解成 `TDA index from DCI 12`，導致 SRB1/UL-DCCH 無法穩定送達。
- Source fix：`openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_primitives.c` 現在透過 `apply_redcap_initial_bwp_if_needed()` 在 connected DCI 前保留 RedCap initial DL/UL BWP start/size。
- Source build evidence：`test_log/build_logs/build_nr-softmodem_2026-07-07_12-42-09_gate-e-redcap-dci-bwp_retry.log`。
- Docker image rebuild evidence：`test_log/build_logs/rebuild_local_oai_images_2026-07-07_23-05-19_gate-e-redcap-dci-bwp_retry2_escalated.log`。
- Summary log：`test_log/compiler_logs/mmtc_stage_scan_2026-07-07_23-18-49_summary.log`。
- gNB log：`test_log/compiler_logs/mmtc_smoke_2026-07-07_23-18-49_gnb.log`。
- xApp/RIC Docker logs：`test_log/compiler_logs/mmtc_smoke_2026-07-07_23-18-49_xapp-rc-moni.log` 與 `test_log/compiler_logs/mmtc_smoke_2026-07-07_23-18-49_nearRT-RIC.log`。
- 結果：`sample=32 running=32 attach=32 pdu=32 tun=32 forward_ping_ok=32 gnb_restart=0 failures=0`。
- Runtime marker 證據：gNB log 有 `128` 筆 `[RedCap RA][gNB DCI BWP]` marker、`32` 筆 `Received RRCSetupComplete`、`32` 筆 `Received RRCReconfigurationComplete`、`32` 筆 `PDU Session Setup: ID=10` marker。
- dApp 證據：gNB log 有 `34291` 筆 `[RedCap dApp Gate D][gNB MAC UL]` apply marker，並有 `28` 筆 12 PRB BWP 上的 `[RedCap dApp Gate E][PUCCH pressure]` marker。
- Retry boundary：gNB log 仍有 `1` 筆 transient `[RedCap RA][gNB Msg4 vrb_map fail]` 與 `90` 筆 compact-fallback marker，但沒有 `RA Procedure failed at Msg4`；最終 stage summary 回報 zero failures。
- UE-side fix 證據：UE1..UE32 都各自產生 `RRCSetupComplete`；UE Docker logs 沒有 `TDA index from DCI 12`。
- xApp/RIC 證據：xApp Docker log 有 E42 setup、兩個 RC subscription、`5` 筆 RC Indication message、`RRC Setup Complete`、`RRC connected`、subscription delete 與 `Test xApp run SUCCESSFULLY`；nearRT-RIC Docker log 有 E2 setup 與 RAN function 3 `ORAN-E2SM-RC`。
- 控制邊界：xApp 與 nearRT-RIC Docker logs 尚未看到 RIC Control request/ACK marker。
- Gate E first32 checker PASS：`gate_e_64ue_stage_check.py --stage first32 --gnb-log test_log/compiler_logs/mmtc_smoke_2026-07-07_23-18-49_gnb.log --summary-log test_log/compiler_logs/mmtc_stage_scan_2026-07-07_23-18-49_summary.log`。
- Gate E runtime PASS 仍然 pending：full 64 UE / 20 MHz proxy stage 與 collision-load access-pressure effectiveness 尚未完成；這次 first32 結果只證明 32 UE 5 MHz stage。

2026-07-09 Gate E-Core 56 UE A/B runtime：

- Gate E 已改成 two-tier：Gate E-Core 是 SDK v1 工程 gate；Gate E-Stretch 保留 strict 64 UE stress evidence，且不阻塞 SDK v1。
- Baseline summary：`test_log/compiler_logs/mmtc_stage_scan_2026-07-09_10-27-10_summary.log`。
- dApp summary：`test_log/compiler_logs/mmtc_stage_scan_2026-07-09_10-42-43_summary.log`。
- Baseline latency CSV：`test_log/compiler_logs/mmtc_smoke_2026-07-09_10-27-10_access_latency.csv`。
- dApp latency CSV：`test_log/compiler_logs/mmtc_smoke_2026-07-09_10-42-43_access_latency.csv`。
- dApp gNB marker log：`test_log/compiler_logs/mmtc_smoke_2026-07-09_10-42-43_gnb.log`。
- 結果：兩次 runtime 都達到 `sample=56 running=56 attach=56 pdu=56 tun=56 forward_ping_ok=56 gnb_restart=0 failures=0`。
- Launch-to-TUN 比較：baseline median/p95/max `436318/703145/722926 ms`；dApp median/p95/max `441487/708146/728189 ms`。
- 邊界：這是有效 A/B 比較，不是 dApp latency improvement claim。
- Gate E-Core checker PASS：`gate_e_64ue_stage_check.py --stage core56-ab`。
- Report：`agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/report/gate_e_core56_ab_latency_2026-07-09.md`。

## Step-by-step recap

1. 確認本地 `dev_refer/` 參考資料存在。
2. 確認 xApp priority hint API 同時存在於 C 與 Python。
3. 確認 dApp PRB allocation API 同時存在於 C 與 Python。
4. 確認 `libe3` 與 I/Q saver 的 SWIG definition 檔存在。
5. 執行 SDK contract self-test。
6. 執行 Gate C E3 loopback checker。
7. 執行 Gate D source readiness checker。
8. 執行 Gate E preflight checker。
9. Runtime 階段執行 `redcap_interface/redcap_mmtc_stage_scan.sh`，再同時驗證 `mmtc_smoke_<timestamp>_gnb.log` 與 `mmtc_stage_scan_<timestamp>_summary.log`。
10. Gate E-Core 已由 56 UE A/B runtime 關閉；Gate E-Stretch 在需要 strict 64 UE upper-bound evidence 前維持 pending。

## Example logic

- xApp 讀取 UE metrics。
- xApp 計算 priority hints。
- dApp 收到被選出的 hint。
- dApp 檢查 I/Q observation 是否存在。
- dApp 依 RA/PUCCH collision proxy 計算 access pressure。
- dApp 驗證 5 MHz BWP profile 與 PUCCH/PUSCH ratios。
- dApp 輸出 apply/reject result。

## Visualization

- 參考 `dev_refer/dapp_dev_need/dApp-library/examples/spectrum_dapp.py` 的可視化模式。
- 相關選項包含：
  - `--demo-gui`
  - `--iq-plotter-gui`
  - `--energy-gui`
  - `--num-prbs <derived 5 MHz PRB count>`
- 可視化不是 PASS gate；必須等 dApp runtime path 接上後才能作為驗收證據。

## Expected markers

- `RedCap xApp priority hint`
- `RedCap dApp PRB decision`
- `RedCap dApp access pressure policy`
- `[RedCap dApp Gate E][PUCCH pressure]`
- `[RedCap RA][gNB DL TDA]`
- `[RedCap dApp Gate D][gNB MAC UL] gNB-side apply marker`
- `[RedCap dApp Gate D][gNB MAC PUCCH] gNB-side PUCCH marker`
- Gate C source path：`dev_refer/dapp_dev_need/libe3/tests/integration/test_role_pair_posix.cpp`
- Gate D source path：`openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_ulsch.c`
- Gate D PUCCH source path：`openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_uci.c`
- Gate D 5 MHz BWP profile：`ci-scripts/conf_files/gnb.sa.band78.fr1.106PRB.usrpb210.redcap.5mhz-bwp.yaml`
- Gate D runtime env passthrough：`ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/docker-compose.mmtc.yml` 的 `OAI_REDCAP_DAPP_GATE_D_MARKER`
- Gate E preflight checker：`agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/gate_e_64ue_stage_check.py`
- Gate E runtime summary：`test_log/compiler_logs/mmtc_stage_scan_<timestamp>_summary.log`
- Gate E 64 UE overlay：`ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/docker-compose.mmtc.yml`
- Gate E CN DB overlay：`test_log/runtime_configs/oai_db_mmtc_64.sql`
- Gate D I/Q reference：`dev_refer/dapp_dev_need/E3Controller/src/e3sm/iq_pipeline.h` 與 `slot_iq_pipeline.h`
- PDCCH command path：ULSCH path 中 `config_uldci()` 後接 `fill_dci_pdu_rel15()` `[Needs Verification: TS 38.212 Section 7.3.1.1 / TS 38.214 Section 6.1]`

## Limitations

- Gate B 目前只驗證 SWIG definition，尚未驗證 generated SWIG module runtime。
- Gate C E3 loopback 已使用 project-local `tl_expected` test shim 通過。
- Official `tl_expected` FetchContent 仍不可用；不要把 local shim 當成 production dependency 證據。
- Gate D source hook readiness、`nr-softmodem` build PASS 與 small RFsim marker validation PASS 已存在。
- DCI bit-length source fix 已通過 `nr-softmodem` 與 `nr-uesoftmodem` build。
- Gate D runtime env passthrough 已加入 compose overlay，且最新 runtime 已將 5 MHz BWP profile mount 進 gNB container。
- 5 MHz profile 保留 106 PRB RF carrier，但 BWP1 與 RedCap DL/UL initial BWP 設為 30 kHz SCS 的 12 PRBs `[Needs Verification]`；runtime log 已確認 RA/SIB1 使用 size `12`。
- Gate D PASS 目前依賴 CLI override 關閉 CSI-RS/SRS；CSI-RS/SRS 啟用時的 RFsim 仍是 Gate E production-style claim 前的 blocker。
- Gate D 目前涵蓋 ULSCH/PUSCH/PDCCH 與 PUCCH marker path；dApp access-pressure policy 已實作並通過單元測試，但碰撞負載下的 runtime effectiveness 仍待驗證。
- Gate E static preflight 已準備好，first32 post-DCI-BWP runtime 已達到 `attach=32`、`pdu=32`、`tun=32`、`forward_ping_ok=32`，且 Gate E-Core 56 UE A/B Launch-to-TUN 比較已通過。
- full 64 UE staged stress runtime validation 仍作為 Gate E-Stretch pending；它不阻塞 SDK v1。
- 精確 O-RAN 與 3GPP clause mapping 仍是 `[Needs Verification]`。
