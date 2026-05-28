# PAPER-11 Research on RedCap UE Performance Indicators

## Source
- [Paper ID]: `PAPER-11`.
- [PDF]: `redcap_doc/evaluation_papers/Research on RedCap UE’s performance indicators in real networkto support iot applications.pdf`.
- [MinerU Cache]: `redcap_doc/mineru_markdown/evaluation_papers/Research_on_RedCap_UEs_performance_indicators_in_real_network_to_support_iot_applications.pdf/Research on RedCap UE’s performance indicators in real networkto support iot applications.pdf/auto/Research on RedCap UE’s performance indicators in real networkto support iot applications.pdf.md`.
- [Venue]: ACM CCIOT 2024.
- [DOI]: `10.1145/3704304.3704305`.

## Paper Purpose
- [Goal]: compare [RedCap UE], [NR UE], and [LTE Cat4 UE] in commercial real networks.
- [Measured Dimensions]: [power consumption], [coverage], [latency], and [data rate].
- [Validation Role]: provide application-level gates for checking whether this RFsim RedCap platform can support industrial sensors, video surveillance, and wearables.

## Test Environment Extracted From Paper
- [2.1 GHz Case]: `20 MHz`, `15 kHz SCS`, `FDD`.
- [3.5 GHz Case]: `100 MHz`, `30 kHz SCS`, `TDD`, frame structure `DDDSUDDSUU`, special slot ratio `10:2:2`.
- [RedCap UE Capability]: `20 MHz`, `1T2R` in the paper's RedCap rows.
- [NR UE Baseline]: up to `100 MHz`, `2T4R` in the 3.5 GHz row.
- [Test Methods]: [Pull-far Test], [Peak Rate Test], [Latency Test], [Power Test], and [CQT] with near/middle/far locations.

## Key Equations And Spec Mapping
- [Peak Rate Formula]: paper references [TS 38.306 Section 4.1.2] for NR maximum data rate calculation.
- [Formula Variables]: layers, modulation order `Qm`, scaling factor, `Rmax = 948/1024`, PRBs, OFDM symbol duration, and overhead.
- [Power Model]:

```text
P_UE = P_SoC * t_SoC + P_FEM * t_FEM + P_PMU * t_PMU + P_sleep * t_sleep
```

- [Latency Model]:

```text
t_UL = t_data + t_trans + t_process + X * t_slot + K2 * t_slot + t_TDD
t_DL = t_data + t_trans + t_process + K0 * t_slot + K1 * t_slot + t_TDD
```

- [Latency Coefficients]:
  - [NR / RedCap UE]: `X=1`, `K0=1`, `K1=1`, `K2=1`, `K3=0`.
  - [LTE Cat4 UE]: `X=2`, `K0=1`, `K1=4`, `K2=4`, `K3=4`.
- [Application Requirement Source]: paper cites [3GPP TR 38.875] for RedCap target applications; exact clause numbers are [Needs Verification].

## Extracted Application Gates
| Application | Paper Requirement | PAPER-11 RedCap Far-Point Result | RFsim Reproduction Gate |
|---|---|---:|---|
| Industrial wireless sensor | data rate `<2 Mbps`, E2E latency `<100 ms`, multi-year battery life | DL `68 Mbps`, UL `17 Mbps`, latency `13.7/14.3 ms` | run UL/DL offered rates at or above `2 Mbps`, ping 32/1500 bytes, require `<100 ms` average RTT |
| Video surveillance economy | `2-4 Mbps`, E2E latency `<500 ms` | DL `68 Mbps`, UL `17 Mbps` | run DL offered rate `4 Mbps`, require `<500 ms` average RTT |
| Video surveillance high-end | `7.5-25 Mbps`, E2E latency `<500 ms` | DL `68 Mbps`, UL `17 Mbps`; paper notes HD video cannot be guaranteed at the weakest coverage point | run DL offered rate `25 Mbps`, require `<500 ms` average RTT; mark coverage part [Not Directly Comparable] |
| Wearable | DL `5-50 Mbps`, UL `2-5 Mbps`; peak DL `150 Mbps`, UL `50 Mbps` | far DL `68 Mbps`, far UL `17 Mbps` | run DL `50 Mbps` and UL `5 Mbps`; peak comparison is [RFsim proxy] |

## Extracted Rate Observations
- [2.1 GHz Uplink]: RedCap near/middle/far rates are about `95%` of NR UE in the paper.
- [2.1 GHz Downlink]: RedCap near/middle/far rates are about `60%`, `76%`, and `77%` of NR UE.
- [3.5 GHz Uplink]: RedCap near/middle/far rates are about `11%`, `14%`, and `55%` of NR UE.
- [3.5 GHz Downlink]: RedCap near/middle/far rates are about `10%`, `17%`, and `19%` of NR UE.
- [Interpretation]: when bandwidth, modulation, and MIMO are made equivalent, RedCap throughput is approximately the same as NR UE; the large 3.5 GHz gap mainly comes from `20 MHz 1T2R` RedCap versus `100 MHz 2T4R` NR UE.

## RFsim Reproduction Scope
- [Directly Runnable]:
  - UL and DL [iperf3] offered-load tests.
  - [Ping] latency tests with 32-byte and 1500-byte payloads.
  - IoT application gate verdicts for industrial sensor, video, and wearable profiles.
- [Proxy Only]:
  - [Near/Middle/Far CQT]: use RFsim channel/SNR or channel model sweeps, not physical site positions.
  - [Coverage Pull-Far]: use throughput drop and attach/tunnel stability under channel degradation, not actual meters.
  - [Power]: use modeled power from PAPER-08/PAPER-11 equations when SoC/FEM/PMU timing assumptions are supplied; RFsim cannot measure UE current in mA.
- [Not Directly Comparable]:
  - Commercial network scheduler behavior.
  - COTS RedCap UE RF front-end current draw.
  - Real RSRP/SINR and drive-test geometry.

