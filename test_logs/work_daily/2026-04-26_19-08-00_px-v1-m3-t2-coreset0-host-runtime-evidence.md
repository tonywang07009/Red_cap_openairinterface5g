# Work Daily Log
## Session Metadata
- Date: 2026-04-26 19:08
- Agent Session ID: N/A
- Task Slug: px-v1-m3-t2-coreset0-host-runtime-evidence
- Task ID: M3-T2
- Batch: B
- Project Path: agent_doc/Project_management/projects/redcap_mmtc_priority_execution_v1/project_plan.md

## Milestone & Sub-task Reference
- Milestone: [M3: BWP & CORESET#0]
- Sub-task: [M3-T2] CORESET#0 Case A/B host runtime evidence completion
- Status: [BLOCKED]

## What Was Done
- 執行 `bash ci-scripts/redcap_runtime_case_matrix.sh container_5g_flexric_rfsim_redcap.xml`。
- 執行輸出紀錄於 `test_log/compiler_logs/m3-t2_case_matrix_2026-04-26_19-07-15.log`。
- 產生 Case A/B runtime log：
  - `test_log/compiler_logs/redcap_runtime_host_case-a_2026-04-26_19-07-15.log`
  - `test_log/compiler_logs/redcap_runtime_host_case-b_2026-04-26_19-07-16.log`
  - `test_log/compiler_logs/redcap_runtime_matrix_2026-04-26_19-07-15.log`

## 3GPP Spec Clauses Referenced
- TS 38.331 Section 6.3.2 — initialDownlinkBWP-RedCap-r17 context for RedCap BWP signaling.
- TS 38.213 Section 13 — CORESET#0 / PDCCH monitoring related behavior.

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| `bash ci-scripts/redcap_runtime_case_matrix.sh container_5g_flexric_rfsim_redcap.xml` | Fail | Case A/B host runtime evidence | 出現 `Docker access is required to run CI scenarios locally`，指令 exit code=1 |

## Known Issues / Blockers
- Docker 權限不足導致 scenario 無法完整跑完。
- `020005` / `030001` / `302005` / `302006` / `030002` 在 `test_results.html` 缺失。

## Next Step
- 進入 [M5-T1]：執行 host validation，確認 UE2 user-plane blocker 是否仍可重現；若同樣受 Docker 權限阻塞，需改在 Docker-enabled host 驗證。
