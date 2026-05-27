# PAPER-08 Fig.9 UDP SNR Sweep Report

## Scope
- [Paper Anchor]: PAPER-08 Fig. 9 UDP DL data rate vs SNR.
- [Method]: RFsim channelmod proxy for PAPER-08 Fig.9 UDP downlink data-rate measurement.
- [Plotting]: Paper07-style CSV to matplotlib PNG/PDF workflow.
- [Guardrail]: `target_snr_proxy_db` is mapped to RFsim `noise_power_dB`; it is not calibrated instrument SNR.
- [CSV]: `analysis/data/paper08_fig9_udp_snr_combined_2026-05-27_16-03-00.csv`.
- [PNG]: `analysis/plots/paper08_fig9_udp_snr_combined_2026-05-27_16-03-00.png`.
- [PDF]: `analysis/plots/paper08_fig9_udp_snr_combined_2026-05-27_16-03-00.pdf`.

## Result Summary
- [Completed Rows]: 22.
- [Blocked/Failed Rows]: 2.
- [Blocked Channel Models]: 3.

| Channel Model | Best Receiver Mbps | Worst Receiver Mbps | Mean Loss % |
|---|---:|---:|---:|
| AWGN | 92.015 | 91.239 | 0.218 |
| Rayleigh1 | 91.407 | 91.029 | 0.183 |
| Rayleigh8 | 89.014 | 86.724 | 0.146 |
| Rice1 | 91.386 | 91.102 | 0.175 |
| Rice8 | 90.832 | 87.493 | 0.205 |
| TDL_A | 52.845 | 42.846 | 0.584 |

## Failed Measurement Rows
| Channel Model | SNR Proxy dB | noise_power_dB | Return Code | Note |
|---|---:|---:|---:|---|
| Rayleigh8 | 10 | -50 | 124 | RFsim noise/channel proxy, not calibrated PAPER-08 channel-emulator SNR |
| Rayleigh8 | 0 | -40 | 124 | RFsim noise/channel proxy, not calibrated PAPER-08 channel-emulator SNR |

## Blocked Channel Models
| Channel Model | Stage | Status | Evidence | Note |
|---|---|---|---|---|
| Rayleigh8 | measurement_sweep | partial | `analysis/data/paper08_fig9_udp_snr_Rayleigh8_2026-05-27_10-41-37.csv` | lower SNR proxy rows timed out at iperf return code 124 |
| Rayleigh1_corr | smoke_setup | blocked | `test_log/compiler_logs/mmtc_smoke_2026-05-27_10-52-16_ue1_state.log` | UE attach and oaitun_ue1 did not become ready |
| Rayleigh1_anticorr | smoke_setup | blocked | `test_log/compiler_logs/mmtc_smoke_2026-05-27_10-53-30_ue1_state.log` | UE attach and oaitun_ue1 did not become ready |

## TDL_A Startup Fix
- [Resolved Issue]: TDL_A initially blocked at smoke setup because RFsim UE could not complete cell search and tunnel setup.
- [Root Cause]: the mMTC entrypoint used `ds_tdl=0.030`, matching NR sim comments for "30 ns", but RFsim passes `sampling_rate` in Hz to `new_channel_desc_scm()`. That made the configured delay spread too large for the RFsim channel path.
- [Fix]: default TDL delay spread in the mMTC UE entrypoint and batch runner is now `0.00000003` for TDL_A / TDL_D / TDL_E, `0.00000010` for TDL_B, and `0.00000030` for TDL_C.
- [Guard]: `tdlModel()` now asserts that computed `channel_length` stays in the `uint8_t` storage range, preventing silent overflow for invalid delay-spread settings.
- [Evidence]: `mmtc_smoke_2026-05-27_16-07-00` passed with `attach=1`, `pdu=1`, `tun=1`, `forward_ping_ok=1`, `gnb_restart=0`, `failures=0`.

## Interpretation
- [Comparable]: this run exercises continuous UDP downlink traffic while sweeping RFsim noise/channel models.
- [Not Directly Comparable]: PAPER-08 used a hardware channel emulator and measured calibrated SNR at the UE.
- [Needs Verification]: exact MCS pinning is not yet equivalent to the radio communication tester setup in PAPER-08.
