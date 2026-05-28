# 2026-05-28 Evaluation Recovery And iperf Panel

## Work Completed
- [DL Gap Diagnosis]: documented why PAPER-07 DL `141 Mbps` did not repeat in PAPER-11.
- [Recovery Folder]: created `redcap_doc/evluation_recover/` using the user-requested spelling.
- [Moved Step-by-Step Docs]:
  - `paper07_tdd_reproduction_step_by_step.md`.
  - `paper07_tdd_reproduction_2026-05-23_report.md`.
  - `paper07_tdd_dl_retest_report.md`.
  - `paper07_ul_peak_rate_test_report.md`.
  - `paper10_multiue_software_throughput_reproduction_2026-05-26_report.md`.
- [PAPER-11 Manual]: added `paper11_real_network_reproduction_step_by_step.md`.
- [Menu Integration]: added PAPER-07 bundle, PAPER-11 panel bundle, standalone panel, and recover-doc list to `redcap_runtime_menu.sh`.
- [Alias]: added `redcap_interface/mmtc.ment.bash` as compatibility launcher.
- [Live Panel]: added `redcap_interface/iperf_live_panel.py` with `--forceflush` interval updates.

## Validation
- [Shell Syntax]: passed for updated shell/menu scripts.
- [Python Compile]: passed for `iperf_live_panel.py`.
- [Standalone Panel Smoke]: `1M/1M`, `5 s`, UL `0.988 Mbps`, DL `1.000 Mbps`, `0%` loss.
- [PAPER-11 Wrapper Smoke]: `P11_PANEL=1`, `1M/1M`, `3 s`, live panel displayed interval rows.

## Key Diagnosis
- [PAPER-07]: peak-rate profile, `PDSCH256QAM=1`, DLSCH `MCS (1) 27`, `60 s`, single UE.
- [PAPER-11]: service-gate profile, existing container state, short run, no peak-rate MCS evidence in the first run.
- [Runtime YAML Evidence]: current UE1 config showed `pusch_256qam: 0` and `pdsch_256qam: 0`.
- [PAPER-10]: `144.675 Mbps` was aggregate multi-UE DL with high loss, not a single-UE clean `141 Mbps`.
