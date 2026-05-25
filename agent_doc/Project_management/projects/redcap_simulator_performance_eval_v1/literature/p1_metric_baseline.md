# P1 Literature Metric Baseline

## Scope
- Milestone: P1
- Task IDs: P1-T1, P1-T2
- Paper source: `redcap_doc/evaluation_papers/`
- DOE source: `agent_doc/exp_skill/taguchi Method.pdf`
- Extraction method: targeted `pdftotext` page and keyword extraction.

## Executive Finding
- [Directly Comparable]: PAPER-06 and PAPER-07 provide throughput and latency values that can map to RFsim `iperf` and `ping` outputs.
- [Partially Comparable]: PAPER-01 and PAPER-04 provide latency/throughput or uplink-performance trends, but some variables such as SUL and SNR are not directly controlled in current RFsim.
- [Proxy Only]: PAPER-02 PDCCH blocking probability can be approximated only through scheduler/control-channel pressure markers unless OAI instrumentation is extended.
- [Not Directly Comparable]: PAPER-03 coverage/MIL/BLER/SINR results depend on link-level and link-budget channel modeling that RFsim does not currently emulate.
- [Scenario Baseline]: PAPER-05 mainly defines wearable/worker-safety requirements and low-power features.

## Paper Metric Extraction Table
| Paper ID | Page/Figure/Table | Metric | Scenario | X-axis | Y-axis | Simulator Equivalent | Confidence |
|---|---|---|---|---|---|---|---|
| PAPER-01 | PDF p.4, Table I | Ping latency | RedCap UE vs LTE UE, near/mid/far points, 32-byte and 1500-byte ping | location class / packet size | latency in ms | `ping` RTT min/avg/max by UE sample | Medium |
| PAPER-01 | PDF p.4, Fig. 3 | UL/DL data-rate ratio | 4G CQT RedCap vs conventional LTE UE | test point / terminal type | throughput ratio | iperf sender/receiver Mbps ratio to baseline UE | Low |
| PAPER-01 | PDF p.4, Fig. 4 | RedCap vs NR UE field rate | 5G drive test | terminal type | UL/DL data rate | iperf Mbps under same RFsim scenario | Low |
| PAPER-01 | PDF p.4, Fig. 5 | BWP performance | CD-SSB vs NCD-SSB BWP | BWP type | throughput / mobility behavior | Case A/B or BWP-specific RFsim run markers | Low |
| PAPER-02 | PDF p.2, Table I | Use-case requirements | IWSN, video surveillance, wearables | use case | data rate, latency, reliability | experiment acceptance targets | High |
| PAPER-02 | PDF p.2, Eq. (2) | PDCCH blocking rate | scheduled users sharing CORESET candidates | scheduled UE count / CORESET / DCI / candidates | blocked UE ratio | scheduler/control-channel pressure proxy; needs instrumentation | Medium |
| PAPER-02 | PDF p.4, Fig. 9 | PDCCH blocking probability | FR1/FR2, 1Rx/2Rx RedCap, DCI 40 bits | total scheduled UEs | blocking probability | proxy via simultaneous UE count and RA/control failures | Medium |
| PAPER-02 | PDF p.4, Fig. 10-11 | DCI size impact | 20/30/40-bit DCI in FR1/FR2 | total scheduled UEs | blocking probability | not directly configurable; possible future DCI-size experiment | Low |
| PAPER-02 | PDF p.5, Fig. 12-14 | Candidate/CORESET impact | PDCCH candidates and CORESET size | candidate set / CORESET CCE count | blocking probability | CORESET/BWP configuration proxy if exposed | Low |
| PAPER-03 | PDF p.1-2, abstract and method | Coverage recovery | Rural/Urban/Indoor, 0.7/2.6/28 GHz | channel/scenario | required recovery in dB | not direct in RFsim; use as limitation and channel-model gap | Medium |
| PAPER-03 | PDF p.9, Fig. 24-25 | PUSCH BLER and data rate | Rural/Urban/Indoor | SNR / carrier scenario | BLER, PUSCH data rate | no direct SNR/BLER RFsim control; possible link-level-only comparison | Low |
| PAPER-03 | PDF p.10-11, Fig. 26-28 | MIL coverage | Rural/Urban/Indoor | physical channel | MIL in dB | not direct in RFsim | Low |
| PAPER-04 | PDF p.4, Table III | Evaluation parameters | RedCap UL/SUL link-level simulation | UL/SUL config | SNR range, TBS, RBs, antennas | define RFsim factor candidates where available | Medium |
| PAPER-04 | PDF p.4, Table IV | PUSCH coverage gain | UL 3.5 GHz vs SUL 700 MHz | carrier | required SNR, MCL, MCL gain | not direct unless SUL/channel model exists; use as limitation | Medium |
| PAPER-04 | PDF p.4, Fig. 2 | PUCCH BLER | UL vs SUL | SNR | BLER | no direct RFsim BLER; possible PUCCH failure proxy | Low |
| PAPER-04 | PDF p.5, Fig. 3 | PRACH detection probability | UL vs SUL | SNR | detection probability | RA success / Msg1-Msg2 proxy | Medium |
| PAPER-04 | PDF p.5, Fig. 4 | PUSCH throughput | UL vs SUL | SNR | throughput Mbps | direct metric is throughput, but RFsim lacks SNR/SUL axis | Medium |
| PAPER-04 | PDF p.5, Fig. 5 | PUSCH BLER | UL vs SUL | SNR | BLER | no direct RFsim BLER | Low |
| PAPER-05 | PDF p.2, Table I | Current IoT protocol data rates | ZigBee/LoRa/BLE/802.15.6 | protocol | data rate/range/Tx power | scenario baseline only | Medium |
| PAPER-05 | PDF p.3, Table II | 5G wearable architecture | current wearable vs 5G-based solution | architecture | qualitative comparison | scenario design only | Medium |
| PAPER-05 | PDF p.4, Table III-IV | Release and power saving features | RedCap, DRX/eDRX/RRM relaxation | feature/release | cycle or feature support | low-power factor baseline for future DOE | Medium |
| PAPER-06 | PDF p.2, Table 1 | Simulation parameters | 2.1/3.5 GHz RedCap performance | parameter | bandwidth/antenna/power | configure RFsim factor assumptions where possible | Medium |
| PAPER-06 | PDF p.2-3 | Edge rate | 3.5 GHz and 2.1 GHz coverage planning | frequency/site planning | UL/DL edge rate | not direct; no RF propagation in RFsim | Low |
| PAPER-06 | PDF p.4, peak-rate table | Single-user peak rate | FDD/TDD, BWP size, 1T2R, QAM | BWP size / duplex / modulation | UL/DL Mbps | direct target for iperf throughput vs BWP/config | High |
| PAPER-06 | PDF p.4, Section V | Latency | current RedCap network ping and mobility | packet size / mobility event | latency in ms | direct target for ping RTT; mobility not in current RFsim | Medium |
| PAPER-07 | PDF p.1-2, Table I-II | Capability and scenario requirements | Cat-1/Cat-4/RedCap and RedCap scenarios | use case | data rate, E2E latency, reliability | acceptance target table | High |
| PAPER-07 | PDF p.3, Table III | RedCap identification | Msg1/Msg3/UE capability | identification point | access tradeoff | RA/RRC traceability, not throughput metric | Medium |
| PAPER-07 | PDF p.4, Table IV | Uplink peak rate test | 3.5 GHz TDD, 64QAM/256QAM, UDP full buffer | modulation order | PHY/PDCP UL Mbps | direct RFsim UDP UL iperf baseline target | High |
| PAPER-07 | PDF p.4, Table V | Downlink peak rate test | 3.5 GHz TDD, 64QAM/256QAM, UDP full buffer | modulation order | PHY/PDCP DL Mbps | RFsim DL iperf target if DL test enabled | Medium |

