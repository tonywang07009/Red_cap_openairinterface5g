# RedCap Build Recovery Unit Test Report

## 1. Technical Background
- [RedCap] 的 [SIB1/BWP] 與 [UE capability] 修改已在前一子任務完成，但 [Milestone 5] 的整合驗證被 [offline CMake/CPM] 與 [nr-softmodem link graph] 阻塞。
- 本輪工作的重點不是新增協議功能，而是恢復 [build determinism]。若 `CPM_SOURCE_CACHE` 與 cache 中殘留的 `CPM_DIRECTORY` 不一致，`CPM_0.40.1.cmake` 會在初始化前提早返回，造成 `CPMAddPackage` 未定義，進而讓 `googletest/benchmark` configure 失敗。
- 另一個問題是 [RedCap YAML parser] 與 [UE-only UICC state] 原本在同一條 link path 上，導致 gNB 側的 `nr-softmodem` 只為了 `load_nr_redcap_config()` 就被迫帶入 `checkUicc()` 對 `NB_UE_INST` 的依賴。
- 本輪修補將 [CPM stale cache reset] 加進 wrapper，並把 [RedCap parser] 拆成獨立 object library，讓 gNB/UE 各自連到真正需要的模組。這使後續 [Milestone 5] 的 [RF simulator attach / throughput] 驗證重新可執行。

## 2. Key C Functions / Data Structures Utilized in This Module
- `load_nr_redcap_config()` in [nr_redcap_config.c](/home/tonywang/OAI/Red_cap_openairinterface5g/openair3/UICC/nr_redcap_config.c)
- `nr_redcap_cfg_t` in [usim_interface.h](/home/tonywang/OAI/Red_cap_openairinterface5g/openair3/UICC/usim_interface.h)
- `nr_redcap_ue_configured()` in [nr_parms.c](/home/tonywang/OAI/Red_cap_openairinterface5g/openair1/PHY/INIT/nr_parms.c)
- [CPM wrapper] in [CPM.cmake](/home/tonywang/OAI/Red_cap_openairinterface5g/cmake_targets/CPM.cmake)

## 3. Test Results Summary Table
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| `cmake --preset tests` | Pass | N/A | `CPMAddPackage` 恢復正常，`googletest/benchmark` 可離線解析 |
| `cmake --build --preset tests --target nr-softmodem nr-uesoftmodem test_nr_frame_params test_nr_ue_power_procedures test_nr_ue_ra_procedures` | Pass | N/A | 以 `CCACHE_DISABLE=1`、`ASAN_OPTIONS=detect_leaks=0` 完成 |
| `ctest --test-dir cmake_targets/ran_build/build_test -R 'test_nr_frame_params|test_nr_ue_power_procedures|test_nr_ue_ra_procedures' --output-on-failure` | Pass | N/A | 3/3 測試通過 |

## 4. 3GPP Specification Mapping
- [TS 38.306 Clause 4.2.21.1]：本輪未改動規格邏輯；修補目的是維持 [FR1 20 MHz RedCap validation] 所依賴的建置路徑。
- [TS 38.331 Clause 5.2.2.4.2]：本輪未改動接入/barred 判斷；修補目的是保留前一輪 [SIB1 RedCap barring checks] 的可重建性。
- [TS 38.331 Clause 5.6.1.3]：本輪未改動 capability signaling；修補目的是保留 [UE capability wiring] 的測試可執行性。

## 5. Practice Exercises
- [Basic]：說明為什麼 `CPM_DIRECTORY` 與本輪 `CPM_SOURCE_CACHE` 不一致時，`CPMAddPackage` 可能消失。
- [Applied]：比較 [單一 `lib_uicc`] 與 [拆成 `lib_uicc` + `lib_nr_redcap_config`] 對 gNB/UE link graph 的差異。
- [Advanced]：若之後要把 [RedCap parser] 擴充到更多 [Rel-18 eRedCap] 欄位，你會如何設計測試，避免再度引入 gNB/UE 的不必要耦合？
