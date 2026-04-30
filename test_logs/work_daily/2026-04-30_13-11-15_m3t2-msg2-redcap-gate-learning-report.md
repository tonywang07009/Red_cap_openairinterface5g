# Educational Learning Report

## 1. Technical Background
[Msg2] is the Random Access Response. A RedCap UE in Case B may monitor [RA-RNTI] on a RedCap-specific initial downlink BWP and [commonControlResourceSet]. The gNB previously scheduled Msg2 using the legacy CORESET#0 view, so the UE and gNB could disagree on the PDCCH location. The new gate uses the Msg1 marker [is_redcap_msg1]. If the preamble is RedCap and Case B is configured, the gNB switches the temporary RA context to [initialDownlinkBWP-RedCap-r17] and [initialUplinkBWP-RedCap-r17] before scheduling Msg2 and Msg3. Baseline UE random access keeps the old path.

## 2. Key C functions / Data structures utilized in this module
- `nr_generate_Msg2()` — schedules RAR PDCCH/PDSCH and prepares Msg3 grant.
- `configure_redcap_msg2_bwp()` — applies the gated RedCap Case B RA BWP view.
- `prepare_dl_pdus()` — creates PDCCH/PDSCH PDUs and fills RA-RNTI DCI.
- `prepare_dci_dl_payload()` — encodes frequency-domain assignment for DCI 1_0.
- `NR_RA_t.is_redcap_msg1` — carries the Msg1 RedCap early indication.
- `NR_BWP_DownlinkCommon_t` / `NR_BWP_UplinkCommon_t` — hold RedCap initial BWP common configs.

## 3. Test Results Summary Table
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| `nr-softmodem` source build | PASS | gNB scheduler compile/link | Runtime not covered |
| `test_nr_redcap_bwp` build | PASS | RedCap BWP helper tests | No direct Msg2 runtime test |
| `ctest -R test_nr_redcap_bwp` | PASS | 1 unit test target | Protects RedCap BWP/RACH helper behavior |

## 4. 3GPP Specification Mapping
| Clause | Mapping |
|--------|---------|
| TS 38.331 Clause 5.2.2.4.2 [Needs Verification] | SIB1 carries RedCap initial BWP configuration. |
| TS 38.321 Clause 5.1.4 [Needs Verification] | UE monitors RA-RNTI and receives RAR during Random Access. |
| TS 38.213 Section 13 [Needs Verification] | Common PDCCH monitoring resources for CORESET#0 / Type0 CSS context. |
| TS 38.214 Section 5.1.2.2 | PDSCH frequency-domain resource assignment for DCI 1_0. |

## 5. Practice Exercises
- Basic: Why is [Msg3 RedCap LCID] too late for choosing the Msg2 CORESET?
- Applied: Compare baseline Msg2 and RedCap Case B Msg2. Which fields must match between UE and gNB logs?
- Advanced: Explain why RIV encoding must use [BWP51] for RedCap Case B instead of legacy [BWP48].
