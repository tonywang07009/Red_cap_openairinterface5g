# 2026-05-27 PAPER-11 Research Real-Network RedCap Reproduction

## Work Completed
- [MinerU Cache]: parsed the new `Research...pdf` into Markdown and updated the scan route.
- [Paper README]: added `PAPER-11` to `redcap_doc/evaluation_papers/README.md`.
- [Literature Index]: added `PAPER-11` and created the extraction note.
- [Validation Matrix]: added PAPER-11 application-gate, CQT-proxy, and live-iperf rows.
- [Live Demo Script]: added `redcap_interface/paper11_iperf_live_demo.sh`.
- [Experiment]: ran four RFsim UE1 iperf/ping rows:
  - [Industrial]: `2M/2M`.
  - [Video High-End]: `17M/25M`.
  - [Wearable]: `5M/50M`.
  - [Paper Far Gate]: `17M/68M`.

## Evidence
- [Report]: `agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/analysis/paper11_real_network_proxy_reproduction_2026-05-27_report.md`.
- [Combined CSV]: `agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/analysis/data/paper11_live_iperf_summary_2026-05-27.csv`.
- [Raw Logs]: `agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/analysis/data/paper11_live_iperf_raw/`.

## Result
- [PASS]: visible iperf traffic process and raw evidence generation.
- [PASS]: high-end video application gate.
- [PASS_WITH_GAP]: industrial gate because the 1500-byte ping row measured `105.556 ms`, slightly above the strict `<100 ms` gate.
- [PASS_WITH_GAP]: wearable gate because DL reached `30.3 Mbps`, inside the `5-50 Mbps` reference range but below the top `50 Mbps` offered target.
- [PASS_WITH_GAP]: PAPER-11 far-gate row because UL matched `17 Mbps`, but DL reached `32.7 Mbps` rather than the paper's `68 Mbps`.

## Remaining Gap
- [CQT / Coverage]: near/middle/far physical site positions are still [Not Directly Comparable] without a calibrated RFsim channel-to-RSRP/SINR mapping.
- [Power]: paper UE current in mA is still [Not Directly Comparable] without external power instrumentation or a verified power model.
