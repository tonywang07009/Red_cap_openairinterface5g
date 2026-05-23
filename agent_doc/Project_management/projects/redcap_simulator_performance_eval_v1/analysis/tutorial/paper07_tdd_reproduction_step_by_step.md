# PAPER-07 TDD Reproduction Step-by-Step Manual

## 0. Scope
- [Paper]: `evaluation_paper/RedCap_Performance_Analysis_and_Deployment_Strategy_Research.pdf`
- [Experiment]: TDD 20MHz 256QAM peak-rate reproduction.
- [Paper Target]: UL `34 Mbps`, DL `140 Mbps`.
- [Simulator]: OAI RFsim RedCap TDD n78 scenario.
- [Output Folder]: `agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/analysis/`
- [Not Covered]: FDD UL/DL. The current runnable scenario is TDD.

## 1. Read The Minimum Context
Run from repo root:

```bash
pwd
```

Expected repo root:

```text
/home/tonywang/OAI/Red_cap_openairinterface5g
```

Read only the active project context:

```bash
sed -n '1,140p' agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/project_plan.md
sed -n '1,140p' agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/agent_rules.md
```

## 2. Confirm The Paper Target
Use `pdftotext` to extract the relevant paper pages:

```bash
pdftotext -layout -f 3 -l 4 evaluation_paper/RedCap_Performance_Analysis_and_Deployment_Strategy_Research.pdf -
```

Expected paper evidence:

```text
TDD 20MHz (256QAM), 1T2R, UL 34 Mbps, DL 140 Mbps
```

Important interpretation:
- Use UL `34 Mbps` as the paper target.
- Use DL `140 Mbps` as the paper target.
- Use throughput plus gNB MAC evidence. Do not accept Mbps alone as proof of 256QAM.

## 3. Prepare Runtime Parameters
Use these experimental factors:

| Factor | Value | Reason |
|---|---|---|
| Duplex | TDD | Current RFsim scenario is TDD n78 |
| Modulation | 256QAM | Matches paper row |
| Measured UE | UE1 | Single-user peak-rate reproduction |
| Total UE services | 29 | Existing smoke script requires `MMTC_TOTAL_UES > 28` |
| UL offered rate | `35M` | Slightly above paper UL target `34 Mbps` |
| DL offered rate | `141M` | Slightly above paper DL target `140 Mbps` |
| Duration | `60s` | Stable full-buffer measurement |
| PUSCH 256QAM | enabled | Required for UL `Qm 8` |
| PDSCH 256QAM | enabled | Required for DL `MCS (1)` |

Rate unit rule:
- Use `35M`, not `35`.
- In `iperf3`, `-b 35` means roughly 35 bits/sec, not 35 Mbps.
- A bad unitless run is easy to identify because the final iperf summary will show only about one datagram over 60 seconds.

Runtime menu shortcut:
- Run `ci-scripts/redcap_runtime_menu.sh`.
- Choose `8) Enable PAPER-07 256QAM profile` to set:
  - `PUSCH256QAM=1`
  - `PDSCH256QAM=1`
  - `iperf rate=35M`
  - `DL iperf rate=141M`
  - `duration=60s`
- Choose `7) Configure 256QAM capability` for manual UL/DL capability switching.
- Choose `3) Run UDP uplink iperf with current rate` after enabling the profile.
- Choose `9) Enable PAPER-07 DL 64QAM profile` for DL 64QAM-level testing:
  - `PDSCH256QAM=0`
  - `DL iperf rate=106M`
- Choose `10) Enable PAPER-07 DL 256QAM profile` for true DL 256QAM testing:
  - `PDSCH256QAM=1`
  - `DL iperf rate=141M`
- After changing `PDSCH256QAM`, choose `2` or `3` to restart/apply the UE capability before running DL iperf.
- Choose `11) Run UDP downlink iperf with current DL rate` for DL reverse iperf.
- Choose `12) Run UDP downlink iperf with custom DL rate` for a one-off DL rate and duration, equivalent to the UL custom option.

## 4. Start RFsim And Run UL 35M
This command restarts the Docker RFsim/CN scenario.

