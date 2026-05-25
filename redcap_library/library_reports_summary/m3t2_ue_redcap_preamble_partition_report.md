# M3-T2 UE RedCap Preamble Partition Report

## 1. Technical Background
- [Goal]: make RedCap UE consume the [redCap-r17] preamble partition broadcast in [RACH-ConfigCommon.ext2.featureCombinationPreamblesList-r17].
- [Spec Basis]: local TS 38.321 extract states that when [(e)RedCap] is applicable, UE selects feature-associated RA resources if available; otherwise it falls back to ordinary resources.
- [Design]: UE 4-step RA now checks the current UL BWP RACH config for a [FeatureCombinationPreambles-r17] entry containing [redCap-r17]. If present and UE RedCap mode is enabled, preamble selection is restricted to that partition.
- [Safety]: if [featureCombinationPreamblesList-r17] is absent or UE RedCap mode is disabled, existing legacy preamble selection remains unchanged.

## 2. Key C Functions / Data Structures
- `is_redcap_ue_configured()`
  - Centralizes the existing `load_nr_redcap_config()` check for UE RedCap mode.
- `get_redcap_feature_preamble_partition()`
  - Finds the [redCap-r17] entry in [featureCombinationPreamblesList-r17].
- `config_preamble_index()`
  - Applies the RedCap partition offset/count before randomizing [ra_PreambleIndex].
- `NR_FeatureCombinationPreambles_r17_t`
  - Carries [startPreambleForThisPartition-r17] and [numberOfPreamblesPerSSB-ForThisPartition-r17].

## 3. Test Results Summary
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| `nr-uesoftmodem` source build | PASS | UE MAC RA compile/link | Rebuilt after C patch and after format cleanup |
| `test_nr_ue_redcap_bwp` build | PASS | UE RedCap helper target | Existing closest UE RedCap unit target |
| `ctest -R test_nr_ue_redcap_bwp --output-on-failure` | PASS | 1 CTest | Does not directly cover static RA preamble selection |

## 4. 3GPP Specification Mapping
- TS 38.300 local RedCap extract — RedCap UE can be identified by [MSG1/MSGA PRACH occasion/preamble] when RedCap-specific RA resources are configured.
- TS 38.321 local MAC extract — [(e)RedCap] UE selects feature-associated RA resources if available; otherwise fallback resources can be used.
- TS 38.331 local ASN.1 `nr-rrc-17.3.0.asn1` — [FeatureCombinationPreambles-r17] provides [redCap-r17] partition fields.
- Exact TS 38.331 clause number for [featureCombinationPreamblesList-r17]: [Needs Verification].

## 5. Practice Exercises
- [Basic]: Why does UE need to choose a RedCap-specific [Msg1] preamble before Msg2?
- [Applied]: What should happen if [featureCombinationPreamblesList-r17] is absent from SIB1?
- [Advanced]: How should gNB map received [preamble_index] to [is_redcap_msg1] while preserving legacy UE RA behavior?

## Modification Log
- [Modification Point] -> `nr_ra_procedures.c`
  - [Reason] -> Implement UE-side selection of [redCap-r17] feature-associated preamble resources.
  - [Before vs. After Comparison] -> Before: RedCap UE only used RedCap [Msg3 LCID]; Msg1 preamble selection remained generic. After: RedCap UE uses [FeatureCombinationPreambles-r17.redCap-r17] partition when available.
  - [Discussion Point] -> This enables the next gNB slice to identify RedCap RA before scheduling Msg2.

## Known Coverage Gap
- The closest UE unit test passed, but there is not yet a direct unit test for `config_preamble_index()` because it is static and tied to RA runtime state.
- Recommended next test addition: extract the RedCap partition lookup/range calculation into a small testable helper if this behavior expands.
