# RedCap 模擬器修改整理報告

## 1. 本次工作的定位
- [來源工作檔] -> [`agent_doc/Project_management/Simluation_mod.Md`](/home/tonywang/OAI/Red_cap_openairinterface5g/agent_doc/Project_management/Simluation_mod.Md)
- [本次聚焦 Milestone]
- [Milestone 1: Hardware / PHY Constraints]
- [Milestone 5: Integration & Throughput Targets]
- [本次目標]
- 先把 [rfsimulator + FlexRIC + RedCap UE capability injection] 這條模擬鏈整理到 [可啟動 / 可驗證 / 可閱讀] 的狀態
- 不一次硬做完 [Milestone 2/3] 全部功能，先修掉會直接讓模擬器或場景失敗的關鍵斷點

## 2. 對應 3GPP 依據
- [TS 38.306 Clause 4.2.21.1]
- [RedCap UE] 在 [FR1] 最大頻寬為 [20 MHz]
- 不支援超過 [2 個 DL MIMO layers]
- 不支援超過 [1 個 UE Tx branch]，也就是 [no UL MIMO]
- [TS 38.331 Clause 5.6.1.3]
- UE 收到 [UECapabilityEnquiry] 後，需要在 [UECapabilityInformation] 中帶回 [UE-NR-Capability]
- [TS 38.331 Clause 5.2.2.4.2]
- 若 [halfDuplexRedCapAllowed] 不存在，且 UE 只支援 [half-duplex FDD]，則需把 cell 視為 [barred]
- 若 [cellBarredRedCap1Rx] 或 [cellBarredRedCap2Rx] 對應為 [barred]，則該類型 RedCap UE 不應接入
- [TS 38.331 SIB1 ASN.1]
- [RedCap-ConfigCommonSIB-r17] 內含 [halfDuplexRedCapAllowed-r17]、[cellBarredRedCap1Rx-r17]、[cellBarredRedCap2Rx-r17]
- [initialDownlinkBWP-RedCap-r17] / [initialUplinkBWP-RedCap-r17] 是後續 [Milestone 3] 的重點

## 3. 我實際改了什麼
- [Modification Point] -> [Reason] -> [Before vs. After Comparison] -> [Discussion Point]
- [[ci-scripts/conf_files/nrue_recap/cp_bash.bash](/home/tonywang/OAI/Red_cap_openairinterface5g/ci-scripts/conf_files/nrue_recap/cp_bash.bash)] -> [修正大量 UE 設定檔生成錯誤] -> [Before: nrue28 之後 IMSI 會少 1 碼，UICC label 也會偏掉；After: 固定產生 15 碼 IMSI，固定保留 `uicc0`] -> [這是資產鏈根因修補]
- [[ci-scripts/conf_files/nrue_recap/nrue28.uicc.yaml](/home/tonywang/OAI/Red_cap_openairinterface5g/ci-scripts/conf_files/nrue_recap/nrue28.uicc.yaml)] / [[nrue29.uicc.yaml](/home/tonywang/OAI/Red_cap_openairinterface5g/ci-scripts/conf_files/nrue_recap/nrue29.uicc.yaml)] / [[nrue30.uicc.yaml](/home/tonywang/OAI/Red_cap_openairinterface5g/ci-scripts/conf_files/nrue_recap/nrue30.uicc.yaml)] -> [修復已經被舊腳本生成壞掉的檔案] -> [Before: 缺 `nrue_recap`、缺 `cells`、IMSI/UICC 錯；After: 與 `nrue2` 模板對齊] -> [其中 `nrue28` 會被 docker-compose 直接用到]
- [[ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/docker-compose.yml](/home/tonywang/OAI/Red_cap_openairinterface5g/ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/docker-compose.yml)] -> [修正場景直接啟動失敗的配置] -> [Before: `custom-dev_dev` image typo、UE28 掛到錯誤路徑、UE28 頻點與其餘 UE 不一致；After: 統一 image、路徑與 RF/SSB 參數] -> [讓 RedCap RF sim 資產鏈收斂]
- [[openair2/GNB_APP/gnb_config.c](/home/tonywang/OAI/Red_cap_openairinterface5g/openair2/GNB_APP/gnb_config.c)] -> [修正 BWP size 判斷邏輯] -> [Before: `bwp_list.bwpSize > 51` 會直接 `AssertFatal`，導致 106 PRB gNB YAML 無法啟動；After: 保留 full-cell/common BWP，僅在 RedCap 情境記錄提示] -> [避免把 [common BWP] 誤當 [RedCap initial BWP]]
- [[ci-scripts/xml_files/container_5g_flexric_rfsim_redcap.xml](/home/tonywang/OAI/Red_cap_openairinterface5g/ci-scripts/xml_files/container_5g_flexric_rfsim_redcap.xml)] -> [新增場景入口] -> [Before: 沒有 RedCap RF simulator 的 XML 測試入口；After: 有 [UE1=normal]、[UE2=RedCap] 的 attach 與 gNB log 驗證流程] -> [可作為後續端到端測試基礎]

