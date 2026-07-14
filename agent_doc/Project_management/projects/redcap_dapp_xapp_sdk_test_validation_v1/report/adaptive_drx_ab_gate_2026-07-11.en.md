# Adaptive C-DRX A/B Gate Report

## Gate Summary

- [Runtime completion date]: 2026-07-14.
- [Scope]: one RedCap UE in `RRC_CONNECTED`, with separate downlink and uplink Arm A/B campaigns.
- [Overall Result]: **PASS** for the frozen RFsim runtime A/B validation.
- [Source Readiness]: E2-enabled gNB/UE, local gNB/UE control modules, Python xApp import, collectors, checker, and focused tests pass.
- [Runtime Smoke]: rebuilt images passed one-UE attach/PDU/TUN/ping, E2 Setup, fixed Arm A apply/RRC completion, UE Active-Time export, and one fixed-byte burst in each direction.
- [Runtime Evidence]: all four campaigns passed independent correlation with `300/300` scored arrivals each and `1200/1200` overall.
- [Claim Boundary]: latency, delivery, goodput, HARQ, and Active-Time/PDCCH ratios are RFsim behavior evidence. No physical-power or battery-life result is claimed.

## Frozen Manifest

The reviewed experiment contract is frozen in:

- `openspec/changes/adaptive-drx-ab-validation/review/experiment_manifest_v1.yaml`
- `openspec/changes/adaptive-drx-ab-validation/review/drx_policy_contract_v1.yaml`

| Campaign | Arm | Direction | Control mode | Planned arrivals | Warm-up | Planned scored | Evidenced scored | Status |
|---|---|---|---|---:|---:|---:|---:|---|
| `arm-a-dl` | A | Downlink | Fixed `drx-320-10`, applied once | 330 | 30 | 300 | 300 | PASS |
| `arm-b-dl` | B | Downlink | Adaptive E2SM-RC Style 2 / Action 1 | 330 | 30 | 300 | 300 | PASS |
| `arm-a-ul` | A | Uplink | Fixed `drx-320-10`, applied once | 330 | 30 | 300 | 300 | PASS |
| `arm-b-ul` | B | Uplink | Adaptive E2SM-RC Style 2 / Action 1 | 330 | 30 | 300 | 300 | PASS |
| **Total** | | | | **1320** | **120** | **1200** | **1200** | **PASS** |

The deterministic trace seed is `41`. Evidence directories are:

- `test_log/runtime_logs/adaptive_drx_2026-07-13_full_ab/arm-a-dl-run2`
- `test_log/runtime_logs/adaptive_drx_2026-07-13_full_ab/arm-b-dl-run7`
- `test_log/runtime_logs/adaptive_drx_2026-07-13_full_ab/arm-a-ul-run1`
- `test_log/runtime_logs/adaptive_drx_2026-07-13_full_ab/arm-b-ul-run1`

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
| E2-enabled gNB/UE plus `telnetsrv_ci`/`ciUE` build | PASS | `test_log/build_logs/build_e2_agent_telnet_gnb_ue_2026-07-11_16-02-bootstrap-metrics.log` |
| FlexRIC SWIG 4.1.1 Python bridge build/import | PASS | `test_log/build_logs/build_xapp_sdk_2026-07-11_15-13-45_swig411.log`; `test_log/compiler_logs/xapp_sdk_import_2026-07-11_15-13-45_swig411.log` |
| Adaptive and evidence Python tests | PASS, 16/16 and 3/3 | `test_log/compiler_logs/adaptive_drx_python_tests_2026-07-14.log`; `test_log/compiler_logs/adaptive_drx_evidence_tests_2026-07-14.log` |
| Current focused C-DRX rebuild/CTest | PASS, gNB 8/8, UE 9/9, RC 3/3 | `test_log/compiler_logs/adaptive_drx_focused_ctest_2026-07-11_20-05-02.log`; detailed suite logs with the same timestamp |
| E2-enabled RFsim image rebuild | PASS | `test_log/build_logs/rebuild_local_oai_images_2026-07-11_20-05-02_adaptive-drx.log` |
| UE image receiver-capture dependency | PASS, `tcpdump` added | `test_log/build_logs/rebuild_oai_nr_ue_tcpdump_2026-07-11_20-05-02.log` |

