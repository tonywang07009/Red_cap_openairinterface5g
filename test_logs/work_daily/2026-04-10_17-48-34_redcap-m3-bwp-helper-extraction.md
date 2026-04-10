# Work Daily Log
## Session Metadata
- Date: 2026-04-10 17:48
- Agent Session ID: N/A
- Task Slug: redcap-m3-bwp-helper-extraction

## Milestone & Sub-task Reference
- Milestone: Milestone 3 / Milestone 5
- Sub-task: RedCap BWP parameter wiring helper extraction
- Status: COMPLETED

## What Was Done
- Added [`openair2/LAYER2/NR_MAC_gNB/nr_mac_redcap_bwp.h`](/home/tonywang/OAI/Red_cap_openairinterface5g/openair2/LAYER2/NR_MAC_gNB/nr_mac_redcap_bwp.h) to hold reusable RedCap initial BWP config structures and helper APIs.
- Added [`openair2/LAYER2/NR_MAC_gNB/nr_mac_redcap_bwp.c`](/home/tonywang/OAI/Red_cap_openairinterface5g/openair2/LAYER2/NR_MAC_gNB/nr_mac_redcap_bwp.c) to centralize FR1 20 MHz PRB validation, initial BWP population, and Case B edge-alignment checks.
- Updated [`openair2/GNB_APP/gnb_config.c`](/home/tonywang/OAI/Red_cap_openairinterface5g/openair2/GNB_APP/gnb_config.c) to use the new helpers instead of file-local RedCap initial BWP validation logic.
- Moved `nr_redcap_bwp_config_t` ownership into the new helper header and updated [`openair2/LAYER2/NR_MAC_gNB/nr_mac_gNB.h`](/home/tonywang/OAI/Red_cap_openairinterface5g/openair2/LAYER2/NR_MAC_gNB/nr_mac_gNB.h) accordingly.
- Added [`openair2/LAYER2/NR_MAC_gNB/tests/test_nr_redcap_bwp.cpp`](/home/tonywang/OAI/Red_cap_openairinterface5g/openair2/LAYER2/NR_MAC_gNB/tests/test_nr_redcap_bwp.cpp) and registered it in [`openair2/LAYER2/NR_MAC_gNB/tests/CMakeLists.txt`](/home/tonywang/OAI/Red_cap_openairinterface5g/openair2/LAYER2/NR_MAC_gNB/tests/CMakeLists.txt).
- Added the new helper source to the main build graph in [`CMakeLists.txt`](/home/tonywang/OAI/Red_cap_openairinterface5g/CMakeLists.txt).

## 3GPP Spec Clauses Referenced
- TS 38.306 Section 4.2.21.1 — RedCap FR1 bandwidth limit used for 15 kHz / 30 kHz initial BWP PRB validation.
- TS 38.331 Section 5.2.2.4.2 — RedCap SIB1 common configuration remains the downstream consumer of the parsed initial DL/UL BWP values.
- TS 38.331 `initialDownlinkBWP-RedCap-r17` / `initialUplinkBWP-RedCap-r17` ASN.1 fields — used as the config-level target semantics for the helper path.

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| `cmake --preset tests` | Pass | N/A | Log: [`cmake_preset_tests_2026-04-10_17-45-46.log`](/home/tonywang/OAI/Red_cap_openairinterface5g/test_log/compiler_logs/cmake_preset_tests_2026-04-10_17-45-46.log) |
| `test_nr_redcap_bwp` build | Pass | N/A | Build required `CCACHE_DISABLE=1`; log: [`test_nr_redcap_bwp_build_noccache_2026-04-10_17-45-46.log`](/home/tonywang/OAI/Red_cap_openairinterface5g/test_log/compiler_logs/test_nr_redcap_bwp_build_noccache_2026-04-10_17-45-46.log) |
| `ctest -R test_nr_redcap_bwp` | Pass | N/A | Log: [`test_nr_redcap_bwp_2026-04-10_17-45-46.log`](/home/tonywang/OAI/Red_cap_openairinterface5g/test_log/compiler_logs/test_nr_redcap_bwp_2026-04-10_17-45-46.log) |
| `gnb_config.c.o` + `nr_mac_redcap_bwp.c.o` object build | Pass | N/A | Needed `ASAN_OPTIONS=detect_leaks=0`; log: [`redcap_m3_object_build_nolsan_2026-04-10_17-45-46.log`](/home/tonywang/OAI/Red_cap_openairinterface5g/test_log/compiler_logs/redcap_m3_object_build_nolsan_2026-04-10_17-45-46.log) |

## Known Issues / Blockers
- The sandbox still cannot execute Docker runtime validation, so compose-based attach/runtime evidence remains host-side work.
- The test/build environment uses `ccache` and ASAN defaults that required local overrides during validation.

## Next Step
- Continue Milestone 3 by reviewing whether `nr_radio_config.c` should consume more of the new RedCap BWP helper surface, then align the compose-side gNB/UE YAML files with the stabilized config path.
