# PAPER-11 Table 3 2.1G Peak-Rate Reproduction Step By Step

## Purpose
- [Target Paper]: `Research on RedCap UE's performance indicators in real network to support iot applications`.
- [Target Table]: `Table 3: The 2.1G theoretical peak rate`.
- [Goal]: use the same execution style as [PAPER-07] to run RedCap gNB + RedCap UE throughput tests against the table's target-rate rows.
- [Run Date]: 2026-05-28.

## Paper Table 3 Targets
| Network | Bandwidth | Duplex | MIMO | UL Target | DL Target |
|---|---:|---|---|---:|---:|
| [2.1G RedCap 64QAM] | 20M | FDD | 1T2R | 90 Mbps | 169.5 Mbps |
| [2.1G RedCap 256QAM] | 20M | FDD | 1T2R | N/A | 226 Mbps |

## Local Platform Mapping
- [Paper Condition]: 2.1G, 20M, FDD, 1T2R.
- [Local RFsim Condition]: stable RedCap RFsim profile uses band 78, 51 PRB, 30 kHz SCS, TDD, RedCap UE.
- [Reason]: no stable project-owned RedCap 2.1G/FDD YAML is currently available for the same docker-compose RFsim flow.
- [Classification]: [Target-Rate Proxy], not calibrated 2.1G FDD RF reproduction.
- [Not Directly Comparable]: throughput target hit means this simulator path can sustain the Paper Table 3 offered rates under RFsim; it does not prove real 2.1G FDD RF equivalence.

## Script Entry
```bash
P11T3_PROFILE=51prb P11T3_DURATION=60 bash redcap_interface/paper11_table3_peak_reproduction.sh
```

## Optional Menu Entry
```bash
bash redcap_interface/mmtc.ment.bash
```
- Choose option `20`: [Run PAPER-11 Table 3 RedCap peak-rate proxy].

## Step-By-Step Procedure
1. [Extract Paper Target]
   - Read Paper11 Table 3.
   - Select RedCap target rows: UL 64QAM `90 Mbps`, DL 64QAM `169.5 Mbps`, DL 256QAM `226 Mbps`.

2. [Select RedCap RFsim Profile]
   - Use `P11T3_PROFILE=51prb`.
   - gNB config: `ci-scripts/conf_files/gnb.sa.band78.fr1.51PRB.usrpb210.redcap.yaml`.
   - UE runtime profile: `nrue_recap.enable=1`, `number_of_rx_redcap_r17=1`, `half_duplex_fdd_type_a_redcap_r17=1`.

3. [Start 64QAM Setup]
   - Run smoke setup with:
     - `MMTC_PUSCH_256QAM=0`.
     - `MMTC_PDSCH_256QAM=0`.
     - `MMTC_SAMPLE_UES=1`.
     - `MMTC_FORWARD_PING_MODE=parallel`.
   - Confirm:
     - UE container starts.
     - `oaitun_ue1` exists.
     - UE can ping `10.0.0.1`.
     - gNB restart count is `0`.

4. [Run UL 64QAM Target]
   - Start `iperf3` server in `oai-ext-dn`.
   - Run UDP UL from RedCap UE to ext-dn:
     - offered rate: `90M`.
     - duration: `60 s`.
   - Capture:
     - iperf sender/receiver Mbps.
     - jitter and packet loss.
     - gNB `nrMAC_stats.log`.

5. [Verify UL MAC Evidence]
   - Expected evidence:
     - `ulsch_rounds`.
     - `MCS (0) 28`.
     - `Qm 6`.
     - `BLER 0`.
   - Interpretation:
     - `Qm 6` confirms 64QAM UL scheduling.

6. [Run DL 64QAM Target]
   - Keep 64QAM setup active.
   - Run UDP reverse iperf from ext-dn to RedCap UE:
     - offered rate: `169.5M`.
     - duration: `60 s`.
   - Capture:
     - iperf receiver Mbps.
     - jitter and packet loss.
     - gNB `nrMAC_stats.log`.

7. [Verify DL 64QAM MAC Evidence]
   - Expected evidence:
     - `dlsch_rounds`.
     - `MCS (0) 28`.
     - `BLER 0`.
   - Interpretation:
     - This is the 64QAM target-rate row in the proxy setup.

