# PAPER-08 / PAPER-10 Extended Validation Matrix

## Scope
- [Paper Anchor 1]: `paper_Empirical_Comparison_of_Power_Consumption_and_Data_Rates_for_5G_New_Radio_and_RedCap_Devices.pdf`.
- [Paper Anchor 2]: `paper_Performance Analysis and Comparison of.pdf`.
- [Purpose]: extend the original RFsim validation matrix with modeled UE uplink power, UL/DL balance, latency, host-resource pressure, and multi-UE stability tests.
- [Guardrail]: PAPER-08 power is a [model estimate], not direct RF power-meter evidence.
- [Guardrail]: PAPER-10 coverage/position tests are [Not Directly Comparable] until RFsim exposes a controlled channel/path-loss axis for this scenario.

## PAPER-08 Power Model
- [Formula Source]: PAPER-08 Section V-A, Equation (1), Table II.
- [Implementation]: `analysis/scripts/p08_uplink_power_calculator.py`.
- [Generated Sweep]: `analysis/data/paper08_power_sweep_text_layer_coefficients_2026-05-26.csv`.
- [Runtime Merge Row]: `analysis/data/paper08_runtime_power_merge_2026-05-26.csv`.
- [Equation]:

```text
if PTx >= PTx_max:
  PUE = Pmax
elif PTx >= gamma1:
  PUE = alpha2 + beta2 * PTx
else:
  PUE = alpha1 + beta1 * PTx
```

- [Default PTx_max]: `23 dBm`.
- [Reason]: FR1 RedCap PC3 maximum transmit power is commonly `23 dBm`; local spec map references TS 38.101-1 Section 6.2.1I [Needs Verification].
- [Unit]: `PTx` is in `dBm`; `PUE` is in `W`.

| Band | alpha1 | beta1 | gamma1 dBm | alpha2 | beta2 | Pmax W |
|---|---:|---:|---:|---:|---:|---:|
| n41 | 0.30 | 1.5e-4 | 4 | 0.19 | 2.1e-2 | 0.69 |
| n78 | 0.35 | 1.1e-4 | 5 | 0.46 | 3.6e-3 | 1.45 |

## Calculator Interfaces
- [CLI Sweep]:

```bash
python3 agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/analysis/scripts/p08_uplink_power_calculator.py \
  --band n78 \
  --ptx-dbm -10 0 5 10 20 23 \
  --tx-seconds-per-period 300 \
  --period-seconds 3600 \
  --json
```

- [Self-Test]:

```bash
python3 agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/analysis/scripts/p08_uplink_power_calculator.py --self-test
```

- [JSON Socket Server]:

```bash
python3 agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/analysis/scripts/p08_uplink_power_calculator.py \
  --listen 127.0.0.1:8765
```

- [JSON Socket Request]:

```json
{"band":"n78","ptx_dbm":10,"tx_seconds_per_period":300,"period_seconds":3600}
```

## Extended Test Rows
| Test ID | Paper Basis | Controlled Factors | Required Metrics | Pass / Status Gate |
|---|---|---|---|---|
| PERF-P08-PWR-001 | PAPER-08 Eq. (1), Table II | band, PTx dBm | `pue_w`, segment, duty-cycle average | calculator self-test passes |
| PERF-P08-PWR-002 | PAPER-08 external calculator concept | JSON socket request | same as CLI response | valid JSON response and error handling |
| PERF-P08-PWR-003 | PAPER-08 uplink-centered application | UL offered rate, band, PTx dBm, duty cycle | UL Mbps, UDP loss, modeled UL power | RFsim hard pass plus model row joined |
| PERF-P10-THR-001 | PAPER-10 data rate method | single UE, UL/DL iperf, duration 180s | UL/DL Mbps, DL/UL ratio | hard pass and parsed UL/DL logs |
| PERF-P10-THR-002 | PAPER-10 multi-UE cases | 2-3 UEs, UL/DL iperf | per-UE Mbps, fairness, restart count | no gNB restart, no unclassified failures |
| PERF-P10-LAT-001 | PAPER-10 ping latency method | single UE, 180s ping window | RTT min/avg/max, ping loss | ping loss 0%, RTT parsed |
| PERF-P10-POS-001 | PAPER-10 Good/Fair/Bad positions | channel or MCS/SNR proxy | throughput drop ratio, MCS/SNR | [BLOCKED] until controlled RFsim channel axis is documented |
| PERF-P10-HOST-001 | PAPER-10 host sensitivity | same test on different host/resource budget | Mbps, RTT, CPU, memory | relative degradation classified |
| PERF-P10-STAB-001 | PAPER-10 multi-UE UL crash risk | 2-3 UEs, UL traffic | gNB restart count, attach/PDU/tunnel | restart count 0 and failures 0 |

