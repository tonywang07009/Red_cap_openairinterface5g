# PAPER-10 Multi-UE Software Throughput Reproduction Report

## Scope
- [Paper]: `paper_Performance Analysis and Comparison of.pdf`.
- [Target Scenario]: PAPER-10 multi-UE data-rate assessment, good-location proxy, 3 UEs.
- [Local Run ID]: `paper10_multiue_2026-05-26_17-26-35`.
- [Raw Evidence]: `analysis/data/paper10_multiue_raw/paper10_multiue_2026-05-26_17-26-35/`.
- [Result CSV]: `analysis/data/paper10_multiue_raw/paper10_multiue_2026-05-26_17-26-35/paper10_multiue_2026-05-26_17-26-35_results.csv`.

## Paper Method Mapping
| Item | PAPER-10 Target | Local RFsim Run | Status |
|---|---|---|---|
| [RAN Software] | OAI-RAN and srsRAN comparison | OAI-RAN only | [PASS_WITH_GAP] |
| [5GC] | Open5GS v2.7.0 fixed 5GC | OAI CN5G container stack | [Needs Verification] |
| [Band] | n78 | n78 | [PASS] |
| [Bandwidth] | 40 MHz | 106 PRB at 30 kHz SCS, about 40 MHz | [PASS] |
| [SCS] | 30 kHz | 30 kHz | [PASS] |
| [TDD Pattern] | `DDDDDDFUUU` | gNB config uses `nrofDownlinkSlots=7`, `nrofDownlinkSymbols=6`, `nrofUplinkSlots=2`, `nrofUplinkSymbols=4` | [PASS_WITH_GAP] |
| [UE Type] | COTS phone + Quectel modems | OAI nrUE containers, `MMTC_REDCAP_ENABLE=0` | [Needs Verification] |
| [RF Channel] | OTA SDR, good positions A1/A2/A3 | RFsim channel, no RSRP/location axis | [Not Directly Comparable] |
| [Traffic Tool] | iperf3, 180 s average | iperf3 UDP, 180 s average | [Needs Verification] |

## Step-by-Step Procedure
- [Step 1] Confirm paper parameters from MinerU cache:
  - [n78], [40 MHz], [30 kHz SCS], [`DDDDDDFUUU`], [iperf3], [180 s], [UE1/UE2/UE3].
- [Step 2] Start local 3-UE RFsim topology:

```bash
GNB_REDCAP_CONFIG=/home/tonywang/OAI/Red_cap_openairinterface5g/ci-scripts/conf_files/gnb.sa.band78.fr1.106PRB.usrpb210.redcap.yaml \
MMTC_N_RB_DL=106 \
MMTC_RF_FREQ=3630360000 \
MMTC_SSB_START=144 \
MMTC_TOTAL_UES=29 \
MMTC_SAMPLE_UES="1 2 3" \
MMTC_IPERF_ENABLE=0 \
MMTC_FORWARD_PING_MODE=parallel \
MMTC_RUN_REVERSE_PING=0 \
MMTC_PUCCH_COMMON_FALLBACK_BWP0=1 \
MMTC_REDCAP_ENABLE=0 \
bash redcap_interface/redcap_mmtc_smoke_validation.sh
```

- [Step 3] Verify attach/session readiness:
  - [Summary]: `sample=3 running=3 attach=3 pdu=3 tun=3 forward_ping_ok=3 gnb_restart=0 failures=0`.
  - [UE TUN IPs]: UE1 `10.0.0.2`, UE2 `10.0.0.3`, UE3 `10.0.0.4`.
- [Step 4] Run concurrent UL/DL iperf3 with a reproducible runner:

```bash
python3 agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/analysis/scripts/p10_multiue_iperf_runner.py \
  --ues 1,2,3 \
  --direction both \
  --duration 180 \
  --protocol udp \
  --ul-rate 35M \
  --dl-rate 141M \
  --output-dir agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/analysis/data/paper10_multiue_raw \
  --limitation-note "RFsim/OAI-CN/OAI-nrUE proxy; paper uses Open5GS, OTA SDR, COTS UEs, and DDDDDDFUUU TDD"
```

- [Step 5] Re-parse raw logs after parser fix:

```bash
python3 -B agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/analysis/scripts/p10_multiue_iperf_runner.py \
  --parse-run-dir agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/analysis/data/paper10_multiue_raw/paper10_multiue_2026-05-26_17-26-35
```

## Throughput Results
| Direction | UE | Offered Rate | Receiver Mbps | Sender Mbps | Jitter ms | Loss % |
|---|---:|---:|---:|---:|---:|---:|
| UL | UE1 | 35M | 31.040 | 35.000 | 0.328 | 0.000 |
| UL | UE2 | 35M | 31.040 | 35.000 | 0.328 | 0.000 |
| UL | UE3 | 35M | 31.038 | 35.000 | 0.315 | 0.000 |
| DL | UE1 | 141M | 48.093 | 141.000 | 0.151 | 61.696 |
| DL | UE2 | 141M | 48.373 | 140.999 | 0.085 | 61.520 |
| DL | UE3 | 141M | 48.209 | 141.000 | 0.068 | 61.649 |

