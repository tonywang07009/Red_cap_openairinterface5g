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

## Plot Axis Rule
- X-axis must be one of the controlled simulator factors, such as [UE count], [offered rate], [run index], or [BWP/scheduler case].
- Y-axis must be one measured metric from this dictionary.
- Do not plot paper-only variables unless the simulator has an explicit equivalent.
