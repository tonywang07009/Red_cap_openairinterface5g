# M3-T2 Case B Safe Design Checkpoint

## Scope
- Milestone: [M3-T2 CORESET#0 Case A/B host validation]
- Problem: [UE2 RedCap Case B] monitors [Msg2 RA-RNTI DCI] on [coreset_id=1 / BWP51], while gNB currently schedules [Msg2] on legacy [CORESET#0 / BWP48].
- Rejected approach: global duplicate [RA-RNTI DCI] for all RA attempts, because it regressed [UE1 baseline].

## Spec-Gated Finding
- [TS 38.300 local RedCap extract]: the network may associate a set of [RACH resources] with features including [(e)RedCap]; a feature-associated set is valid only for RA procedures applicable to that feature.
- [TS 38.300 local RedCap extract]: RedCap UE identification during random access can be via [MSG1/MSGA PRACH occasion or preamble], or later by [MSG3/MSGA RedCap-specific LCID].
- [TS 38.321 local DRX/MAC extract]: when [(e)RedCap] is applicable and [initialUplinkBWP-RedCap] / [initialDownlinkBWP-RedCap] are configured, UE switches to those BWPs for random access and monitors PDCCH there.
- [TS 38.331 ASN.1, local nr-rrc-17.3.0.asn1]: [RACH-ConfigCommon.ext2.featureCombinationPreamblesList-r17] contains [FeatureCombinationPreambles-r17], with [FeatureCombination-r17.redCap-r17], [startPreambleForThisPartition-r17], and [numberOfPreamblesPerSSB-ForThisPartition-r17].
- Conclusion: [Msg3 RedCap LCID] is too late to select [Msg2] CORESET/BWP. A mixed UE cell must use [Msg1 feature-associated RACH preamble/occasion] if gNB is to schedule [Msg2] differently for RedCap without harming legacy UE.

## Current OAI Implementation Evidence
- [UE side]: `openair2/LAYER2/NR_MAC_UE/nr_ra_procedures.c`
  - Current RedCap behavior only switches [Msg3] LCID via `use_redcap_msg3_ccch_lcid()`.
  - `config_preamble_index()` does not yet select [featureCombinationPreamblesList-r17].
- [gNB SIB1 side]: `openair2/LAYER2/NR_MAC_gNB/nr_radio_config.c`
  - `clone_redcap_uplink_bwp()` clones [RACH-ConfigCommon] into [initialUplinkBWP-RedCap-r17].
  - It does not yet populate [featureCombinationPreamblesList-r17].
- [gNB scheduler side]: `openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_RA.c`
  - `nr_initiate_ra_proc()` stores [preamble_index] before [Msg2].
  - This is the earliest safe point to mark an RA process as [RedCap Msg1-indicated].
  - `prepare_dl_pdus()` currently only logs [Msg2 DCI] placement; no safe RedCap gate is applied.

## Safe Design
- [Modification Point] -> [SIB1 RedCap UL BWP RACH partition]
  - [Reason] -> Broadcast a spec-defined [RedCap feature-associated preamble partition] inside [initialUplinkBWP-RedCap-r17].
  - [Before vs. After Comparison] -> Before: RedCap UL BWP clones common RACH only. After: cloned RedCap RACH includes [featureCombinationPreamblesList-r17] with [redCap-r17].
  - [Discussion Point] -> This gives UE2 a standards-based [Msg1] signal path; no global duplicate DCI is needed.

- [Modification Point] -> [UE preamble selection]
  - [Reason] -> RedCap UE must select the RedCap-associated RACH partition when the feature applies.
  - [Before vs. After Comparison] -> Before: RedCap UE only uses RedCap [Msg3 LCID]. After: RedCap UE also chooses the [redCap-r17] preamble partition before sending Msg1.
  - [Discussion Point] -> This keeps [Msg3 LCID] as later confirmation, not as the Msg2 scheduling gate.

- [Modification Point] -> [gNB RA process marking]
  - [Reason] -> gNB must know before scheduling [Msg2] whether the RA attempt is RedCap.
  - [Before vs. After Comparison] -> Before: all RA-RNTI attempts use legacy RA context. After: RA context records [is_redcap_msg1] when the received [preamble_index] falls inside the configured RedCap partition.
  - [Discussion Point] -> Legacy UE1 remains on legacy [CORESET#0]; only UE2 RedCap Msg1-indicated RA can use [coreset_id=1 / BWP51].

- [Modification Point] -> [Msg2 scheduler gate]
  - [Reason] -> Apply Case B [CORESET/BWP] only when [is_redcap_msg1] is true.
  - [Before vs. After Comparison] -> Before: unsafe global duplicate or legacy-only DCI. After: single gated RA-RNTI DCI path selected by Msg1 feature indication.
  - [Discussion Point] -> If no [featureCombinationPreamblesList-r17] is configured, mixed UE Case B must remain blocked/fallback because gNB cannot know RedCap before Msg2.

## Next Implementation Slice
- Add RedCap RACH partition fields/helper in gNB RedCap config.
- Populate [featureCombinationPreamblesList-r17] in `clone_redcap_uplink_bwp()`.
- Update UE `config_preamble_index()` to honor [redCap-r17] partition.
- Add RA context flag and gated Msg2 Case B path.
- Rebuild after C changes:
  - [source build] `cmake --build --preset default --target nr-softmodem`
  - [source build] `cmake --build --preset default --target nr-uesoftmodem`
- Unit/runtime validation:
  - [unit test] `test_nr_redcap_bwp`
  - [runtime] 2-UE RFsim: UE1 baseline attach/PDU/ping must remain PASS; UE2 RedCap Case B must receive Msg2 on [coreset_id=1 / BWP51].

## Status
- [source build] Not run: no C/C++ source was modified in this checkpoint.
- [unit test] Not run: design checkpoint only.
- [container image rebuilt] Not run.
- [RFsim UE/gNB/CN runtime] Not run.
