# RedCap Simulator Unit Test Report - 2026-04-09

## 1. Technical Background
- [RedCap UE] 需要在 [FR1] 下符合較低複雜度限制，核心約束包括 [20 MHz maximum bandwidth]、[1Rx mandatory / 2Rx optional]、以及 [no UL MIMO]。
- 本次工作集中在 [simulation integration]，不是完整實作 [Milestone 2/3] 的全部功能；目標是先讓 [rfsimulator + FlexRIC + RedCap UE capability injection] 的資產鏈可以穩定啟動與驗證。
- 另外，現有 [gNB bwp_list] 在模擬器場景中仍描述 [cell/common BWP]，而不是 [initialDownlinkBWP-RedCap-r17]；因此本次修正避免把 [full-cell BWP = 106 PRBs] 誤判為違規的 [RedCap initial BWP]。

## 2. Key C Functions / Data Structures Utilized in This Module
- [`get_bwp_config()`] in [`openair2/GNB_APP/gnb_config.c`](/home/tonywang/OAI/Red_cap_openairinterface5g/openair2/GNB_APP/gnb_config.c)
- [`nr_mac_config_t::redcap`] in [`openair2/LAYER2/NR_MAC_gNB/nr_mac_gNB.h`](/home/tonywang/OAI/Red_cap_openairinterface5g/openair2/LAYER2/NR_MAC_gNB/nr_mac_gNB.h)
- [`NR_DL_FRAME_PARMS`] and [`nr_validate_redcap_gnb_frame_parms()` / `nr_validate_redcap_ue_frame_parms()`] in [`openair1/PHY/INIT/nr_parms.c`](/home/tonywang/OAI/Red_cap_openairinterface5g/openair1/PHY/INIT/nr_parms.c)
- [`load_nr_redcap_config()`] in [`openair3/UICC/usim_interface.c`](/home/tonywang/OAI/Red_cap_openairinterface5g/openair3/UICC/usim_interface.c)

## 3. Test Results Summary Table
| Test Item | Pass-Fail Status | Code Coverage | Modification Logs |
| --- | --- | --- | --- |
| `test_nr_frame_params` | [Pass] | [⚠ Needs Verification] | Targeted test passed after building with `ASAN_OPTIONS=detect_leaks=0`; build log: [`test_nr_frame_params_build_2026-04-09_14-50-50.log`](/home/tonywang/OAI/Red_cap_openairinterface5g/test_log/compiler_logs/test_nr_frame_params_build_2026-04-09_14-50-50.log), test log: [`test_nr_frame_params_2026-04-09_14-50-50.log`](/home/tonywang/OAI/Red_cap_openairinterface5g/test_log/compiler_logs/test_nr_frame_params_2026-04-09_14-50-50.log) |
| `RedCap asset sanity check` | [Pass] | [N/A] | Confirmed [`nrue28-30.uicc.yaml`] carry valid `uicc0` and 15-digit IMSI; confirmed new XML parses successfully |

