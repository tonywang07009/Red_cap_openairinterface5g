---

# Work Daily Log

## Session Metadata
- Date: 2026-04-09 21:19
- Agent Session ID: N/A
- Task Slug: redcap-build-cpm-linkfix

## Milestone & Sub-task Reference
- Milestone: Milestone 3 [BWP & CORESET#0] + Milestone 5 [Integration & Throughput Targets]
- Sub-task: [offline CMake/CPM configure recovery] + [RedCap parser / UICC link decoupling]
- Status: [COMPLETED]

## What Was Done
- [cmake_targets/CPM.cmake] 新增 [stale CPM internal cache reset]，避免 `CPM_DIRECTORY` 與本輪 `CPM_SOURCE_CACHE` 不一致時，`CPM.cmake` 提前返回。
- [openair3/UICC/CMakeLists.txt] 新增 `lib_nr_redcap_config` object library。
- [openair3/UICC/nr_redcap_config.c] 獨立承接 `load_nr_redcap_config()`，將 [RedCap YAML parser] 從 [UE-only UICC path] 分離。
- [CMakeLists.txt] 讓 `nr-softmodem` 只連 `lib_nr_redcap_config`；`nr-uesoftmodem` 則同時連 `lib_uicc` 與 `lib_nr_redcap_config`。
- [Build execution path] 以 `CCACHE_DISABLE=1`、`ASAN_OPTIONS=detect_leaks=0`、`LSAN_OPTIONS=detect_leaks=0` 繞過目前 sandbox 下的 [ccache readonly] 與 [LeakSanitizer helper] 問題，完成正式重建與回歸測試。

## 3GPP Spec Clauses Referenced
- TS 38.306 Clause 4.2.21.1 — 本輪未變更 [RedCap FR1 20 MHz] 行為；修補目的是恢復其 build/test 可執行性。
- TS 38.331 Clause 5.2.2.4.2 — 本輪未變更 [half-duplex / RedCap barred] 判斷；修補目的是支撐前一輪 SIB1 接入檢查。
- TS 38.331 Clause 5.6.1.3 — 本輪未變更 [UE capability signaling]；修補目的是支撐先前 capability wiring 的重建路徑。

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| `cmake --preset tests` | Pass | N/A | `CPMAddPackage` 可正常解析；log: `test_log/build_logs/cmake_configure_tests_resume_split_2026-04-09_21-18-21.log` |
| `cmake --build --preset tests --target nr-softmodem nr-uesoftmodem test_nr_frame_params test_nr_ue_power_procedures test_nr_ue_ra_procedures` | Pass | N/A | log: `test_log/build_logs/redcap_m3_m5_build_resume_split_2026-04-09_21-18-35.log` |
| `ctest --test-dir cmake_targets/ran_build/build_test -R 'test_nr_frame_params|test_nr_ue_power_procedures|test_nr_ue_ra_procedures' --output-on-failure` | Pass | N/A | 3/3 通過；log: `test_log/compiler_logs/redcap_m3_m5_ctest_resume_2026-04-09_21-18-55.log` |

## Known Issues / Blockers
- [Environment workaround still needed] 在目前 sandbox 下，若直接使用預設 [ccache] 路徑與 [LeakSanitizer]，build-time helper 仍可能失敗；正式 CI/host 環境是否受影響仍需驗證。
- [Plan file gap] `agent_doc/Project_management/redcap_mmtc_plan.md` 目前不存在，暫以 `agent_doc/Project_management/Simluation_mod.Md` 對齊里程碑。⚠ Needs Verification
- [Full E2E blocker remains] 尚未實跑 `container_5g_flexric_rfsim_redcap.xml` 的 [attach/ping/iperf] runtime 驗證。

## Next Step
- 以已恢復的 build 路徑實跑 `ci-scripts/xml_files/container_5g_flexric_rfsim_redcap.xml` 對應場景，收集 [attach log]、[gNB RedCap detection]、[302003]、[030001]、[030002] 結果。
