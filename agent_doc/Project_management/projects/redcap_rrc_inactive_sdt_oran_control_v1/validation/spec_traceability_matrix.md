# Spec Traceability Matrix

## Purpose
- Track the relationship between local RedCap behavior, 3GPP clauses, and O-RAN service model usage.
- Mark uncertain mappings as `[Needs Verification]`.
- Avoid fabricated clause numbers in reports.

## Local Spec Sources
- `redcap_doc/specs/redcap_3gpp/spec.md`
- `redcap_doc/specs/redcap_3gpp/redcap5g_spec.md`
- `redcap_doc/mineru_markdown/scan_manifest.md`

## Traceability Table
| Feature | Gate | Local Behavior | Reference | Verification Status |
|---|---|---|---|---|
| RRC_INACTIVE state | T2-1 | UE enters inactive after `RRCRelease.suspendConfig` | TS 38.331 | [Needs Verification] |
| RRCRelease suspendConfig | T2-1 | gNB releases UE with suspend context | TS 38.331 | [Needs Verification] |
| UE context retention | T2-1/T2-2 | gNB preserves UE context for resume | TS 38.331 | [Needs Verification] |
| PDCP counter preservation | T2-1/T2-2 | INACTIVE period does not reset PDCP SN | TS 38.331 / TS 38.323 | [Needs Verification] |
| RRCResumeRequest | T2-2 | UE requests resume from INACTIVE | TS 38.331 | [Needs Verification] |
| RRCResume / RRCResumeComplete | T2-2 | gNB resumes UE and UE returns CONNECTED | TS 38.331 | [Needs Verification] |
| SDT trigger | T2-3 | UE sends small data from INACTIVE path | TS 38.321 / TS 38.331 | [Needs Verification] |
| configuredGrantConfig | T2-3 | UE parses and stores configured grant resource | TS 38.331 | [Needs Verification] |
| cg-SDT | T2-3 | UE uses CG PUSCH for small data | TS 38.321 / TS 38.331 | [Needs Verification] |
| TA/RSRP threshold | T2-4 | UE falls back to 4-step RA when threshold is exceeded | TS 38.321 / TS 38.331 | [Needs Verification] |
| KPM observation | T2B | xApp receives metrics for policy decision | O-RAN E2SM-KPM | [Non-3GPP Scope] |
| RAN control | T2B | xApp sends bounded control request | O-RAN E2SM-RC / custom SM | [Non-3GPP Scope] |

## Reporting Rule
- [MUST] Keep `[Needs Verification]` until a local spec citation is confirmed.
- [MUST] Separate [3GPP protocol correctness] from [O-RAN control orchestration].
