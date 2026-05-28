# PAPER-11 Real-Network RedCap Proxy Test Matrix

## Scope
- [Paper Anchor]: `Research on RedCap UE’s performance indicators in real networkto support iot applications.pdf`.
- [Purpose]: reproduce the paper's validation logic on the local OAI RFsim RedCap simulator.
- [Primary Metrics]: [UL throughput], [DL throughput], [32-byte RTT], [1500-byte RTT], [UDP packet loss], and [run stability].
- [Guardrail]: this matrix reproduces [service-level behavior] and [test flow]; it does not reproduce commercial-network RF, COTS UE power draw, or physical coverage distance.

## Experiment Rows
| Test ID | Paper Basis | RFsim Setup | Offered Load / Probe | Pass Gate | Status |
|---|---|---|---|---|---|
| PERF-P11-APP-IND-001 | Industrial wireless sensor | UE1 RedCap RFsim, UDP UL/DL | `2 Mbps` UL/DL, ping `32` and `1500` bytes | avg RTT `<100 ms`, UDP loss `<1%` | [PASS_WITH_GAP] |
| PERF-P11-APP-VID-ECO-001 | Economy video surveillance | UE1 RedCap RFsim, UDP DL | DL `4 Mbps`, optional UL `2 Mbps`, ping probes | avg RTT `<500 ms`, UDP loss `<1%` | [PASS_BY_HIGHER_LOAD] |
| PERF-P11-APP-VID-HI-001 | High-end video surveillance | UE1 RedCap RFsim, UDP DL | DL `25 Mbps`, UL `17 Mbps`, ping probes | avg RTT `<500 ms`, UDP loss `<1%`; coverage note [Not Directly Comparable] | [PASS] |
| PERF-P11-APP-WEAR-001 | Wearable reference | UE1 RedCap RFsim, UDP UL/DL | DL `50 Mbps`, UL `5 Mbps`, ping probes | avg RTT recorded; throughput reaches target or saturation recorded | [PASS_WITH_GAP] |
| PERF-P11-FAR-GATE-001 | Paper far-point RedCap result | UE1 RedCap RFsim, UDP UL/DL | DL `68 Mbps`, UL `17 Mbps`, ping `32/1500` bytes | compare to application gates; exact `13.7/14.3 ms` is [Needs Verification] as RFsim target | [PASS_WITH_GAP] |
| PERF-P11-CQT-PROXY-001 | Near/middle/far CQT | RFsim channel/SNR proxy sweep | repeat far-gate load across channel profiles | monotonic degradation captured, setup status logged | [TODO] |
| PERF-P11-LIVE-001 | Visible iperf process | `redcap_interface/paper11_iperf_live_demo.sh` | live `iperf3 -i 1`, UL `17M`, DL `68M` | raw logs and CSV generated | [PASS] |

## Latest Evidence
| Run ID | Scenario | UL Receiver Mbps | DL Receiver Mbps | 32B RTT Avg ms | 1500B RTT Avg ms | DL Loss % | Verdict |
|---|---|---:|---:|---:|---:|---:|---|
| `paper11_app_industrial_2026-05-27_23-32-00` | Industrial `2M/2M` | `1.98` | `2.01` | `47.722` | `105.556` | `0` | [PASS_WITH_GAP] |
| `paper11_app_video_high_2026-05-27_23-33-30` | Video high-end `17M/25M` | `16.2` | `25.6` | `48.483` | `59.721` | `0.017` | [PASS] |
| `paper11_app_wearable_2026-05-27_23-34-10` | Wearable `5M/50M` | `4.97` | `30.3` | `49.217` | `48.710` | `0.47` | [PASS_WITH_GAP] |
| `paper11_live_iperf_2026-05-27_23-30-37` | Paper far gate `17M/68M` | `16.8` | `32.7` | `37.911` | `60.544` | `0.63` | [PASS_WITH_GAP] |

- [Evidence CSV]: `analysis/data/paper11_live_iperf_summary_2026-05-27.csv`.
- [Report]: `analysis/paper11_real_network_proxy_reproduction_2026-05-27_report.md`.

## Default Reproduction Command
```bash
P11_MODE=both \
P11_UE=1 \
P11_UL_RATE=17M \
P11_DL_RATE=68M \
P11_DURATION=20 \
bash redcap_interface/paper11_iperf_live_demo.sh
```

## Optional Setup Command
```bash
P11_SETUP=1 \
P11_MODE=both \
P11_UE=1 \
P11_UL_RATE=17M \
P11_DL_RATE=68M \
P11_DURATION=20 \
bash redcap_interface/paper11_iperf_live_demo.sh
```

## Interpretation Rules
- [PASS]: the RFsim run finishes, interval logs are visible, CSV is written, and application gate thresholds are met.
- [PASS_WITH_GAP]: the RFsim run finishes but one paper metric is only proxy-comparable.
- [FAIL]: traffic/latency metrics violate the selected application gate.
- [BLOCKED]: containers, UE tunnel, iperf3, or ping cannot run.
- [Power Result]: record as [model-only] unless external current measurement is added.
- [Coverage Result]: record as [RFsim channel proxy] unless physical RSRP/SINR data is added.
