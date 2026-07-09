# Gate E-Core 56 UE Manual Reproduction

## Scope

- This page reproduces the RedCap dApp/xApp SDK [Gate E-Core] result.
- The gate is a 56 UE [Baseline] versus [dApp Enabled] access-latency comparison.
- The primary metric is [Launch-to-TUN]: per-UE launch epoch to first observed `oaitun_ue1`.
- This page is for manual reproduction; the final accepted result is summarized in `report/gate_e_core56_ab_latency_2026-07-09.md`.

## Runtime Profile

- [Repository root]: run commands from `/home/tonywang/OAI/Red_cap_openairinterface5g`.
- [CN5G source]: the wrapper defaults to `/home/tonywang/OAI/oai-cn5g/docker-compose.yaml`.
- [RFsim source]: `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/`.
- [gNB profile]: `ci-scripts/conf_files/gnb.sa.band78.fr1.51PRB.usrpb210.redcap.yaml`.
- [Expanded-bandwidth proxy]: `MMTC_N_RB_DL=51`; exact 20 MHz terminology remains `[Needs Verification]`.
- [No CSI/SRS workaround]: keep `MMTC_GNB_EXTRA_OPTIONS="--gNBs.[0].do_CSIRS 0 --gNBs.[0].do_SRS 0"`.
- [iperf]: keep `MMTC_IPERF_ENABLE=0`; iperf is diagnostic only for this gate.

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

Expected artifacts:

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

Expected artifacts:

- `test_log/compiler_logs/mmtc_stage_scan_<timestamp>_summary.log`
- `test_log/compiler_logs/mmtc_smoke_<timestamp>_access_latency.csv`
- `test_log/compiler_logs/mmtc_smoke_<timestamp>_gnb.log`

## Evidence Check

Use the concrete accepted 2026-07-09 artifacts:

```bash
python3 -B agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/gate_e_64ue_stage_check.py \
  --stage core56-ab \
  --baseline-summary-log test_log/compiler_logs/mmtc_stage_scan_2026-07-09_10-27-10_summary.log \
  --dapp-summary-log test_log/compiler_logs/mmtc_stage_scan_2026-07-09_10-42-43_summary.log \
  --baseline-latency-log test_log/compiler_logs/mmtc_smoke_2026-07-09_10-27-10_access_latency.csv \
  --dapp-latency-log test_log/compiler_logs/mmtc_smoke_2026-07-09_10-42-43_access_latency.csv \
  --dapp-gnb-log test_log/compiler_logs/mmtc_smoke_2026-07-09_10-42-43_gnb.log
```

Expected checker result:

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

- [dApp marker]: `RedCap dApp PRB decision` in the dApp-enabled gNB log.
- [Crash scan]: no checker-detected `Assertion`, `Aborted`, or `segfault`.
- [Summary health]: both summary logs must report `sample=56`, `running=56`, `attach=56`, `pdu=56`, `tun=56`, `gnb_restart=0`, and `failures=0`.
- [Latency rows]: both latency CSV files must contain 56 successful Launch-to-TUN rows.

## Interpretation

- [Gate E-Core Status]: PASS for SDK v1 engineering completion.
- [dApp Latency Claim]: no improvement claim. The dApp-enabled run was slightly slower in this accepted run.
- [xApp Boundary]: the 56 UE wrapper run started `xapp-rc-moni_redcap`, but standalone xApp/RIC logs were not captured for that timestamp.
- [Control Path Boundary]: one-RNTI xApp/RIC/gNB control ACK/apply evidence exists separately from the 56 UE A/B comparison.
- [Stretch Boundary]: 64 UE strict validation remains [Gate E-Stretch] and does not block SDK v1 documentation.
