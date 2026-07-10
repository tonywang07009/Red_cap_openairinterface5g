# Gate E-Core36 Batch-Start Pressure Report

## English Summary

- [Date]: 2026-07-10.
- [Gate]: Gate E-Core36, 56 UE topology with 36 UE launched by one zero-gap compose call.
- [Result]: FAIL for mitigation effectiveness.
- [Finding]: true batch-start creates access pressure: baseline reaches only 17/36 attach/PDU/TUN.
- [dApp Result]: dApp with selected priority UE36 also reaches 17/36 attach/PDU/TUN, so it does not improve success count, failure count, or access latency in this run.
- [STOP Boundary]: wrapper ACK marker is emitted; user-plane STOP/pause was previously observed, but the selected pressure UE has no TUN in the true batch-start run, so traffic-stop effectiveness is not proven here.
- [Scheduler Hook Update]: a post-report gNB RA hook now supports `OAI_REDCAP_DAPP_RA_RETRY_PRIORITY=1`, scheduling `nrRA_Msg3_retransmission` before new `nrRA_Msg2`.
- [Post-Hook Runtime Boundary]: the source build and local image rebuild passed, but the new core36 A/B runtime rerun is not available yet because Docker compose escalation was rejected when workspace credits were exhausted.

## 繁體中文摘要

- [日期]: 2026-07-10。
- [Gate]: Gate E-Core36，56 UE 拓撲下，以單次 zero-gap compose call 啟動 36 UE。
- [結果]: mitigation effectiveness FAIL。
- [觀察]: 真正一次啟動 36 UE 會製造接入壓力；baseline 只有 17/36 attach/PDU/TUN。
- [dApp 結果]: dApp 使用 selector 選出的 priority UE36 後，同樣只有 17/36 attach/PDU/TUN，沒有改善成功數、失敗數或接入延遲。
- [STOP 邊界]: wrapper ACK marker 有出現；舊 run 曾觀察到 pause 35 台非優先 UE，但在真正 batch-start run 中，priority UE36 本身沒有 TUN，因此本輪不能證明流量停止有效。
- [Scheduler Hook 更新]: 後續已新增 gNB RA hook，`OAI_REDCAP_DAPP_RA_RETRY_PRIORITY=1` 時會把 `nrRA_Msg3_retransmission` 排在新的 `nrRA_Msg2` 前面。
- [Post-Hook Runtime 邊界]: source build 與 local image rebuild 已通過，但新的 core36 A/B runtime 尚未取得，因為 Docker compose escalation 因 workspace credits 用完而被拒絕。

## Algorithm Under Test

- [Priority Rule]: select the UE with the highest `ra_retry_count` first.
- [Tie-Break]: if RA retry count ties, prefer higher computed pressure, then higher priority weight, then lower RNTI.
- [Selector API]: `redcap_dapp_select_ra_pressure_priority`.
- [Selector Runner]: `select_core36_pressure_priority.py`.
- [Runtime Profile]: `MMTC_STAGE_PROFILE=core36_pressure`.
- [Batch Start]: `UE_START_GAP=0` and `ADAPTIVE_BURST_ON_ZERO_GAP=0` now use one `compose up -d` call for all sampled UE services.
- [STOP Intent]: `MMTC_DAPP_STOP_NON_PRIORITY=1` with `MMTC_DAPP_PRIORITY_UES=<selected UE list>`.
- [Scheduler Hook]: `OAI_REDCAP_DAPP_RA_RETRY_PRIORITY=1` enables a gNB-side retry-first action in `nr_schedule_RA()`: process RA entries already in `nrRA_Msg3_retransmission` before new `nrRA_Msg2` entries.
- [Scheduler Boundary]: the gNB cannot identify Linux service `UE36` at Msg1/Msg2 time; it sees RA process state, preamble/RA-RNTI/TC-RNTI. Therefore the post-hook action prioritizes [failed/retrying RA process] rather than a hard-coded UE service index.
- [Spec Mapping]: TS 38.321 Section 5.1 [Random Access procedure] is the behavioral area; exact scheduler ordering within OAI remains implementation-specific. [Needs Verification]

## Runtime Commands

### Baseline Batch-Start

