# PAPER-10 Platform Improvement Checklist

## Scope
- [Paper]: `paper_Performance Analysis and Comparison of.pdf`.
- [Focus]: compare this RedCap RFsim platform against PAPER-10 themes: throughput balance, E2E latency, position sensitivity, host sensitivity, and multi-UE stability.
- [Important Limit]: this platform currently runs OAI RFsim, not the PAPER-10 SDR/COTS UE testbed. Coverage and physical location results are [Not Directly Comparable].

## PAPER-10 Comparison Checklist
| Item | PAPER-10 Claim / Method | Current Platform Evidence | Current Status | Next Validation |
|---|---|---|---|---|
| Throughput UL/DL balance | OAI tends to be DL-strong and UL-weaker than srsRAN | Paper07 RFsim reproduced UL/DL target-rate runs; new matrix adds explicit UL/DL ratio | [Needs New Run] | `PERF-P10-THR-001`, `PERF-P10-THR-002` |
| E2E latency | OAI latency is a key advantage; paper reports OAI shorter than srsRAN in tested cases | Existing DOE captures ping RTT proxy; no srsRAN baseline in this repo | [Partial] | `PERF-P10-LAT-001` |
| Good/Fair/Bad position sensitivity | PAPER-10 uses physical UE locations and RSRP/MCS drop | RFsim does not yet expose a verified Good/Fair/Bad channel axis in this scenario | [Blocked] | define controlled RFsim path-loss/SNR/MCS proxy before claim |
| Host PC sensitivity | PAPER-10 compares host PC resource effects | current matrix adds CPU/memory capture; no second physical host evidence yet | [Needs New Run] | `PERF-P10-HOST-001` |
| Multi-UE stability | PAPER-10 notes OAI crash tendency under weak signal or multi-UE UL | existing mMTC DOE passed hard gates; new rows focus 2-3 UE UL traffic with restart evidence | [Partial] | `PERF-P10-STAB-001` |

## Platform Logic That Improves Original OAI Workflow
| Improvement Area | File / Flow | Change Effect | PAPER-10 Relevance |
|---|---|---|---|
| RedCap BWP PUCCH reservation fit | `openair2/LAYER2/NR_MAC_gNB/nr_radio_config.c`, `get_max_supported_ues_for_pucch()` | avoids legacy full `MAX_MOBILES_PER_GNB` PUCCH reservation abort for smaller RedCap BWPs | improves multi-UE startup stability and RedCap BWP validity |
| PUCCH BWP0 fallback wiring | `redcap_interface/redcap_mmtc_smoke_validation.sh`; `redcap_interface/bash_library/generate_mmtc_overlay.sh` | makes UE runtime default to stable common-BWP PUCCH behavior for the RFsim scenario | reduces attach/user-plane instability during scaled tests |
| RedCap UE capability YAML | `openair3/UICC/nr_redcap_config.c`; runtime YAML `/tmp/nr-ue-mmtc.yaml` | makes RedCap capability, Rx branch count, PUSCH/PDSCH 256QAM flags reproducible per UE | enables controlled UL/DL throughput comparisons |
| Full-carrier 51PRB profile | `ci-scripts/conf_files/gnb.sa.band78.fr1.51PRB.usrpb210.redcap.yaml`; runtime menu options 13/14 | aligns UE `-r`, RF frequency, SSB, and gNB 51PRB carrier semantics | improves RedCap 20MHz experiment validity |
| mMTC overlay and CN subscriber generation | `redcap_interface/redcap_mmtc_smoke_validation.sh`; generated CN DB overlays | allows repeatable 29/32/56 UE-scale experiments instead of manual static compose edits | supports PAPER-10 multi-UE stability tests |
| gNB restart diagnostics | smoke validation logs, Docker inspect state, restart tail logs | converts crash/restart symptoms into classified evidence paths | directly targets PAPER-10 OAI crash-risk discussion |
| UL PRB cap through RC xApp | `openair2/E2AP/RAN_FUNCTION/O-RAN/ran_func_rc.c`; `openair2/LAYER2/NR_MAC_gNB/nr_mac_redcap.h`; `gNB_scheduler_ulsch.c` | external control can cap RedCap UL PRBs per UE for eRedCap-like or fairness tests | gives an explicit UL scheduler-control knob missing in a plain throughput-only setup |
| Paper08 power calculator | `analysis/scripts/p08_uplink_power_calculator.py` | adds modeled UE power and duty-cycle average to throughput rows | connects throughput/power tradeoff to RedCap energy papers |

## Checklist For Claiming Improvement
- [ ] [Throughput] collect baseline and improved UL/DL rows with the same PRB profile, 256QAM setting, offered rate, and duration.
- [ ] [Throughput] report UL Mbps, DL Mbps, DL/UL ratio, MCS table, Qm, and NPRB.
- [ ] [Latency] collect ping RTT during the same runtime window and preserve target IP.
- [ ] [Position Proxy] verify a controlled RFsim channel/SNR/MCS axis before using Good/Fair/Bad labels.
- [ ] [Host Sensitivity] collect CPU and memory with the monitor source and sampling interval.
- [ ] [Multi-UE Stability] run at least 2-UE and 3-UE UL traffic rows and require `gnb_restart_count=0`.
- [ ] [Failure Discipline] create a failure-to-improvement record for every [FAIL], [BLOCKED], or [PASS_WITH_GAP].

## Current Conclusion
- [Can Claim Now]: the platform has better repeatability and evidence capture than a manual OAI RFsim run because it adds RedCap capability wiring, mMTC overlay generation, hard-pass gates, restart diagnostics, and reusable paper-specific matrices.
- [Cannot Claim Yet]: absolute throughput improvement over original OAI or srsRAN without rerunning the new PAPER-10 rows against a recorded baseline.
- [Blocked Item]: physical Good/Fair/Bad coverage equivalence because RFsim does not provide RSRP/location evidence in the current validated flow.
