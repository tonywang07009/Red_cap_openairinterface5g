# Work Daily Log
## Session Metadata
- Date: 2026-04-21 23:45
- Agent Session ID: N/A
- Task Slug: mmtc-enbapp-assessment-and-stage50-baseline

## Milestone & Sub-task Reference
- Milestone: [Milestone 5: Compose Architecture, Integration & UL Throughput Targets]
- Sub-task: [52/56 成功經驗回溯 + ENB_APP(eMTC)可移植性評估 + 50 UE 最低穩定基準驗證]
- Status: [COMPLETED]

## What Was Done
- [Analysis] 回溯 stage52 成功紀錄：
  - `mmtc_stage_scan_2026-04-21_11-07-59_summary.log`：52/56 全通。
  - `mmtc_stage_scan_2026-04-21_18-33-11_summary.log`：52/56 全通，60/64 失敗。
- [Analysis] 檢視 `openair2/ENB_APP` eMTC 實作：
  - `enb_config.c` 以 `eMTC_configured` gate + `fill_eMTC_configuration()` 入口整合。
  - `enb_paramdef_emtc.h` 提供集中式參數描述、預設值與檢查框架。
- [Analysis] 對照 NR gNB 現行 RedCap 配置：
  - `openair2/GNB_APP/gnb_config.c` 已有 `GNB_REDCAP_PARAMS_DESC`、`get_redcap_config()`、`get_redcap_initial_bwp_config()`。
  - 判定 ENB_APP(eMTC)不宜直接移植，但其 [參數化配置模式] 值得借鑑。
- [Validation] 依使用者要求測試 50 UE 最低穩定標準（同條件連跑兩次）：
  - `MMTC_STAGE_LIST=50 MMTC_REBUILD_IMAGES_BEFORE_SCAN=0 MMTC_UE_START_GAP=0 MMTC_GNB_WARMUP=10 MMTC_SLEEP_AFTER_UP=25`
  - 兩輪皆 `sample=50 running=50 attach=50 pdu=50 tun=50 forward_ping_ok=50 gnb_restart=0 failures=0`。

## 3GPP Spec Clauses Referenced
- TS 38.321 Section 5.1 — Random Access procedure（高併發 attach 下 RA 視窗行為）。
- TS 38.331 Section 5.3.1 — RRC connection establishment（attach / setup complete 穩定度）。

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| `env MMTC_STAGE_LIST=50 ... bash ci-scripts/redcap_mmtc_stage_scan.sh` (run#1) | Pass | Runtime stage50 | `mmtc_stage_scan_2026-04-21_23-36-58_summary.log` 全指標 50/50 |
| `env MMTC_STAGE_LIST=50 ... bash ci-scripts/redcap_mmtc_stage_scan.sh` (run#2) | Pass | Runtime stage50 | `mmtc_stage_scan_2026-04-21_23-40-02_summary.log` 全指標 50/50 |
| Stage52 historical pass check | Pass | Historical logs | 2026-04-21 11:07:59、18:33:11 皆 52/52 |

## Known Issues / Blockers
- stage60 以上仍有 gNB `Killed` 風險；60/64 尚未達穩定。
- eMTC 路徑為 LTE eNB 架構，無法直接套用於 NR gNB；需在 `openair2/GNB_APP` RedCap 管線落地。

## Next Step
- 以 [50 UE 穩定] 作為短期最低驗收線，先固定回歸。
- 針對 stage56→60 的拐點做配置分段（RA/SR/PUCCH）並在 `GNB_APP` RedCap 參數層新增可控開關。
