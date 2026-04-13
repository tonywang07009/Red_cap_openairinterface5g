# Work Daily Log
## Session Metadata
- Date: 2026-04-12 19:08
- Agent Session ID: N/A
- Task Slug: redcap-m5-pucch-budget-assert-rca

## Milestone & Sub-task Reference
- Milestone: [Milestone 5: Integration & UL Throughput Targets]
- Sub-task: [Root-cause analysis of gNB abort after UE Msg3 in disabled E2 mode]
- Status: [COMPLETED]

## What Was Done
- 讀取 [disabled runtime] 新一輪 [gNB/UE artifact logs]，確認 [rfsimulator section] 修正已被帶入新產生的 runtime YAML。
- 確認 [UE1/UE2] 已不再卡在 [ASAN telnet] 或 [PBCH sync]；兩者都完成 [PBCH decode]、[SIB1 decode]、[RAR-Msg2]、[RA-Msg3 transmitted]。
- 確認 [gNB] 在收到 [UE Msg3] 後，於 [prepare_initial_ul_rrc_message] / [verify_radio_configuration] 路徑上 [Abort]。
- 鎖定實際 assertion：`Cannot allocate all required PUCCH resources for max number of 64 UEs in BWP with 51 PRBs`。
- 交叉比對程式碼，確認 [MAX_MOBILES_PER_GNB] 目前為 [64]，而 [RedCap initial BWP] 為 [51 PRBs] 時，現行 [PUCCH1 + PUCCH2] 預留檢查在數學上不可滿足。

## 3GPP Spec Clauses Referenced
- TS 38.306 Section 4.2.21.1 — [RedCap UE] FR1 reduced capability / reduced BWP size 為本 scenario 的設計前提。
- TS 38.331 Section 5.2.2.4.2 — [RedCap SIB1] 被 UE 成功解碼，代表 attach 已進入 common configuration 套用階段。

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| [disabled runtime YAML carries fixed rfsimulator section] | [Pass] | [Runtime config generation] | `rfsimulator.serveraddr: server` 已存在於新 YAML |
| [UE1 PBCH / SIB1 / RAR / Msg3 path] | [Pass] | [RF attach pre-RRC] | [UE1] 完成 [PBCH decode]、[SIB1 decoded]、[RA-Msg3 transmitted] |
| [UE2 PBCH path] | [Pass] | [RF attach pre-RRC] | [UE2] 至少完成 [PBCH decode] |
| [gNB post-Msg3 initial cell-group build] | [Fail] | [MAC/RRC config path] | [exit 134] due to [PUCCH resource budget assertion] |

## Known Issues / Blockers
- [Confirmed Root Cause]：`get_nb_pucch2_per_slot()` 以 [MAX_MOBILES_PER_GNB=64] 預留 [PUCCH] 資源，但 [RedCap BWP size=51] 無法滿足此檢查。
- [Code Reference]：`common/openairinterface5g_limits.h` 目前將 [MAX_MOBILES_PER_GNB] 設為 [64]；`nr_radio_config.c` 直接用該值做 [PUCCH] 預留。
- [⚠ Needs Verification]：下一步需決定是採 [scenario-aware PUCCH budgeting patch]，或恢復較小的 [global UE cap]。

## Next Step
- 優先實作 [scenario-aware PUCCH budget] 修正，讓 [51-PRB RedCap BWP] 不再因 [64-UE global reservation] 直接 abort。
- 修正後先重跑 [disabled E2 mode]，確認 [UE1 attach] 與 [302001/333332] 能再往下走。
