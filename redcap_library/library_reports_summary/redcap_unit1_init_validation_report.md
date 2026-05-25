# [RedCap Unit 1 Report]

## [1. Technical Background]

- [Unit Name] [RedCap FR1 init-time validation]
- [Module Scope] [openair1/PHY/INIT/nr_parms.c]
- [Goal] 在 [PHY init] 階段先驗證 [RedCap FR1] 的基本能力限制，避免非法配置流入後續 [allocator]、[transport path]、[rfsimulator] 執行流程。
- [Why This Matters]
  - [TS 38.306 Clause 4.2.21.1] 定義 [RedCap UE] 在 [FR1] 的最大頻寬為 [20 MHz]。
  - 同一條款也限制 [FR1] 只能有 [1Rx mandatory / 2Rx optional]、[DL layers <= 2]、[UL MIMO not supported]。
  - [TS 38.331 Clause 5.2.2.4.2] 指出 [(e)RedCap UE] 使用的 [initial DL/UL BWP] 不得超過 UE 的最大頻寬。
- [Engineering Intuition]
  - [init-time validation] 是最早防線。
  - 若在這一層就擋下非法 [PRB]、[antenna]、[TX branch] 配置，後面的 [scheduler]、[PDSCH/PUSCH path]、[rfsimulator] 都不需要在錯誤狀態下繼續跑。

## [2. Key C Functions / Data Structures]

- [Function] [nr_validate_redcap_gnb_frame_parms()]
  - [Purpose] 驗證 [gNB] 初始化後的 [NR_DL_FRAME_PARMS] 是否符合 [RedCap FR1] 限制。
- [Function] [nr_validate_redcap_ue_frame_parms()]
  - [Purpose] 驗證 [UE] 初始化後的 [NR_DL_FRAME_PARMS] 是否符合 [RedCap FR1] 限制。
- [Function] [nr_assert_redcap_fr1_grid_size()]
  - [Purpose] 根據 [numerology] 檢查 [DL/UL PRB] 是否落在 [20 MHz FR1] 可接受範圍。
- [Function] [nr_init_frame_parms()]
  - [Purpose] [gNB/RU] 初始化入口，接收 [nfapi_nr_config_request_scf_t] 並填入 [NR_DL_FRAME_PARMS]。
- [Function] [nr_init_frame_parms_ue()]
  - [Purpose] [UE] 初始化入口，接收 [fapi_nr_config_request_t] 並填入 [NR_DL_FRAME_PARMS]。
- [Structure] [NR_DL_FRAME_PARMS]
  - [Key Fields]
    - [numerology_index]
    - [N_RB_DL]
    - [N_RB_UL]
    - [nb_antennas_rx]
    - [nb_antennas_tx]
    - [freq_range]
    - [redcap_restricted]
- [Structure] [nfapi_nr_config_request_scf_t] / [fapi_nr_config_request_t]
  - [Role] 提供 [grid size]、[SCS]、[antenna count] 等原始配置來源。

## [3. Modification Summary]

- [Modification Point] [openair1/PHY/INIT/nr_parms.c]
  - [Reason] 將既有 [RedCap FR1] 規則集中在可重用 helper，讓 [init path] 與 [unit test] 可共用。
  - [Before vs. After Comparison]
    - [Before] 規則只存在於 init 流程內部，不易單元測試與教學導讀。
    - [After] [gNB/UE validation helper] 成為正式介面，可直接被測試呼叫。
  - [Discussion Point] 這是 [backend-neutral] 修改，對 [rfsimulator] 與 [B210] 都一致有效。
- [Modification Point] [openair1/PHY/INIT/nr_phy_init.h]
  - [Reason] 匯出 [validation helper] 宣告。
  - [Before vs. After Comparison]
    - [Before] helper 為內部 static function。
    - [After] helper 可供 [unit test] 與後續模組 reuse。
  - [Discussion Point] 沒有改變 production path 的呼叫順序。
- [Modification Point] [openair1/PHY/INIT/tests/test_nr_frame_params.cpp]
  - [Reason] 補上 [RedCap init-time] regression coverage。
  - [Before vs. After Comparison]
    - [Before] 沒有 RedCap 相關測試。
    - [After] 新增 [合法 gNB case]、[非法 bandwidth]、[非法 RX branches]、[非法 UL MIMO] 測試。
  - [Discussion Point] 另外加了 [test-only stub] 來隔離 [load_nr_redcap_config()] 的 link 依賴。

## [4. Test Results Summary Table]

