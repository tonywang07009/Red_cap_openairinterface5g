# Work Daily Log
## Session Metadata
- Date: 2026-04-21 12:03
- Agent Session ID: N/A
- Task Slug: redcap-m5-stage60-restart-cause-instrumentation

## Milestone & Sub-task Reference
- Milestone: M5 RCA [survivor vs failed]
- Sub-task: [最小 restart-cause instrumentation patch] + [stage60 rerun]
- Status: [COMPLETED]

## What Was Done
- 在 `executables/softmodem-common.c` 新增 `mmtc_is_fatal_signal()`，擴充 fatal signal 覆蓋到 `SIGSEGV/SIGABRT/SIGBUS/SIGILL/SIGFPE`。
- 在 `signal_handler()` 新增 `[CGDBG][SIG] caught fatal signal ...` marker 與 `backtrace_symbols_fd(...)`。
- 在 `set_softmodem_sighandler()` 於 `MMTC_SEGV_BACKTRACE=1` 時安裝上述 fatal signals handler。
- 重新執行 `stage60`：
  - `env MMTC_STAGE_LIST=60 MMTC_SEGV_BACKTRACE=1 MMTC_REBUILD_IMAGES_BEFORE_SCAN=0 MMTC_UE_START_GAP=0 MMTC_GNB_WARMUP=10 MMTC_SLEEP_AFTER_UP=25 bash ci-scripts/redcap_mmtc_stage_scan.sh`
- 產生新摘要與 stage log：
  - `test_log/compiler_logs/mmtc_stage_scan_2026-04-21_11-58-44_summary.log`
  - `test_log/compiler_logs/mmtc_stage_scan_2026-04-21_11-58-44_ue60.log`

## 3GPP Spec Clauses Referenced
- TS 38.321 Section 5.1 — Random Access procedure context (觀察 UE 連線規模壓力下的 RA 相關失敗行為)。
- TS 38.331 Section 5.3.5 — RRC connection/reconfiguration procedure context (對齊 CellGroupConfig 套用前後觀測窗口)。
- ⚠ Needs Verification: 本次 patch 為 [診斷 instrumentation]，不改協定流程，條文僅作故障定位脈絡對照。

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| stage60 smoke rerun | Fail | N/A | `[SUMMARY] sample=60 running=3 attach=48 pdu=48 tun=0 forward_ping_ok=0 reverse_ping_ok=0 gnb_restart=1 failures=61` |
| UE fatal handler install marker | Pass | N/A | 多個 `*_ue*_docker.log` 有 `[CGDBG][SIG] MMTC_SEGV_BACKTRACE=1, installing fatal signal handlers...` |
| fatal crash marker (`caught fatal signal`) | Fail | N/A | 本輪 `gnb.log`/`ue*_markers.log` 未見 `caught fatal signal` |

## Known Issues / Blockers
- gNB restart 仍發生，但未捕捉到 `caught fatal signal` marker。
- `gnb.log` 可見 `[INFO tini] Main child exited with signal Killed`，較像外部 kill 或非目前 handler 可截獲路徑。
- 目前 `MMTC_SEGV_BACKTRACE=1` 的 install marker 主要出現在 UE docker log，gNB 側 marker 不明顯。

## Next Step
- 最小下一步：在 gNB entrypoint/compose 增加 `[MMTC_SEGV_BACKTRACE=1]` 明確注入與回顯 marker，並補 `SIGTERM/SIGKILL-path` 的 pre-exit marker（不改主流程）。
- 驗證命令：
  - `env MMTC_STAGE_LIST=60 MMTC_SEGV_BACKTRACE=1 MMTC_UE_START_GAP=0 MMTC_GNB_WARMUP=10 MMTC_SLEEP_AFTER_UP=25 bash ci-scripts/redcap_mmtc_stage_scan.sh`
  - `rg -n "\[CGDBG\]\[SIG\]|Main child exited with signal" test_log/compiler_logs/mmtc_smoke_<timestamp>_*.log`