```bash
MMTC_TOTAL_UES=29 \
MMTC_SAMPLE_UES=1 \
MMTC_IPERF_SAMPLE_UES=1 \
MMTC_IPERF_ENABLE=1 \
MMTC_IPERF_UDP=1 \
MMTC_IPERF_RATE=35M \
MMTC_IPERF_DURATION=60 \
MMTC_FORWARD_PING_MODE=parallel \
MMTC_RUN_REVERSE_PING=0 \
MMTC_PING_COUNT=10 \
MMTC_GNB_WARMUP=5 \
MMTC_SLEEP_AFTER_UP=25 \
MMTC_UE_START_GAP=0 \
MMTC_PUCCH_COMMON_FALLBACK_BWP0=1 \
MMTC_PUSCH_256QAM=1 \
MMTC_PDSCH_256QAM=1 \
ci-scripts/redcap_mmtc_smoke_validation.sh
```

Expected health summary:

```text
[SUMMARY] sample=1 running=1 attach=1 pdu=1 tun=1 forward_ping_ok=1 reverse_ping_ok=0 iperf_ul_ok=1 iperf_ul_run=1 gnb_restart=0 failures=0 mode=parallel
```

Pass gate:
- `attach=1`
- `pdu=1`
- `tun=1`
- `iperf_ul_ok=1`
- `gnb_restart=0`
- `failures=0`

## 5. Confirm UE Runtime Capability
After the smoke command completes:

```bash
docker exec rfsim5g-oai-nr-ue1_redcap cat /tmp/nr-ue-mmtc.yaml
```

Expected fields:

```yaml
nrue_recap:
  support_of_redcap_r17: 1
  number_of_rx_redcap_r17: 1
  half_duplex_fdd_type_a_redcap_r17: 1
  pusch_256qam: 1
  pdsch_256qam: 1
```

Check UE log:

```bash
rg -n "PUSCH256QAM|PDSCH256QAM|Built UE NR capability" test_log/compiler_logs/mmtc_smoke_*_ue1_docker.log
```

Expected evidence:

```text
PUSCH256QAM=1 PDSCH256QAM=1
Built UE NR capability from nrue_recap YAML
```

## 6. Record UL Result
Find the newest UE1 UL iperf log:

```bash
ls -t test_log/compiler_logs/mmtc_smoke_*_ue1_iperf3_ul.log | head -n 1
```

Expected final lines:

```text
[  5]   0.00-60.00  sec   250 MBytes  35.0 Mbits/sec  0.000 ms  0/181282 (0%)  sender
[  5]   0.00-60.04  sec   250 MBytes  35.0 Mbits/sec  0.392 ms  0/181282 (0%)  receiver
```

Record these fields:
- sender throughput
- receiver throughput
- jitter
- lost datagrams
- total datagrams
- loss percentage

## 7. Capture UL gNB Evidence
While UL iperf is running, or immediately after a manual UL rerun, sample gNB MAC stats:

```bash
docker exec rfsim5g-oai-gnb_redcap sh -c 'tail -n 100 /opt/oai-gnb/nrMAC_stats.log | grep -E "ulsch_rounds|MCS|Qm|NPRB|SNR"'
```

Required UL evidence:

```text
MCS (1) 27 (Qm 8 ... ) NPRB 106
```

Interpretation:
- `MCS (1)` means 256QAM MCS table was selected.
- `Qm 8` is direct UL modulation-order evidence.
- `NPRB 106` shows the active UL scheduling resource allocation in this RFsim runtime.

## 8. Run DL 141M Reverse iperf
Menu path:
- In `ci-scripts/redcap_runtime_menu.sh`, choose `10` for the DL 256QAM profile.
- Choose `2` to restart/apply UE capability without UL iperf, or choose `3` if an UL check is also desired.
- Choose `11` to run DL reverse iperf with the current DL rate.
- Choose `12` if a custom DL rate or shorter validation duration is needed.

64QAM-level menu path:
- Choose `9` for the DL 64QAM profile.
- Choose `2` to restart/apply `PDSCH256QAM=0`.
- Choose `11` to run DL reverse iperf at `106M`.
- Choose `12` to manually test another DL 64QAM-level rate.

Manual command path:

Restart the ext-dn iperf server:

```bash
docker exec oai-ext-dn sh -c 'pids=$(pidof iperf3 2>/dev/null || true); [ -z "$pids" ] || kill $pids; iperf3 -s -D'
```

Run DL reverse iperf from UE:

