# PAPER-07 QAM-Observed UL Retest

## Status
- [Completed]
- Paper: `redcap_doc/evaluation_papers/paper_07Research_on_5G_RedCap_Standard_and_Key_Technologies.pdf`
- Paper evidence: PDF page 4, Table IV, RedCap uplink peak-rate test.
- Retest goal: distinguish actual [64QAM] versus [256QAM] using gNB MAC stats, not only offered UDP rate.

## Measurement Method
- Reused the active healthy RFsim containers.
- UE: `rfsim5g-oai-nr-ue1_redcap`, source IP `10.0.0.2`.
- Server: `oai-ext-dn`, target IP `192.168.72.135`.
- Traffic: UDP UL iperf3, 60 seconds per point.
- QAM evidence: sampled `rfsim5g-oai-gnb_redcap:/opt/oai-gnb/nrMAC_stats.log` during iperf.

## Code Evidence
- `doc/MAC/mac-usage.md`: scheduler stats define `MCS (Q) M`, where `Q=0` is the 64QAM table and `Q=1` is the 256QAM table.
- `doc/MAC/mac-usage.md`: `Qm 6` maps to 64QAM and `Qm 8` maps to 256QAM.
- `openair2/LAYER2/NR_MAC_COMMON/nr_mac_common.c`: `nr_get_Qm_ul()` maps UL MCS table/index to Qm.
- `openair2/LAYER2/NR_MAC_gNB/nr_radio_config.c`: `set_ul_mcs_table()` only selects PUSCH `qam256` when UE capability exposes `pusch_256QAM` support.

## Result Table
| Run | Paper point | Expected Qm/table | Observed Qm/table/MCS | Receiver Mbps | Jitter ms | UDP Loss % | Verdict |
|---|---|---:|---:|---:|---:|---:|---|
| PAPER07-QAM-64-OBSERVED | 64QAM | Qm 6 / table 0 | Qm 6 / table 0 / MCS 28 | 26.0 | 0.562 | 0.0 | MATCH_64QAM |
| PAPER07-QAM-256-OBSERVED | 256QAM | Qm 8 / table 1 | Qm 6 / table 0 / MCS 28 | 35.0 | 0.670 | 0.0 | MISMATCH_EXPECTED_256QAM |

## Outputs
- CSV: `analysis/data/paper07_qam_observed_retest.csv`
- PNG: `analysis/plots/paper07_qam_observed_retest.png`
- PDF: `analysis/plots/paper07_qam_observed_retest.pdf`

## Interpretation
- The 26M point matched [64QAM] behavior: gNB reported `MCS (0) 28` and `Qm 6`.
- The 35M point did not match [256QAM] behavior: gNB still reported `MCS (0) 28` and `Qm 6`.
- Therefore the current active RFsim scenario can reproduce PAPER-07 UL target throughput, but it did not exercise true 256QAM uplink.
- To run a true 256QAM retest, the platform needs a clean restart with UE capability/PUSCH configuration enabling `mcs_Table=qam256`, then MAC stats must show `MCS (1)` and `Qm 8` during traffic.