## Step-By-Step Flow
- [Step 1]: run the PAPER-08 calculator self-test.
- [Step 2]: generate `PTx` sweeps for `n41` and `n78`; store output under `analysis/data/`.
- [Step 3]: run an RFsim UL throughput row using the Paper07-style hard-pass gates.
- [Step 4]: add the modeled power columns to the RFsim row using the same `band`, `PTx`, and duty-cycle assumptions.
- [Step 5]: run PAPER-10 single-UE UL/DL balance using `180s` windows where runtime cost allows.
- [Step 6]: run PAPER-10 multi-UE UL stability for 2 and 3 selected UEs.
- [Step 7]: collect host CPU/memory during the same traffic window.
- [Step 8]: classify each row with `validation/success_criteria.md`.
- [Step 9]: update `validation/test_matrix.md`, `analysis/data/paper08_10_extended_run_matrix_2026-05-26.csv`, and the final report.

## RFsim Command Templates
- [PAPER-08 UL + Power Merge]:

```bash
MMTC_TOTAL_UES=29 \
MMTC_SAMPLE_UES=1 \
MMTC_IPERF_SAMPLE_UES=1 \
MMTC_IPERF_ENABLE=1 \
MMTC_IPERF_UDP=1 \
MMTC_IPERF_RATE=35M \
MMTC_IPERF_DURATION=60 \
MMTC_FORWARD_PING_MODE=parallel \
MMTC_RUN_REVERSE_PING=0 \
MMTC_PUCCH_COMMON_FALLBACK_BWP0=1 \
MMTC_PUSCH_256QAM=1 \
MMTC_PDSCH_256QAM=1 \
bash redcap_interface/redcap_mmtc_smoke_validation.sh
```

- [PAPER-10 Single-UE UL Baseline]:

```bash
MMTC_TOTAL_UES=29 \
MMTC_SAMPLE_UES=1 \
MMTC_IPERF_SAMPLE_UES=1 \
MMTC_IPERF_ENABLE=1 \
MMTC_IPERF_UDP=1 \
MMTC_IPERF_RATE=35M \
MMTC_IPERF_DURATION=180 \
MMTC_FORWARD_PING_MODE=parallel \
MMTC_RUN_REVERSE_PING=0 \
bash redcap_interface/redcap_mmtc_smoke_validation.sh
```

- [PAPER-10 Multi-UE UL Stability]:

```bash
MMTC_TOTAL_UES=29 \
MMTC_SAMPLE_UES="1 2 3" \
MMTC_IPERF_SAMPLE_UES=all \
MMTC_IPERF_ENABLE=1 \
MMTC_IPERF_UDP=1 \
MMTC_IPERF_RATE=10M \
MMTC_IPERF_DURATION=180 \
MMTC_FORWARD_PING_MODE=parallel \
MMTC_RUN_REVERSE_PING=0 \
bash redcap_interface/redcap_mmtc_smoke_validation.sh
```

## Required CSV Columns
```csv
run_id,paper_anchor,test_id,status,total_ues,sample_ues,traffic_direction,offered_rate_mbps,duration_s,band,ptx_dbm,modeled_pue_w,modeled_avg_power_mw,receiver_mbps,sender_mbps,jitter_ms,udp_loss_percent,ping_loss_percent,rtt_avg_ms,observed_mcs_table,observed_mcs_index,observed_qm,observed_nprb,host_cpu_percent,host_memory_percent,gnb_restart_count,failure_count,evidence_path,limitation_note
```

## Interpretation Rules
- [Modeled Power]: use only as a PAPER-08 model comparison and energy estimate.
- [Throughput Improvement]: do not claim improvement until the corresponding PAPER-10 rows pass against a recorded baseline.
- [Position Sensitivity]: do not claim Good/Fair/Bad reproduction until the RFsim channel knob is verified.
- [Host Sensitivity]: if only one physical host is available, use constrained CPU/memory containers as a proxy and mark it [Needs Verification].

## Latest PAPER-10 Multi-UE Evidence
- [Run ID]: `paper10_multiue_2026-05-26_17-26-35`.
- [Report]: `analysis/paper10_multiue_software_throughput_reproduction_2026-05-26_report.md`.
- [Raw Directory]: `analysis/data/paper10_multiue_raw/paper10_multiue_2026-05-26_17-26-35/`.
- [Combination Summary]: `analysis/data/paper10_multiue_combination_summary_2026-05-26.csv`.
- [Status]:
  - `PERF-P10-THR-002`: [PASS_WITH_GAP].
  - `PERF-P10-STAB-001`: [PASS].
- [Result Summary]:
  - UL aggregate receiver throughput: `93.117 Mbps`, Jain fairness `1.000000`, UDP loss `0%`.
  - DL aggregate receiver throughput: `144.675 Mbps`, Jain fairness `0.999994`, UDP loss about `61.5%` due saturation load.
- [2-UE Extension]:
  - `UE1+UE2`: UL `69.982 Mbps`, DL `195.658 Mbps`.
  - `UE1+UE3`: UL `69.983 Mbps`, DL `166.903 Mbps`.
  - `UE2+UE3`: [BLOCKED_BY_ESCALATION_LIMIT].
- [Limitation]:
  - RFsim/OAI-CN/OAI-nrUE proxy; PAPER-10 uses Open5GS, OTA SDR, COTS UEs, and `DDDDDDFUUU` TDD.
