# Work Daily Log
## Session Metadata
- Date: 2026-04-12 19:16
- Agent Session ID: N/A
- Task Slug: redcap-m5-pucch-budget-bwp-fit-fix

## Milestone & Sub-task Reference
- Milestone: [Milestone 5: Integration & UL Throughput Targets]
- Sub-task: [Stabilize RedCap RFsim SA runtime by fitting PUCCH reservation to the active RedCap initial BWP]
- Status: [COMPLETED]

## What Was Done
- [RCA] 依據 host log 確認 [oai-gnb] 在 UE [RA-Msg3] 後於 `get_nb_pucch2_per_slot()` 觸發 assert，而非 [FlexRIC-disabled] 啟動前崩潰。
- [Code Change] 在 [openair2/LAYER2/NR_MAC_gNB/nr_radio_config.c] 新增 `get_max_supported_ues_for_pucch()`，依 [current BWP size] 計算可容納的 [PUCCH UE budget]。
- [Code Change] 將 `get_nb_pucch2_per_slot()` 從固定使用 [MAX_MOBILES_PER_GNB] 改為使用 [BWP-fit UE budget]，避免 [51-PRB RedCap BWP] 對 [64 UEs] 做不可能的預留。
- [Code Change] 將 `verify_radio_configuration()` 的 [PUCCH resource validation] 改為使用 [max_supported_ues]，並在 [uid exceeds budget] 時回傳 reject，而不是對所有 RedCap 小 BWP 直接 abort。
- [Context] 保留先前本日已完成的兩個 runtime unblock：
  - [ci-scripts/conf_files/gnb.sa.band78.fr1.106PRB.usrpb210.redcap.yaml] 修正 `rfsimulator:` 為 [mapping]，讓 gNB 正確進入 [server] role。
  - [ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/docker-compose.yml] 移除 [UE1/UE2 `--telnetsrv`]，排除 [ASAN ODR violation]。

## 3GPP Spec Clauses Referenced
- TS 38.306 Section 4.2.21.1 — [RedCap UE] 在 [FR1] 受限於較小帶寬，且可使用獨立 [initial DL/UL BWP]；本次修補的前提是 [51-PRB RedCap initial BWP] 屬於合理部署，不應被 OAI 以 [64-UE global PUCCH reservation] 直接否決。
- TS 38.321 Section 5.1 — [Random Access procedure]；host log 已達 [Msg3 transmitted]，因此本次故障定位在 [RA 之後的 gNB RRC/MAC resource preparation]，不是 [RF sync / PBCH / SIB1 / RAR] 階段。

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| `cmake --build --preset default --target nr-softmodem -j2` | Pass | [nr-softmodem target] | 完整 build 成功，最終完成 [Linking CXX executable nr-softmodem] |
| `cmake --build --preset default --target nr-softmodem -j2 | tee test_log/build_logs/nr-softmodem_redcap_pucch_fix_2026-04-12_19-16-36.log` | Pass | [incremental rebuild] | 已留下 timestamped build log |
| `git diff --check -- openair2/LAYER2/NR_MAC_gNB/nr_radio_config.c` | Pass | [modified file formatting] | 無 whitespace / patch format 問題 |

## Known Issues / Blockers
- [Host Docker runtime] 無法在目前 sandbox 內執行，因此 [disabled E2 mode] 是否已完整穿過 [UE attach / IP assignment / 302001 / 302002] 仍需 host 重跑確認。
- [enabled E2 mode] 先前已確認仍卡在 [FlexRIC plugin loading / ABI mismatch]；此問題尚未處理。
- [xapp-rc-moni log analysis] 在既有 CI 分析器中仍可能被標為 [passed analysis False]，但這不是本次 [gNB abort] 的主因。

## Next Step
- 在 host 重新執行：
  - `REDCAP_USE_LOCAL_OAI_IMAGES=1 REDCAP_E2_AGENT_MODE=disabled bash ci-scripts/redcap_runtime_host_validation.sh`
- 若 [disabled] 已可讓 [UE1/UE2] attach 並完成 [302001 / 302002] 前半流程，下一步回到 [enabled] 模式，針對 [FlexRIC plugin ABI mismatch] 做 [plugin inventory / symbol / build-chain consistency] 精查。
