# Work Daily Log

## Session Metadata
- Date: 2026-04-10 11:58
- Agent Session ID: N/A
- Task Slug: redcap-m3-coreset0-selector

## Milestone & Sub-task Reference
- Milestone: Milestone 3 [BWP & CORESET#0]
- Sub-task: [RedCap CORESET#0 runtime selector] + [Simluation_v2 tracker alignment]
- Status: [COMPLETED]

## What Was Done
- 更新 [`agent_doc/Project_management/Simluation_v2.md`]，補上 [repo path alignment]、[progress tracker legend]、[M1/M2/M3/M5 current status]，避免計畫檔與 repo 現況持續脫鉤。
- 新增 [`openair2/LAYER2/NR_MAC_gNB/nr_mac_redcap.h`]，定義 [coreset0_redcap_mode]、[mode string helper]、[edge-aligned BWP helper]。
- 擴充 [`openair2/GNB_APP/gnb_paramdef.h`] 與 [`openair2/GNB_APP/gnb_config.c`]，讓 gNB 可讀取 `coreset0_redcap_mode_r17`，並在載入 RedCap initial DL BWP 時驗證模式值。
- 修改 [`openair2/LAYER2/NR_MAC_gNB/nr_mac_gNB.h`] 與 [`openair2/LAYER2/NR_MAC_gNB/nr_radio_config.c`]，支援：
  - [Case A]：沿用 `controlResourceSetZero` / `searchSpaceZero`
  - [Case B]：改用 `commonControlResourceSet`，並要求 [initial DL BWP] 必須 [edge-aligned]
- 在 [Case B] 路徑中，補上 [commonSearchSpaceList → new CORESET id] 的 rebinding，並清除舊的 [Type0 CSS] 參照，避免殘留 `searchSpaceZero` / `searchSpaceSIB1`。
- 新增 [`openair2/LAYER2/NR_MAC_gNB/tests/test_nr_redcap_coreset0.cpp`] 與對應 CMake wiring，驗證 [mode validity] 與 [edge alignment] 規則。
- 更新 [`ci-scripts/conf_files/gnb.sa.band78.fr1.106PRB.usrpb210.redcap.yaml`]，加入 `coreset0_redcap_mode_r17` 範例欄位，預設維持 [Case A]。

## 3GPP Spec Clauses Referenced
- TS 38.331 Clause 6.3.2 / `PDCCH-ConfigCommon` ASN.1 — `controlResourceSetZero`、`commonControlResourceSet`、`searchSpaceZero`、`commonSearchSpaceList` 的欄位關係；本輪用於區分 [Case A] 與 [Case B]。⚠ Needs Verification
- TS 38.331 SIB1 ASN.1 — `initialDownlinkBWP-RedCap-r17`；本輪用於將 RedCap-specific initial DL BWP 與新的 CORESET mode 綁定。⚠ Needs Verification
- TS 38.306 Clause 4.2.21.1 — [FR1 20 MHz RedCap bandwidth constraint]；本輪沿用既有 BWP size guard，不擴張 RedCap 頻寬能力。

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| `cmake --preset tests` | Pass | N/A | log: `test_log/build_logs/cmake_configure_redcap_m3_2026-04-10_11-56-45.log` |
| `cmake --build --preset tests --target nr-softmodem test_nr_redcap_coreset0` | Pass | N/A | log: `test_log/build_logs/redcap_m3_coreset0_build_2026-04-10_11-57-29.log` |
| `ctest --test-dir cmake_targets/ran_build/build_test -R 'test_nr_redcap_coreset0|test_nr_frame_params' --output-on-failure` | Fail | N/A | 失敗原因為 [LeakSanitizer / ptrace sandbox]，非功能錯誤；log: `test_log/compiler_logs/redcap_m3_coreset0_ctest_2026-04-10_11-58-03.log` |
| `ASAN_OPTIONS=detect_leaks=0 LSAN_OPTIONS=detect_leaks=0 ctest --test-dir cmake_targets/ran_build/build_test -R 'test_nr_redcap_coreset0|test_nr_frame_params' --output-on-failure` | Pass | N/A | 2/2 通過；log: `test_log/compiler_logs/redcap_m3_coreset0_ctest_noleak_2026-04-10_11-58-10.log` |

## Known Issues / Blockers
- [Runtime evidence pending] 本輪只完成 [M3 code + unit test]，尚未在 [rfsimulation] 驗證 [Case A / Case B] 的 PDCCH decode。
- [Milestone 4 gap remains] [SDT / RRC_INACTIVE] 仍未開始，照新版 `Simluation_v2.md` 順序，這是下一個主要功能缺口。
- [Docker blocker remains] [Milestone 5] 的 attach / ping / iperf / FlexRIC runtime 仍需在具備 Docker 權限的 host 上收集。

## Next Step
- 以本輪新增的 [coreset0_redcap_mode_r17] 為基礎，完成 [Milestone 3] 的 runtime close-out：
  - 準備 [Case A] 與 [Case B] 配置
  - 在 [rfsimulation] 檢查 [PDCCH decode] 與 [edge-only PRB allocation] 行為
  - 再更新 [Simluation_v2.md] 的 [M3 Test / Docs] 欄位