## 4. 為什麼 [gnb_config.c] 一定要改
- 你的 RedCap gNB YAML 使用的是 [106 PRB full cell carrier]
- 但先前 `get_bwp_config()` 把所有 `bwp_list.bwpSize` 都套用成 [RedCap initial BWP <= 51 PRB] 的限制
- 這在語意上不正確
- [full cell common BWP] 不等於 [initialDownlinkBWP-RedCap-r17]
- 如果不改，gNB 還沒進到後續 RRC/SIB1/UE attach 階段就會直接因為 `AssertFatal` 結束
- 所以本次先做 [guard cleanup]
- 真正的 [RedCap initial BWP] 之後應在 [Milestone 3] 另開結構與配置，不應直接拿現在的 `bwp_list` 代替

## 5. 目前可驗證到哪裡
- [已完成]
- [test_nr_frame_params] 單元測試通過
- [RedCap asset sanity check] 通過
- 新的 [XML scenario] 已可被 parser 讀取
- [已知限制]
- 還沒實跑 [docker compose] 把整個 [Core + gNB + UE + FlexRIC] 全部拉起來驗證
- 還沒做 [50-120 Mbps] throughput 驗證
- 還沒把 [initialDownlinkBWP-RedCap-r17] / [initialUplinkBWP-RedCap-r17] 接進完整 RRC 路徑

## 6. 驗證結果
- [Build/Test]
- [Command] -> `ASAN_OPTIONS=detect_leaks=0 ctest --test-dir cmake_targets/ran_build/build_test -R test_nr_frame_params --output-on-failure`
- [Result] -> [Pass]
- [Log Files]
- [[test_nr_frame_params_build_2026-04-09_14-50-50.log](/home/tonywang/OAI/Red_cap_openairinterface5g/test_log/compiler_logs/test_nr_frame_params_build_2026-04-09_14-50-50.log)]
- [[test_nr_frame_params_2026-04-09_14-50-50.log](/home/tonywang/OAI/Red_cap_openairinterface5g/test_log/compiler_logs/test_nr_frame_params_2026-04-09_14-50-50.log)]
- [補充]
- 建置時若不加 `ASAN_OPTIONS=detect_leaks=0`，既有 [check_vcd] 會遇到 [LeakSanitizer/ptrace] 環境問題
- 這不是本次 patch 引入的新錯誤

## 7. 今晚閱讀建議順序
- [Step 1] 先看 [[test_log/report/redcap_simulator_summary_2026-04-09.md](/home/tonywang/OAI/Red_cap_openairinterface5g/test_log/report/redcap_simulator_summary_2026-04-09.md)]，理解整體脈絡
- [Step 2] 再看 [[agent_doc/Project_management/redcap_simulator_unit_test_report_2026-04-09.md](/home/tonywang/OAI/Red_cap_openairinterface5g/agent_doc/Project_management/redcap_simulator_unit_test_report_2026-04-09.md)]，對齊 [spec] 與 [test]
- [Step 3] 看這 3 個核心檔案
- [[openair2/GNB_APP/gnb_config.c](/home/tonywang/OAI/Red_cap_openairinterface5g/openair2/GNB_APP/gnb_config.c)]
- [[ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/docker-compose.yml](/home/tonywang/OAI/Red_cap_openairinterface5g/ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/docker-compose.yml)]
- [[ci-scripts/xml_files/container_5g_flexric_rfsim_redcap.xml](/home/tonywang/OAI/Red_cap_openairinterface5g/ci-scripts/xml_files/container_5g_flexric_rfsim_redcap.xml)]
- [Step 4] 最後看 [[ci-scripts/conf_files/nrue_recap/cp_bash.bash](/home/tonywang/OAI/Red_cap_openairinterface5g/ci-scripts/conf_files/nrue_recap/cp_bash.bash)] 和 `nrue28-30.uicc.yaml`，理解資產是怎麼壞掉又怎麼修回來的

## 8. 下一步建議
- [Milestone 3]
- 正式把 [initialDownlinkBWP-RedCap-r17] / [initialUplinkBWP-RedCap-r17] 加進 [RRC SIB1 build path]
- 補 [CORESET#0] 在 RedCap 情境下的配置與 scheduler 假設
- [Milestone 5]
- 實跑新的 [[container_5g_flexric_rfsim_redcap.xml](/home/tonywang/OAI/Red_cap_openairinterface5g/ci-scripts/xml_files/container_5g_flexric_rfsim_redcap.xml)]
- 收集 [attach log]、[ping]、[iperf] 與 [gNB RedCap detection] 結果
