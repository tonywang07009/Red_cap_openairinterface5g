# Evaluation Reproduction Recovery Manuals

## Purpose
- [Scope]: stable step-by-step reproduction procedures for evaluation papers.
- [Folder Name]: `evluation_recover` keeps the user-requested spelling.
- [Usage]: start here before running a paper reproduction demo.

## Inventory
| File | Scope |
|---|---|
| `paper07_tdd_reproduction_step_by_step.md` | PAPER-07 TDD UL/DL 256QAM peak-rate reproduction procedure |
| `paper07_ul_peak_rate_test_report.md` | PAPER-07 UL peak-rate and true PUSCH 256QAM verification report |
| `paper07_tdd_dl_retest_report.md` | PAPER-07 DL reverse iperf and PDSCH 256QAM retest report |
| `paper07_tdd_reproduction_2026-05-23_report.md` | PAPER-07 final TDD reproduction report |
| `paper10_multiue_software_throughput_reproduction_2026-05-26_report.md` | PAPER-10 multi-UE software-throughput reproduction report |
| `paper11_real_network_reproduction_step_by_step.md` | PAPER-11 real-network RedCap service-gate reproduction procedure |
| `paper11_table3_2p1g_peak_rate_step_by_step.md` | PAPER-11 Table 3 2.1G RedCap target-rate proxy reproduction procedure |
| `paper11_dl_gap_diagnosis.md` | Diagnosis for why PAPER-07 DL `141 Mbps` did not repeat in PAPER-11 |

## Demo Entry Points
```bash
bash redcap_interface/mmtc.menu.bash
bash redcap_interface/mmtc.ment.bash
```

- [PAPER-07]: choose menu option `16`.
- [PAPER-11]: choose menu option `17`.
- [Standalone iperf Panel]: choose menu option `18`.
- [PAPER-11 Table 3]: choose menu option `20`.
