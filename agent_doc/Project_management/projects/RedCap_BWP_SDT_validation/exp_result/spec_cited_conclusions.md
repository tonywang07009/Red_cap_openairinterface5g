# Spec-Cited Conclusions For BWP / SDT Validation

## Converted Local Spec Sources

- [TS 38.523-1 BWP/SDT subset]: `../spec_refs/TS_38_523_Rel18_clauses_7_1_1_12_7_1_1_13_subset.md`
- [TS 38.321 MAC behavior]: `../spec_refs/TS_38_321_MAC_timers_DRX.md`
- [TS 38.300 SDT general behavior]: `../spec_refs/TS_38_300_RedCap_eRedCap_architecture.md`
- [Clause risk]: user request listed [TS 38.321 clause 5.9] for BWP; local TS 38.321 V18.2.0 places [BWP operation] at [clause 5.15], while [clause 5.9] is [Activation/Deactivation of SCells]. Treat the 5.9 mapping as `[Needs Verification]`.

## BWP Conclusions

- [BWP switch behavior] maps primarily to [TS 38.321 clause 5.15.1] and [TS 38.523-1 clause 7.1.1.12].
  - [Reason]: local TS 38.321 describes BWP switching as activation of an inactive BWP and deactivation of the active BWP, controlled by [PDCCH], [bwp-InactivityTimer], [RRC signalling], or [MAC random access behavior].
  - [Local impact]: `BWP_results.csv` currently proves only a clean UE2 RFsim baseline; it does not yet prove [active/default BWP occupancy] or [bwp-InactivityTimer expiry].

- [Power saving conclusion] is valid only after measuring [Default BWP ratio] and [Dedicated BWP ratio].
  - [Reason]: local TS 38.321 says the MAC does not monitor/transmit/receive on inactive or dormant BWPs, so a power-saving conclusion must be tied to actual BWP state residency.
  - [Current status]: coarse paper-side anchors exist, but local BWP state counters are `[TBD]`; no final power-saving claim should be made from the current UE2 attach/in-sync result alone.

- [Latency conclusion] must distinguish [scheduler health] from [BWP switch delay].
  - [Reason]: TS 38.321 clause 5.15.1 ties BWP switching to PDCCH/RRC/MAC events and `bwp-InactivityTimer`; a delay curve must capture the switch trigger and the resulting scheduling delay.
  - [Current status]: local counters show `dlsch_errors = 0`, `ulsch_errors = 0`, and zero retransmission ratio, but those are RFsim health metrics, not the paper's [PDU scheduling delay] reproduction.

## SDT Conclusions

- [RA-SDT gating] maps to [TS 38.523-1 clause 7.1.1.13.1] and [TS 38.300 clause 18].
  - [Reason]: the conformance test requires UE in [NR RRC_INACTIVE], configured RA-SDT resources, pending UL data not exceeding [sdt-DataVolumeThreshold], and RSRP above [sdt-RSRP-Threshold] before initiating RA-SDT.
  - [Current status]: `SDT_results.csv` now contains coarse paper-side anchors, but local SDT runtime values remain `[TBD]` because the Docker SDT run was blocked by workspace-credit approval rejection.

- [Threshold failure behavior] must be treated as a separate scenario, not a failed SDT run.
  - [Reason]: TS 38.523-1 clause 7.1.1.13.1 says when data volume exceeds [sdt-DataVolumeThreshold] or RSRP is below threshold, the UE should not initiate RA-SDT and should use normal RRC Resume.
  - [Local impact]: the SDT extractor must classify [normal resume due threshold] separately from [RA-SDT success] and [RA-SDT failure].

- [CG-SDT behavior] maps to [TS 38.523-1 clause 7.1.1.13.5] and [TS 38.300 clause 18].
  - [Reason]: CG-SDT requires [SDT-CG-Config-r17], data volume within threshold, RSRP/SSB conditions, and a running [cg-SDT-TimeAlignmentTimer]; timer expiry can redirect the UE to RA-SDT or terminate ongoing CG-SDT.
  - [Current status]: local runtime proof still requires a successful SDT log bundle showing [RRC_INACTIVE], [RA-SDT or CG-SDT initiation], [threshold decision], and final [RRC state].

## Evidence Status

| Area | Current evidence | Conclusion strength |
|---|---|---|
| [BWP RFsim health] | `BWP_runtime_evidence_20260625_213152.md`, `BWP_results.csv` | [Baseline only] |
| [BWP paper curve] | `paper_curve_digitization_template.csv` | `[TBD]` |
| [BWP clause mapping] | TS 38.321 [5.15.1] found; requested [5.9] is `[Needs Verification]` | [Partially confirmed] |
| [SDT runtime] | `SDT_runtime_blocker_20260625.md` | [Blocked] |
| [SDT clause mapping] | TS 38.523-1 [7.1.1.13.1], [7.1.1.13.5]; TS 38.300 [18] | [Confirmed from local Markdown] |