| [Test Item] | [Status] | [Code Coverage] | [Modification Logs] |
|---|---|---:|---|
| [Focused rebuild: nr_parms.c.o] | [Pass] | [Module compile check] | [test_log/build_logs/nr_parms_obj_2026-04-09_13-41-21.log] |
| [Configure tests preset] | [Pass] | [Build tree setup] | [test_log/build_logs/cmake_configure_tests_2026-04-09_13-41-21.log] |
| [Build test_nr_frame_params] | [Pass] | [Unit test binary build] | [test_log/build_logs/test_nr_frame_params_build_rerun_2026-04-09_13-41-21.log] |
| [Run ctest -R test_nr_frame_params] | [Pass] | [4 new RedCap checks + existing frame-param tests] | [test_log/compiler_logs/test_nr_frame_params_2026-04-09_13-41-21.log] |

## [5. 3GPP Specification Mapping]

- [TS 38.306 Clause 4.2.21.1]
  - [Brief Excerpt] [RedCap UE] 在 [FR1] 最大頻寬為 [20 MHz]。
  - [Mapped Code]
    - [nr_redcap_fr1_max_prbs()]
    - [nr_assert_redcap_fr1_grid_size()]
- [TS 38.306 Clause 4.2.21.1]
  - [Brief Excerpt] [FR1] 僅支援 [1Rx mandatory / 2Rx optional]，不支援超過 [2 DL layers] 與任何 [UL MIMO]。
  - [Mapped Code]
    - [nr_validate_redcap_gnb_frame_parms()]
    - [nr_validate_redcap_ue_frame_parms()]
- [TS 38.331 Clause 5.2.2.4.2]
  - [Brief Excerpt] [(e)RedCap UE] 使用的 [initialDownlinkBWP] / [initialUplinkBWP] 不得超過其最大頻寬。
  - [Mapped Code]
    - [init-time grid size validation] 作為 [BWP / carrier grid] 的前置保護。

## [6. How To Use This Code]

- [Production Path]
  - 執行 [nr-softmodem]、[nr-uesoftmodem]、[nr-ru]、或 [rfsimulator] 初始化時，
  - 若系統判定目前是 [RedCap restricted]，
  - 就會在 [nr_init_frame_parms()] 或 [nr_init_frame_parms_ue()] 完成 [NR_DL_FRAME_PARMS] 填值後，自動做檢查。
- [Developer Path]
  - 若你在寫額外測試或重構初始化流程，
  - 可以直接呼叫：
    - [nr_validate_redcap_gnb_frame_parms()]
    - [nr_validate_redcap_ue_frame_parms()]
- [Focused Rebuild]
  - [cmake --preset default]
  - [ninja -C cmake_targets/ran_build/build CMakeFiles/PHY_NR.dir/openair1/PHY/INIT/nr_parms.c.o]
- [Focused Unit Test]
  - [cmake --preset tests]
  - [cmake --build cmake_targets/ran_build/build_test --target test_nr_frame_params]
  - [cd cmake_targets/ran_build/build_test]
  - [ctest --output-on-failure -R test_nr_frame_params]

## [7. Systematic Walkthrough]

- [Step 1] [Configuration enters the system]
  - [gNB] 使用 [nfapi_nr_config_request_scf_t]
  - [UE] 使用 [fapi_nr_config_request_t]
- [Step 2] [Frame parameters are populated]
  - 主要填入 [SCS]、[PRB]、[antenna count]、[frequency range]
- [Step 3] [RedCap mode is detected]
  - [gNB] 看是否存在 [RedCap config section]
  - [UE] 看 [load_nr_redcap_config()] 是否回報 [support_of_redcap_r17]
- [Step 4] [Validation runs]
  - 檢查 [FR1 only]
  - 檢查 [20 MHz PRB limit]
  - 檢查 [RX branch count]
  - 檢查 [DL/UL antenna or TX branch constraints]
- [Step 5] [Illegal configs are rejected early]
  - 這樣後面 [allocator]、[transport path]、[runtime PHY] 不會在錯誤狀態下繼續工作

## [8. Practice Exercises]

- [Basic]
  - [Question] 為什麼 [RedCap FR1] 的限制要先在 [init-time] 檢查，而不是等到 [nr_dlsch.c] 或 [nr_ulsch.c] 才檢查？
- [Applied]
  - [Question] 若 [numerology = 1] 且 [N_RB_DL = 52]，這個配置為什麼應該在 [nr_assert_redcap_fr1_grid_size()] 被拒絕？
- [Advanced]
  - [Question] 若下一階段要支援 [half-duplex FDD Type A]，你會把限制放在 [init-time validation]、[scheduler]、還是 [duplex slot selection]？請說明各層的責任分工。

## [9. Open Risks / Next Steps]

- [Risk] [runtime data path] 還沒有 guard [DL layers > 2] / [UL layers > 1]
- [Risk] [half-duplex FDD Type A] 尚未實作 [duplex behavior] 限制
- [Risk] production build 仍有獨立的 [load_nr_redcap_config] linkage 議題，與本單元測試已分離，但後續仍要收斂
- [Next Unit Suggestion] [openair1/PHY/INIT/nr_init.c + nr_init_ue.c]

