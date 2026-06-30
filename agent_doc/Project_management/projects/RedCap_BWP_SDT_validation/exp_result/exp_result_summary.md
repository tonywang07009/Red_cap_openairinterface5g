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
- [BWP implementation note]: local source scan marks [UE bwp-InactivityTimer implementation] as `[gap_present]`; current BWP traffic/timer/switch-delay scenario fields are `[wrapper_label]`.
- [BWP crash note]: the historical `20260628_151500_bwp_matrix_recreate` matrix reproduced the BWP 1 -> 0 crash; the post-fix `20260630_100615_bwp_matrix_apply_marker` matrix completed 8/8 rows with `runner_failures = 0`.
- [BWP instrumentation note]: source markers `[RedCap BWP][gNB reconfiguration]`, `[RedCap BWP][gNB apply]`, `[RedCap BWP][gNB interrupt]`, and `[RedCap BWP][UE RA]` are available, and the extractor now derives BWP residency, switch/apply delay, PDU scheduling delay, throughput, and estimated power saving from timestamped logs.
- [BWP extractor note]: `scripts/test_extract_bwp_metrics.py` validates marker parsing and residency/delay extraction; `scripts/test_merge_runtime_metrics.py` prevents stale local metric leakage when newer runtime CSVs omit a metric.
- [SDT aggregation note]: `scripts/test_extract_sdt_metrics.py` validates attempt/success/fallback/timeout counters; `scripts/aggregate_sdt_success.py` writes `SDT_repeated_run_aggregate.csv`.
- [Runtime layering note]: SDT protocol runtime is owned by `redcap_rrc_inactive_sdt_oran_control_v1` [Case A Gate 3]; this project performs paper-facing log collation, CSV merge, and comparison reporting.

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
| high_load_bwp_8ms_1ms | default_bwp_ratio_percent | 0 | 0.000000 | 0.000000 | NA |
| low_load_bwp_8ms_1ms | default_bwp_ratio_percent | 80 | 0.000000 | -80.000000 | -100.000000 |
| low_load_bwp_8ms_1ms | power_saving_percent | 23.4857 | 0.000000 | -23.485700 | -100.000000 |
| low_load_bwp_8ms_1ms | pdu_scheduling_delay_ms | 6.5583 | TBD | TBD | TBD |
| local_rfsim_ue2_bwp_trigger_1_0 | bwp_gnb_reconfiguration_count | TBD | 1 | TBD | TBD |
| local_rfsim_ue2_bwp_trigger_1_0 | bwp_gnb_reconfiguration_last_new_bwp_id | TBD | 0 | TBD | TBD |
| local_rfsim_ue2_bwp_trigger_1_0 | bwp_ue_ra_operation_count | TBD | 2 | TBD | TBD |
| local_rfsim_ue2_bwp_trigger_1_0 | bwp_inactivity_timer_gap_seen | TBD | 1 | TBD | TBD |
| local_rfsim_ue2_bwp_trigger_1_0 | default_bwp_ratio_percent | TBD | 10.674214 | TBD | TBD |
| local_rfsim_ue2_bwp_trigger_1_0 | bwp_switch_apply_delay_ms | TBD | 1.445000 | TBD | TBD |
| local_rfsim_ue2_bwp_trigger_1_0 | pdu_scheduling_delay_ms | TBD | 4.249000 | TBD | TBD |
| local_rfsim_ue2_bwp_trigger_1_0 | power_saving_percent | TBD | 5.538507 | TBD | TBD |

## BWP Runtime Evidence

- [Run ID]: `20260625_213152_bwp`
- [Log Bundle]: `test_log/redcap_bwp_sdt_validation/20260625_213152_bwp/container_logs/full/`
- [Stable Evidence]: `exp_result/BWP_runtime_evidence_20260625_213152.md`
- [Extractor]: `scripts/extract_bwp_metrics.py`
- [Interpretation]: this is a local RFsim baseline proving UE2 RedCap attach/in-sync and clean HARQ counters; it is not yet a paper-curve reproduction because paper-comparable local BWP timer/switch-delay metrics remain `[TBD]`.
- [Marker Run ID]: `20260626_231100_bwp_local_ci`
- [Marker Log Bundle]: `test_log/redcap_bwp_sdt_validation/20260626_231100_bwp_local_ci_bwp/container_logs/full/`
- [Marker Evidence]: `exp_result/BWP_runtime_evidence_20260626_231100.md`
- [Interpretation]: local-image run proves BWP 0 reconfiguration marker, UE RA marker extraction, and marker-derived residency/delay estimates. It still does not reproduce the full paper delay/power curve because `bwp-InactivityTimer` remains a source gap and no high/low traffic matrix was run.
- [Marker-derived local estimates]:
  - `default_bwp_ratio_percent = 10.674214`
  - `power_saving_percent = 5.538507` using `default_ratio_x_prb_delta`
  - `bwp_switch_apply_delay_ms = 1.445000`
  - `pdu_scheduling_delay_ms = 4.249000`