## Aggregate Results
| Direction | Aggregate Receiver Mbps | Jain Fairness | Interpretation |
|---|---:|---:|---|
| UL | 93.117 | 1.000000 | [PASS] Equal multi-UE sharing; no UDP loss. |
| DL | 144.675 | 0.999994 | [PASS_WITH_GAP] Equal sharing under saturation; high loss due offered load. |

## Two-UE Combination Extension
- [Purpose]: extend the PAPER-10 good-location multi-UE software-throughput proxy from `{UE1,UE2,UE3}` to the 2-UE combinations used by the paper's test set.
- [Summary CSV]: `analysis/data/paper10_multiue_combination_summary_2026-05-26.csv`.
- [Common Parameters]:
  - [Duration]: `180 s`.
  - [Protocol]: UDP iperf3.
  - [UL Offered Rate]: `35M` per active UE.
  - [DL Offered Rate]: `141M` per active UE.
  - [Idle UE Handling]: non-selected UEs remained attached but did not run iperf3.

| Combination | Direction | Aggregate Receiver Mbps | Jain Fairness | Mean Loss % | Status |
|---|---|---:|---:|---:|---|
| UE1+UE2 | UL | 69.982 | 1.000000 | 0.000 | [PASS_WITH_GAP] |
| UE1+UE2 | DL | 195.658 | 0.999993 | 28.450 | [PASS_WITH_GAP] |
| UE1+UE3 | UL | 69.983 | 1.000000 | 0.000 | [PASS_WITH_GAP] |
| UE1+UE3 | DL | 166.903 | 1.000000 | 38.245 | [PASS_WITH_GAP] |
| UE2+UE3 | UL | - | - | - | [BLOCKED_BY_ESCALATION_LIMIT] |
| UE2+UE3 | DL | - | - | - | [BLOCKED_BY_ESCALATION_LIMIT] |
| UE1+UE2+UE3 | UL | 93.117 | 1.000000 | 0.000 | [PASS_WITH_GAP] |
| UE1+UE2+UE3 | DL | 144.675 | 0.999994 | 61.622 | [PASS_WITH_GAP] |

- [Blocked Item]:
  - `{UE2,UE3}` could not start because Docker escalation was rejected after the session hit its escalation usage limit.
  - The blocked run should be launched with the same runner command after the escalation budget resets.

## Stability Evidence
- [Smoke Gate]: attach/PDU/tunnel/ping passed for all 3 UEs before traffic.
- [gNB Restart Count Before Traffic]: `0`.
- [gNB State After Traffic]: `restart_count=0`, `state=running`, `exit_code=0`.
- [Post-Traffic Container Health]: gNB, UE1, UE2, UE3, CN, and ext-dn remained `healthy`.

## Interpretation
- [Comparable Claim]:
  - The local platform reproduces the PAPER-10 [multi-UE software throughput method] at the RFsim level: 3 UEs, n78-like 40 MHz numerology, and 180 s iperf windows.
  - The local result shows near-perfect [fairness] across UE1/UE2/UE3 in both UL and DL.
- [Not Directly Comparable]:
  - Do not compare absolute Mbps against PAPER-10 Table II as a final scientific claim, because the local run does not use Open5GS, OTA SDR, COTS UEs, paper good-location RSRP, or the exact TDD slot pattern.
  - DL loss is expected from the selected stress setting: `141M x 3` offered DL load exceeds the observed RFsim DL receiver capacity.
- [Needs Verification]:
  - PAPER-10 MinerU text states iperf3 and 180 s averages, but does not expose whether the authors used TCP or UDP in the extracted text.
  - For a stricter paper match, rerun with TCP iperf3 or confirm the paper's iperf protocol from the original artifact.

## Validation Classification
- [PERF-P10-THR-002] -> [PASS_WITH_GAP]:
  - Required per-UE throughput and fairness were captured.
  - Absolute-paper comparability remains limited by environment mismatch.
- [PERF-P10-STAB-001] -> [PASS]:
  - No gNB restart, no attach/PDU/tunnel failure, and all 3 UEs remained healthy after the run.

## Next Exact-Reproduction Requirements
- [Open5GS]: replace or add Open5GS v2.7.0 as fixed 5GC.
- [OTA Hardware]: use USRP B210 or X410 with antennas and controlled UE positions.
- [UE Set]: use one phone UE and two Quectel modem UEs, or document OAI nrUE as a software-only proxy.
- [TDD Pattern]: add or verify an OAI gNB configuration matching `DDDDDDFUUU`.
- [Protocol Confirmation]: verify whether PAPER-10 iperf3 was TCP or UDP.