```bash
MMTC_REBUILD_IMAGES_BEFORE_SCAN=0 \
MMTC_STAGE_PROFILE=core36_pressure \
MMTC_START_XAPP=0 \
MMTC_USE_EXISTING_CN_DB=0 \
MMTC_N_RB_DL=51 \
MMTC_IPERF_ENABLE=0 \
GNB_REDCAP_CONFIG=../../conf_files/gnb.sa.band78.fr1.51PRB.usrpb210.redcap.yaml \
MMTC_GNB_EXTRA_OPTIONS="--gNBs.[0].do_CSIRS 0 --gNBs.[0].do_SRS 0" \
rtk bash redcap_interface/redcap_mmtc_stage_scan.sh
```

### dApp Batch-Start Access-Only

```bash
MMTC_REBUILD_IMAGES_BEFORE_SCAN=0 \
MMTC_STAGE_PROFILE=core36_pressure \
MMTC_START_XAPP=1 \
OAI_REDCAP_DAPP_GATE_D_MARKER=1 \
OAI_REDCAP_DAPP_RA_RETRY_PRIORITY=1 \
MMTC_DAPP_STOP_NON_PRIORITY=1 \
MMTC_DAPP_PRIORITY_UES=36 \
MMTC_IPERF_ENABLE=0 \
MMTC_USE_EXISTING_CN_DB=0 \
MMTC_N_RB_DL=51 \
GNB_REDCAP_CONFIG=../../conf_files/gnb.sa.band78.fr1.51PRB.usrpb210.redcap.yaml \
MMTC_GNB_EXTRA_OPTIONS="--gNBs.[0].do_CSIRS 0 --gNBs.[0].do_SRS 0" \
rtk bash redcap_interface/redcap_mmtc_stage_scan.sh
```

## Evidence Artifacts

| Item | Path |
|---|---|
| Baseline batch summary | `test_log/compiler_logs/mmtc_stage_scan_2026-07-10_01-58-27_summary.log` |
| Baseline batch run log | `test_log/compiler_logs/mmtc_stage_scan_2026-07-10_01-58-27_ue36.log` |
| Baseline batch latency CSV | `test_log/compiler_logs/mmtc_smoke_2026-07-10_01-58-27_access_latency.csv` |
| dApp batch summary | `test_log/compiler_logs/mmtc_stage_scan_2026-07-10_02-00-43_summary.log` |
| dApp batch run log | `test_log/compiler_logs/mmtc_stage_scan_2026-07-10_02-00-43_ue36.log` |
| dApp batch latency CSV | `test_log/compiler_logs/mmtc_smoke_2026-07-10_02-00-43_access_latency.csv` |
| dApp batch gNB log | `test_log/compiler_logs/mmtc_smoke_2026-07-10_02-00-43_gnb.log` |
| Selector source baseline | `test_log/compiler_logs/mmtc_stage_scan_2026-07-10_01-58-27_summary.log` |
| Prior STOP+pause evidence | `test_log/compiler_logs/mmtc_stage_scan_2026-07-10_01-51-15_ue36.log` |
| Post-hook source build | `test_log/build_logs/build_nr-softmodem_2026-07-10_02-14-47_ra-retry-priority.log` |
| Post-hook image rebuild | `test_log/build_logs/rebuild_local_oai_images_2026-07-10_02-15-34_ra-retry-priority.log` |

## Batch-Start Marker

| Run | Marker |
|---|---|
| Baseline | `Starting sampled UE services in one zero-gap compose call` |
| dApp | `Starting sampled UE services in one zero-gap compose call` |

## Selector Result

| Selected UE | Reason |
|---:|---|
| 36 | highest observed `ra_retry_count=452`, `pucch_resource_reject_count=46`, and `no_tun` in the baseline evidence |

## Health Summary

| Run | sample | running | attach | pdu | tun | forward_ping_ok | gnb_restart | failures |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Baseline batch-start | 36 | 36 | 17 | 17 | 17 | 17 | 0 | 19 |
| dApp batch-start | 36 | 36 | 17 | 17 | 17 | 17 | 0 | 19 |
| dApp minus Baseline | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

## Launch-to-TUN Comparison

| Run | Rows | TUN Success | No TUN | Median ms | p95 ms | Max ms |
|---|---:|---:|---:|---:|---:|---:|
| Baseline batch-start | 36 | 17 | 19 | 37651 | 43189 | 44453 |
| dApp batch-start | 36 | 17 | 19 | 37687 | 43991 | 44369 |
| dApp minus Baseline | 0 | 0 | 0 | +36 | +802 | -84 |