- [Matrix Run ID]: `20260628_151500_bwp_matrix_recreate`
- [Matrix Evidence]: `exp_result/BWP_runtime_evidence_20260628_151500.md`
- [Matrix Interpretation]: 8/8 force-recreate RFsim rows completed, but every BWP 0 trigger crashed gNB; matrix values are crash-repro evidence and do not satisfy Gate 5 PASS criteria.
- [Backtrace Run ID]: `20260628_154000_bwp_trigger0_bt`
- [Backtrace Frame]: `update_cellGroupConfig_for_BWP_switch+0x151`, called through `nr_mac_trigger_reconfiguration` and `nr_trigger_bwp_switch`.
- [Post-fix Single Trigger Run ID]: `20260630_100054_bwp_trigger0_apply_marker`
- [Post-fix Bidirectional Run ID]: `20260630_100329_bwp_bidirectional_apply_marker`
- [Post-fix Matrix Run ID]: `20260630_100615_bwp_matrix_apply_marker`
- [Post-fix Matrix Evidence]: `exp_result/BWP_runtime_evidence_20260630_100615.md`
- [Post-fix Matrix Interpretation]: 8/8 force-recreate RFsim rows completed with no gNB crash markers; each row produced numeric local values for Default BWP ratio, estimated power saving, switch apply delay, PDU scheduling delay, throughput, and final BWP0 apply evidence.

## Local Validation On 2026-06-26

| item | result |
|---|---|
| `nr-softmodem` build | [PASS] with `CCACHE_DIR=/tmp/ccache` and `CCACHE_TEMPDIR=/tmp/ccache-tmp` |
| `nr-uesoftmodem` build | [PASS] with `CCACHE_DIR=/tmp/ccache` and `CCACHE_TEMPDIR=/tmp/ccache-tmp` |
| BWP extractor smoke test | [PASS] |
| BWP extractor CLI dry run on existing logs | [PASS]; marker counts remain `0` because the existing log bundle predates the new markers |
| OAI hook audit | [PASS]; instrumentation hooks are listed in `oai_hook_inventory.md` |
| local image rebuild | [PASS]; `oai-gnb:latest` and `oai-nr-ue:latest` contain `[RedCap BWP]` markers |
| SDT local-image runtime | [PASS]; `20260626_230300_sdt_local`, 15 runtime rows merged |
| BWP local-image marker runtime | [PASS]; `20260626_231100_bwp_local_ci`, 21 runtime rows merged |
| BWP residency/delay extractor rerun | [PASS]; `20260626_231100_bwp_local_ci`, 35 runtime rows merged |
| SDT success-counter extractor rerun | [PASS]; `20260626_230300_sdt_local`, 24 runtime rows merged |
| SDT aggregate script | [PASS]; `SDT_repeated_run_aggregate.csv` generated for `local_rfsim_ue2_minimal_sdt` |
| BWP/SDT matrix dry-run | [PASS]; BWP expands 8 scenarios, SDT expands 12 scenarios x `SDT_REPEATS=3` |
| Plot refresh | [PASS]; `rtk python agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/exp_pictture/plot_paper_vs_local.py` refreshed `exp_pictture/BWP_paper_vs_local.png` and `exp_pictture/SDT_paper_vs_local.png` |

## Local Validation On 2026-06-27

| item | result |
|---|---|
| SDT matrix runner correction | [PASS]; `run_sdt_validation.sh` can delegate through `smoke` for scenario-specific gate flags, while standalone default remains `gate3` |
| SDT matrix failure handling | [PASS]; `run_sdt_matrix.sh` continues after per-run runner rc failures and aggregates the current `BASE_RUN_ID` only |
| SDT extractor classifier correction | [PASS]; RA scenarios use `rrc_resume_complete`, SDT scenarios use `cg_sdt_marker` |
| SDT 12 scenario repeated runtime | [PARTIAL PASS]; `20260627_200958_sdt_matrix`, 36/36 runtime CSVs generated, 12 scenarios x 3 repeats |
| SDT repeated-run aggregate | [PASS]; `SDT_repeated_run_aggregate.csv` has `run_count = 3` for all 12 scenarios |
| SDT local probability values | [PARTIAL]; all 12 scenarios are marker-classified `1.000000`, but 2-step RA, slot10, and `lambda_dp_5` dimensions are `[wrapper_label]` |
| RFsim user-plane ping | [PARTIAL]; attach/PDU/TUN repeatedly appeared, but many forward/reverse ping checks failed; do not use ping success as the SDT success-probability source |
| Plot refresh | [PASS]; `BWP_paper_vs_local.png` and `SDT_paper_vs_local.png` refreshed after CSV update |
| Docker cleanup/status | [BLOCKED]; escalated Docker status/cleanup was rejected because workspace credits are unavailable |

