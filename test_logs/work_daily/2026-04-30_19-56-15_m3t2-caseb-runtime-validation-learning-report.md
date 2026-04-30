# Educational Learning Report

## 1. Technical Background
- [RedCap Case B] uses a non-baseline common CORESET/search-space path for RedCap initial access.
- In this runtime, [UE2] correctly applied [SIB1 RedCap initial DL/UL BWP] and monitored [RA-RNTI] with `coreset_id=1` and `bwp_size=51`.
- The [gNB] still generated [Msg2 DCI] with `coreset_id=0` and `bwp_size=48`.
- This mismatch explains the repeated [RAR reception failed] events: the UE monitors the RedCap RA search space, while gNB schedules Msg2 on the baseline path.
- The immediate engineering question is why [gNB Msg1 RedCap marking] did not trigger for RedCap preambles.

## 2. Key C Functions / Data Structures Utilized
- [nr_initiate_ra_proc()] — creates/updates gNB RA context after PRACH detection.
- [NR_RA_t.is_redcap_msg1] — expected runtime flag for RedCap Msg1 classification.
- [nr_redcap_is_msg1_preamble()] — expected helper for checking RedCap preamble partition.
- [nr_generate_Msg2()] — generates Msg2/RAR scheduling.
- [prepare_dci_dl_payload()] — encodes Msg2 DCI payload fields.
- [ServingCellConfigCommon] / [initialDownlinkBWP_RedCap_r17] — RRC config source for RedCap BWP.

## 3. Test Results Summary Table
| Test Item | Status | Evidence |
|-----------|--------|----------|
| RFsim Case B scenario | FAIL | `333332` UE2 attach failed |
| UE1 baseline attach | PASS | UE1 got `10.0.0.2` |
| UE2 RedCap BWP apply | PASS | UE2 log shows RedCap DL/UL BWP start=0 size=51 |
| UE2 RA-RNTI monitor path | PASS | UE2 log shows `coreset_id 1`, `bwp_size 51` |
| gNB RedCap Msg1 marker | FAIL | `[RedCap RA][gNB Msg1]` not found |
| gNB RedCap Msg2 gate | FAIL | `[RedCap RA][gNB Msg2 gate]` not found |
| gNB Msg2 DCI path | FAIL | gNB DCI shows `coreset_id 0`, `bwp_size 48` |
| UE2 RAR reception | FAIL | UE2 log shows repeated `RAR reception failed` |

## 4. 3GPP Specification Mapping
- TS 38.331 Section 5.2.2.4.2 — [SIB1] broadcast of serving cell common configuration, relevant to RedCap initial BWP delivery.
- TS 38.321 Section 5.1 — [Random Access] procedure, relevant to Msg1/Msg2/Msg3/Msg4 flow.
- TS 38.321 Section 5.1.4 — [Random Access Response reception]. [⚠ Needs Verification]

## 5. Practice Exercises
- Basic: Explain why [UE2] monitoring `coreset_id=1` cannot decode [Msg2 DCI] scheduled by gNB on `coreset_id=0`.
- Applied: Use the gNB log to identify whether the RA flow reached [Msg1 marking], [Msg2 gate], or only [Msg2 DCI generation].
- Advanced: Propose one instrumentation point in `nr_initiate_ra_proc()` to prove whether RedCap preamble index 60-63 is being compared against the correct `FeatureCombinationPreambles-r17` range.