## STOP Evidence Boundary

- [Current Batch ACK]: `test_log/compiler_logs/mmtc_stage_scan_2026-07-10_02-00-43_ue36.log` contains `[RedCap dApp wrapper STOP] ACK selected_ues=36 action=pause`.
- [Current Batch Limitation]: selected UE36 did not create `oaitun_ue1`, so sampled user-plane traffic cannot validate STOP effectiveness for the selected priority UE.
- [Prior Pause Evidence]: `test_log/compiler_logs/mmtc_stage_scan_2026-07-10_01-51-15_ue36.log` contains `Quiesced 35 non-selected UE container(s) before iperf3` and `Unpausing 35 non-selected UE container(s) after iperf3`.
- [Prior STOP Blocker]: the sampled UL iperf client timed out across bounded `timeout 20s docker exec ... iperf3` attempts.

## Validation

### Pre-Hook A/B Evidence Check

```bash
rtk python3 -B agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/gate_e_64ue_stage_check.py \
  --stage core36-pressure \
  --baseline-summary-log test_log/compiler_logs/mmtc_stage_scan_2026-07-10_01-58-27_summary.log \
  --dapp-summary-log test_log/compiler_logs/mmtc_stage_scan_2026-07-10_02-00-43_summary.log \
  --baseline-latency-log test_log/compiler_logs/mmtc_smoke_2026-07-10_01-58-27_access_latency.csv \
  --dapp-latency-log test_log/compiler_logs/mmtc_smoke_2026-07-10_02-00-43_access_latency.csv \
  --dapp-gnb-log test_log/compiler_logs/mmtc_smoke_2026-07-10_02-00-43_gnb.log
```

- [Checker Result]: PASS before the RA retry-priority strict condition was added, `Gate E-Core36 zero-gap pressure A/B evidence found`.
- [Checker Boundary]: PASS means valid pre-hook A/B evidence exists; it does not mean mitigation improvement.
- [Post-Hook Checker Boundary]: current checker now expects `dapp_ra_retry_priority=1`; the pre-hook dApp summary from `2026-07-10_02-00-43` must not be used as post-hook mitigation proof.

### Post-Hook Source And Image Readiness

```bash
rtk bash -n redcap_interface/bash_library/fc_mmtc_smoke_validation.sh redcap_interface/bash_library/fc_mmtc_stage_scan.sh ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/scripts/generate_mmtc_overlay.sh
env PYTHONDONTWRITEBYTECODE=1 rtk python3 -B agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/check_dapp_xapp_sdk_test_validation.py
rtk openspec validate redcap-dapp-xapp-sdk-test-validation --strict
CCACHE_DIR=/tmp/ccache CCACHE_TEMPDIR=/tmp/ccache-tmp cmake --build --preset default --target nr-softmodem
rtk bash -lc 'redcap_interface/redcap_rebuild_local_oai_images.sh'
```

- [Source Build]: PASS, `nr-softmodem` relinked with the RA scheduler hook.
- [Image Rebuild]: PASS, local `oai-gnb:latest` and `oai-nr-ue:latest` rebuilt from workspace.
- [Runtime Rerun]: BLOCKED. Starting the new core36 baseline/dApp Docker compose run required escalation, but the automatic review rejected it because workspace credits were exhausted.

## Engineering Interpretation

- [What Passed]: the script now truly starts 36 sampled UE services in one zero-gap compose call.
- [What Passed]: selector identifies the most failed UE from baseline evidence.
- [What Did Not Pass]: dApp did not improve attach/PDU/TUN or failures under true batch-start pressure.
- [What Is Now Wired]: gNB has a real RA-state scheduler action for retry-first RA handling under `OAI_REDCAP_DAPP_RA_RETRY_PRIORITY=1`.
- [What Is Not Yet Proven]: the retry-first scheduler action has not yet been remeasured in a fresh core36 A/B runtime run.
- [What Cannot Be Claimed]: no evidence that dApp mitigates 56 UE access pressure or reduces access latency in this run.
- [Next Pull]: rerun post-hook batch-start A/B once Docker compose escalation is available; separately inspect user-plane STOP/iperf reachability.