## Local Validation On 2026-06-28

| item | result |
|---|---|
| SymDex hook audit | [PASS]; RA/SDT gate env hooks found, SDT 2-step/slot/lambda dimensions marked `[wrapper_label]` |
| BWP matrix wrapper fix | [PASS]; `run_bwp_matrix.sh` now sets `BWP_TRIGGER_SEQUENCE='1 0'`, `STOP_AFTER_RUN=1`, and `REDCAP_COMPOSE_FORCE_RECREATE=1` |
| BWP full matrix runtime | [BLOCKED]; `20260628_151500_bwp_matrix_recreate` completed 8/8 rows, but all 8 rows hit gNB `Segmentation fault` after BWP 0 trigger |
| BWP crash backtrace | [PASS]; `20260628_154000_bwp_trigger0_bt` captured `update_cellGroupConfig_for_BWP_switch+0x151` in the gNB backtrace |
| Runtime merge hygiene | [PASS]; `merge_runtime_metrics.py --replace-scenario` resets stale local values when newer runtime CSVs omit a metric |
| BWP plot refresh | [PASS]; plot refreshed after CSV cleanup |

## Local Validation On 2026-06-30

| item | result |
|---|---|
| BWP trigger0 crash fix | [PASS]; `20260630_100054_bwp_trigger0_apply_marker` completed with final `bwp_gnb_apply_last_new_dl_bwp_id = 0` and no gNB crash marker |
| BWP bidirectional trigger sanity | [PASS]; `20260630_100329_bwp_bidirectional_apply_marker` completed `0 1 0`, final apply returned to BWP 0 |
| BWP full matrix runtime | [PASS]; `20260630_100615_bwp_matrix_apply_marker` completed 8/8 rows with `runner_failures = 0` |
| BWP runtime metrics | [PASS]; all eight matrix scenarios have numeric `default_bwp_ratio_percent`, `power_saving_percent`, `bwp_switch_apply_delay_ms`, and `pdu_scheduling_delay_ms` rows |
| Plot refresh | [PASS]; `BWP_paper_vs_local.png` and `SDT_paper_vs_local.png` refreshed after CSV update |
| Paper-equivalence status | [LIMITED]; BWP traffic profile, inactivity timer, and switch-delay controls remain `[wrapper_label]` / source-gap limited |

## SDT Comparison

| scenario | metric | paper_value | local_value | diff_absolute | diff_percent |
|---|---|---:|---:|---:|---:|
| 4_step_ra | packet_transmission_success_probability | TBD | 1.000000 | TBD | TBD |
| 2_step_ra | packet_transmission_success_probability | TBD | 1.000000 | TBD | TBD |
| 4_step_sdt | packet_transmission_success_probability | TBD | 1.000000 | TBD | TBD |
| 2_step_sdt | packet_transmission_success_probability | TBD | 1.000000 | TBD | TBD |
| 2_step_sdt_lambda_dp_5 | packet_transmission_success_probability | 0.4201 | 1.000000 | 0.579900 | 138.038562 |
| 4_step_ra_slot10 | packet_transmission_success_probability | 0.2203 | 1.000000 | 0.779700 | 353.926464 |
| 2_step_ra_slot10 | packet_transmission_success_probability | 0.3805 | 1.000000 | 0.619500 | 162.812089 |
| 4_step_sdt_slot10 | packet_transmission_success_probability | 0.3093 | 1.000000 | 0.690700 | 223.310702 |
| 2_step_sdt_slot10 | packet_transmission_success_probability | 0.4008 | 1.000000 | 0.599200 | 149.500998 |
| 4_step_ra_lambda_dp_5 | packet_transmission_success_probability | 0.2511 | 1.000000 | 0.748900 | 298.247710 |
| 2_step_ra_lambda_dp_5 | packet_transmission_success_probability | 0.4018 | 1.000000 | 0.598200 | 148.880040 |
| 4_step_sdt_lambda_dp_5 | packet_transmission_success_probability | 0.3288 | 1.000000 | 0.671200 | 204.136253 |
| local_rfsim_ue2_minimal_sdt | packet_transmission_success_probability | TBD | 1.000000 | TBD | TBD |
| local_rfsim_ue2_minimal_sdt | packet_attempt_count | TBD | 1 | TBD | TBD |
| local_rfsim_ue2_minimal_sdt | packet_success_count | TBD | 1 | TBD | TBD |
| local_rfsim_ue2_minimal_sdt | threshold_fallback_count | TBD | 0 | TBD | TBD |
| local_rfsim_ue2_minimal_sdt | timeout_failure_count | TBD | 0 | TBD | TBD |

