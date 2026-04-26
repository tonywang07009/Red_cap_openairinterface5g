# Work Daily Log
## Session Metadata
- Date: 2026-04-26 19:52
- Agent Session ID: N/A
- Task Slug: px-v1-m3-t2-coreset0-host-runtime-evidence-rerun
- Task ID: M3-T2
- Batch: B
- Project Path: agent_doc/Project_management/projects/redcap_mmtc_priority_execution_v1/project_plan.md

## Milestone & Sub-task Reference
- Milestone: [M3: BWP & CORESET#0]
- Sub-task: [M3-T2] CORESET#0 Case A/B host runtime evidence completion
- Status: [BLOCKED]

## What Was Done
- 以升權方式重跑：
  - `bash ci-scripts/redcap_runtime_case_matrix.sh container_5g_flexric_rfsim_redcap.xml`
- 執行輸出紀錄於 `test_log/compiler_logs/m3-t2_case_matrix_escalated_2026-04-26_19-42-54.log`。
- Case A / Case B 皆產生完整 summary 與 runtime logs：
  - `test_log/compiler_logs/redcap_runtime_host_case-a_2026-04-26_19-42-54.log`
  - `test_log/compiler_logs/redcap_runtime_host_case-b_2026-04-26_19-46-51.log`
  - `test_log/compiler_logs/redcap_runtime_matrix_2026-04-26_19-42-54.log`
- 已確認 CORESET#0 mode marker 存在：
  - Case A: `mode=case-a-full-cell`
  - Case B: `mode=case-b-edge-only` + `Case B edge-aligned PRB allocation`

## 3GPP Spec Clauses Referenced
- TS 38.331 Section 6.3.2 — initialDownlinkBWP-RedCap-r17 context.
- TS 38.213 Section 13 — CORESET#0 / PDCCH monitoring behavior.

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| `case-a` runtime matrix branch | Fail | attach + BWP + ping + UL50 + PRB control path | `302005` 失敗：`ci-scripts/redcap_send_ul_prb_control.sh` 缺檔，導致 `302006/030002` skip |
| `case-b` runtime matrix branch | Fail | CORESET#0 Case B + UE attach chain | `333332` 失敗：UE2 無法取得 IP / container not running，後續全 skip |

## Known Issues / Blockers
- [Case A blocker] `302005` 依賴腳本 `ci-scripts/redcap_send_ul_prb_control.sh` 不存在。
- [Case B blocker] UE2 attach 不穩定（IP 未分配，container 在檢查時非 running）。
- [Env note] log 顯示 prebuilt image tag；若要驗證本地 C patch，需重建/重標記 image。

## Next Step
- 先修正 [M5-T1] 的 `302005` 腳本路徑/名稱問題，再回頭重跑 `M3-T2` case matrix，避免 Case A 再次卡在同一點。
- 針對 Case B，先做 UE2 attach 失敗 RCA（容器退出原因與 gNB/UE關聯 log）。
