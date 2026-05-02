# M3 BWP CORESET RA

## Scope
- RedCap initial DL/UL BWP.
- CORESET#0 Case A and Case B behavior.
- RA Msg2 DCI/PDSCH alignment for RedCap UE.

## Out of Scope
- 30/64 UE load scaling fixes.
- DRX/eDRX/PSM low-power implementation.
- New XML scenarios unless explicitly approved.

## 3GPP Spec Mapping
- TS 38.331 Section 6.3.2 — `initialDownlinkBWP-RedCap-r17` and related RedCap initial BWP fields. Exact subsection: [Needs Verification].
- TS 38.213 Section 13 — Type0 CSS and CORESET#0 behavior. Exact subsection: [Needs Verification].
- TS 38.321 Section 5.1 — Random Access procedure for Msg1/Msg2/Msg3/Msg4 flow.

## Target Files
- `openair2/GNB_APP/gnb_config.c`
- `openair2/LAYER2/NR_MAC_gNB/nr_mac_redcap_bwp.c`
- `openair2/LAYER2/NR_MAC_gNB/nr_mac_redcap_bwp.h`
- `openair2/LAYER2/NR_MAC_gNB/nr_radio_config.c`
- `openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_RA.c`
- `openair2/LAYER2/NR_MAC_UE/nr_ue_procedures.c`
- `ci-scripts/conf_files/gnb.sa.band78.fr1.106PRB.usrpb210.redcap.yaml`
- `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/`

## Implementation Tasks
- `M3-T1`: RedCap initial BWP config parse and validation.
- `M3-T2`: CORESET#0 Case A/B host runtime evidence.
- `M3-T3`: UE RA-RNTI common search space BWP alignment.

## Flow Validation
- Msg1 preamble is marked as RedCap when it belongs to the RedCap partition.
- Msg2 Case A uses Type0 CSS / CORESET0 behavior.
- Msg2 Case B uses `coreset_id=1` and BWP51.
- UE RA-RNTI monitoring must use the same BWP domain as gNB Msg2 DCI/PDSCH.

## System Unit Tests
- `UT-M3-001`: RedCap BWP helper and PRB cap test.
- `UT-M3-002`: CORESET#0 mode config parser test.
- `UT-M3-003`: UE RA-RNTI common search space BWP domain test.

## RFsim Runtime Tests
- `RT-M3-CASEA`: Case A RFsim attach and RAR validation.
- `RT-M3-CASEB`: Case B RFsim attach and RAR validation.
- `RT-M3-UE2-RAR`: UE2 RedCap RAR decode without LDPC failure.

## Completion Criteria
- [source build PASS]
- [unit test PASS]
- [container image rebuilt after C/C++ changes]
- [Case A RFsim runtime PASS]
- [Case B RFsim runtime PASS]
- [gNB and UE logs preserved]
