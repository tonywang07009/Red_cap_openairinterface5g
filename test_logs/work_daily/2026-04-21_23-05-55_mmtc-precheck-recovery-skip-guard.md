# Work Daily Log
## Session Metadata
- Date: 2026-04-21 23:10
- Agent Session ID: N/A
- Task Slug: mmtc-precheck-recovery-skip-guard

## Milestone & Sub-task Reference
- Milestone: [Milestone 5: Compose Architecture, Integration & UL Throughput Targets]
- Sub-task: [Stage60 restart RCA stabilization] 避免 precheck 偵測到 gNB 重啟後，再觸發 60 UE 全量 recovery 導致二次重啟
- Status: [COMPLETED]

## What Was Done
- [Code Change] `ci-scripts/redcap_mmtc_smoke_validation.sh`
  - 新增 `MMTC_RECOVER_ON_PRECHECK_GNB_RESTART`（預設 `0`）。
  - 當 precheck 已檢出 `gNB restart` 且未明確開啟上述旗標時，跳過 UE auto-recovery，避免 recovery storm。
  - 保留原有 recovery 機制，可透過 `MMTC_RECOVER_ON_PRECHECK_GNB_RESTART=1` 強制啟用。
  - 更新 runtime 顯示的 recovery config 行，納入新旗標。
- [Validation] 撤回本回合無效實驗：
  - 回退 `openair2/LAYER2/NR_MAC_gNB/nr_radio_config.c` 的 SR offset 試驗改動。
  - 回退 `ci-scripts/conf_files/gnb.sa.band78.fr1.106PRB.usrpb210.redcap.yaml` 的 `ra_ResponseWindow` 試驗改動。

## 3GPP Spec Clauses Referenced
- TS 38.321 Section 5.1 — Random Access procedure（高併發 attach 下 Msg2/Msg3/Msg4 視窗與穩定度觀測）。
- TS 38.331 Section 5.3.1 — RRC connection/reconfiguration（attach / reconfiguration 完成比對）。

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| `bash -n ci-scripts/redcap_mmtc_smoke_validation.sh` | Pass | Script syntax | 無語法錯誤 |
| `env MMTC_STAGE_LIST=60 MMTC_REBUILD_IMAGES_BEFORE_SCAN=0 MMTC_UE_START_GAP=0 MMTC_GNB_WARMUP=10 MMTC_SLEEP_AFTER_UP=25 bash ci-scripts/redcap_mmtc_stage_scan.sh` (before skip-guard) | Fail | Runtime stage60 | `[SUMMARY] ... attach=48 ... gnb_restart=2 ...` |
| 同上 command (after skip-guard) | Fail | Runtime stage60 | `[SUMMARY] ... attach=47 ... gnb_restart=1 ...`，成功避免第二次重啟風暴 |

## Known Issues / Blockers
- [Core blocker] stage60 仍出現 gNB 主程序被 `Killed`（restart=1），attach 仍卡在 ~47~57 區間，尚未根治。
- [Inference] 目前已證實「二次重啟」有一部分是腳本 recovery storm 放大，不是唯一根因。

## Next Step
- 針對 `mmtc_smoke_*_gnb.log` 的第一次 `Main child exited with signal 'Killed'` 前後窗口做精準 RCA：
  - 比對 `UID exceeds PUCCH resource budget`、`Cannot schedule SR`、`exceeded RA window` 三者的時序。
  - 先在 gNB/MAC 層提出最小修補（避免在高負載下進入 kill 前連鎖）。
