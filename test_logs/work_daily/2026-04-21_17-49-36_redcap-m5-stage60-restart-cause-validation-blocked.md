# Work Daily Log
## Session Metadata
- Date: 2026-04-21 17:49
- Agent Session ID: N/A
- Task Slug: redcap-m5-stage60-restart-cause-validation-blocked

## Milestone & Sub-task Reference
- Milestone: M5 RCA [restart-cause instrumentation]
- Sub-task: stage60 runtime 驗證 [CGDBG][RESTART_CAUSE] marker
- Status: [BLOCKED]

## What Was Done
- 重跑 `MMTC_STAGE_LIST=60` 驗證流程（含 `MMTC_SEGV_BACKTRACE=1`）。
- 依規範檢查最新 compiler log：`test_log/compiler_logs/mmtc_stage60_2026-04-21_17-49-11.log`。
- 用 symdex 定位 `ci-scripts/redcap_mmtc_stage_scan.sh` 的重建入口訊息（line 38）。

## 3GPP Spec Clauses Referenced
- TS 38.321 Section 5.1 — RA procedure context（stage60 attach window 觀測）。
- TS 38.331 Section 5.3.5 — RRC connection/reconfiguration context（CellGroupConfig 前後 RCA 視窗）。
- ⚠ Needs Verification: 本子任務為 runtime 驗證與診斷資料擷取，未變更協定流程。

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| `env MMTC_STAGE_LIST=60 ... bash ci-scripts/redcap_mmtc_stage_scan.sh` | Fail | N/A | 執行終端回報 `permission denied while trying to connect to the docker API at unix:///var/run/docker.sock` |
| log file capture | Pass | N/A | 產生 `test_log/compiler_logs/mmtc_stage60_2026-04-21_17-49-11.log`（僅含 stdout；stderr 錯誤於終端） |

## Known Issues / Blockers
- 當前工作環境無 Docker daemon 存取權限（`/var/run/docker.sock`），無法進行 stage60 runtime 與 gNB restart cause 實測。

## Next Step
- 在具 Docker 權限環境執行：
  - `env MMTC_STAGE_LIST=60 MMTC_SEGV_BACKTRACE=1 MMTC_UE_START_GAP=0 MMTC_GNB_WARMUP=10 MMTC_SLEEP_AFTER_UP=25 bash ci-scripts/redcap_mmtc_stage_scan.sh 2>&1 | tee test_log/compiler_logs/mmtc_stage60_<timestamp>.log`
- 驗證 marker：
  - `rg -n "\[CGDBG\]\[RESTART_CAUSE\]|\[CGDBG\]\[ENTRYPOINT\]|\[CGDBG\]\[SIG\]|child exit rc" test_log/compiler_logs/mmtc_smoke_<timestamp>_gnb.log`
