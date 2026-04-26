# Work Daily Log
## Session Metadata
- Date: 2026-04-26 19:58
- Agent Session ID: N/A
- Task Slug: px-v1-m5-t1-prb-control-pathfix-rerun
- Task ID: M5-T1
- Batch: B
- Project Path: agent_doc/Project_management/projects/redcap_mmtc_priority_execution_v1/project_plan.md

## Milestone & Sub-task Reference
- Milestone: [M5: Compose + mMTC]
- Sub-task: [M5-T1] fixed-UE path UE2 user-plane blocker RCA
- Status: [IN-PROGRESS]

## What Was Done
- 修正 XML 測項 `302005` 腳本路徑：
  - `ci-scripts/xml_files/container_5g_flexric_rfsim_redcap.xml`
  - 從 `ci-scripts/redcap_send_ul_prb_control.sh` 改為 `./redcap_send_ul_prb_control.sh`
- 重新執行 host validation：
  - `REDCAP_USE_LOCAL_OAI_IMAGES=1 REDCAP_E2_AGENT_MODE=enabled bash ci-scripts/redcap_runtime_host_validation.sh container_5g_flexric_rfsim_redcap.xml`
- 新執行 log：
  - `test_log/compiler_logs/m5-t1_host_validation_after302005fix_2026-04-26_19-55-09.log`

## 3GPP Spec Clauses Referenced
- TS 38.321 Section 5 — UL scheduling and control behavior context.
- TS 38.331 Section 6 — RRC signaling context for RedCap attach and config.

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| `302002/302003/302004` | Pass | RedCap UE identification + SIB1 BWP evidence | OK |
| `020005` | Pass | UE1/UE2 user-plane ping | 0% packet loss |
| `030001` | Pass | UE2 UL 50 Mbps baseline | Receiver 50 Mbps, 0% loss |
| `302005` | Fail | E2 xApp UL PRB cap path | 由「找不到腳本」轉為 xApp runtime assertion：`dec_ran_func: Assertion 'RAN Function not found' failed` |
| `302006/030002` | Fail (Skipped) | PRB cap verify + post-cap UL throughput | 因 `302005` 失敗而 skip |

## Known Issues / Blockers
- `302005` 新阻塞為 FlexRIC/xApp 執行期斷言，不再是路徑缺檔。
- 相關 build log：`test_log/build_logs/redcap_ul_prb_ctrl_xapp_build_2026-04-26_19-57-52.log`。

## Next Step
- 針對 `redcap_send_ul_prb_control.sh` / `redcap_ul_prb_ctrl_xapp` 進行 RCA：確認 RAN Function 註冊/查找條件與目前 nearRT-RIC runtime 是否匹配，修復後重跑 `M5-T1`。
