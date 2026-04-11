# Work Daily Log
## Session Metadata
- Date: 2026-04-11 22:56
- Agent Session ID: N/A
- Task Slug: redcap-m3-caseb-runtime-coverage

## Milestone & Sub-task Reference
- Milestone: Milestone 3: BWP & CORESET#0
- Sub-task: RedCap CORESET#0 Case B runtime conversion coverage
- Status: COMPLETED

## What Was Done
- Extracted the Case B `commonControlResourceSet` rebinding path into `openair2/LAYER2/NR_MAC_gNB/nr_mac_redcap_bwp.c` as `nr_redcap_apply_case_b_common_coreset()`.
- Reused the shared helper from `openair2/LAYER2/NR_MAC_gNB/nr_radio_config.c` so the runtime Case B branch no longer keeps a private copy of the search-space rebinding logic.
- Added direct unit coverage in `openair2/LAYER2/NR_MAC_gNB/tests/test_nr_redcap_bwp.cpp` for:
  - Type0 CSS field cleanup.
  - `commonControlResourceSet` installation.
  - `commonSearchSpaceList` rebinding to the new CORESET id.
  - Rejection when the common search-space list is absent.
- Updated `openair2/LAYER2/NR_MAC_gNB/tests/CMakeLists.txt` so `test_nr_redcap_bwp` links the ASN.1 RRC surface required by the new Case B runtime test.

## 3GPP Spec Clauses Referenced
- TS 38.306 Section 4.2.21.1 — RedCap reduced-bandwidth operation in FR1 constrains the initial BWP envelope that the Case B runtime path clones.
- TS 38.331 Section 5.2.2.4.2 — RedCap common configuration anchors the initial DL/UL BWP context used when cloning RedCap SIB1-derived BWP state.
- TS 38.331 exact clause for `PDCCH-ConfigCommon` / `commonControlResourceSet` / `commonSearchSpaceList`: ⚠ Needs Verification.

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| `cmake --build --preset tests --target test_nr_redcap_bwp test_nr_redcap_coreset0 test_nr_redcap_sdt_fsm test_nr_rrc_redcap nr-softmodem` | Pass | `nr_mac_redcap_bwp.c`, `nr_radio_config.c` Case B call-site, adjacent RedCap gNB path | Log: `test_log/build_logs/redcap_m3_caseb_runtime_build_final_2026-04-11_22-31-51.log` |
| `test_nr_redcap_bwp` | Pass | New Case B positive/death coverage for `commonControlResourceSet` rebinding | Includes direct runtime helper coverage |
| `ctest -R 'test_nr_redcap_bwp|test_nr_redcap_coreset0|test_nr_rrc_redcap|test_nr_redcap_sdt_fsm|test_nr_ue_redcap_bwp'` | Pass | Case B runtime helper plus adjacent RedCap regression suite | Log: `test_log/compiler_logs/redcap_m3_caseb_runtime_regression_2026-04-11_22-32-23.log` |

## Known Issues / Blockers
- Docker runtime is still unavailable in the sandbox, so M5 end-to-end UL throughput evidence remains blocked.
- TS 38.331 exact `PDCCH-ConfigCommon` clause number for the Case B `commonControlResourceSet` mapping still needs direct clause confirmation.

## Next Step
- Continue with Milestone 5 and close the local `E2/xApp UL PRB control` gap before returning to Docker-based runtime evidence.
