# BWP Runtime Evidence 20260626_231100

## Run Metadata

- [Run ID]: `20260626_231100_bwp_local_ci`
- [Wrapper]: `agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/scripts/run_bwp_validation.sh`
- [Runtime Helper]: `agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/scripts/redcap_runtime_common.sh`
- [Images]: `oai-gnb:latest`, `oai-nr-ue:latest`, `oai-flexric:custom-dev`
- [Log Bundle]: `test_log/redcap_bwp_sdt_validation/20260626_231100_bwp_local_ci_bwp/container_logs/full/`
- [Runtime CSV]: `test_log/redcap_bwp_sdt_validation/20260626_231100_bwp_local_ci_bwp/bwp_runtime_metrics.csv`
- [Merged CSV]: `agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/exp_result/BWP_results.csv`

## Key Metrics

| metric | local_value |
|---|---:|
| `active_ue_count` | 1 |
| `ue_in_sync_seen` | 1 |
| `dlsch_errors` | 0 |
| `ulsch_errors` | 0 |
| `bwp_gnb_reconfiguration_count` | 1 |
| `bwp_gnb_reconfiguration_last_new_bwp_id` | 0 |
| `bwp_gnb_interrupt_count` | 0 |
| `bwp_ue_ra_operation_count` | 2 |
| `bwp_ue_ra_bwp_change_count` | 0 |
| `bwp_inactivity_timer_gap_seen` | 1 |
| `default_bwp_size_prb` | 51 |
| `dedicated_bwp_size_prb` | 106 |
| `default_bwp_residency_ms` | 7089.643000 |
| `dedicated_bwp_residency_ms` | 59328.765000 |
| `default_bwp_ratio_percent` | 10.674214 |
| `bwp_switch_apply_delay_ms` | 1.445000 |
| `pdu_scheduling_delay_ms` | 4.249000 |
| `power_saving_percent` | 5.538507 |
| `gnb_mac_total_throughput_mbps` | 0.013830 |

## Trigger Evidence

- [Trigger sequence]: `1 0`
- [BWP 1 trigger]: failed because the UE was already on BWP 1.
- [BWP 0 trigger]: succeeded.
- [gNB evidence]:
  - `triggered BWP switch to BWP ID 0 for UE 9fbf`
  - `[RedCap BWP][gNB reconfiguration] RNTI 9fbf old_bwp_id 1 new_bwp_id 0 local_bwp_id 1`
  - `Switching to DL-BWP 0`
  - `Switching to UL-BWP 0`

## Interpretation

- [BWP local runtime gap closed]: the local run now produces real BWP reconfiguration and UE RA BWP markers from rebuilt local images, plus marker-derived residency/delay estimates.
- [Estimator boundary]: `power_saving_percent` uses `default_ratio_x_prb_delta`; `pdu_scheduling_delay_ms` is measured from gNB reconfiguration marker to first post-switch scheduled SDU.
- [Layering note]: BWP remains a paper-specific runtime extension because the existing SDT Gate 3 project does not own BWP telnet trigger or BWP residency metrics.
- [Remaining boundary]: this is still not a full paper-comparable delay/power curve because `bwp-InactivityTimer` remains not implemented and no high/low throughput/power sweep has been run.
- [3GPP mapping]: BWP operation remains mapped to TS 38.321 clause 5.15.1; the requested TS 38.321 clause 5.9 mapping remains `[Needs Verification]`.
