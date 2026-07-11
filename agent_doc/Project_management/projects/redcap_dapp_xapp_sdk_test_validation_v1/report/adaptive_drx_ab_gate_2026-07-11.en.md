# Adaptive C-DRX A/B Gate Report

## Gate Summary

- [Date]: 2026-07-11.
- [Scope]: one RedCap UE in `RRC_CONNECTED`, with separate downlink and uplink Arm A/B campaigns.
- [Overall Result]: **BLOCKED** for runtime A/B validation.
- [Source Readiness]: gNB, UE, local control module, and focused tests pass.
- [Runtime Boundary]: no adaptive-DRX RFsim campaign artifact is available. The evidenced scored population is `0/300` for each campaign and `0/1200` overall.
- [Claim Boundary]: no latency, throughput, retransmission, monitoring-time, energy-proxy, or physical-power result is claimed.

## Frozen Manifest

The reviewed experiment contract is frozen in:

- `openspec/changes/adaptive-drx-ab-validation/review/experiment_manifest_v1.yaml`
- `openspec/changes/adaptive-drx-ab-validation/review/drx_policy_contract_v1.yaml`

| Campaign | Arm | Direction | Control mode | Planned arrivals | Warm-up | Planned scored | Evidenced scored | Status |
|---|---|---|---|---:|---:|---:|---:|---|
| `arm-a-dl` | A | Downlink | Seeded local RRC profile | 330 | 30 | 300 | 0 | BLOCKED / not run |
| `arm-b-dl` | B | Downlink | Adaptive E2SM-RC Style 2 / Action 1 | 330 | 30 | 300 | 0 | BLOCKED / not run |
| `arm-a-ul` | A | Uplink | Seeded local RRC profile | 330 | 30 | 300 | 0 | BLOCKED / not run |
| `arm-b-ul` | B | Uplink | Adaptive E2SM-RC Style 2 / Action 1 | 330 | 30 | 300 | 0 | BLOCKED / not run |
| **Total** | | | | **1320** | **120** | **1200** | **0** | **BLOCKED** |

The trace seed and Arm A profile seed remain `required_at_run`. No generated `adaptive_drx_campaign_manifest_v1.json`, trace CSV, command-plan JSONL, metrics CSV, or correlated runtime log is present in the worktree.

## Build And Test Evidence

| Surface | Result | Evidence |
|---|---|---|
| Full gNB build, including gNB scheduler, DRX state, RRC handler, and C dApp SDK | PASS | `test_log/build_logs/build_nr-softmodem_2026-07-11_00-31-09_adaptive-drx.log` |
| Final gNB incremental link | PASS | `test_log/build_logs/build_nr-softmodem_2026-07-11_00-50-00_adaptive-drx.log` |
| UE build, including `config_ue.c`, `nr_ue_drx.c`, `nr_ue_procedures.c`, and `nr_ue_scheduler.c` | PASS | `test_log/build_logs/build_nr-uesoftmodem_2026-07-11_00-53-00_adaptive-drx.log` |
| Local CI/telnet DRX control module | PASS | `test_log/build_logs/build_telnetsrv_ci_2026-07-11_01-03-00_adaptive-drx.log` |
| Focused UE DRX, RC helper, and gNB DRX CTest targets | PASS, 3/3 | `test_log/compiler_logs/ctest_adaptive_drx_final_2026-07-11_01-04-00.log` |
| Deterministic trace, predictor, window, and checker tests | PASS, 4/4 | `test_log/compiler_logs/test_adaptive_drx_python_2026-07-11_00-57-00.log` |
| C dApp guard self-check | PASS | `test_log/compiler_logs/test_redcap_dapp_drx_2026-07-11_00-58-00.log` |
| C xApp RC request-builder self-check | PASS | `test_log/compiler_logs/test_redcap_xapp_drx_2026-07-11_00-59-00.log` |
| SDK static validation | PASS, SWIG module reported as `definition-only` | `test_log/compiler_logs/check_dapp_xapp_sdk_2026-07-11_01-05-00.log` |
| SDK contract self-test | PASS | `test_log/compiler_logs/dapp_xapp_contract_2026-07-11_01-05-00.log` |

These checks prove source-level behavior and buildability only. The Python tests create synthetic evidence in temporary directories; they are not RFsim campaign results.

## Runtime Metrics

All frozen metrics are unavailable because there are no observed scored rows or adaptive-DRX runtime logs.

