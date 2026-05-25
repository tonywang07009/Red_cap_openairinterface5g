# RedCap [Milestone 3 / Milestone 5] Summary

## Scope
- [Milestone 3]：完成 [SIB1 RedCap initial DL/UL BWP] 與 [UE SIB1 barring] wiring。
- [Milestone 5]：補齊 [RF simulator XML] 的 attach / gNB log / iperf case 入口。

## Current Validation
- [Pass] `test_nr_frame_params`
- [Pass] `test_nr_ue_power_procedures`
- [Pass] `test_nr_ue_ra_procedures`
- [Pass] `xmllint --noout ci-scripts/xml_files/container_5g_flexric_rfsim_redcap.xml`
- [Pass] `docker compose -f ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/docker-compose.yml config -q`

## Current Blockers
- [Build system] `nr-softmodem` 的 `lib_uicc` link wiring 已補，但 source-level rebuild 會被 [offline CPM / googletest cache] 的 CMake regenerate 卡住。
- [Runtime] 還沒執行真正的 [Core + gNB + UE + FlexRIC] attach / ping / iperf。

## Next Action
- 先修通 [offline CMake configure]。
- 再執行 `container_5g_flexric_rfsim_redcap.xml` 的 `302003` / `030001` / `030002`。
