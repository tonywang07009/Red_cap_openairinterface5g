# M3-T2 RedCap RACH Feature Partition Report

## 1. Technical Background
- [Goal]: prepare the spec-compliant Msg1-stage signal path for [UE2 RedCap Case B] before touching [Msg2 scheduler gating].
- [Spec Basis]: local TS 38.300 / TS 38.321 extracts require [(e)RedCap] UE random access to use RedCap-applicable resources when available; local TS 38.331 ASN.1 exposes [RACH-ConfigCommon.ext2.featureCombinationPreamblesList-r17].
- [Design]: the gNB now adds a [FeatureCombinationPreambles-r17] entry with [FeatureCombination-r17.redCap-r17] to the cloned [initialUplinkBWP-RedCap-r17] RACH config.
- [Safety]: this patch only broadcasts the RedCap feature-associated preamble partition. It does not yet change UE preamble choice or gNB Msg2 CORESET/BWP scheduling, so [UE1 baseline] scheduler behavior remains untouched in this slice.

## 2. Key C Functions / Data Structures
- `nr_redcap_configure_rach_feature_combination_preambles()`
  - Adds an idempotent [redCap-r17] feature preamble partition to `NR_RACH_ConfigCommon_t`.
- `clone_redcap_uplink_bwp()`
  - Calls the new helper after cloning [RACH-ConfigCommon] for [initialUplinkBWP-RedCap-r17].
- `NR_FeatureCombinationPreambles_r17_t`
  - Carries [startPreambleForThisPartition-r17] and [numberOfPreamblesPerSSB-ForThisPartition-r17].

## 3. Test Results Summary
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| `nr-softmodem` source build | PASS | gNB/RRC/MAC build | First sandbox run failed due ccache `/run/user/1000` read-only; escalated rebuild passed |
| `cmake --build --preset tests --target test_nr_redcap_bwp` | PASS | RedCap BWP helper test build | Added RACH feature partition tests |
| `ctest -R test_nr_redcap_bwp --output-on-failure` | PASS | 1 CTest / 13 GTest cases | `LSAN_OPTIONS=detect_leaks=0` used to avoid prior local LSAN ptrace issue |

## 4. 3GPP Specification Mapping
- TS 38.300 local RedCap extract — [(e)RedCap] can be associated with a set of [RACH resources], and RedCap UE can be identified by [MSG1/MSGA PRACH occasion/preamble].
- TS 38.321 local MAC extract — [(e)RedCap] UE selects feature-associated RA resources when available and switches to RedCap initial UL/DL BWP for RA when configured.
- TS 38.331 local ASN.1 `nr-rrc-17.3.0.asn1` — [RACH-ConfigCommon.ext2.featureCombinationPreamblesList-r17] and [FeatureCombinationPreambles-r17] define [redCap-r17] preamble partition fields.
- Exact TS 38.331 clause number for [featureCombinationPreamblesList-r17]: [Needs Verification].

## 5. Practice Exercises
- [Basic]: What is the difference between [Msg1 RedCap feature indication] and [Msg3 RedCap LCID]?
- [Applied]: Why is [Msg3 RedCap LCID] too late to decide the [Msg2] CORESET/BWP?
- [Advanced]: Design the next gNB scheduler gate that maps a received [preamble_index] to [is_redcap_msg1] without affecting legacy UE RA.

## Modification Log
- [Modification Point] -> `nr_mac_redcap_bwp.h`
  - [Reason] -> Export a small helper for RedCap RACH feature preamble partitioning.
  - [Before vs. After Comparison] -> Before: no API for [featureCombinationPreamblesList-r17]. After: `nr_redcap_configure_rach_feature_combination_preambles()` is available.
  - [Discussion Point] -> Keeping this helper near other RedCap BWP helpers makes it unit-testable.
- [Modification Point] -> `nr_mac_redcap_bwp.c`
  - [Reason] -> Populate [FeatureCombinationPreambles-r17.redCap-r17] with a tail partition.
  - [Before vs. After Comparison] -> Before: RedCap BWP helpers only handled BWP/CORESET. After: helper adds idempotent RACH feature partition.
  - [Discussion Point] -> Default partition uses the last 4 preambles per SSB; future UE/gNB gates should consume the same policy.
- [Modification Point] -> `nr_radio_config.c`
  - [Reason] -> Broadcast the partition in [initialUplinkBWP-RedCap-r17].
  - [Before vs. After Comparison] -> Before: RedCap UL BWP cloned common RACH unchanged. After: cloned RedCap RACH carries [featureCombinationPreamblesList-r17].
  - [Discussion Point] -> This is the prerequisite for spec-compliant Msg1-stage RedCap identification.
- [Modification Point] -> `test_nr_redcap_bwp.cpp`
  - [Reason] -> Guard ASN.1 field population, total preamble handling, and idempotence.
  - [Before vs. After Comparison] -> Before: 10 helper cases. After: 13 helper cases.
  - [Discussion Point] -> Runtime behavior still requires the next UE/gNB slices.
