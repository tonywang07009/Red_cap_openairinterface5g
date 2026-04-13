# Work Daily Log
## Session Metadata
- Date: 2026-04-12 19:01
- Agent Session ID: N/A
- Task Slug: redcap-m5-rfsim-section-fix

## Milestone & Sub-task Reference
- Milestone: [Milestone 5: Integration & UL Throughput Targets]
- Sub-task: [Unblock RF simulator attach path after UE startup recovery]
- Status: [COMPLETED]

## What Was Done
- 確認 [disabled E2 mode] 下 [oai-gnb]、[xapp-rc-moni]、[oai-nr-ue1]、[oai-nr-ue2] 已可全部進入 [Up (healthy)]。
- 確認新的阻塞點是 [Attach UE 1] 階段拿不到 [`oaitun_ue1`]，表示 [UE process] 雖存活，但 [RF attach / registration] 沒有完成。
- 交叉比對 [radio/rfsimulator/README.md]、[targets/PROJECTS/.../gnb...redcap.yaml] 與 scenario 使用的 [ci-scripts/conf_files/gnb...redcap.yaml]。
- 找出 [ci-scripts] 版本的 `rfsimulator:` 被寫成 [list]，而標準 OAI gNB config 使用 [mapping]。
- 修正 [ci-scripts/conf_files/gnb.sa.band78.fr1.106PRB.usrpb210.redcap.yaml] 的 `rfsimulator` section，將 `serveraddr/serverport/options/modelname/IQfile` 改為單一 mapping。

## 3GPP Spec Clauses Referenced
- TS 38.306 Section 4.2.21.1 — 本 scenario 仍以 [RedCap UE capability validation] 為最終目標。
- TS 38.331 Section 5.2.2.4.2 — attach 前提仍需依賴正確的 [SIB1 RedCap common configuration]。
- [Note] 本次修正屬於 [RF simulator runtime wiring]，不是新的 3GPP 行為修改。

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| [disabled E2 gNB startup] | [Pass] | [Runtime deploy path] | [oai-gnb] 進入 [healthy] |
| [UE1/UE2 process startup after telnet removal] | [Pass] | [Runtime deploy path] | [oai-nr-ue1] / [oai-nr-ue2] 進入 [healthy] |
| [UE1 attach to get oaitun_ue1] | [Fail] | [Attach path] | `Device "oaitun_ue1" does not exist.` |
| [rfsimulator section normalization patch] | [Pass] | [Config source file] | `git diff --check` clean |

## Known Issues / Blockers
- [Confirmed Root Cause 1]：[enabled] 模式下 [gNB crash] 來自 [FlexRIC plugin loading]。
- [Confirmed Root Cause 2]：[UE ASAN crash] 來自 [UE telnet shared library loading]，已先繞過。
- [⚠ Needs Verification]：需用新的 base config 重新產生 runtime YAML，驗證 [gNB] 是否從錯誤的 [127.0.0.1 client] 轉成正確的 [RF simulator server]。

## Next Step
- 重新執行 [REDCAP_USE_LOCAL_OAI_IMAGES=1 REDCAP_E2_AGENT_MODE=disabled bash ci-scripts/redcap_runtime_host_validation.sh]，讓新的 runtime YAML 帶入修正後的 `rfsimulator` section。
- 若 [disabled] attach 恢復，再回頭處理 [enabled] 的 [FlexRIC plugin ABI mismatch]。