## Simulator Metric Map
| Simulator Metric | Paper Evidence | RFsim Signal | Initial Use |
|---|---|---|---|
| [Receiver throughput Mbps] | PAPER-06 peak-rate table; PAPER-07 Table IV/V; PAPER-04 Fig. 4 | iperf receiver Mbps | Primary throughput response |
| [Sender throughput Mbps] | PAPER-06 and PAPER-07 throughput tests | iperf sender Mbps | Cross-check sender/receiver gap |
| [RTT latency ms] | PAPER-01 Table I; PAPER-06 Section V; PAPER-02 Table I use-case latency | ping RTT | Primary latency response |
| [UDP jitter ms] | No strong paper value found in current extraction | iperf UDP jitter | Simulator-only metric; use for stability |
| [UDP loss percent] | PAPER-02 reliability/use-case needs; no direct UDP-loss plot found | iperf UDP loss | Reliability proxy |
| [Attach/PDU/tunnel success ratio] | PAPER-07 access recognition; PAPER-02 control-channel pressure | UE/gNB/CN logs | Runtime readiness metric |
| [RA/control pressure] | PAPER-02 blocking probability; PAPER-04 PRACH detection | RA Msg1/Msg2/Msg4 markers, scheduler failures | Proxy for control-channel saturation |
| [gNB restart count] | No paper metric | Docker inspect/log markers | Platform stability only |