```bash
docker exec rfsim5g-oai-nr-ue1_redcap iperf3 -c 192.168.72.135 -B 10.0.0.2 -t 60 -u -b 141M -R
```

Again, keep the unit suffix. `141M` means 141 Mbps; `141` would mean bits/sec scale.

Expected final lines:

```text
[  5]   0.00-60.09  sec  1010 MBytes   141 Mbits/sec  0.000 ms  0/0 (0%)  sender
[  5]   0.00-60.00  sec  1009 MBytes   141 Mbits/sec  0.039 ms  436/731378 (0.06%)  receiver
```

## 9. Capture DL gNB Evidence
During DL iperf, sample gNB MAC stats:

```bash
docker exec rfsim5g-oai-gnb_redcap sh -c 'tail -n 100 /opt/oai-gnb/nrMAC_stats.log | grep -E "dlsch_rounds|MCS|UE"'
```

Required DL evidence:

```text
dlsch_rounds ... MCS (1) 27
```

Interpretation:
- DL stats in this runtime expose the MCS table as `MCS (1)`.
- Unlike UL, the DL stats do not print `Qm`.
- For this experiment, DLSCH `MCS (1)` is the DL 256QAM table evidence.

## 10. Write CSV
Create or update:

```text
agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/analysis/data/paper07_tdd_reproduction_YYYY-MM-DD.csv
```

Required columns:

```text
timestamp,run_id,paper_file,duplex,bwp_mhz,modulation,traffic_direction,offered_rate_mbps,paper_target_mbps,receiver_mbps,sender_mbps,jitter_ms,udp_loss_percent,lost_datagrams,total_datagrams,ping_loss_percent,rtt_avg_ms,pusch_256qam,pdsch_256qam,observed_mcs_table,observed_mcs_index,observed_qm,observed_nprb,observed_snr_db,gnb_restart_count,verdict,evidence
```

Example rows from 2026-05-23:

```text
UL: paper target 34 Mbps, receiver 35.0 Mbps, jitter 0.392 ms, loss 0%, MCS (1), Qm 8
DL: paper target 140 Mbps, receiver 141.0 Mbps, jitter 0.039 ms, loss 0.06%, MCS (1)
```

## 11. Generate Plot
Use the existing plotting script:

```bash
python3 agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/analysis/scripts/p7_tdd_reproduction_20260523_plot.py
```

Expected outputs:

```text
agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/analysis/plots/paper07_tdd_reproduction_2026-05-23.png
agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/analysis/plots/paper07_tdd_reproduction_2026-05-23.pdf
```

Note:
- If matplotlib reports that `~/.config/matplotlib` is not writable and uses `/tmp`, this is non-fatal.
- The plot is valid if the PNG/PDF files are generated.

## 12. Write Final Report
Create or update:

```text
agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/analysis/paper07_tdd_reproduction_YYYY-MM-DD_report.md
```

Report must include:
- paper source
- target table/values
- factors and parameter settings
- step-by-step execution
- health summary
- UL result
- DL result
- gNB MAC evidence
- artifact paths
- limitations
- conclusion

## 13. Validate Files
Run:

```bash
git diff --check -- \
  agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/analysis/tutorial/paper07_tdd_reproduction_step_by_step.md \
  agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/analysis/tutorial/README.md
```

Expected:

```text
no output
```

## 14. Pass/Fail Criteria
| Check | Pass Condition |
|---|---|
| Runtime health | `failures=0`, `gnb_restart=0` |
| UE capability | `pusch_256qam: 1`, `pdsch_256qam: 1` |
| UL throughput | receiver throughput >= `34 Mbps` |
| UL 256QAM evidence | `MCS (1)` and `Qm 8` |
| DL throughput | receiver throughput >= `140 Mbps` |
| DL 256QAM evidence | DLSCH `MCS (1)` |
| Plot generation | PNG and PDF generated |

## 15. Known Limitations
- This procedure validates the TDD portion only.
- The paper also lists FDD 20MHz 256QAM targets: UL `120 Mbps`, DL `226 Mbps`.
- RFsim does not reproduce paper base-station power, UE power, distance, or field-channel conditions exactly.
- The current runtime uses `N_RB_DL=106`, while the paper row is a 20MHz target-rate row.
- This is a target-rate and scheduler-evidence reproduction, not a one-to-one RF channel reproduction.
