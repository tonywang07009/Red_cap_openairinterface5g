# Metric Dictionary

## Core Metrics
| Metric | Unit | Source | Notes |
|---|---:|---|---|
| Offered rate | Mbit/s | iperf command | X-axis candidate |
| Sender throughput | Mbit/s | iperf sender log | UE/container-side value |
| Receiver throughput | Mbit/s | iperf receiver log | ext-dn/server-side value |
| UDP jitter | ms | iperf receiver log | UDP only |
| UDP loss | datagrams / percent | iperf receiver log | Include numerator and denominator |
| RTT latency | ms | ping log | RFsim proxy, not a full 5G user-plane latency model |
| Packet loss | percent | ping/iperf | Separate ping loss and UDP datagram loss |
| Attach success ratio | percent | UE/gNB/CN logs | Runtime readiness metric |
| PDU session success ratio | percent | UE/CN logs | User-plane readiness metric |
| Tunnel readiness ratio | percent | UE/container network check | Data-path readiness metric |
| gNB restart count | count | Docker inspect/log markers | Stability metric |
| Modeled UE UL power | W / mW | `analysis/scripts/p08_uplink_power_calculator.py` | PAPER-08 Equation (1) estimate, not RF power-meter evidence |
| Duty-cycle average power | W / mW | `analysis/scripts/p08_uplink_power_calculator.py` | Uses transmit, connected-idle, and eDRX time shares |
| Uplink transmit power input | dBm | experiment matrix / external calculator input | Model input axis for PAPER-08 power estimate |
| Host CPU utilization | percent / cores | `top`, `docker stats`, or host monitor log | PAPER-10 host-resource sensitivity metric |
| Host memory utilization | percent / MiB | `top`, `docker stats`, or host monitor log | PAPER-10 host-resource sensitivity metric |
| Observed MCS / Qm / NPRB | table/index/order/PRB | gNB `nrMAC_stats.log` | Scheduler evidence for throughput interpretation |

## Plot Axis Rule
- X-axis must be one of the controlled simulator factors, such as [UE count], [offered rate], [run index], or [BWP/scheduler case].
- Y-axis must be one measured metric from this dictionary.
- Do not plot paper-only variables unless the simulator has an explicit equivalent.
- PAPER-08 power plots must label [Modeled UE UL power] as a calculator output, not a direct RFsim measurement.
- PAPER-10 host-resource plots must record the monitor source and sampling window.
