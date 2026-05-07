# Spec Traceability Matrix

## Purpose
- Track which local behavior maps to which 3GPP clause.
- Mark uncertain clause mappings as [Needs Verification].
- Prevent fabricated clause numbers in reports.

## Local Spec Sources
- `spec/redcap_3gpp/spec.md`
- `spec/redcap_3gpp/redcap5g_spec.md`
- `spec/redcap_3gpp/Redcap/`
- `spec/redcap_3gpp/DRX/`
- `spec/redcap_3gpp/eDRX/`
- `spec/redcap_3gpp/PSM/`
- `spec/redcap_3gpp/WUS/`
- `spec/redcap_3gpp/RRM/`

## Traceability Table
| Feature | Milestone | Local Behavior | 3GPP Reference | Verification Status |
|---|---|---|---|---|
| RedCap FR1 PRB cap | M1 | 20 MHz constrained RedCap BWP size | TS 38.101-1 Section 5.3; TS 38.306 Section 4 | [Needs Verification] |
| RedCap 1Rx / antenna limits | M1 | 1Rx mandatory, 2Rx optional, single Tx | TS 38.306 Section 4 | [Needs Verification] |
| SIB1 RedCap support | M2 | RedCap support and barring fields | TS 38.331 Section 6.3.1 / 6.3.2 | [Needs Verification] |
| RedCap initial BWP | M3 | `initialDownlinkBWP-RedCap-r17`, `initialUplinkBWP-RedCap-r17` | TS 38.331 Section 6.3.2 | [Needs Verification] |
| CORESET#0 Case A/B | M3 | Case A Type0 CSS, Case B common CORESET in RedCap BWP | TS 38.213 Section 13 | [Needs Verification] |
| Random Access | M3/M5 | Msg1, Msg2/RAR, Msg3, Msg4 | TS 38.321 Section 5.1 | [Partially Verified] |
| RAR reception | M3/M5 | UE receives RAR and decodes Msg2 | TS 38.321 Section 5.1.4 | [Needs Verification] |
| Contention resolution | M5 | Msg4 ACK and RA contention timer | TS 38.321 Section 5.1.5 | [Needs Verification] |
| Connected DRX | M4-B | Connected DRX timer handling and UE active-time gating | TS 38.321 Section 5.7; TS 38.331 Section 6.3.2 | [Partially Verified] |
| eDRX | M4-B | Idle/inactive eDRX advertisement and UE gating | TS 38.331 Section 6.3.2; TS 38.304 exact paging clause pending | [Partially Verified] |
| PSM | M4-B | NAS T3324/T3512 timer hooks for low-power behavior | TS 24.501 Section 8.2.7.1.1; TS 24.501 Section 5.5.1 | [Partially Verified] |
| FlexRIC xApp checks | M5/M6 | Existing KPM/RC runtime monitor only | O-RAN, non-3GPP | [Out of 3GPP Scope] |

## Reporting Rule
- If the exact clause cannot be confirmed from local specs, write `[Needs Verification]`.
- Do not upgrade any row to `[Verified]` without a local spec citation or user-provided source.
