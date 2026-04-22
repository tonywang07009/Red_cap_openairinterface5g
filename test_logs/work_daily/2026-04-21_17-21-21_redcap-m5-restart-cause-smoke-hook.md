# Work Daily Log
## Session Metadata
- Date: 2026-04-21 17:21
- Agent Session ID: N/A
- Task Slug: redcap-m5-restart-cause-smoke-hook

## Milestone & Sub-task Reference
- Milestone: M5 RCA [restart-cause instrumentation]
- Sub-task: 在 smoke validation 偵測 gNB restart 時即時輸出 [CGDBG][RESTART_CAUSE] 摘要
- Status: [COMPLETED]

## What Was Done
- 修改 `ci-scripts/redcap_mmtc_smoke_validation.sh`：
  - 新增函式 `capture_gnb_restart_cause()`。
  - 在函式中加入 `docker inspect --format '{{json .State}}'` 擷取並寫入獨立 log。
  - 在函式中加入 `docker logs --tail 300` 擷取並寫入獨立 log。
  - 產生單行 `[CGDBG][RESTART_CAUSE]` 摘要（restart_count/status/exit_code/oom_killed/error/started_at/finished_at/marker excerpt）。
  - 新增變數 `GNB_RESTART_STATE_JSON_LOG`、`GNB_RESTART_TAIL300_LOG`。
  - 在 `GNB_RESTART_COUNT != 0` 分支呼叫 `capture_gnb_restart_cause`。

## 3GPP Spec Clauses Referenced
- TS 38.321 Section 5.1 — RA procedure context（用於大量 UE attach 階段的事件窗口對照）。
- TS 38.331 Section 5.3.5 — RRC connection/reconfiguration context（用於 CellGroupConfig 前後窗口的 RCA 對照）。
- ⚠ Needs Verification: 本次屬 [diagnostic instrumentation]，未改動 RRC/MAC 協定流程本身。

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| `bash -n ci-scripts/redcap_mmtc_smoke_validation.sh` | Pass | N/A | 腳本語法正常 |
| `env MMTC_STAGE_LIST=60 ... bash ci-scripts/redcap_mmtc_stage_scan.sh` | Fail | N/A | Docker socket 權限錯誤：`permission denied while trying to connect to the docker API at unix:///var/run/docker.sock`；log: `test_log/compiler_logs/mmtc_stage60_2026-04-21_17-21-14.log` |

## Known Issues / Blockers
- 目前執行環境無法存取 Docker daemon（socket 權限），因此無法完成 stage60 runtime 驗證與 marker 實際觀測。

## Next Step
- 在具備 Docker 權限的環境重跑：
  - `env MMTC_STAGE_LIST=60 MMTC_SEGV_BACKTRACE=1 MMTC_UE_START_GAP=0 MMTC_GNB_WARMUP=10 MMTC_SLEEP_AFTER_UP=25 bash ci-scripts/redcap_mmtc_stage_scan.sh`
- 驗證 marker：
  - `rg -n "\[CGDBG\]\[RESTART_CAUSE\]|\[CGDBG\]\[ENTRYPOINT\]|\[CGDBG\]\[SIG\]|child exit rc" test_log/compiler_logs/mmtc_smoke_<timestamp>_gnb.log`
