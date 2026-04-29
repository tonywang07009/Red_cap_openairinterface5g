# Work Daily Log
## Session Metadata
- Date: 2026-04-29 16:54
- Agent Session ID: N/A
- Task Slug: m3t2-redcap-rach-feature-partition
- Project Path: agent_doc/Project_management/projects/redcap_mmtc_priority_execution_v1/project_plan.md

## Milestone & Sub-task Reference
- Milestone: [M3-T2 CORESET#0 Case A/B host validation]
- Sub-task: [Populate RACH-ConfigCommon.ext2.featureCombinationPreamblesList-r17]
- Status: [COMPLETED]

## What Was Done
- Added `nr_redcap_configure_rach_feature_combination_preambles()` in `openair2/LAYER2/NR_MAC_gNB/nr_mac_redcap_bwp.c`.
- Exported the helper in `openair2/LAYER2/NR_MAC_gNB/nr_mac_redcap_bwp.h`.
- Updated `clone_redcap_uplink_bwp()` in `openair2/LAYER2/NR_MAC_gNB/nr_radio_config.c` to add [featureCombinationPreamblesList-r17] to cloned [initialUplinkBWP-RedCap-r17] RACH config.
- Extended `openair2/LAYER2/NR_MAC_gNB/tests/test_nr_redcap_bwp.cpp` with tests for [redCap-r17] partition creation, total-preamble handling, and idempotence.

## 3GPP Spec Clauses Referenced
- TS 38.300 local RedCap extract — [(e)RedCap] may be associated with feature-specific [RACH resources] and can be indicated by [MSG1/MSGA PRACH occasion/preamble].
- TS 38.321 local MAC extract — [(e)RedCap] UE selects feature-associated RA resources when available.
- TS 38.331 local ASN.1 `nr-rrc-17.3.0.asn1` — [RACH-ConfigCommon.ext2.featureCombinationPreamblesList-r17] and [FeatureCombinationPreambles-r17] expose [redCap-r17] preamble partition fields.
- TS 38.331 exact clause for [featureCombinationPreamblesList-r17]: [Needs Verification].

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| `nr-softmodem` source build | PASS | gNB/RRC/MAC | Sandbox ccache run failed first; escalated rebuild passed |
| `test_nr_redcap_bwp` build | PASS | RedCap helper unit target | Built with tests preset |
| `ctest -R test_nr_redcap_bwp --output-on-failure` | PASS | 1 CTest / 13 GTest cases | `LSAN_OPTIONS=detect_leaks=0` |

## Known Issues / Blockers
- UE still does not select [redCap-r17] preamble partition in `nr_ra_procedures.c`.
- gNB RA context still does not mark [is_redcap_msg1] from [preamble_index].
- Msg2 scheduler still does not gate [coreset_id=1 / BWP51] by RedCap Msg1 indication.
- Mixed UE Case B runtime remains expected to fail for UE2 until the next slices are implemented.

## Next Step
- Implement [UE RedCap preamble partition selection] in `openair2/LAYER2/NR_MAC_UE/nr_ra_procedures.c`, then rebuild `nr-uesoftmodem` and run the closest UE/unit validation.
