# BWP Runtime Evidence 20260630_100615

## Run Metadata

- [Run ID]: `20260630_100615_bwp_matrix_apply_marker`
- [Wrapper]: `agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/scripts/run_bwp_matrix.sh`
- [Runtime mode]: low/high x 8/80 ms x 1/3 ms matrix, force-recreate per scenario
- [Trigger sequence]: `BWP_TRIGGER_SEQUENCE=1 0`
- [Force recreate]: `REDCAP_COMPOSE_FORCE_RECREATE=1`
- [Runtime CSV count]: 8
- [Runner result]: `runs=8 runner_failures=0`
- [Merged CSV]: `agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/exp_result/BWP_results.csv`

## Matrix Summary

| scenario | default_bwp_ratio_percent | power_saving_percent | pdu_scheduling_delay_ms | bwp_switch_apply_delay_ms | throughput_mbps | reconfig_count | last_apply_dl_bwp |
|---|---:|---:|---:|---:|---:|---:|---:|
| `low_load_bwp_8ms_1ms` | 10.811418 | 5.609698 | 4.270000 | 1.350000 | 0.016267 | 1 | 0 |
| `low_load_bwp_8ms_3ms` | 10.741547 | 5.573444 | 3.679000 | 1.022000 | 0.016030 | 1 | 0 |
| `low_load_bwp_80ms_1ms` | 10.687102 | 5.545194 | 4.000000 | 1.102000 | 0.016448 | 1 | 0 |
| `low_load_bwp_80ms_3ms` | 10.644483 | 5.523081 | 4.676000 | 1.128000 | 0.015596 | 1 | 0 |
| `high_load_bwp_8ms_1ms` | 10.724843 | 5.564777 | 4.243000 | 1.243000 | 0.016233 | 1 | 0 |
| `high_load_bwp_8ms_3ms` | 10.774346 | 5.590463 | 3.858000 | 1.172000 | 0.016394 | 1 | 0 |
| `high_load_bwp_80ms_1ms` | 10.658819 | 5.530519 | 4.179000 | 1.114000 | 0.016486 | 1 | 0 |
| `high_load_bwp_80ms_3ms` | 10.776664 | 5.591665 | 3.797000 | 1.181000 | 0.016631 | 1 | 0 |

## Runtime Proof

- [Crash scan]: no `Segmentation fault`, `core dumped`, `AddressSanitizer`, or `AssertFatal` markers were found in the eight post-fix gNB logs.
- [Single trigger proof]: `20260630_100054_bwp_trigger0_apply_marker` completed with `bwp_gnb_reconfiguration_last_new_bwp_id = 0` and `bwp_gnb_apply_last_new_dl_bwp_id = 0`.
- [Bidirectional proof]: `20260630_100329_bwp_bidirectional_apply_marker` completed `0 1 0` with three reconfiguration markers and final apply back to BWP 0.
- [Matrix proof]: each matrix row has one BWP reconfiguration marker and final `bwp_gnb_apply_last_new_dl_bwp_id = 0`.

## Interpretation

- [Crash blocker]: fixed for the tested RFsim BWP 1 -> 0 and `0 1 0` trigger paths.
- [Gate 5 runtime status]: post-fix RFsim matrix evidence is now available and numeric BWP residency, estimated power saving, switch apply delay, PDU scheduling delay, and throughput rows are merged.
- [Paper-comparability limitation]: `MMTC_BWP_TRAFFIC_PROFILE`, `MMTC_BWP_INACTIVITY_TIMER_MS`, and `MMTC_BWP_SWITCH_DELAY_MS` remain runner/manifest labels. The UE `bwp-InactivityTimer` source gap is still present, so these values are local marker-derived RFsim evidence, not publication-grade paper reproduction.

## Validation Commands

| command | result |
|---|---|
| `rtk python agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/scripts/test_extract_bwp_metrics.py` | [PASS] |
| `rtk python agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/scripts/audit_oai_hooks.py` | [PASS] |
| `rtk bash -lc 'CCACHE_DIR=/tmp/oai-ccache CCACHE_TEMPDIR=/tmp/oai-ccache-tmp cmake --build --preset default --target nr-softmodem ...'` | [PASS] |
| `rtk bash redcap_interface/redcap_rebuild_local_oai_images.sh` | [PASS] |
| `rtk bash agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/scripts/run_bwp_matrix.sh --run` | [PASS], `runs=8 runner_failures=0` |
| `rtk python agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/exp_pictture/plot_paper_vs_local.py` | [PASS] |

## Next Action

- Keep BWP Gate 5 conclusion as [runtime fixed / paper-limited] until real traffic, `bwp-InactivityTimer`, and switch-delay behavior hooks are implemented or otherwise verified.
- Use `BWP_results.csv` and `exp_pictture/BWP_paper_vs_local.png` as the refreshed local evidence artifacts for the current project report.