## SDT Runtime Status

- [Dry-run ID]: `20260625_213537_sdt`
- [Runtime Run ID]: `20260626_230300_sdt_local`
- [Runtime status]: local-image Docker runtime completed and merged 15 rows into `SDT_results.csv`.
- [Stable Evidence]: `exp_result/SDT_runtime_evidence_20260626_230300.md`
- [Extractor]: `scripts/extract_sdt_metrics.py`
- [Aggregator]: `scripts/aggregate_sdt_success.py`
- [Observed local markers]: `rrc_inactive_marker_seen = 1`, `configured_grant_marker_seen = 1`, `cg_sdt_marker_seen = 1`, `cg_sdt_rx_candidate_count = 313`, `rrc_resume_request_seen = 0`, `rrc_resume_complete_seen = 0`.
- [Observed local counters]: `packet_attempt_count = 1`, `packet_success_count = 1`, `threshold_fallback_count = 0`, `timeout_failure_count = 0`, `packet_transmission_success_probability = 1.000000`.
- [Matrix Run ID]: `20260627_200958_sdt_matrix`
- [Matrix Evidence Root]: `test_log/redcap_bwp_sdt_validation/20260627_200958_sdt_matrix_*_sdt/`
- [Matrix aggregate]: `SDT_repeated_run_aggregate.csv`; 12 scenarios x 3 repeats, `packet_attempt_count = 3`, `packet_success_count = 3`, `threshold_fallback_count = 0`, `timeout_failure_count = 0`, `sdt_failure_count = 0` for every scenario.
- [Bilingual explanation]: `report/SDT_small_packet_experiment_explanation_bilingual.md`
- [Runner alignment]: standalone SDT validation still defaults to `redcap_interface/mmtc.menu.bash gate3`; matrix runs use `MMTC_SDT_MENU_SUBCOMMAND=smoke` so RA/SDT gate flags are preserved.
- [Classifier limitation]: RA rows are classified by `rrc_resume_complete`; SDT rows are classified by `cg_sdt_marker`. The local probabilities are marker-classified values, not publication-grade stochastic paper reproduction.
- [Runtime limitation]: `MMTC_RA_ACCESS_STEPS=2`, `slot10`, and `lambda_dp_5` are `[wrapper_label]` dimensions in the current implementation; exact OAI hook impact is not present.

## Remaining Paper-Comparable Work

- [~] [BWP inactivity timer / residency counters]: current gap is instrumented and post-fix matrix rows produce numeric residency and delay estimates; real UE `bwp-InactivityTimer` behavior remains a source gap.
- [~] [BWP low/high load sweep]: 8/8 post-fix force-recreate runtime rows completed, but traffic/timer/switch-delay fields remain `[wrapper_label]`, so this is local RFsim evidence rather than publication-grade paper reproduction.
- [~] [SDT RA/SDT success-probability matrix]: 36 repeated RFsim samples completed and aggregate values are numeric; 2-step RA, slot10, and `lambda_dp_5` are `[wrapper_label]`.
- [~] [Final report/plot refresh]: CSVs, aggregate, and plots were refreshed after SDT matrix execution; conclusion text still marks non-paper-equivalent local limitations.

## Initial Reliable Conclusions

- [BWP] The paper reports that high offered load shows little BWP switching impact because UEs remain in Dedicated BWP; local validation must therefore include both high-load and low-load cases before judging BWP behavior.
- [BWP] The paper reports that shorter `bwp-InactivityTimer` increases time in Default BWP and estimated power saving, but can increase PDU scheduling delay and reduce throughput under low load.
- [BWP local baseline] UE2 RedCap RFsim now completes BWP 1 -> 0 and `0 1 0` telnet reconfiguration without gNB crash, and the 2026-06-30 matrix provides numeric local BWP residency, estimated power saving, switch apply delay, PDU scheduling delay, and throughput evidence.
- [SDT] The paper reports that [2-step SDT RA] has the highest packet transmission success probability, while the gain decreases as device intensity increases.
- [SDT local status] SDT RFsim marker generation is available, and `20260627_200958_sdt_matrix` produced marker-classified repeated-run values for all 12 paper scenarios; paper-equivalent stochastic success-probability claims remain limited by unverified 2-step/slot/lambda runtime semantics and ping flakiness.
- [Spec citation status] see `spec_cited_conclusions.md`; TS 38.321 [BWP operation] is locally confirmed at clause 5.15.1, while the requested clause 5.9 mapping remains `[Needs Verification]`.
