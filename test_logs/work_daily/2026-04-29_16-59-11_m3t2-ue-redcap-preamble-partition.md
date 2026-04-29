# Work Daily Log
## Session Metadata
- Date: 2026-04-29 16:59
- Agent Session ID: N/A
- Task Slug: m3t2-ue-redcap-preamble-partition
- Project Path: agent_doc/Project_management/projects/redcap_mmtc_priority_execution_v1/project_plan.md

## Milestone & Sub-task Reference
- Milestone: [M3-T2 CORESET#0 Case A/B host validation]
- Sub-task: [UE RedCap preamble partition selection]
- Status: [COMPLETED]

## What Was Done
- Updated `openair2/LAYER2/NR_MAC_UE/nr_ra_procedures.c`.
- Added `is_redcap_ue_configured()` so RedCap UE checks can be reused by [Msg1] preamble selection and [Msg3] LCID selection.
- Added `get_redcap_feature_preamble_partition()` to find [FeatureCombinationPreambles-r17.redCap-r17].
- Updated `config_preamble_index()` so RedCap UE selects from [startPreambleForThisPartition-r17, numberOfPreamblesPerSSB-ForThisPartition-r17] when available.
- Preserved fallback behavior when UE is not RedCap or SIB1 does not contain [featureCombinationPreamblesList-r17].

## 3GPP Spec Clauses Referenced
- TS 38.300 local RedCap extract — RedCap UE may be identified by [MSG1/MSGA PRACH occasion/preamble].
- TS 38.321 local MAC extract — [(e)RedCap] UE selects feature-associated RA resources when available.
- TS 38.331 local ASN.1 `nr-rrc-17.3.0.asn1` — [FeatureCombinationPreambles-r17] contains [redCap-r17], [startPreambleForThisPartition-r17], and [numberOfPreamblesPerSSB-ForThisPartition-r17].
- TS 38.331 exact clause for [featureCombinationPreamblesList-r17]: [Needs Verification].

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| `nr-uesoftmodem` source build | PASS | UE MAC RA compile/link | Rebuilt after patch and format cleanup |
| `test_nr_ue_redcap_bwp` build | PASS | Closest UE RedCap unit target | Existing target |
| `ctest -R test_nr_ue_redcap_bwp --output-on-failure` | PASS | 1 CTest | Static RA selection not directly unit-covered |

## Known Issues / Blockers
- gNB RA context still does not mark [is_redcap_msg1] from received [preamble_index].
- Msg2 scheduler still does not gate [coreset_id=1 / BWP51] by [is_redcap_msg1].
- Runtime RFsim validation should wait until gNB Msg1 marking and Msg2 gate are implemented.

## Next Step
- Implement [gNB RA context RedCap Msg1 marking] from [preamble_index], then rebuild `nr-softmodem` and run the closest RedCap unit test.
