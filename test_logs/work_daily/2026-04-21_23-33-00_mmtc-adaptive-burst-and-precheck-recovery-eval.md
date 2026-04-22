# Work Daily Log
## Session Metadata
- Date: 2026-04-21 23:33
- Agent Session ID: N/A
- Task Slug: mmtc-adaptive-burst-and-precheck-recovery-eval

## Milestone & Sub-task Reference
- Milestone: [Milestone 5: Compose Architecture, Integration & UL Throughput Targets]
- Sub-task: [Stage60 restart RCA stabilization] 降低 UE 啟動尖峰並驗證 precheck 後 recovery 策略
- Status: [COMPLETED]

## What Was Done
- [Code Change] `ci-scripts/redcap_mmtc_smoke_validation.sh`
  - 新增 [adaptive burst 啟動節流] 參數：
    - `MMTC_ADAPTIVE_BURST_ON_ZERO_GAP`（預設 `1`）
    - `MMTC_UE_START_BURST_THRESHOLD`（預設 `32`）
    - `MMTC_UE_START_BURST_SIZE`（預設 `8`）
    - `MMTC_UE_START_BURST_PAUSE`（預設 `2` 秒）
  - 當 `MMTC_UE_START_GAP=0` 且 sample UE 達門檻時，自動每批 pause，降低瞬時 attach 壓力。
  - 擴充 [precheck recovery mode]：
    - `MMTC_RECOVER_ON_PRECHECK_GNB_RESTART=0`：skip（預設）
    - `=1`：immediate recovery
    - `=2`：gentle recovery（使用 `MMTC_PRECHECK_RECOVERY_UE_GAP` / `MMTC_PRECHECK_RECOVERY_SETTLE`）
  - 保留預設為 `0`（skip），避免把 `gNB_restart` 預設拉高。

## 3GPP Spec Clauses Referenced
- TS 38.321 Section 5.1 — Random Access procedure（高併發 attach 的 RA 視窗與 Msg2 調度壓力）。
- TS 38.331 Section 5.3.1 — RRC connection establishment（attach / setup 完成率觀測）。

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| `bash -n ci-scripts/redcap_mmtc_smoke_validation.sh` | Pass | Script syntax | 無語法錯誤 |
| `env MMTC_STAGE_LIST=60 MMTC_REBUILD_IMAGES_BEFORE_SCAN=0 MMTC_UE_START_GAP=0 MMTC_GNB_WARMUP=10 MMTC_SLEEP_AFTER_UP=25 bash ci-scripts/redcap_mmtc_stage_scan.sh`（adaptive burst + precheck skip） | Fail | Runtime stage60 | `mmtc_stage_scan_2026-04-21_23-16-20_summary.log`: `running=2 attach=49 pdu=49 gnb_restart=1` |
| 同上 command（precheck gentle recovery mode=2） | Fail | Runtime stage60 | `mmtc_stage_scan_2026-04-21_23-21-55_summary.log`: `running=5 attach=51 pdu=50 gnb_restart=2`，有改善 attach 但觸發第 2 次 gNB restart |

## Known Issues / Blockers
- [Core blocker] stage60 仍出現 `Main child exited with signal 'Killed'`，尚未定位外部 kill 來源。
- [Observed tradeoff] gentle recovery 可提升 attach/pdu，但會放大 gNB 第二次重啟風險。
- [Environment limitation] `dmesg` 無法讀取（Operation not permitted），無法直接核對 kernel OOM 記錄。

## Next Step
- 進一步縮小 first kill 前 5~10 秒窗口，對齊三類事件時序：
  - `exceeded RA window`
  - `Cannot schedule SR. PRBs not available`
  - `UID exceeds PUCCH resource budget`
- 在不引入第二次重啟的前提下，評估 `MMTC_RECOVER_ON_PRECHECK_GNB_RESTART=1` + 更大 `RECOVERY_UE_GAP` 的折衷參數（先以 stage60 單點驗證）。
