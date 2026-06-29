# SDT Runtime Evidence 20260626_230300

## Run Metadata

- [Run ID]: `20260626_230300_sdt_local`
- [Wrapper]: `agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/scripts/run_sdt_validation.sh`
- [Runtime Layer]: historical paper-project wrapper run; standalone wrapper defaults to `redcap_interface/mmtc.menu.bash gate3`, while matrix rows delegate through `smoke` to preserve scenario-specific gate flags.
- [Baseline Project]: `agent_doc/Project_management/projects/redcap_rrc_inactive_sdt_oran_control_v1/` [Case A Gate 3]
- [Images]: `oai-gnb:latest`, `oai-nr-ue:latest`, `oai-flexric:custom-dev`
- [Log Bundle]: `test_log/redcap_bwp_sdt_validation/20260626_230300_sdt_local_sdt/container_logs/full/`
- [Runtime CSV]: `test_log/redcap_bwp_sdt_validation/20260626_230300_sdt_local_sdt/sdt_runtime_metrics.csv`
- [Merged CSV]: `agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/exp_result/SDT_results.csv`

## Key Metrics

| metric | local_value |
|---|---:|
| `active_ue_count` | 1 |
| `ue_in_sync_seen` | 1 |
| `rrc_inactive_marker_seen` | 1 |
| `rrc_resume_request_seen` | 0 |
| `rrc_resume_complete_seen` | 0 |
| `configured_grant_marker_seen` | 1 |
| `cg_sdt_marker_seen` | 1 |
| `cg_sdt_rx_candidate_count` | 313 |
| `packet_attempt_count` | 1 |
| `packet_success_count` | 1 |
| `threshold_fallback_count` | 0 |
| `timeout_failure_count` | 0 |
| `sdt_failure_count` | 0 |
| `packet_transmission_success_probability` | 1.000000 |
| `dlsch_errors` | 0 |
| `ulsch_errors` | 0 |
| `dlsch_retx_ratio_percent` | 0.000000 |
| `ulsch_retx_ratio_percent` | 0.000000 |

## Interpretation

- [SDT local runtime gap closed]: the run produced local SDT markers, success/fallback/timeout counters, and merged them into `SDT_results.csv`.
- [Aggregation evidence]: `agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/exp_result/SDT_repeated_run_aggregate.csv` records the current `1/1` local minimal success aggregate.
- [Layering note]: the accepted protocol baseline is the existing `redcap_rrc_inactive_sdt_oran_control_v1` Gate 3 flow; `RedCap_BWP_SDT_validation` owns paper-facing metric extraction and reporting.
- [Remaining boundary]: this is a single-UE RFsim marker run, not the paper's stochastic multi-device success-probability curve.
- [Resume boundary]: `RRCResumeRequest` and `RRCResumeComplete` were not observed in this run, so resume-path success probability remains `[TBD]`.
- [3GPP mapping]: SDT interpretation remains mapped to TS 38.523-1 clause 7.1.1.13 and TS 38.300 clause 18 with `[Needs Verification]` for exact conformance language.
