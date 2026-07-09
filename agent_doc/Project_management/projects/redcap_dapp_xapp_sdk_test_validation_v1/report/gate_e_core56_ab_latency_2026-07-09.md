# Gate E-Core 56 UE dApp A/B Access-Latency Report

## English Summary

- [Date]: 2026-07-09.
- [Gate]: Gate E-Core, 56 UE baseline-vs-dApp access-latency comparison.
- [Result]: PASS for SDK v1 engineering completion.
- [Metric]: Launch-to-TUN, measured from per-UE launch epoch to first observed `oaitun_ue1`.
- [Boundary]: this proves a valid A/B comparison. It does not prove dApp latency improvement or collision-load reduction.
- [Stretch Boundary]: 64 UE strict validation remains Gate E-Stretch and is not blocking SDK v1.

## 繁體中文摘要

- [日期]: 2026-07-09。
- [Gate]: Gate E-Core，56 UE baseline-vs-dApp 接入延遲比較。
- [結果]: SDK v1 工程完成門檻 PASS。
- [指標]: Launch-to-TUN，從每台 UE launch epoch 到第一次觀察到 `oaitun_ue1`。
- [邊界]: 本次證明有有效 A/B 比較；不宣稱 dApp 讓延遲下降，也不宣稱 collision-load reduction。
- [Stretch 邊界]: 64 UE 嚴格驗證仍是 Gate E-Stretch，不阻塞 SDK v1。

## Runtime Commands

### Baseline

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

### dApp Enabled

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

## Evidence Artifacts

| Item | Path |
|---|---|
| Baseline summary | `test_log/compiler_logs/mmtc_stage_scan_2026-07-09_10-27-10_summary.log` |
| dApp summary | `test_log/compiler_logs/mmtc_stage_scan_2026-07-09_10-42-43_summary.log` |
| Baseline latency CSV | `test_log/compiler_logs/mmtc_smoke_2026-07-09_10-27-10_access_latency.csv` |
| dApp latency CSV | `test_log/compiler_logs/mmtc_smoke_2026-07-09_10-42-43_access_latency.csv` |
| dApp gNB log | `test_log/compiler_logs/mmtc_smoke_2026-07-09_10-42-43_gnb.log` |

## Health Summary

| Run | sample | running | attach | pdu | tun | forward_ping_ok | gnb_restart | failures |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Baseline | 56 | 56 | 56 | 56 | 56 | 56 | 0 | 0 |
| dApp Enabled | 56 | 56 | 56 | 56 | 56 | 56 | 0 | 0 |

## Launch-to-TUN Comparison

| Run | Success Count | Median ms | p95 ms | Max ms |
|---|---:|---:|---:|---:|
| Baseline | 56 | 436318 | 703145 | 722926 |
| dApp Enabled | 56 | 441487 | 708146 | 728189 |
| dApp minus Baseline | 0 | +5169 | +5001 | +5263 |

## dApp Marker Evidence

- [gNB marker]: `RedCap dApp PRB decision`.
- [Marker count]: `1862706` matches in the dApp-enabled gNB log.
- [Sample marker]:
  - `RNTI afda`
  - `bwp_prbs 51`
  - `pusch_ratio_permille 99`
  - `pucch_ratio_permille 0`
  - `marker "RedCap dApp PRB decision"`
- [Crash scan]: no `Assertion`, `Aborted`, or `segfault` marker was found by the checker scan.
- [xApp/RIC log boundary]: the dApp-enabled wrapper run started `xapp-rc-moni_redcap`, but standalone xApp/RIC log files were not captured under `test_log/compiler_logs` for this timestamp.

## Validation

```bash
rtk python3 -B agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/gate_e_64ue_stage_check.py \
  --stage core56-ab \
  --baseline-summary-log test_log/compiler_logs/mmtc_stage_scan_2026-07-09_10-27-10_summary.log \
  --dapp-summary-log test_log/compiler_logs/mmtc_stage_scan_2026-07-09_10-42-43_summary.log \
  --baseline-latency-log test_log/compiler_logs/mmtc_smoke_2026-07-09_10-27-10_access_latency.csv \
  --dapp-latency-log test_log/compiler_logs/mmtc_smoke_2026-07-09_10-42-43_access_latency.csv \
  --dapp-gnb-log test_log/compiler_logs/mmtc_smoke_2026-07-09_10-42-43_gnb.log
```

- [Checker Result]: PASS, `Gate E-Core 56 UE A/B latency evidence found`.

## Engineering Interpretation

- [Pass Reason]: both runs have complete 56 UE health and complete Launch-to-TUN rows.
- [dApp Behavior]: dApp marker path is active on the 51 PRB expanded-bandwidth proxy.
- [Latency Result]: dApp-enabled latency is slightly higher in this run. This is acceptable for v1 because the gate requires a valid comparison, not an improvement claim.
- [Next Pull]: keep 64 UE as Gate E-Stretch, or proceed to SDK documentation/API guide work.