| Metric | Arm A DL | Arm B DL | Arm A UL | Arm B UL | Evidence status |
|---|---|---|---|---|---|
| `scored_delivery_success_count` | N/A | N/A | N/A | N/A | No campaign run |
| `scheduled_to_first_receive_latency_ms` | N/A | N/A | N/A | N/A | Receive timestamp is not captured in the current metrics CSV |
| `latency_median_ms` | N/A | N/A | N/A | N/A | No scored latency population |
| `latency_p95_ms` | N/A | N/A | N/A | N/A | No scored latency population |
| `latency_max_ms` | N/A | N/A | N/A | N/A | No scored latency population |
| `pdcch_monitoring_slot_ratio` | N/A | N/A | N/A | N/A | No monitoring-slot counter/export |
| `drx_active_time_slot_ratio` | N/A | N/A | N/A | N/A | No Active-Time counter/export |
| `burst_goodput_mbps` | N/A | N/A | N/A | N/A | Raw iPerf output is not parsed into the metrics CSV |
| `udp_loss_percent` | N/A | N/A | N/A | N/A | Raw iPerf output is not parsed into the metrics CSV |
| `udp_jitter_ms` | N/A | N/A | N/A | N/A | Raw iPerf output is not parsed into the metrics CSV |
| `dl_harq_retransmission_count` | N/A | N/A | N/A | N/A | No campaign HARQ counter/export |
| `ul_harq_retransmission_count` | N/A | N/A | N/A | N/A | No campaign HARQ counter/export |
| `policy_apply_latency_ms` | N/A | N/A | N/A | N/A | No correlated request-to-completion timestamps |
| `policy_reject_count` | N/A | N/A | N/A | N/A | No runtime decisions |
| `rollback_count` | N/A | N/A | N/A | N/A | No runtime decisions |
| `rrc_reconfiguration_count` | N/A | N/A | N/A | N/A | No runtime marker population |
| `rrc_reconfiguration_timeout_count` | N/A | N/A | N/A | N/A | No runtime marker population |

`N/A` means not measured. It must not be interpreted as zero events or successful delivery.

## Instrumentation Gap

`scripts/adaptive_drx/run_campaign.py` currently writes these metrics columns:

```text
campaign_id,arrival_id,scheduled_source_tx_time_us,delivery_success,
policy_version,profile_id,client_launch_time_us,iperf_returncode
```

`scripts/adaptive_drx/check_campaign.py` can validate 300 unique scored rows, ten policy versions with 30 arrivals each, trace timestamps, approved profiles, delivery status, and required runtime markers. It does not derive the latency, goodput, loss, jitter, HARQ, monitoring-slot, or Active-Time metrics required by the frozen manifest. Raw iPerf stdout/stderr is retained in the command-plan JSONL, but it still requires parsing; MAC monitoring and HARQ proxies require explicit counters or log exports.

## E2 And SWIG Boundary

- The host has SWIG `4.0.2`; FlexRIC requires SWIG `4.1` or newer in `openair2/E2AP/flexric/src/xApp/swig/CMakeLists.txt`.
- `cmake_targets/ran_build/build/CMakeCache.txt` and `cmake_targets/ran_build/build_test/CMakeCache.txt` both record `E2_AGENT=OFF`.
- Therefore, the passing softmodem builds do not prove compilation or runtime execution of the main `ran_func_rc.c` E2 path.
- The static SDK check explicitly reports the generated SWIG module as `definition-only`; no Python `xapp_sdk` import or live E2 control request has been demonstrated for this Gate.

## RFsim And Physical-Power Boundary

RFsim does not measure UE receiver current, watts, joules, or battery life. A completed RFsim campaign may report `pdcch_monitoring_slot_ratio` and `drx_active_time_slot_ratio` only as energy-related behavior proxies, alongside latency, delivery, goodput, loss, and retransmission results. No such proxy result exists in this evidence set, so this report makes neither an energy-saving claim nor a physical-power claim.

## Next Evidence Gate

The runtime Gate can change from BLOCKED only after all of the following evidence is saved:

1. Build the FlexRIC Python binding with SWIG `>= 4.1` and compile the gNB with `E2_AGENT=ON`.
2. Generate and retain the seeded JSON manifest plus paired DL/UL trace CSV files.
3. Add the missing result parsers and MAC/HARQ/monitoring counters required by the frozen metric list.
4. Run all four campaigns against a live gNB, UE, E2 connection, persistent iPerf2 server, and combined runtime log.
5. Retain exactly 330 arrivals per campaign, with arrivals 31 through 330 forming 300 correlated scored rows.
6. Correlate request, E2 acknowledgement, dApp decision, gNB apply, UE configuration, and RRC completion markers by policy version.
7. Run `check_campaign.py` for each campaign and require four PASS results before calculating or comparing Arm A/B statistics.

Until this evidence exists, OpenSpec task 2.11 and the adaptive C-DRX runtime Gate remain incomplete.
