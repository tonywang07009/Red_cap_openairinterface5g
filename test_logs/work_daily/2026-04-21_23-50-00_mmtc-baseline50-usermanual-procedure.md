# Work Daily Log
## Session Metadata
- Date: 2026-04-21 23:50
- Agent Session ID: N/A
- Task Slug: mmtc-baseline50-usermanual-procedure

## Milestone & Sub-task Reference
- Milestone: [Milestone 5: Compose Architecture, Integration & UL Throughput Targets]
- Sub-task: [50 UE 短期驗收基線文件化] 建立可重複執行之系統化使用步驟
- Status: [COMPLETED]

## What Was Done
- [Validation] 以相同條件完成 stage50 連跑兩輪，均為 PASS。
- [Docs] 建立 `usermaun/系統化使用步驟.md`：
  - 定義 [MMTC_BASELINE_50] 驗收條件。
  - 提供兩輪重現性驗證步驟與判定規則。
  - 收錄常見失敗排查入口與已驗證參考 log。
- [Directory] 依需求使用 `mkdir -p usermaun` 建立手冊目錄。

## 3GPP Spec Clauses Referenced
- TS 38.321 Section 5.1 — Random Access procedure（高併發 attach 基本行為對照）。
- TS 38.331 Section 5.3.1 — RRC connection establishment（attach/pdu/tun 穩定性驗證背景）。

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| `env MMTC_STAGE_LIST=50 MMTC_REBUILD_IMAGES_BEFORE_SCAN=0 MMTC_UE_START_GAP=0 MMTC_GNB_WARMUP=10 MMTC_SLEEP_AFTER_UP=25 bash ci-scripts/redcap_mmtc_stage_scan.sh` (run#1) | Pass | Runtime stage50 | `mmtc_stage_scan_2026-04-21_23-36-58_summary.log` 全指標 50/50 |
| 同上 command (run#2) | Pass | Runtime stage50 | `mmtc_stage_scan_2026-04-21_23-40-02_summary.log` 全指標 50/50 |
| 手冊文件建立 | Pass | Doc deliverable | `usermaun/系統化使用步驟.md` |

## Known Issues / Blockers
- stage60/64 仍非穩定通過，需繼續針對 gNB `Killed` 做 RCA。

## Next Step
- 以手冊中的 [MMTC_BASELINE_50] 流程作為日常回歸守門，再逐步推進 52/56/60 階段化壓測。
