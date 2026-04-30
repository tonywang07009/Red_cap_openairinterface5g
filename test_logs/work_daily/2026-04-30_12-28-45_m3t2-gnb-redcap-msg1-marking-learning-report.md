# Educational Learning Report

## 1. Technical Background
[RedCap] UE can expose an early indication during [Random Access] by using feature-associated Msg1 preambles. In this task, the UE-side preamble selection already used [FeatureCombinationPreambles-r17.redCap-r17]. The missing part was gNB-side recognition. The gNB receives a [preamble_index] from PHY and creates a temporary [RA context]. We added a persistent flag, [is_redcap_msg1], so later scheduling code can distinguish a RedCap RA attempt from a baseline RA attempt before Msg2. This is important for [CORESET#0 Case B], where RedCap may use a separate initial BWP and common CORESET. Without the flag, Msg2 scheduling cannot safely decide whether to use the RedCap-specific control path or the baseline path.

## 2. Key C functions / Data structures utilized in this module
- `nr_initiate_ra_proc()` — creates or updates the gNB RA context after Msg1 PRACH detection.
- `NR_RA_t` — stores the temporary gNB-side Random Access state.
- `nr_redcap_is_msg1_preamble()` — checks if the received preamble belongs to a RedCap feature partition.
- `NR_RACH_ConfigCommon_t` — carries RACH common configuration, including Rel-17 extension fields.
- `NR_FeatureCombinationPreambles_r17_t` — ASN.1 structure for feature-associated preamble partitions.

## 3. Test Results Summary Table
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| `nr-softmodem` source build | PASS | gNB MAC RA compile/link | Validates C integration |
| `test_nr_redcap_bwp` build | PASS | RedCap RACH helper binary | Validates test target build |
| `ctest -R test_nr_redcap_bwp` | PASS | Unit test for RedCap Msg1 partition detection | Runtime RFsim not covered |

## 4. 3GPP Specification Mapping
| Clause | Mapping |
|--------|---------|
| TS 38.321 Random Access procedure [Needs Verification] | RedCap early indication may use Msg1/MsgA/Msg3 resources. |
| TS 38.331 `FeatureCombinationPreambles-r17` ASN.1 [Needs Verification] | Provides [redCap-r17], [startPreambleForThisPartition-r17], and [numberOfPreamblesPerSSB-ForThisPartition-r17]. |
| TS 38.213 Section 13 | Relevant to the next Msg2 CORESET#0 Case B scheduling gate. |

## 5. Practice Exercises
- Basic: Explain why gNB needs to store [is_redcap_msg1] instead of only storing [preamble_index].
- Applied: Given [startPreambleForThisPartition-r17 = 12] and [numberOfPreamblesPerSSB-ForThisPartition-r17 = 4], identify which preambles are RedCap for one SSB.
- Advanced: Propose how Msg2 scheduling should choose between baseline [CORESET#0] and RedCap Case B [commonControlResourceSet] using `ra->is_redcap_msg1`.
