# Runtime Probe Library

## Contents
| Group | Files | Role |
|---|---|---|
| Paper 07 UL 106PRB | `paper07_tdd_*_106prb_final.log` | Baseline TDD UL evidence |
| Paper 07 UL 51PRB | `paper07_tdd_*_51prb_final.log` | Paper-aligned 51PRB TDD UL evidence |
| Paper 07 256QAM attempt | `paper07_tdd_*_256qam_final.log` | UE capability marker plus gNB scheduler evidence |
| Paper 07 DL menu run | `paper07_tdd_dl_iperf_menu_final.log` | DL UDP iperf menu evidence |
| RedCap vs non-RedCap probe | `redcap_vs_nonredcap_*_final.*` | Live probe output and compose override |
| FlexRIC service models | `flexric_service_models/lib*_sm.so` | Runtime plugin symlinks/libraries used by control xApp scripts |

## Current Interpretation
- 106PRB and 51PRB UL tests both reached 35.0 Mbits/sec receiver throughput with 0% UDP loss.
- The 256QAM UE capability marker was present, but gNB runtime stats still showed UL `Qm 2`; treat this as a simulator capability/config debug item, not as proof of true 256QAM modulation.
- DL menu evidence reached 141 Mbits/sec receiver throughput with 0.061% UDP loss.

## Usage
- Use these logs as retained raw evidence for current reports.
- Do not place every new runtime log here. Keep timestamped new runs in `test_log/compiler_logs/` until they are promoted.
