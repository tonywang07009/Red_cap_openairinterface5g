# Spec-Cited Conclusions For BWP / SDT Validation

## Converted Local Spec Sources

- [TS 38.523-1 BWP/SDT subset]: `../spec_refs/TS_38_523_Rel18_clauses_7_1_1_12_7_1_1_13_subset.md`
- [TS 38.321 MAC behavior]: `../spec_refs/TS_38_321_MAC_timers_DRX.md`
- [TS 38.300 SDT general behavior]: `../spec_refs/TS_38_300_RedCap_eRedCap_architecture.md`
- [Clause risk]: user request listed [TS 38.321 clause 5.9] for BWP; local TS 38.321 V18.2.0 places [BWP operation] at [clause 5.15], while [clause 5.9] is [Activation/Deactivation of SCells]. Treat the 5.9 mapping as `[Needs Verification]`.

## BWP Conclusions

- [BWP switch behavior] maps primarily to [TS 38.321 clause 5.15.1] and [TS 38.523-1 clause 7.1.1.12].
  - [Reason]: local TS 38.321 describes BWP switching as activation of an inactive BWP and deactivation of the active BWP, controlled by [PDCCH], [bwp-InactivityTimer], [RRC signalling], or [MAC random access behavior].
  - [Local impact]: `BWP_results.csv` now includes post-fix marker-derived BWP matrix rows from `20260630_100615_bwp_matrix_apply_marker`; the tested BWP 1 -> 0 telnet trigger path no longer crashes gNB and emits post-ACK BWP0 apply evidence. It still does not prove full [bwp-InactivityTimer expiry] behavior because the timer remains a source gap.

- [Power saving conclusion] is valid only after measuring [Default BWP ratio] and [Dedicated BWP ratio].
  - [Reason]: local TS 38.321 says the MAC does not monitor/transmit/receive on inactive or dormant BWPs, so a power-saving conclusion must be tied to actual BWP state residency.
  - [Current status]: coarse paper-side anchors exist, and the 2026-06-30 post-fix matrix produced numeric marker-derived rows, but [traffic profile], [inactivity timer], and [switch delay] fields are `[wrapper_label]`; no final paper-equivalent power-saving claim should be made until runtime hooks are implemented or verified.

- [Latency conclusion] must distinguish [scheduler health] from [BWP switch delay].
  - [Reason]: TS 38.321 clause 5.15.1 ties BWP switching to PDCCH/RRC/MAC events and `bwp-InactivityTimer`; a delay curve must capture the switch trigger and the resulting scheduling delay.
  - [Current status]: 2026-06-30 matrix rows produce numeric `bwp_switch_apply_delay_ms` and `pdu_scheduling_delay_ms` values after BWP0 apply. These are local RFsim marker-derived delay values; the configured switch-delay dimension is still a wrapper label.

## SDT Conclusions

- [RA-SDT gating] maps to [TS 38.523-1 clause 7.1.1.13.1] and [TS 38.300 clause 18].
  - [Reason]: the conformance test requires UE in [NR RRC_INACTIVE], configured RA-SDT resources, pending UL data not exceeding [sdt-DataVolumeThreshold], and RSRP above [sdt-RSRP-Threshold] before initiating RA-SDT.
  - [Current status]: `20260627_200958_sdt_matrix` generated 36 RFsim samples across 12 RA/SDT scenarios, and `SDT_repeated_run_aggregate.csv` now has `run_count = 3` for every scenario. The local probabilities are marker-classified values, not publication-grade paper-equivalent stochastic curves.

- [Threshold failure behavior] must be treated as a separate scenario, not a failed SDT run.
  - [Reason]: TS 38.523-1 clause 7.1.1.13.1 says when data volume exceeds [sdt-DataVolumeThreshold] or RSRP is below threshold, the UE should not initiate RA-SDT and should use normal RRC Resume.
  - [Local impact]: the SDT extractor now exports `threshold_fallback_count` separately from `packet_success_count`, `timeout_failure_count`, and `sdt_failure_count`.

- [CG-SDT behavior] maps to [TS 38.523-1 clause 7.1.1.13.5] and [TS 38.300 clause 18].
  - [Reason]: CG-SDT requires [SDT-CG-Config-r17], data volume within threshold, RSRP/SSB conditions, and a running [cg-SDT-TimeAlignmentTimer]; timer expiry can redirect the UE to RA-SDT or terminate ongoing CG-SDT.
  - [Current status]: local runtime marker proof exists for [RRC_INACTIVE], [configuredGrantConfig], and [cg-SDT] from `SDT_runtime_evidence_20260626_230300.md` and the 2026-06-27 matrix. SDT rows are classified by `cg_sdt_marker`; RA rows are classified separately by `rrc_resume_complete`.

- [Scenario-semantics limitation] is now classified as `[wrapper_label]`.
  - [Reason]: `MMTC_RA_ACCESS_STEPS=2`, `slot10`, and `lambda_dp_5` are recorded in the runner/manifest, but targeted source scan found no OAI C or compose hook that changes RA steps, slot timing, or device intensity.
  - [Local impact]: `SDT_results.csv` may show `1.000000` local success probability for all 12 rows, but these are [marker-classified local RFsim probabilities] and must not be reported as final paper reproduction curves.

## Evidence Status

| Area | Current evidence | Conclusion strength |
|---|---|---|
| [BWP RFsim health] | `BWP_runtime_evidence_20260625_213152.md`, `BWP_runtime_evidence_20260628_151500.md`, `BWP_runtime_evidence_20260630_100615.md`, `BWP_results.csv` | [Post-fix matrix executed, no crash markers in tested rows] |
| [BWP paper curve] | `paper_curve_digitization_template.csv`; 2026-06-30 matrix rows in `BWP_results.csv` | [Local RFsim numeric evidence with wrapper-label semantics] |
| [BWP clause mapping] | TS 38.321 [5.15.1] found; requested [5.9] is `[Needs Verification]` | [Partially confirmed] |
| [SDT runtime] | `SDT_runtime_evidence_20260626_230300.md`; `20260627_200958_sdt_matrix`; `SDT_repeated_run_aggregate.csv` | [Marker-classified 12-scenario aggregate with limitations] |
| [SDT clause mapping] | TS 38.523-1 [7.1.1.13.1], [7.1.1.13.5]; TS 38.300 [18] | [Confirmed from local Markdown] |

## Remaining Verification Tasks

- [~] [BWP inactivity timer / residency counters]: current `bwp-InactivityTimer` gap is instrumented and Default/Dedicated BWP residency is derived from runtime logs; full timer behavior remains open.
- [~] [BWP low/high load sweep]: post-fix force-recreate matrix ran 8/8 rows and no longer crashes, but wrapper-label traffic/timer semantics still limit power-saving and delay claims.
- [~] [SDT RA/SDT success-probability matrix]: 12 scenarios x 3 repeated RFsim samples are complete and aggregated; paper-equivalent interpretation remains blocked by `[wrapper_label]` scenario semantics.
- [~] [Final report/plot refresh]: `SDT_results.csv`, `SDT_repeated_run_aggregate.csv`, `exp_result_summary.md`, and `exp_pictture/*.png` were refreshed after the 2026-06-27 matrix.
