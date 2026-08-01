# M3-T2 Case B RA/RAR DCI Mismatch Report

## Technical Background
- [Task Name]：[M3-T2 CORESET#0 Case B host runtime evidence]
- [3GPP Spec Mapping]：
  - [TS 38.331 Clause 5.2.2.4.2]：SIB1 provides [initialDownlinkBWP-RedCap-r17] and [initialUplinkBWP-RedCap-r17] for RedCap UE cell access.
  - [TS 38.321 Clause 5.1.4]：UE monitors [RA-RNTI] during [ra-ResponseWindow] and processes [RAR] before Msg3.
  - [TS 38.213 Clause 13]：Type0 CSS / CORESET#0 determines common PDCCH monitoring resources.
- [Finding]：Case B SIB1 and UE BWP application are present, but [Msg2 DCI] is transmitted by gNB on legacy [CORESET#0/BWP48] while RedCap UE monitors [commonControlResourceSet id=1/BWP51].

## Code Modifications
- [Modification Point] → [Reason] → [Before vs. After Comparison] → [Discussion Point]
- [openair2/LAYER2/NR_MAC_UE/nr_ue_dci_configuration.c] → [Add UE-side RA-RNTI DCI diagnostics] → [Before: no visible RA DCI BWP/CORESET evidence; After: logs ss_id, coreset_id, BWPStart/BWPSize, FDR, DCI bits, candidates] → [Confirms UE monitors RedCap Case B CORESET id=1 and BWP size 51]
- [openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_RA.c] → [Add gNB-side Msg2 DCI diagnostics] → [Before: only Msg2 generation marker; After: logs ss_id, coreset_id, PDCCH/PDSCH BWP, FDR, CCE, aggregation, DCI bits] → [Confirms gNB schedules Msg2 on legacy CORESET id=0 and BWP size 48]
- [openair2/LAYER2/NR_MAC_UE/tests/CMakeLists.txt] → [Fix existing unit-test link dependency] → [Before: test_nr_ue_ra_procedures missed lib_nr_redcap_config; After: target links lib_nr_redcap_config] → [Keeps RA unit test buildable after RedCap config hooks]

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| [source build: nr-uesoftmodem] | PASS | UE MAC DCI config | Rebuilt after C patch |
| [source build: nr-softmodem] | PASS | gNB MAC RA scheduler | Rebuilt after C patch |
| [unit test: test_nr_ue_ra_procedures] | PASS | UE RA procedure unit test | `LSAN_OPTIONS=detect_leaks=0` |
| [container image rebuild] | PASS | ran-build / oai-gnb / oai-nr-ue | Local runtime images rebuilt |
| [RFsim Case B runtime] | FAIL | UE/gNB/CN host validation | UE1 attach OK; UE2 RedCap attach fails before PDU/ping |

## Runtime Evidence
- [gNB Case B marker]：
  - `RedCap CORESET#0 Case B edge-aligned PRB allocation: start=0 size=51 carrier_bw=106 common_coreset_id=1`
- [gNB Msg2 DCI]：
  - `rnti 010b ss_id 1 coreset_id 0 bwp_start 0 bwp_size 48 pdcch_bwp_start 0 pdcch_bwp_size 48 ... dci_bits 39`
- [UE RedCap DCI config]：
  - `rnti 010b ss_id 1 coreset_id 1 bwp_start 0 bwp_size 51 current_bwp_start 0 current_bwp_size 51 ... dci_bits 39`
- [UE failure]：
  - `RAR reception failed`
- [gNB failure]：
  - `RA failed at state WAIT_Msg3 (Reached msg3 max harq rounds)`

## Artifacts
- [Runtime summary]：`test_log/report/redcap_runtime_host_summary_case-b_disabled_2026-04-29_12-26-31.md`
- [Runtime wrapper log]：`test_log/compiler_logs/redcap_runtime_host_case-b_m3t2_ra_dci_diag_2026-04-29_12-26-31.log`
- [Runtime gNB log]：`cmake_targets/log/container_5g_flexric_rfsim_redcap.xml.d/27-100009-oai-gnb.logs`
- [Runtime UE2 log]：`cmake_targets/log/container_5g_flexric_rfsim_redcap.xml.d/27-100009-oai-nr-ue2.logs`
- [Unit test log]：`test_log/compiler_logs/ctest_test_nr_ue_ra_procedures_2026-04-29_12-23-19_m3t2-ra-dci-diag.log`

## Known Issues / Blockers
- [Case B attach blocker]：gNB [Msg2 DCI] and UE [RA-RNTI monitoring] use different [CORESET/BWP] views.
- [Next patch candidate]：teach gNB RA Msg2 scheduling to cover the RedCap Case B [commonControlResourceSet id=1 / BWP51] path without breaking normal UE1 legacy RA.

## Practice Exercises
- [Basic]：Explain why [RA-RNTI] DCI mismatch can cause [RAR reception failed].
- [Applied]：Compare gNB and UE log fields and identify which fields must match for Msg2 decode.
- [Advanced]：Design a dual-path Msg2 scheduling strategy that supports both normal UE and RedCap UE before the gNB knows UE capability.
