# RedCap Test Log Curated Summary

## Cleanup Scope
- Approved target folders:
  - `test_log/build_logs`
  - `test_log/compiler_logs`
  - `test_log/report`
  - `test_log/runtime_artifacts`
  - `test_log/runtime_bins`
  - `test_log/runtime_configs`
  - `test_log/runtime_libs`
- Before cleanup, the target scope contained:
  - `36119` `.log` files
  - `28` `.logs` files
  - `96` `.md` files
  - `73` `.yaml` files
  - `11` `.yml` files
  - `2` `.sql` files
  - one generated binary without extension
- After promotion, the target scope has no remaining files.

## Promoted Library Counts
| Library | Count | Meaning |
|---|---:|---|
| `library_cn5g/` (historical) | 6 | At the time of promotion: README plus CN5G static backup, 50/64 UE SQL seeds, and Compose overrides; removed with explicit approval on 2026-07-15 |
| `library_gnb_config/` | 6 | README plus five reusable gNB runtime configs |
| `library_runtime_probe/` | 24 | README, Paper 07 raw evidence, RedCap/non-RedCap probe, and FlexRIC plugin symlinks |
| `library_build_evidence/` | 3 | README plus retained 256QAM build/rebuild evidence |
| `library_reports_summary/` | 27 | README plus curated M3-M7 reports, latency RCA, and this summary |

## High-Value Results Kept
| Area | Result | Where To Read |
|---|---|---|
| Paper 07 106PRB UL | 35.0 Mbits/sec receiver, 0% UDP loss, avg ping 3.904 ms | `library_runtime_probe/paper07_tdd_ul_iperf_106prb_final.log` |
| Paper 07 51PRB UL | 35.0 Mbits/sec receiver, 0% UDP loss, avg ping 2.795 ms | `library_runtime_probe/paper07_tdd_ul_iperf_51prb_final.log` |
| Paper 07 256QAM attempt | UE capability marker present, but gNB UL stats remained `Qm 2` | `library_runtime_probe/paper07_tdd_gnb_256qam_final.log` |
| Paper 07 DL menu run | 141 Mbits/sec receiver, 0.061% UDP loss | `library_runtime_probe/paper07_tdd_dl_iperf_menu_final.log` |
| M5 accepted scaling point | 56/56 UE attach, PDU, tunnel, and forward ping PASS | `m5_caseb_56ue_static_cn_pass_report.md` |
| M5 upper boundary | 64 UE run classified as gNB runtime SIGKILL/restart threshold | `m5_caseb_64ue_static_cn_threshold_report.md` |
| Latency RCA | 50 UE pass, RTT avg 808 ms, p95 1099 ms, TCP UL 20 Mbps | `redcap_mmtc_latency_rca_latest.md` |

## Deleted As Low Value
- Duplicate timestamped runtime/compiler/build logs already captured by promoted reports.
- Runtime artifact folders containing raw Docker logs for superseded M3/M5 runs.
- Repeated `redcap_runtime_host_summary_*` reports where final reports already summarize the outcome.
- Generated xApp binary under `test_log/runtime_bins`; source remains in `ci-scripts/redcap_ul_prb_ctrl_xapp.c`.
- Old timestamped runtime configs after final reusable configs were promoted.

## Current Lookup Rule
- Start at `redcap_library/README.md`.
- Use the target subfolder README next.
- Only open raw `.log` files when a report's summarized metric needs verification.
- New generated logs remain under `test_log/` until explicitly promoted.
