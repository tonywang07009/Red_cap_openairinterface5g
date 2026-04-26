# Work Daily Log
## Session Metadata
- Date: 2026-04-26 19:12
- Agent Session ID: N/A
- Task Slug: px-v1-m5-t1-fixed-ue-up-blocker-rca
- Task ID: M5-T1
- Batch: B
- Project Path: agent_doc/Project_management/projects/redcap_mmtc_priority_execution_v1/project_plan.md

## Milestone & Sub-task Reference
- Milestone: [M5: Compose + mMTC]
- Sub-task: [M5-T1] fixed-UE path UE2 user-plane blocker RCA
- Status: [BLOCKED]

## What Was Done
- 以升權方式執行：
  - `REDCAP_USE_LOCAL_OAI_IMAGES=1 REDCAP_E2_AGENT_MODE=enabled bash ci-scripts/redcap_runtime_host_validation.sh container_5g_flexric_rfsim_redcap.xml`
- 本次批次輸出紀錄於 `test_log/compiler_logs/m5-t1_host_validation_escalated_2026-04-26_19-09-04.log`。
- 成功取得 runtime 證據：
  - UE attach / RedCap辨識 (`302002`)
  - SIB1 DL/UL BWP (`302003`/`302004`)
  - `020005` ping OK（0% packet loss）
  - `030001` UL 50 Mbps UDP OK（Receiver 50 Mbps, loss 0%）
- 失敗點：`302005` 執行 `ci-scripts/redcap_send_ul_prb_control.sh` 時回報 `No such file or directory`，導致 `302006` 與 `030002` 被 skip。

## 3GPP Spec Clauses Referenced
- TS 38.321 Section 5 — UL scheduling and MAC behavior context.
- TS 38.331 Section 6 — RRC config context for RedCap signaling.
- TS 38.306 Section 4.2.21.1 — RedCap capability context (runtime summary mapping).

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| `333331/302001/333332/302002/302003/302004` | Pass | fixed-UE attach + RedCap + SIB1 BWP evidence | 皆為 OK |
| `020005` | Pass | UE1/UE2 user-plane reachability | packet loss 0% |
| `030001` | Pass | UE2 UL throughput baseline | Receiver 50.00 Mbps, loss 0% |
| `302005` | Fail | E2 xApp UL PRB cap control path | `ci-scripts/redcap_send_ul_prb_control.sh` 缺檔 |
| `302006` / `030002` | Fail (Skipped) | PRB cap applied verification + post-cap UL throughput | 因 `302005` 失敗連帶跳過 |

## Known Issues / Blockers
- `ci-scripts/redcap_send_ul_prb_control.sh` 路徑不存在（或檔名不一致），E2 PRB 控制流程中斷。
- `M5-T1` 目前屬於 [BLOCKED]，需先修正控制腳本路徑或對應呼叫點。

## Next Step
- 執行 [M5-T2] `ci-scripts/redcap_mmtc_smoke_validation.sh`，收集 32/64 UE staged validation 現況；若再受同類腳本缺檔影響，彙整失敗訊息並提出修復 patch 目標。
