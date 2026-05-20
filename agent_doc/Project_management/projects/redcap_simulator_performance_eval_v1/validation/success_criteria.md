# RFsim Performance Evaluation Success Criteria

## Scope
- Project: `redcap_simulator_performance_eval_v1`
- Applies to:
  - `DOE-BASE-001`
  - `DOE-L9-01..09`
- Input design:
  - `validation/taguchi_doe_matrix.md`
  - `analysis/data/p2_taguchi_l9_run_matrix.csv`
- Purpose:
  - define experiment pass/fail criteria,
  - separate paper-comparable trends from RFsim platform-health criteria,
  - preserve failures as simulator improvement evidence.

## Criteria Layers

### Layer 1: Hard Pass Criteria
- These decide whether a run is operationally usable.
- A run is [HARD PASS] only if all conditions are satisfied:
  - `attach_success_ratio = 100%` for sampled UEs.
  - `pdu_success_ratio = 100%` for sampled UEs.
  - `tunnel_success_ratio = 100%` for sampled UEs.
  - `forward_ping_success_ratio = 100%` for sampled UEs.
  - `gnb_restart_count = 0`.
  - `failure_count = 0`.
  - iperf log exists for each selected iperf UE.
  - each selected iperf UE has sender throughput parsed.
- Receiver-side iperf output is preferred. If UDP sender succeeds but server report is unavailable, classify as [HARD PASS WITH MEASUREMENT GAP] instead of plain [HARD PASS].

### Layer 2: Paper-Comparable Trend Criteria
- These decide whether the run can support a cautious paper-comparison narrative.
- Paper decides [what to inspect], not absolute pass/fail values unless RFsim configuration equivalence is verified.
- Trend criteria:
  - [Throughput Trend]: receiver/sender throughput should generally increase with offered rate until saturation.
  - [Load Trend]: as UE scale increases, throughput, jitter, loss, and failure markers should degrade gradually, not collapse unexpectedly.
  - [Latency Trend]: ping RTT should remain stable enough to use as a proxy; do not claim full 5G E2E latency equivalence.
  - [Control Pressure Trend]: RA/control failure markers should be reported with UE scale; do not claim true PDCCH blocking probability without instrumentation.
- Primary paper anchors:
  - PAPER-06: RedCap throughput and latency performance.
  - PAPER-07: UDP peak-rate verification and RedCap access traceability.
  - PAPER-02: scheduled UE / PDCCH pressure rationale.

### Layer 3: Exploratory Metrics
- These are not hard pass/fail criteria yet.
- Track them for anomaly detection and later simulator improvement:
  - UDP jitter.
  - UDP loss percent.
  - sender/receiver throughput gap.
  - RA Msg2/Msg4 retry or failure markers.
  - PUCCH fallback markers.
  - CPU/memory pressure if collected.
  - container restart timing.

### Layer 4: Failure-To-Improvement Log
- Every [FAIL] or [BLOCKED] run must produce a structured improvement record.
- The purpose is to convert runtime errors into simulator modification direction.

## Run Status Labels
| Status | Meaning | Required Action |
|---|---|---|
| [PASS] | Hard pass criteria satisfied and required metrics parsed | Include in trend analysis |
| [PASS_WITH_GAP] | Runtime passed but one or more non-critical measurements are missing | Include with limitation note |
| [FAIL] | Runtime completed but hard pass criteria failed | Create failure-to-improvement record |
| [BLOCKED] | Runtime could not start or environment/tooling prevented evaluation | Create blocker record before rerun |
| [INVALID] | Run configuration does not match the DOE row or cannot be interpreted | Do not include in trend analysis |

## Required CSV Columns For P3
```csv
run_id,status,hard_pass,pass_with_gap,blocked,invalid,total_ues,sample_ues,iperf_rate,receiver_mbps,sender_mbps,jitter_ms,udp_loss_percent,ping_loss_percent,rtt_min_ms,rtt_avg_ms,rtt_max_ms,attach_success_ratio,pdu_success_ratio,tunnel_success_ratio,forward_ping_success_ratio,gnb_restart_count,failure_count,raw_log_dir,iperf_log_paths,ping_log_paths,trend_note,failure_category,improvement_direction
```

## Failure Categories
| Category | Typical Evidence | Simulator Modification Direction |
|---|---|---|
| [ENVIRONMENT] | Docker compose failure, missing image, missing config, CN unavailable | Improve preflight checks, path validation, container readiness gates |
| [ATTACH] | UE does not reach RRC/Registration Accept | Inspect UE/gNB/RRC/NAS configuration and UE launch timing |
| [PDU_SESSION] | Registration succeeds but PDU Session Establishment fails | Inspect CN/SMF/UPF path and subscriber/session config |
| [TUNNEL] | PDU accept exists but `oaitun_ue1` missing or misconfigured | Inspect UE tunnel setup and container network state capture |
| [USER_PLANE] | tunnel exists but ping or iperf fails | Inspect routing, UPF, ext-dn reachability, ip rules, packet forwarding |
| [THROUGHPUT] | iperf succeeds but throughput collapses unexpectedly | Inspect scheduler, PUSCH allocation, CPU pressure, offered-rate saturation |
| [JITTER_LOSS] | jitter/loss spikes while hard pass holds | Inspect host load, packet pacing, UDP rate, sequential/parallel test effects |
| [GNB_STABILITY] | gNB restart or killed process | Inspect gNB logs, memory pressure, UE start burst, scheduler/resource limits |
| [MEASUREMENT_GAP] | sender report exists but receiver/server report missing | Improve log parser, iperf server lifecycle, result collection |
| [INSTRUMENTATION_GAP] | Desired metric is not exposed | Add logging/instrumentation before claiming paper-level metric |

## Failure-To-Improvement Record Template
| Field | Required Content |
|---|---|
| Run ID | DOE row or baseline ID |
| Status | [FAIL] / [BLOCKED] / [PASS_WITH_GAP] / [INVALID] |
| Failed Criteria | Which hard criterion or measurement gap triggered the status |
| Evidence Paths | Raw logs, iperf logs, ping logs, container snapshots |
| Suspected Layer | PHY / MAC / RRC / NAS / CN / Docker / host / parser |
| Paper Impact | Whether the issue affects paper-comparable trend claims |
| Improvement Direction | Concrete simulator or automation change to investigate |
| Rerun Requirement | Whether rerun is required after fix |

## Paper-Comparison Guardrails
- Do not claim RFsim reproduces PAPER-03 or PAPER-04 link-level SNR/BLER/MIL/MCL results.
- Do not claim true PAPER-02 PDCCH blocking probability unless scheduler/control-channel instrumentation exists.
- Do not claim PAPER-06/PAPER-07 absolute throughput equivalence unless RFsim radio/config equivalence is documented.
- It is acceptable to claim [trend-level comparison] when:
  - DOE row is [PASS] or [PASS_WITH_GAP],
  - metric source is clearly stated,
  - RFsim limitation is documented.

## Initial Success Standard For P3
- [Minimum Acceptable Dataset]:
  - `DOE-BASE-001` passes.
  - At least 7 of 9 L9 rows are [PASS] or [PASS_WITH_GAP].
  - No unclassified [FAIL] remains.
  - Every [FAIL]/[BLOCKED]/[PASS_WITH_GAP] has a failure-to-improvement record.
- [Strong Dataset]:
  - All 10 rows are [PASS] or [PASS_WITH_GAP].
  - At least 8 rows have receiver-side throughput parsed.
  - `gnb_restart_count = 0` for all rows.
  - Throughput/loss/jitter trends can be plotted without dropping failed rows.