These checks prove source-level behavior and buildability only. The Python tests create synthetic evidence in temporary directories; they are not RFsim campaign results.

## Runtime Smoke Evidence

| Check | Result | Evidence |
|---|---|---|
| UE1 attach/PDU/TUN/ping; gNB restart | PASS `1/1/1/1`; restart `0` | `test_log/compiler_logs/adaptive_drx_rfsim_prereq_2026-07-11_20-05-02.log` |
| E2 Setup request/response | PASS | `test_log/compiler_logs/mmtc_smoke_2026-07-11_20-14-07_gnb.log` |
| Arm A `drx-320-10` policy version 1 | PASS staged/applied/RRC complete | `test_log/compiler_logs/adaptive_drx_live_arm_a_apply_2026-07-11_20-05-02.log` |
| UE Active-Time export | PASS; live counter returned valid `active_slots <= observed_slots` | `ciUE drx_stats` runtime query |
| Fixed-byte UL burst bound to `10.0.0.2` | PASS; receiver report, `0/29` loss | `test_log/compiler_logs/adaptive_drx_live_ul_burst_2026-07-11_20-05-02_bind-fix.log` |
| Fixed-byte DL reverse burst bound to `10.0.0.2` | PASS; receiver report, `1/29` loss | `test_log/compiler_logs/adaptive_drx_live_dl_burst_2026-07-11_20-05-02_bind-fix.log` |

The smoke exposed and fixed a route-integrity issue: runtime execution now
requires `--bind-address`, mapped to iPerf2 `-B`, so traffic cannot bypass the
UE PDU-session route through container `eth0`.

## Runtime Metrics

Each value below is emitted by the independent checker from 300 scored arrivals.

| Metric | Arm A DL | Arm B DL | Arm A UL | Arm B UL |
|---|---:|---:|---:|---:|
| `delivery_success_count` | 300 | 300 | 300 | 300 |
| `policy_versions` | 1 | 10 | 1 | 10 |
| `scheduled_to_first_receive_median_ms` | 59.0125 | 58.891 | 5.2345 | 5.217 |
| `scheduled_to_first_receive_p95_ms` | 67.991 | 71.028 | 5.768 | 5.853 |
| `scheduled_to_first_receive_max_ms` | 75.193 | 3642.133 | 407.981 | 3206.300 |
| `drx_active_slots / drx_observed_slots` | 1092797 / 14383008 | 419910 / 14292512 | 1124628 / 14247199 | 499363 / 14395015 |
| `drx_active_time_slot_ratio` | 0.075978 | 0.029380 | 0.078937 | 0.034690 |
| `pdcch_monitoring_slot_ratio` | 0.075978 | 0.029380 | 0.078937 | 0.034690 |
| `burst_goodput_mean_mbps` | 10.229333 | 10.232600 | 9.749533 | 9.740133 |
| `udp_jitter_mean_ms` | 0.050337 | 0.048847 | 0.193457 | 0.197967 |
| `udp_loss_mean_percent` | 3.4 | 3.4 | 0.0 | 0.0 |
| `DL / UL HARQ retransmission count` | 0 / 0 | 0 / 0 | 0 / 0 | 2 / 3 |
| `policy_apply_latency_median / p95 / max_ms` | 5.025 / 5.025 / 5.025 | 38.470 / 184.165 / 184.165 | 4.338 / 4.338 / 4.338 | 2.259 / 3.871 / 3.871 |
| `policy_reject / rollback / timeout count` | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| `rrc_reconfiguration_count` | 1 | 10 | 1 | 10 |

Arm B reduced the observed Active-Time ratio in both directions. Its maximum
scheduled-to-first-receive latency increased because RRC policy application at
30-arrival boundaries delayed some bursts; this is part of the measured result,
not discarded as an outlier.

## Instrumentation Readiness

`scripts/adaptive_drx/run_campaign.py` currently writes these metrics columns:

