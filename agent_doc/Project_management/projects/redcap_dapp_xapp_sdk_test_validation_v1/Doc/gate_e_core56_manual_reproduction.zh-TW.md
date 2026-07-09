# Gate E-Core 56 UE 手動復現

## Scope

- 本頁用來手動復現 RedCap dApp/xApp SDK [Gate E-Core] 結果。
- Gate 內容是 56 UE [Baseline] 與 [dApp Enabled] 的接入延遲 A/B 比較。
- 主要指標是 [Launch-to-TUN]：每台 UE launch epoch 到第一次觀察到 `oaitun_ue1`。
- 本頁是手動復現文件；最後接受結果彙整於 `report/gate_e_core56_ab_latency_2026-07-09.md`。

## Runtime Profile

- [Repository root]：請從 `/home/tonywang/OAI/Red_cap_openairinterface5g` 執行指令。
- [CN5G source]：wrapper 預設使用 `/home/tonywang/OAI/oai-cn5g/docker-compose.yaml`。
- [RFsim source]：`ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/`。
- [gNB profile]：`ci-scripts/conf_files/gnb.sa.band78.fr1.51PRB.usrpb210.redcap.yaml`。
- [Expanded-bandwidth proxy]：`MMTC_N_RB_DL=51`；是否可精確稱為 20 MHz 仍標為 `[Needs Verification]`。
- [No CSI/SRS workaround]：保留 `MMTC_GNB_EXTRA_OPTIONS="--gNBs.[0].do_CSIRS 0 --gNBs.[0].do_SRS 0"`。
- [iperf]：保留 `MMTC_IPERF_ENABLE=0`；在本 gate 中 iperf 只當 diagnostic。

## Baseline Run

```bash
MMTC_REBUILD_IMAGES_BEFORE_SCAN=0 \
MMTC_TOTAL_UES_TARGET=56 \
MMTC_STAGE_LIST=56 \
MMTC_START_XAPP=0 \
MMTC_USE_EXISTING_CN_DB=0 \
MMTC_N_RB_DL=51 \
GNB_REDCAP_CONFIG=../../conf_files/gnb.sa.band78.fr1.51PRB.usrpb210.redcap.yaml \
OAI_REDCAP_DAPP_GATE_D_MARKER=0 \
MMTC_IPERF_ENABLE=0 \
MMTC_SLEEP_AFTER_UP=90 \
MMTC_GNB_EXTRA_OPTIONS="--gNBs.[0].do_CSIRS 0 --gNBs.[0].do_SRS 0" \
bash redcap_interface/redcap_mmtc_stage_scan.sh
```

預期產物：

- `test_log/compiler_logs/mmtc_stage_scan_<timestamp>_summary.log`
- `test_log/compiler_logs/mmtc_smoke_<timestamp>_access_latency.csv`

## dApp Enabled Run

```bash
MMTC_REBUILD_IMAGES_BEFORE_SCAN=0 \
MMTC_TOTAL_UES_TARGET=56 \
MMTC_STAGE_LIST=56 \
MMTC_START_XAPP=1 \
MMTC_USE_EXISTING_CN_DB=0 \
MMTC_N_RB_DL=51 \
GNB_REDCAP_CONFIG=../../conf_files/gnb.sa.band78.fr1.51PRB.usrpb210.redcap.yaml \
OAI_REDCAP_DAPP_GATE_D_MARKER=1 \
MMTC_IPERF_ENABLE=0 \
MMTC_SLEEP_AFTER_UP=90 \
MMTC_GNB_EXTRA_OPTIONS="--gNBs.[0].do_CSIRS 0 --gNBs.[0].do_SRS 0" \
bash redcap_interface/redcap_mmtc_stage_scan.sh
```

預期產物：

- `test_log/compiler_logs/mmtc_stage_scan_<timestamp>_summary.log`
- `test_log/compiler_logs/mmtc_smoke_<timestamp>_access_latency.csv`
- `test_log/compiler_logs/mmtc_smoke_<timestamp>_gnb.log`

## Evidence Check

使用 2026-07-09 已接受的具體 artifacts：

```bash
python3 -B agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/gate_e_64ue_stage_check.py \
  --stage core56-ab \
  --baseline-summary-log test_log/compiler_logs/mmtc_stage_scan_2026-07-09_10-27-10_summary.log \
  --dapp-summary-log test_log/compiler_logs/mmtc_stage_scan_2026-07-09_10-42-43_summary.log \
  --baseline-latency-log test_log/compiler_logs/mmtc_smoke_2026-07-09_10-27-10_access_latency.csv \
  --dapp-latency-log test_log/compiler_logs/mmtc_smoke_2026-07-09_10-42-43_access_latency.csv \
  --dapp-gnb-log test_log/compiler_logs/mmtc_smoke_2026-07-09_10-42-43_gnb.log
```

預期 checker 結果：

- `[PASS] Gate E-Core 56 UE A/B latency evidence found`

## Accepted Result

| Run | sample | running | attach | pdu | tun | forward_ping_ok | gnb_restart | failures |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Baseline | 56 | 56 | 56 | 56 | 56 | 56 | 0 | 0 |
| dApp Enabled | 56 | 56 | 56 | 56 | 56 | 56 | 0 | 0 |

| Run | Success Count | Median ms | p95 ms | Max ms |
|---|---:|---:|---:|---:|
| Baseline | 56 | 436318 | 703145 | 722926 |
| dApp Enabled | 56 | 441487 | 708146 | 728189 |
| dApp minus Baseline | 0 | +5169 | +5001 | +5263 |

## Expected Markers

- [dApp marker]：dApp-enabled gNB log 需出現 `RedCap dApp PRB decision`。
- [Crash scan]：checker 不得偵測到 `Assertion`、`Aborted` 或 `segfault`。
- [Summary health]：兩份 summary log 都必須回報 `sample=56`、`running=56`、`attach=56`、`pdu=56`、`tun=56`、`gnb_restart=0`、`failures=0`。
- [Latency rows]：兩份 latency CSV 都必須有 56 筆成功的 Launch-to-TUN row。

## Interpretation

- [Gate E-Core Status]：SDK v1 工程完成門檻 PASS。
- [dApp Latency Claim]：不宣稱改善延遲；本次接受結果中 dApp-enabled run 略慢。
- [xApp Boundary]：56 UE wrapper run 有啟動 `xapp-rc-moni_redcap`，但該 timestamp 沒有額外保存 standalone xApp/RIC logs。
- [Control Path Boundary]：one-RNTI xApp/RIC/gNB control ACK/apply 證據存在，但它是 56 UE A/B 比較之外的獨立證據。
- [Stretch Boundary]：64 UE strict validation 仍屬於 [Gate E-Stretch]，不阻塞 SDK v1 文件化。
