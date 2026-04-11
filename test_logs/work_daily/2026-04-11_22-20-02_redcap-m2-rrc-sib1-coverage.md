# Work Daily Log
## Session Metadata
- Date: 2026-04-11 22:20
- Agent Session ID: N/A
- Task Slug: redcap-m2-rrc-sib1-coverage

## Milestone & Sub-task Reference
- Milestone: Milestone 2: RRC / SIB1 Support
- Sub-task: RedCap SIB1 encode/decode coverage and UE-side barring gating
- Status: COMPLETED

## What Was Done
- Extracted RedCap UE helper logic from `openair2/RRC/NR_UE/rrc_UE.c` into `openair2/RRC/NR_UE/rrc_ue_redcap.[ch]`.
- Kept `rrc_UE.c` on the original UE runtime path while switching the capability builder call to `nr_rrc_build_redcap_ue_capability()`.
- Added `openair2/RRC/NR/tests/test_nr_rrc_redcap.cpp` covering:
  - `halfDuplexRedCapAllowed-r17` omission for half-duplex-only RedCap UE.
  - `cellBarredRedCap1Rx-r17` / `cellBarredRedCap2Rx-r17` barring behavior.
  - UPER encode/decode round-trip for `NR_SIB1_v1700_IEs`.
  - UPER encode/decode round-trip for `NR_UE_NR_Capability`.
- Registered the new test in `openair2/RRC/NR/tests/CMakeLists.txt` and linked the helper into `NR_L2_UE` from root `CMakeLists.txt`.
- Fixed an adjacent UE MAC build regression in `openair2/LAYER2/NR_MAC_UE/config_ue.c` by switching stale `get_sib1_initial_*` calls to `nr_ue_get_sib1_initial_*`.

## 3GPP Spec Clauses Referenced
- TS 38.331 Section 5.2.2.4.2 — half-duplex-only RedCap UE shall treat the cell as barred if `halfDuplexRedCapAllowed` is absent in acquired SIB1; `cellBarredRedCap1Rx/2Rx` semantics apply per UE Rx capability.
- TS 38.306 Section 4.2.21.1 — RedCap UE reduced-capability definition and RedCap capability components, including `supportOfRedCap-r17`.
- TS 38.331 ASN.1 `SIB1-v1700-IEs` / `RedCap-ConfigCommonSIB-r17` exact clause number: ⚠ Needs Verification.

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| `cmake --build --preset tests --target test_nr_rrc_redcap nr-uesoftmodem` | Pass | `rrc_ue_redcap.c`, `rrc_UE.c` call-site, `config_ue.c` link path | Log: `test_log/build_logs/redcap_m2_rrc_sib1_build_nolsan_final_2026-04-11_22-18-49.log` |
| `test_nr_rrc_redcap` | Pass | Half-duplex barring, 1Rx/2Rx barring, SIB1 UPER round-trip, UE capability UPER round-trip | Rebuilt with logging init; final regression log below |
| `ctest -R 'test_nr_rrc_redcap|test_nr_ue_redcap_bwp|test_nr_redcap_bwp|test_nr_redcap_coreset0|test_nr_redcap_sdt_fsm'` | Pass | New RRC test plus adjacent RedCap BWP/CORESET/SDT regressions | Log: `test_log/compiler_logs/redcap_m2_rrc_sib1_regression_retry_2026-04-11_22-19-41.log` |

## Known Issues / Blockers
- Docker runtime is still unavailable in the sandbox, so M5 end-to-end UL throughput evidence remains blocked.
- `TS 38.331` exact ASN.1 clause number for `SIB1-v1700-IEs` / `RedCap-ConfigCommonSIB-r17` still needs direct clause confirmation.

## Next Step
- Continue with Milestone 3: close the remaining `CORESET#0 Case B` runtime gap and verify the scheduler path against the RedCap initial DL BWP behavior.
