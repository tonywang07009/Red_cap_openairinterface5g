# Work Daily Log
## Session Metadata
- Date: 2026-04-21 13:37
- Agent Session ID: N/A
- Task Slug: redcap-m5-gnb-restart-cause-entrypoint-sigdiag

## Milestone & Sub-task Reference
- Milestone: M5 RCA [restart-cause instrumentation]
- Sub-task: [最小 gNB env + entrypoint signal diagnostic patch] + [stage60 rerun]
- Status: [COMPLETED]

## What Was Done
- 修改 `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/scripts/generate_mmtc_overlay.sh`：
  - 在 overlay `services` 頂層加入 `oai-gnb.environment.MMTC_SEGV_BACKTRACE`，確保 gNB 也收到診斷環境變數。
- 修改 `docker/scripts/gnb_entrypoint.sh`：
  - 新增 `[CGDBG][ENTRYPOINT]` 啟動 marker（顯示 `MMTC_SEGV_BACKTRACE` 與 `diag_mode`）。
  - 在 `MMTC_SEGV_BACKTRACE>0` 時採用最小診斷執行路徑：背景啟動 child、輸出 `launched child pid`、等待 child，輸出 `child exit rc=<code>`。
  - 增加 `TERM/INT/QUIT/HUP` trap marker，轉送 signal 到 child（僅診斷模式）。
- 修正回歸：
  - `executables/softmodem-common.c` 將 `set_softmodem_sighandler()` 中的 `LOG_W(...)` 改為 `dprintf(STDERR_FILENO,...)`，避免 gNB 在 logger 未就緒時早期崩潰。
- 實測流程：
  - 兩次重建 image（`ci-scripts/redcap_rebuild_local_oai_images.sh`）
  - 重跑 `stage60`（`MMTC_SEGV_BACKTRACE=1`）

## 3GPP Spec Clauses Referenced
- TS 38.321 Section 5.1 — RA procedure context (大量 UE 啟動階段觀察 gNB restart 對 attach 的影響)。
- TS 38.331 Section 5.3.5 — RRC connection/reconfiguration context (CellGroupConfig 前後窗口關聯觀測)。
- ⚠ Needs Verification: 本次變更屬診斷 instrumentation，未改 RRC/MAC 協定流程；條文用於 RCA 事件窗口對照。

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| stage60 (第一次，entrypoint patch 後) | Fail | N/A | `[SUMMARY] sample=60 running=60 attach=0 ... gnb_restart=3`；gNB 反覆 `child exit rc=139` |
| regression fix (`LOG_W` -> `dprintf`) local build | Pass | N/A | `env CCACHE_DISABLE=1 cmake --build --preset default --target nr-softmodem` 通過 |
| stage60 (第二次，修正後) | Fail | N/A | `[SUMMARY] sample=60 running=2 attach=48 pdu=48 tun=0 ... gnb_restart=1 failures=61` |
| gNB restart-cause marker availability | Pass | N/A | gNB log 出現 `[CGDBG][ENTRYPOINT] child exit rc=137` 與 `[CGDBG][SIG] ... installing fatal signal handlers` |

## Known Issues / Blockers
- stage60 仍失敗，主症狀未變：attach/pdu 48、tun 0、ping 0、failures 61。
- 本輪 gNB restart cause 已可量化為 `rc=137`（非先前不可見的 "Killed" 黑箱）。
- 尚未在 gNB log 捕獲 `caught fatal signal`（代表目前重啟主因非已安裝 fatal handler 直接攔截到的 signal 路徑）。

## Next Step
- 針對 `rc=137` 做最小後續診斷：
  - 在 `redcap_mmtc_smoke_validation.sh` 於偵測到 gNB restart 時，立即抓取一次 `docker inspect --format {{json .State}}` + 最近 300 行 gNB docker log，並輸出單行 `[CGDBG][RESTART_CAUSE]` 摘要。
- 驗證命令：
  - `env MMTC_STAGE_LIST=60 MMTC_SEGV_BACKTRACE=1 MMTC_UE_START_GAP=0 MMTC_GNB_WARMUP=10 MMTC_SLEEP_AFTER_UP=25 bash ci-scripts/redcap_mmtc_stage_scan.sh`
  - `rg -n "\[CGDBG\]\[ENTRYPOINT\]|\[CGDBG\]\[SIG\]|\[CGDBG\]\[RESTART_CAUSE\]|child exit rc" test_log/compiler_logs/mmtc_smoke_<timestamp>_gnb.log`
