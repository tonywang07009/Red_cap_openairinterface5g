# Work Daily Log
## Session Metadata
- Date: 2026-04-10 23:34
- Agent Session ID: N/A
- Task Slug: redcap-m3m5-dual-direction-bwp-evidence

## Milestone & Sub-task Reference
- Milestone: Milestone 3 / Milestone 5
- Sub-task: Make `[DL + UL]` RedCap initial BWP handling explicit and verifiable for both `[gNB]` and `[UE]`
- Status: COMPLETED

## What Was Done
- Re-checked [`spec/redcap_3gpp/spec.md`](/home/tonywang/OAI/Red_cap_openairinterface5g/spec/redcap_3gpp/spec.md) with SymDex and confirmed the dual-direction requirement is explicit:
  - `initialDownlinkBWP-RedCap-r17`
  - `initialUplinkBWP-RedCap-r17`
- Confirmed the gNB-side SIB1 build path in [`openair2/LAYER2/NR_MAC_gNB/nr_radio_config.c`](/home/tonywang/OAI/Red_cap_openairinterface5g/openair2/LAYER2/NR_MAC_gNB/nr_radio_config.c) already broadcasts both RedCap BWPs.
- Extracted the UE-side BWP selection logic into a dedicated helper module:
  - [`openair2/LAYER2/NR_MAC_UE/nr_ue_redcap_bwp.h`](/home/tonywang/OAI/Red_cap_openairinterface5g/openair2/LAYER2/NR_MAC_UE/nr_ue_redcap_bwp.h)
  - [`openair2/LAYER2/NR_MAC_UE/nr_ue_redcap_bwp.c`](/home/tonywang/OAI/Red_cap_openairinterface5g/openair2/LAYER2/NR_MAC_UE/nr_ue_redcap_bwp.c)
- Updated [`openair2/LAYER2/NR_MAC_UE/config_ue.c`](/home/tonywang/OAI/Red_cap_openairinterface5g/openair2/LAYER2/NR_MAC_UE/config_ue.c) to use the shared helper instead of local `static` functions.
- Added a new UE-side unit test:
  - [`openair2/LAYER2/NR_MAC_UE/tests/test_nr_ue_redcap_bwp.cpp`](/home/tonywang/OAI/Red_cap_openairinterface5g/openair2/LAYER2/NR_MAC_UE/tests/test_nr_ue_redcap_bwp.cpp)
  - covers:
    - non-RedCap fallback to common DL/UL BWP
    - RedCap use of dedicated DL/UL BWP when present
    - UL fallback when `initialUplinkBWP-RedCap-r17` is absent
- Extended the runtime scenario and summary tooling so host reruns now check both directions explicitly:
  - [`ci-scripts/xml_files/container_5g_flexric_rfsim_redcap.xml`](/home/tonywang/OAI/Red_cap_openairinterface5g/ci-scripts/xml_files/container_5g_flexric_rfsim_redcap.xml)
    - added `[302004]` for `SIB1 RedCap initial UL BWP`
  - [`ci-scripts/redcap_runtime_summary.py`](/home/tonywang/OAI/Red_cap_openairinterface5g/ci-scripts/redcap_runtime_summary.py)
    - added `[302004]`
    - added gNB UL marker parsing
    - made UE dual-direction `[DL + UL]` apply logs part of exit criteria

## 3GPP Spec Clauses Referenced
- TS 38.331 Section 5.2.2.4.2 — RedCap common configuration broadcast in SIB1, including the dedicated initial DL/UL BWP entries
- TS 38.306 Section 4.2.21.1 — FR1 RedCap reduced-capability profile that constrains the UE/gNB operating point
- `spec/redcap_3gpp/spec.md` — local project mapping for:
  - `initialDownlinkBWP-RedCap-r17`
  - `initialUplinkBWP-RedCap-r17`

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| `ASAN_OPTIONS=detect_leaks=0 LSAN_OPTIONS=detect_leaks=0 cmake --build --preset tests --target test_nr_ue_redcap_bwp` | Pass | new UE helper compile/link | Log: `test_log/build_logs/test_nr_ue_redcap_bwp_no_lsan_2026-04-10_23-20-43.log` |
| `ASAN_OPTIONS=detect_leaks=0 LSAN_OPTIONS=detect_leaks=0 ctest --test-dir cmake_targets/ran_build/build_test -R test_nr_ue_redcap_bwp --output-on-failure` | Pass | UE helper unit test | Log: `test_log/compiler_logs/ctest_test_nr_ue_redcap_bwp_2026-04-10_23-20-43.log` |
| `python3 -m py_compile ci-scripts/redcap_runtime_summary.py` | Pass | runtime summary syntax | Confirms the new `[302004]` summary logic parses cleanly |
| `rg -n "302004|initial UL BWP" ci-scripts/xml_files/container_5g_flexric_rfsim_redcap.xml ci-scripts/redcap_runtime_summary.py` | Pass | runtime dual-direction evidence wiring | Confirms XML and summary now carry the new UL-side check |
| `ASAN_OPTIONS=detect_leaks=0 LSAN_OPTIONS=detect_leaks=0 ctest --test-dir cmake_targets/ran_build/build_test -R 'test_nr_ue_redcap_bwp|test_nr_redcap_sdt_fsm' --output-on-failure` | Pass | regression spot-check | Confirms the new UE helper work did not break the SDT FSM test |

## Known Issues / Blockers
- Live Docker runtime evidence is still blocked in the current sandbox, so `[302004]` is wired but not executed end-to-end here.
- This sub-task strengthens `[DL + UL initial BWP]` selection and validation; it does not change the project-wide `[UL-only throughput]` policy in Milestone 5.

## Next Step
- Continue with the next code gap by using SymDex to inspect where the SDT FSM should be wired into the active MAC scheduler path, unless Milestone 2 SIB1 encode/decode coverage is reprioritized first.