## Initial RFsim Acceptance Targets
| Target ID | Basis | Proposed Initial Criterion | Status |
|---|---|---|---|
| LIT-THR-UL-01 | PAPER-07 Table IV | Compare single-UE UDP UL against 25.5 Mbps PDCP at 64QAM and 34.7 Mbps PDCP at 256QAM only if RFsim config is comparable | [Needs Verification] |
| LIT-THR-DL-01 | PAPER-07 Table V | Compare DL throughput against 106.1/140.5 Mbps PDCP only if DL test and config are comparable | [Needs Verification] |
| LIT-LAT-01 | PAPER-01 Table I / PAPER-06 Section V | Use ping RTT as latency proxy; do not claim E2E 5G latency equivalence | [Needs Verification] |
| LIT-CTRL-01 | PAPER-02 Fig. 9 | Track failure pressure as UE count increases; do not claim true PDCCH blocking probability without instrumentation | [Needs Verification] |
| LIT-COV-01 | PAPER-03 / PAPER-04 | Treat SNR/BLER/MIL/MCL evidence as non-direct RFsim comparison | [Accepted Limitation] |

## Recommended P2 Factors
| Factor | Candidate Levels | Paper Basis | Simulator Availability |
|---|---|---|---|
| UE count | 1, 16, 32, 56 | PAPER-02 scheduled UE load; project runtime history | Available through RFsim staging |
| Offered UL rate | 10M, 50M, 85M | PAPER-06/07 throughput baseline and current helper | Available via iperf |
| Traffic direction | UL, DL, bidirectional [if supported] | PAPER-06/07 UL/DL peak-rate tests | UL available; DL needs helper check |
| BWP/CORESET case | Case A, Case B | PAPER-01 BWP, PAPER-02 CORESET pressure | Available in existing RedCap scenario history [Needs Verification] |
| Low-power mode | baseline, DRX/eDRX/PSM marker mode | PAPER-05 power-saving features | Marker/runtime support only [Needs Verification] |

## Taguchi DOE Notes For P2
- Source: `agent_doc/exp_skill/taguchi Method.pdf`.
- Extracted principles:
  - Select [control input parameters], [response variable], and [levels].
  - Choose an [orthogonal array] based on number of factors and levels.
  - Assign factors to columns.
  - Run experiments according to level combinations.
  - Analyze outputs using [ANOVA], [S/N ratio], and response means.
- Response direction:
  - [Larger is better]: receiver throughput, attach/PDU/tunnel success ratio.
  - [Smaller is better]: RTT latency, jitter, loss, failure markers, restart count.
  - [Nominal is better]: not recommended for first RFsim phase.
- Limitation:
  - Taguchi can reduce runs, but interaction effects are limited unless the selected OA explicitly supports them.

## P1 Decision
- Use PAPER-06 and PAPER-07 as the first performance-comparison baseline.
- Use PAPER-02 as the control-channel pressure and UE-count scaling rationale.
- Use PAPER-03 and PAPER-04 to document RFsim's channel-model limitation.
- Use PAPER-05 for scenario and low-power-factor justification.
