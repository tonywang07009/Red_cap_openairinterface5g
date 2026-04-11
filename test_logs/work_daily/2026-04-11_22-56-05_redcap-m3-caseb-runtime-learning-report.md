# RedCap M3 Learning Report

## 1. Technical Background
RedCap Case B is not just a smaller BWP. It changes how the common control region is represented after the RedCap-specific initial DL BWP is cloned from SIB1/runtime config into the active gNB structures. In the older Type0 CSS path, `controlResourceSetZero`, `searchSpaceZero`, and `searchSpaceSIB1` describe the common search space. In the Case B path, those Type0 CSS anchors must be replaced by `commonControlResourceSet`, and every common search-space entry has to point to the new CORESET id. If that rebinding is skipped, the cloned RedCap BWP can look structurally valid while the PDCCH search spaces still point at the old Type0 CORESET representation. This sub-task therefore focused on making the runtime conversion itself testable, rather than only validating static configuration values.

## 2. Key C functions / Data structures utilized
- `nr_redcap_apply_case_b_common_coreset()` in `openair2/LAYER2/NR_MAC_gNB/nr_mac_redcap_bwp.c`
- `clone_redcap_downlink_bwp()` in `openair2/LAYER2/NR_MAC_gNB/nr_radio_config.c`
- `nr_redcap_validate_coreset0_dl_bwp()` in `openair2/LAYER2/NR_MAC_gNB/nr_mac_redcap_bwp.c`
- `NR_PDCCH_ConfigCommon_t`
- `NR_ControlResourceSet_t`
- `NR_SearchSpace_t`

## 3. Test Results Summary Table
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| `case_b_conversion_rebinds_common_searchspaces_and_clears_type0_css` | Pass | `commonControlResourceSet` install + search-space rebinding | Confirms the new Case B runtime helper mutates the cloned PDCCH config correctly |
| `case_b_conversion_requires_common_searchspace_list` | Pass | Failure path for malformed runtime clone input | Confirms the helper rejects missing common search-space state |
| Adjacent regression suite | Pass | `test_nr_ue_redcap_bwp`, `test_nr_redcap_coreset0`, `test_nr_redcap_sdt_fsm`, `test_nr_rrc_redcap` | Confirms M3 runtime coverage did not regress neighboring RedCap units |

## 4. 3GPP Specification Mapping
- TS 38.306 Section 4.2.21.1
  - RedCap UE operates with reduced bandwidth; the runtime BWP clone and Case B CORESET choice must stay inside that reduced envelope.
- TS 38.331 Section 5.2.2.4.2
  - RedCap common configuration in SIB1 anchors the initial BWP context later reused by the runtime cloning path.
- TS 38.331 `PDCCH-ConfigCommon`
  - ⚠ Needs Verification: exact clause number for the `commonControlResourceSet` / `commonSearchSpaceList` relationship used by the Case B runtime helper.

## 5. Practice Exercises
1. [Basic] Why is replacing `controlResourceSetZero` not sufficient by itself when moving a RedCap BWP into Case B?
2. [Applied] If the cloned PDCCH config keeps `searchSpaceZero` after `commonControlResourceSet` is installed, what scheduler symptom would you expect?
3. [Advanced] If future eRedCap work adds a third CORESET mode, which parts of the current helper should remain shared infrastructure and which parts should become per-mode policy?
