# BWP / SDT Result Summary

## Difference Formula

- [diff_absolute] = `local_value - paper_value`
- [diff_percent] = `(local_value - paper_value) / paper_value * 100%`
- [Zero paper value rule]: if `paper_value = 0`, set [diff_percent] to `[NA]`.
- [TBD rule]: if either side is `[TBD]`, keep all diff fields as `[TBD]`.

## Paper Digitization Status

- [Template]: `paper_curve_digitization_template.csv`
- [Rendered pages]: `paper_figures/`
- [Digitization notes]: `paper_digitization_notes.md`
- [Calibration evidence]: `paper_digitization_calibration.csv`
- [Apply script]: `../scripts/apply_digitized_paper_values.py`
- [Current status]: 12 coarse paper-side anchors are marked `[text_anchor]` or `[calibrated_visual_digitized]` in `paper_curve_digitization_template.csv` and applied to the result CSVs.
- [Precision rule]: these anchors are suitable for workflow validation and placeholder plotting, not publication-grade curve digitization.

## Spec-Cited Conclusions

- [Report]: `spec_cited_conclusions.md`
- [OAI hook inventory]: `oai_hook_inventory.md`
- [BWP clause note]: local TS 38.321 V18.2.0 places [BWP operation] at [clause 5.15]; the originally requested [clause 5.9] maps to [Activation/Deactivation of SCells] and remains `[Needs Verification]`.
- [SDT clause note]: local Markdown confirms [TS 38.523-1 clause 7.1.1.13.1], [TS 38.523-1 clause 7.1.1.13.5], and [TS 38.300 clause 18] for the current SDT reproduction plan.
- [BWP implementation note]: local source scan marks [UE bwp-InactivityTimer implementation] as `[gap_present]`; current BWP RFsim data must remain [baseline only].

## BWP Comparison

| scenario | metric | paper_value | local_value | diff_absolute | diff_percent |
|---|---|---:|---:|---:|---:|
| local_rfsim_ue2_minimal_bwp | active_ue_count | TBD | 1 | TBD | TBD |
| local_rfsim_ue2_minimal_bwp | ue_in_sync_seen | TBD | 1 | TBD | TBD |
| local_rfsim_ue2_minimal_bwp | dlsch_errors | TBD | 0 | TBD | TBD |
| local_rfsim_ue2_minimal_bwp | ulsch_errors | TBD | 0 | TBD | TBD |
| local_rfsim_ue2_minimal_bwp | dlsch_retx_ratio_percent | TBD | 0.000000 | TBD | TBD |
| local_rfsim_ue2_minimal_bwp | ulsch_retx_ratio_percent | TBD | 0.000000 | TBD | TBD |
| local_rfsim_ue2_minimal_bwp | gnb_mac_tx_bytes | TBD | 15096 | TBD | TBD |
| local_rfsim_ue2_minimal_bwp | gnb_mac_rx_bytes | TBD | 146434 | TBD | TBD |
| high_load_bwp_8ms_1ms | default_bwp_ratio_percent | 0 | TBD | TBD | TBD |
| low_load_bwp_8ms_1ms | default_bwp_ratio_percent | 80 | TBD | TBD | TBD |
| low_load_bwp_8ms_1ms | power_saving_percent | 23.4857 | TBD | TBD | TBD |
| low_load_bwp_8ms_1ms | pdu_scheduling_delay_ms | 6.5583 | TBD | TBD | TBD |

## BWP Runtime Evidence

- [Run ID]: `20260625_213152_bwp`
- [Log Bundle]: `test_log/redcap_bwp_sdt_validation/20260625_213152_bwp/container_logs/full/`
- [Stable Evidence]: `exp_result/BWP_runtime_evidence_20260625_213152.md`
- [Extractor]: `scripts/extract_bwp_metrics.py`
- [Interpretation]: this is a local RFsim baseline proving UE2 RedCap attach/in-sync and clean HARQ counters; it is not yet a paper-curve reproduction because paper-comparable local BWP timer/switch-delay metrics remain `[TBD]`.

## SDT Comparison

| scenario | metric | paper_value | local_value | diff_absolute | diff_percent |
|---|---|---:|---:|---:|---:|
| 4_step_ra | packet_transmission_success_probability | TBD | TBD | TBD | TBD |
| 2_step_ra | packet_transmission_success_probability | TBD | TBD | TBD | TBD |
| 4_step_sdt | packet_transmission_success_probability | TBD | TBD | TBD | TBD |
| 2_step_sdt | packet_transmission_success_probability | TBD | TBD | TBD | TBD |
| 2_step_sdt_lambda_dp_5 | packet_transmission_success_probability | 0.4201 | TBD | TBD | TBD |
| 4_step_ra_slot10 | packet_transmission_success_probability | 0.2203 | TBD | TBD | TBD |
| 2_step_ra_slot10 | packet_transmission_success_probability | 0.3805 | TBD | TBD | TBD |
| 4_step_sdt_slot10 | packet_transmission_success_probability | 0.3093 | TBD | TBD | TBD |
| 2_step_sdt_slot10 | packet_transmission_success_probability | 0.4008 | TBD | TBD | TBD |
| 4_step_ra_lambda_dp_5 | packet_transmission_success_probability | 0.2511 | TBD | TBD | TBD |
| 2_step_ra_lambda_dp_5 | packet_transmission_success_probability | 0.4018 | TBD | TBD | TBD |
| 4_step_sdt_lambda_dp_5 | packet_transmission_success_probability | 0.3288 | TBD | TBD | TBD |

## SDT Runtime Status

- [Dry-run ID]: `20260625_213537_sdt`
- [Runtime status]: Docker `--run` was not executed in this turn because escalation was rejected with workspace credits unavailable.
- [Stable Evidence]: `exp_result/SDT_runtime_blocker_20260625.md`
- [Extractor]: `scripts/extract_sdt_metrics.py` is ready for the next successful SDT log bundle.

## Initial Reliable Conclusions

- [BWP] The paper reports that high offered load shows little BWP switching impact because UEs remain in Dedicated BWP; local validation must therefore include both high-load and low-load cases before judging BWP behavior.
- [BWP] The paper reports that shorter `bwp-InactivityTimer` increases time in Default BWP and estimated power saving, but can increase PDU scheduling delay and reduce throughput under low load.
- [BWP local baseline] UE2 RedCap RFsim ran in-sync with `dlsch_errors = 0`, `ulsch_errors = 0`, and retransmission ratios of `0.000000%`; this is a valid local RAN-health baseline, not yet the final paper delay/power curve.
- [SDT] The paper reports that [2-step SDT RA] has the highest packet transmission success probability, while the gain decreases as device intensity increases.
- [SDT local status] SDT RFsim metric generation remains pending until Docker runtime approval is available again; no SDT local curve should be inferred from BWP logs.
- [Spec citation status] see `spec_cited_conclusions.md`; TS 38.321 [BWP operation] is locally confirmed at clause 5.15.1, while the requested clause 5.9 mapping remains `[Needs Verification]`.
