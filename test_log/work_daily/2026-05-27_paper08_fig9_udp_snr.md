# 2026-05-27 PAPER-08 Fig.9 UDP SNR-Proxy Reproduction

## Scope
- [Paper Anchor]: `paper_Empirical_Comparison_of_Power_Consumption_and_Data_Rates_for_5G_New_Radio_and_RedCap_Devices.pdf`.
- [Target Figure]: Fig.9 UDP downlink data rate vs SNR.
- [Method]: OAI RFsim channelmod proxy with UDP DL iperf3 reverse mode.
- [Guardrail]: `target_snr_proxy_db` maps to RFsim `noise_power_dB`; it is not calibrated hardware-emulator SNR.

## Outputs
- [Runner]: `agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/analysis/scripts/p08_fig9_udp_snr_sweep.py`.
- [Batch Entry]: `redcap_interface/paper08_fig9_chanmod_batch.sh`.
- [Report]: `agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/analysis/paper08_fig9_udp_snr_sweep_report.md`.
- [Combined CSV]: `agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/analysis/data/paper08_fig9_udp_snr_combined_2026-05-27_10-41-37.csv`.
- [Blocked CSV]: `agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/analysis/data/paper08_fig9_udp_snr_blocked_2026-05-27_10-41-37.csv`.
- [Plot]: `agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/analysis/plots/paper08_fig9_udp_snr_combined_2026-05-27_10-41-37.png`.

## Result
- [Completed Rows]: `22`.
- [Failed Measurement Rows]: `2`, both `Rayleigh8` low-SNR proxy rows with iperf timeout code `124`.
- [Blocked Startup Models]: `Rayleigh1_corr`, `Rayleigh1_anticorr`.
- [Stable Completed Models]: `AWGN`, `Rayleigh1`, `Rice1`, and `Rice8` produced completed rows near the `90 Mbps` offered-load ceiling.
- [TDL_A Result]: all four SNR-proxy rows completed after correcting RFsim `ds_tdl` default to `0.00000003`; best receiver throughput was `52.845 Mbps`.

## Updated Outputs
- [Combined CSV]: `agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/analysis/data/paper08_fig9_udp_snr_combined_2026-05-27_16-03-00.csv`.
- [Blocked CSV]: `agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/analysis/data/paper08_fig9_udp_snr_blocked_2026-05-27_16-03-00.csv`.
- [Plot]: `agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/analysis/plots/paper08_fig9_udp_snr_combined_2026-05-27_16-03-00.png`.
- [TDL_A Smoke Evidence]: `mmtc_smoke_2026-05-27_16-07-00`, summary `attach=1 pdu=1 tun=1 forward_ping_ok=1 gnb_restart=0 failures=0`.

## Follow-Up
- [Needs Verification]: exact PAPER-08 MCS pinning is not yet equivalent to the tester-side fixed MCS setup.
- [Needs Verification]: RFsim `target_snr_proxy_db` remains a noise/path-loss proxy, not a calibrated channel-emulator SNR measurement.
