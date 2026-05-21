# PAPER-07 Manual Current-Container Capture

## Scope
- Date: 2026-05-21
- Reason: Full compose-based reproduction was blocked by Docker socket sandbox permissions.
- Safer fallback: reuse existing healthy RFsim containers without restarting compose.
- UE container: `rfsim5g-oai-nr-ue1_redcap`
- Server container: `oai-ext-dn`
- UE source interface: `oaitun_ue1`
- UE source IP: `10.0.0.2`
- Server target IP: `192.168.72.135`

## Commands
- Server reset before each point:
  - `docker exec oai-ext-dn sh -c 'pids=$(pidof iperf3 2>/dev/null || true); [ -z "$pids" ] || kill $pids; iperf3 -s -D'`
- 64QAM proxy:
  - `docker exec rfsim5g-oai-nr-ue1_redcap iperf3 -c 192.168.72.135 -t 60 -B 10.0.0.2 -u -b 26M`
- 256QAM proxy:
  - `docker exec rfsim5g-oai-nr-ue1_redcap iperf3 -c 192.168.72.135 -t 60 -B 10.0.0.2 -u -b 35M`
- RTT check:
  - `docker exec rfsim5g-oai-nr-ue1_redcap ping -I oaitun_ue1 -c 10 192.168.72.135`

## Captured Summary
| Point | Offered UDP rate | Sender Mbps | Receiver Mbps | Jitter ms | UDP loss | Datagrams |
|---|---:|---:|---:|---:|---:|---:|
| PAPER07-UL-64QAM-PROXY | 26M | 26.0 | 26.0 | 0.550 | 0/134667 (0%) | 134667 |
| PAPER07-UL-256QAM-PROXY | 35M | 35.0 | 35.0 | 0.472 | 0/181283 (0%) | 181283 |

## Ping Summary
- Packets: 10 transmitted, 10 received.
- Packet loss: 0%.
- RTT min/avg/max/mdev: 12.453/13.070/13.836/0.390 ms.

## Limitation
- This capture reuses the active RFsim runtime state and does not re-run full compose orchestration.
- Offered UDP rate is used as the paper modulation-point proxy because the current workflow does not independently lock or verify 64QAM/256QAM MCS.