```text
campaign_id,arrival_id,scheduled_source_tx_time_us,delivery_success,
policy_version,profile_id,client_launch_time_us,iperf_returncode,
burst_goodput_mbps,udp_jitter_ms,udp_lost_packets,udp_total_packets,udp_loss_percent
```

`check_campaign.py` validates traffic metrics, receiver CSV, UE Active-Time summary, staged-to-RRC latency, RNTI-specific HARQ deltas, versions, profiles, and markers. `adaptive_drx.py receive-csv` converts a filtered tcpdump log; the four measured results above use this path.

## E2 And SWIG Boundary

- The system SWIG is 4.0.2, while the repository SWIG 4.1.1 successfully builds `xapp_sdk` for Python 3.12.
- The isolated `/tmp/oai-e2-agent-build` cache records `E2_AGENT=ON`; both softmodems and both telnet modules build.
- Live Python xApp discovery returned `nodes 1`. Both Arm B campaigns completed ten E2 CONTROL requests with correlated request, ACK, dApp ACCEPT, gNB apply, and RRC-complete markers.

## RFsim And Physical-Power Boundary

RFsim does not measure UE receiver current, watts, joules, or battery life. The reported `pdcch_monitoring_slot_ratio` and `drx_active_time_slot_ratio` are energy-related behavior proxies only. This report makes no physical-power or battery-life claim.

## Educational Test Note

### 1. Technical Background

C-DRX limits when an `RRC_CONNECTED` UE must monitor PDCCH. The network
configures legal timer/cycle values, while UE MAC executes Active Time from the
configured timers and runtime events. The gNB scheduler must use the matching
profile so it does not schedule ordinary new data while the UE is outside
Active Time. This experiment compares a fixed profile with a 30-arrival adaptive
policy, but RFsim counters remain behavior proxies rather than power readings.

### 2. Key C Functions And Data Structures

- `nr_mac_apply_drx_policy()` and `nr_gnb_drx_state_t`: staged gNB policy, apply, rollback, and version state.
- `nr_ue_drx_is_active()` and `nr_ue_drx_slot_counts_t`: UE Active-Time decision and atomic counters.
- `redcap_dapp_guard_e2_drx_cycle()`: narrow legal/state guard for the live E2 cycle request.

### 3. Test Results Summary

| Test item | Status | Code coverage | Modification log |
|---|---|---|---|
| gNB C-DRX state/guard | PASS 8/8 | N/A, not instrumented | `test_nr_gnb_drx_2026-07-11_20-05-02.log` |
| UE C-DRX Active Time | PASS 9/9 | N/A, not instrumented | `test_nr_ue_drx_2026-07-11_20-05-02.log` |
| RC request contract | PASS 3/3 | N/A, not instrumented | `test_nr_redcap_rc_ctrl_2026-07-11_20-05-02.log` |
| Four one-UE RFsim campaigns | PASS, 1200/1200 scored | N/A, runtime proxy | `test_log/runtime_logs/adaptive_drx_2026-07-13_full_ab/` |

### 4. 3GPP Specification Mapping

- [TS 38.321 §5.7]: MAC DRX operation defines Active Time from On Duration,
  inactivity, HARQ, SR, and related events.
- [TS 38.331 §6.3.2]: `DRX-Config` carries the RRC-configured timer, cycle,
  and offset fields. Exact release-specific ASN.1 field applicability remains
  `[Needs Verification]` against the frozen local release text.

### 5. Practice Exercises

1. [Basic]: Explain why On Duration controls UE PDCCH monitoring, not gNB sleep.
2. [Applied]: Trace policy version 1 from telnet request to the RRC-complete marker.
3. [Advanced]: Design a failure test proving a rejected Arm B window is retained and rollback state is unchanged.

## Gate Closure

- All four campaigns preserve 330 arrivals and 300 scored receiver records.
- Arm B preserves ten 30-arrival policy windows per direction.
- All required traffic, UE counter, HARQ, E2/dApp/gNB, UE configuration, and RRC completion evidence passed correlation.
- OpenSpec task 2.12 is complete; the adaptive C-DRX runtime Gate is closed for the stated RFsim scope.
