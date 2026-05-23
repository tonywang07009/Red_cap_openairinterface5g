# PAPER-07 TDD Reproduction Report - Full-Carrier 51PRB

## Objective
- Convert the separate 51PRB YAML from BWP-only semantics to full-carrier 51PRB semantics.
- Keep the original 106PRB YAML clean.
- Add runtime menu support for switching 106PRB and 51PRB profiles.
- Rerun PAPER-07 TDD UL/DL.

## Configuration Summary
| Item | 106PRB Profile | Full 51PRB Profile |
|---|---:|---:|
| gNB YAML | `gnb.sa.band78.fr1.106PRB.usrpb210.redcap.yaml` | `gnb.sa.band78.fr1.51PRB.usrpb210.redcap.yaml` |
| `bwpSize` | 106 | 51 |
| `dl_carrierBandwidth` | 106 | 51 |
| `ul_carrierBandwidth` | 106 | 51 |
| `dl_absoluteFrequencyPointA` | 640752 | 640564 |
| `initialDLBWPcontrolResourceSetZero` | 10 | 12 |
| UE `-r` | 106 | 51 |
| UE `-C` | 3630360000 | 3617640000 |
| UE `--ssb` | 144 | 238 |

## Results
| Direction | PAPER-07 Target | Offered Rate | Measured Throughput | Jitter | Loss | Status |
|---|---:|---:|---:|---:|---:|---|
| UL | about 34 Mbps | 35 Mbps | 35.0 Mbps | 0.380 ms | 0/181282 (0%) | PASS |
| DL | about 140 Mbps | 141 Mbps | 141 Mbps | 0.025 ms | 410/731293 (0.056%) | PASS |

## Runtime Evidence
- Smoke run:
  - `mmtc_smoke_2026-05-23_16-28-19`
- Smoke summary:
  - `attach=1 pdu=1 tun=1 forward_ping_ok=1 iperf_ul_ok=1 gnb_restart=0 failures=0`
- gNB container confirmed:
  - `dl_carrierBandwidth: 51`
  - `ul_carrierBandwidth: 51`
  - `dl_absoluteFrequencyPointA: 640564`
- UE container confirmed:
  - `-r 51`
  - `-C 3617640000`
  - `--ssb 238`

## Menu Update
- Main runtime menu:
  - `ci-scripts/redcap_runtime_menu.sh`
- Wrapper:
  - `ci-scripts/mmtc.menu.bash`
- New actions:
  - `13) Select 106PRB carrier profile`
  - `14) Select 51PRB full-carrier profile`

## Conclusion
- Full-carrier 51PRB now matches PAPER-07 51PRB semantics more closely than the earlier BWP-only run.
- With synchronized gNB/UE RF parameters, PAPER-07 TDD UL/DL offered-rate reproduction passes.

## Evidence Files
- CSV: `agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/analysis/data/paper07_tdd_reproduction_full51prb_2026-05-23.csv`
- Process log: `agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/analysis/data/paper07_tdd_reproduction_full51prb_2026-05-23_process_log.md`
- UL iperf: `test_log/compiler_logs/mmtc_smoke_2026-05-23_16-28-19_ue1_iperf3_ul.log`