8. [Restart For DL 256QAM Setup]
   - Re-run smoke setup with:
     - `MMTC_PUSCH_256QAM=0`.
     - `MMTC_PDSCH_256QAM=1`.
   - Confirm:
     - UE attach/PDU/TUN are rebuilt.
     - forward ping succeeds.
     - gNB restart count is `0`.

9. [Run DL 256QAM Target]
   - Run UDP reverse iperf:
     - offered rate: `226M`.
     - duration: `60 s`.
   - Capture:
     - iperf receiver Mbps.
     - jitter and packet loss.
     - gNB `nrMAC_stats.log`.

10. [Verify DL 256QAM MAC Evidence]
    - Expected evidence:
      - `dlsch_rounds`.
      - `MCS (1) 27`.
      - `BLER 0`.
    - Interpretation:
      - `MCS (1)` confirms PDSCH 256QAM table usage in this OAI run.

11. [Parse And Classify]
    - Store one summary CSV per run.
    - Classify each row:
      - [PASS]: receiver Mbps >= paper target.
      - [PASS_WITH_GAP]: receiver Mbps is slightly below target or the run is a proxy with known comparability limitation.
      - [FAIL]: missing receiver metric or unstable attach/tunnel.

## 2026-05-28 Run Result
| Test ID | Direction | Modulation | Offered | Paper Target | Receiver | Jitter | Loss | Status |
|---|---|---|---:|---:|---:|---:|---:|---|
| `P11-T3-UL-64QAM-90M` | UL | 64QAM | 90M | 90 Mbps | 89.9 Mbps | 0.165 ms | 0% | PASS_WITH_GAP |
| `P11-T3-DL-64QAM-169M5` | DL | 64QAM | 169.5M | 169.5 Mbps | 170 Mbps | 0.035 ms | 0.053% | PASS |
| `P11-T3-DL-256QAM-226M` | DL | 256QAM | 226M | 226 Mbps | 226 Mbps | 0.034 ms | 0.058% | PASS |

## MAC Evidence Snapshot
| Test ID | Evidence |
|---|---|
| `P11-T3-UL-64QAM-90M` | `ulsch_rounds 39981/0/0/0`, `MCS (0) 28`, `Qm 6`, `NPRB 18`, `SNR 51.0 dB` |
| `P11-T3-DL-64QAM-169M5` | `dlsch_rounds 66503/0/0/0`, `dlsch_errors 0`, `BLER 0.00000`, `MCS (0) 28` |
| `P11-T3-DL-256QAM-226M` | `dlsch_rounds 44497/0/0/0`, `dlsch_errors 0`, `BLER 0.00000`, `MCS (1) 27` |

## Evidence Paths
- [Runner]: `redcap_interface/paper11_table3_peak_reproduction.sh`.
- [Summary CSV]: `agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/analysis/data/paper11_table3_raw/paper11_table3_2026-05-28_10-40/paper11_table3_2026-05-28_10-40_summary.csv`.
- [Raw Logs Directory]: `agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/analysis/data/paper11_table3_raw/paper11_table3_2026-05-28_10-40/`.
- [64QAM UE Runtime YAML]: `paper11_table3_2026-05-28_10-40_64qam_ue_runtime_yaml.log`.
- [DL 256QAM UE Runtime YAML]: `paper11_table3_2026-05-28_10-40_dl256qam_ue_runtime_yaml.log`.
- [MAC Logs]: `*_mac.log`.
- [iperf Logs]: `*_iperf.log`.

## Key Limitations
- [2.1G FDD Gap]: this run uses band 78 TDD RFsim, not the paper's 2.1G FDD physical setup.
- [MIMO Gap]: local RFsim RedCap UE is configured as a simulator UE; it does not reproduce commercial UE RF-chain behavior.
- [Channel Gap]: RFsim channel is deterministic enough to hit offered rates; real-network fading, scheduler load, and core-network congestion are not reproduced.
- [Paper Evidence Needs Verification]: if a stable 2.1G FDD RedCap YAML is later added, this same script should be rerun with that profile before claiming full Paper Table 3 reproduction.
