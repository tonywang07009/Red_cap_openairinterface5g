# BWP Runtime Evidence 20260628_151500

## Run Metadata

- [Run ID]: `20260628_151500_bwp_matrix_recreate`
- [Wrapper]: `agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/scripts/run_bwp_matrix.sh`
- [Runtime mode]: low/high x 8/80 ms x 1/3 ms matrix, force-recreate per scenario
- [Trigger sequence]: `BWP_TRIGGER_SEQUENCE=1 0`
- [Force recreate]: `REDCAP_COMPOSE_FORCE_RECREATE=1`
- [Runtime CSV count]: 8
- [Merged CSV]: `agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/exp_result/BWP_results.csv`
- [Debug backtrace run]: `20260628_154000_bwp_trigger0_bt`

## Matrix Summary

| scenario | active_ue | reconfig_count | default_bwp_ratio | throughput_mbps | segv |
|---|---:|---:|---:|---:|---:|
| `high_load_bwp_80ms_1ms` | 1 | 1 | 0.000000 | 0.015315 | 1 |
| `high_load_bwp_80ms_3ms` | 1 | 1 | 0.000000 | 0.015363 | 1 |
| `high_load_bwp_8ms_1ms` | 1 | 1 | 0.000000 | 0.015336 | 1 |
| `high_load_bwp_8ms_3ms` | 1 | 1 | 0.000000 | 0.015341 | 1 |
| `low_load_bwp_80ms_1ms` | 1 | 1 | 0.000000 | 0.015173 | 1 |
| `low_load_bwp_80ms_3ms` | 1 | 1 | 0.000000 | 0.015212 | 1 |
| `low_load_bwp_8ms_1ms` | 1 | 1 | 0.000000 | 0.015415 | 1 |
| `low_load_bwp_8ms_3ms` | 1 | 1 | 0.000000 | 0.015225 | 1 |

## Crash Evidence

- [Crash trigger]: `ci trigger_bwp_switch 0`
- [Crash marker]: `[CGDBG][SIG] caught fatal signal 11 (Segmentation fault)`
- [Crash frame]: `update_cellGroupConfig_for_BWP_switch+0x151`
- [Caller path]: `nr_mac_trigger_reconfiguration` -> `nr_trigger_bwp_switch` -> `trigger_bwp_switch`
- [Source path]: `openair2/LAYER2/NR_MAC_gNB/nr_radio_config.c:4106`
- [Backtrace log]: `test_log/redcap_bwp_sdt_validation/20260628_154000_bwp_trigger0_bt_bwp/container_logs/full/gnb.log`

## Interpretation

- [BWP Gate 5 runtime matrix]: executed 8/8 scenario rows with independent Docker logs.
- [Gate result]: [BLOCKED], not PASS, because every BWP 0 trigger crashed the gNB after the reconfiguration marker.
- [CSV hygiene]: `merge_runtime_metrics.py --replace-scenario` now resets stale local values for metrics absent from a newer runtime CSV.
- [Metric limitation]: `pdu_scheduling_delay_ms` and `bwp_switch_apply_delay_ms` were not produced by the 2026-06-28 matrix due the crash.
- [Scenario limitation]: `MMTC_BWP_TRAFFIC_PROFILE`, `MMTC_BWP_INACTIVITY_TIMER_MS`, and `MMTC_BWP_SWITCH_DELAY_MS` are runner/manifest labels; targeted source scan found no OAI C or compose hook that changes traffic load, timer behavior, or switch-delay behavior.

## Next Action

- Debug `update_cellGroupConfig_for_BWP_switch()` for BWP 1 -> BWP 0 reconfiguration.
- After the crash is fixed, rerun `20260628_151500_bwp_matrix_recreate` equivalent matrix before claiming BWP Gate 5 PASS.