- [Modification Point] -> [Reason] -> [Before vs. After Comparison] -> [Discussion Point]
- [cp_bash.bash IMSI generation] -> [nrue28 之後會產生錯誤 IMSI 與錯誤 UICC label] -> [Before: `00101000000028`, `uicc27`; After: `001010000000028`, `uicc0`] -> [這是 [simulation asset chain] 的根因修補，後續新增 UE 不會再持續擴散壞檔]
- [nrue28-30.uicc.yaml regeneration] -> [既有資產已經被錯誤腳本生成] -> [Before: 缺少 `nrue_recap` / `cells`; After: 與 `nrue2` 模板一致並只替換 IMSI] -> [目前 [docker-compose] 用到 `nrue28`，所以至少需要修正到可啟動]
- [5g_rfsimulator_flexric_redcap/docker-compose.yml] -> [場景存在映像名稱 typo 與 UE28 掛載錯路徑] -> [Before: `custom-dev_dev`, `../../conf_files/nrue/nrue28.uicc.yaml`, `-C 3319680000`; After: `custom-dev`, `../../conf_files/nrue_recap/nrue28.uicc.yaml`, `-C 3630360000`, `--ssb 144`] -> [此修改讓 [UE28] 與其餘 [RedCap UE] 對齊]
- [get_bwp_config() RedCap gate] -> [原本把 full-cell BWP 誤當成 RedCap initial BWP 限制] -> [Before: `bwpSize > 51` 直接 `AssertFatal`; After: 保留一般 BWP 解析，只在 [RedCap] 情境記錄提示] -> [完整 [initialDownlinkBWP-RedCap-r17] / [initialUplinkBWP-RedCap-r17] 仍待後續實作]
- [container_5g_flexric_rfsim_redcap.xml] -> [RedCap RF simulator scenario 原本沒有 CI/XML 入口] -> [Before: 無場景入口; After: 有 [UE1 normal] / [UE2 RedCap] 的 attach 與 gNB log 驗證流程] -> [這是 [Milestone 5] 的最小可驗證整合入口，不是大規模 throughput 測試版]

## 4. 3GPP Specification Mapping
- [TS 38.306 Clause 4.2.21.1] -> [Definition of RedCap UE] -> [RedCap UE 在 FR1 的最大頻寬為 20 MHz；不支援超過 2 個 DL MIMO layers，也不支援超過 1 個 UE Tx branch / UL MIMO] -> [對應本次 [PHY constraint] 與 [BWP guard] 的判斷依據]
- [TS 38.306 Clause 4.2.21.6] / [4.2.21.6.1] -> [Physical layer parameters / BandNR parameters] -> [RedCap 專屬實體層能力會以 BandNR 與 capability field 呈現] -> [對應本專案後續要補齊的 [BWP / CORESET#0] 與 [band-limited capability] 工作]
- [TS 38.331 Clause 5.6.1.3] -> [Reception of the UECapabilityEnquiry by the UE] -> [UE 在收到 capability enquiry 後，需於 `UECapabilityInformation` 中攜帶 `UE-NR-Capability`] -> [對應目前 [nrue_recap YAML -> UE capability fallback] 的模擬注入流程]
- [TS 38.331 Clause 5.2.2.4.2] -> [Actions upon reception of the SIB1] -> [若 `halfDuplexRedCapAllowed` 不存在且 UE 僅支援 half-duplex FDD，UE 需視小區為 barred；若 `cellBarredRedCap1Rx` 為 barred，1Rx RedCap UE 需視為 barred] -> [對應目前 [gNB SIB1 RedCap config] 與未來 [half-duplex] 完整支援]
- [TS 38.331 SIB1 ASN.1 `RedCap-ConfigCommonSIB-r17`] -> [包含 `halfDuplexRedCapAllowed-r17`、`cellBarredRedCap1Rx-r17`、`cellBarredRedCap2Rx-r17`] -> [本 repo 已有對應欄位與部分 SIB1 組裝邏輯] -> [⚠ Needs Verification: [initialDownlinkBWP-RedCap-r17] / [initialUplinkBWP-RedCap-r17] 仍未完成端到端配置]

## 5. Practice Exercises
- [Basic] 請說明為什麼 [RedCap UE] 在 [FR1] 不能直接把 [full-cell 106 PRBs] 視為自己的 [initial BWP]，並指出這和 [TS 38.306 Clause 4.2.21.1] 有何關聯。
- [Applied] 假設你要讓 [UE2] 成為 [2Rx RedCap UE]，請列出至少 3 個你會同步檢查的面向，包含 [UE capability]、[SIB1 barring]、以及 [PHY antenna constraint]。
- [Advanced] 請設計一個 [Milestone 3] 的實作方案，讓 [gNB] 能同時維持 [106-PRB full cell common BWP] 與 [51-PRB RedCap initial BWP]，並說明你會如何修改 [config schema]、[RRC SIB1 build path]、與 [scheduler assumptions]。
