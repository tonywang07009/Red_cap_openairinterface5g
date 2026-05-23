# PAPER-07 RedCap UL Peak-Rate Test Report

## 1. Report Scope
- [Report Name]: PAPER-07 RedCap UL peak-rate reproduction and true 256QAM verification.
- [Paper ID]: PAPER-07.
- [Paper File]: `evaluation_paper/Research_on_5G_RedCap_Standard_and_Key_Technologies.pdf`.
- [Paper Evidence]: PDF page 4, Table IV, RedCap uplink peak-rate test.
- [Simulator]: OAI NR RFsim-based RedCap scenario.
- [Objective]: verify whether the simulator can reproduce PAPER-07 uplink peak-rate behavior and distinguish [64QAM] from [256QAM] by MAC-layer evidence.

## 2. PAPER-07 Target Extracted For This Test
- [Scenario]: RedCap uplink peak-rate validation.
- [Traffic Type]: UDP uplink full-buffer traffic.
- [Duration]: 1 minute per test point.
- [Carrier Type]: 3.5 GHz TDD, mapped to simulator band n78.
- [Paper RB Setting]: 51 RB.
- [Paper RSRP Setting]: `-65 dBm`.
- [Paper 64QAM Target]:
  - PHY UL throughput: `26.4 Mbps`.
  - PDCP UL throughput: `25.5 Mbps`.
- [Paper 256QAM Target]:
  - PHY UL throughput: `35.4 Mbps`.
  - PDCP UL throughput: `34.7 Mbps`.

## 3. Test Question
- [Main Question]: Can the OAI RFsim platform reproduce the PAPER-07 RedCap UL peak-rate points?
- [Sub-question 1]: Does the 64QAM point produce receiver throughput near or above the PAPER-07 PDCP target?
- [Sub-question 2]: Does the 256QAM point produce receiver throughput near or above the PAPER-07 PDCP target?
- [Sub-question 3]: Does the gNB scheduler actually use the correct modulation table?
  - 64QAM must show `MCS (0)` and `Qm 6`.
  - 256QAM must show `MCS (1)` and `Qm 8`.

## 4. Environment Design

### 4.1 Simulator Topology
| Component | Container / Path | Role |
|---|---|---|
| gNB | `rfsim5g-oai-gnb_redcap` | NR gNB scheduler, MAC stats source |
| UE | `rfsim5g-oai-nr-ue1_redcap` | RedCap UE under test |
| Data Network | `oai-ext-dn` | iperf3 UDP server endpoint |
| Compose path | `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/` | RFsim RedCap scenario |
| UE generated config | `rfsim5g-oai-nr-ue1_redcap:/tmp/nr-ue-mmtc.yaml` | Runtime UE/UICC/RedCap capability config |

### 4.2 Radio And Protocol Setting
| Factor | Simulator Setting | PAPER-07 Mapping | Notes |
|---|---:|---|---|
| Band | `n78` | 3.5 GHz TDD family | Comparable frequency family, not exact paper center frequency |
| RF frequency | `3630360000 Hz` | 3.5 GHz TDD | Simulator configured in n78 range |
| Numerology | `1` | NR mid-band TDD assumption | 30 kHz SCS |
| Carrier RB | `N_RB_DL=106` | Paper RB=51 | Not identical; simulator logs also show RedCap initial BWP size 51, but active MAC stats observed `NPRB 106` |
| Channel model | RFsim AWGN template | Paper RSRP=-65 dBm | Not physically equivalent; used for functional throughput reproduction |
| UE RedCap | `support_of_redcap_r17=1` | RedCap UE | UE capability generated from YAML fallback |
| UE Rx branch | `number_of_rx_redcap_r17=1` | RedCap reduced capability | Matches reduced UE capability intent |
| Half-duplex FDD Type A | `half_duplex_fdd_type_a_redcap_r17=1` | RedCap capability flag | Present as simulator capability input, not the main UL throughput factor |

## 5. Experiment Design Factors
| Factor | Level 1 | Level 2 | Why It Matters |
|---|---|---|---|
| [A: Modulation Capability] | `pusch_256qam=0` | `pusch_256qam=1` | Controls whether UE advertises PUSCH 256QAM capability |
| [B: Offered UDP Rate] | `26M` | `35M` | Aligns simulator traffic load with PAPER-07 64QAM and 256QAM PDCP targets |
| [C: Traffic Duration] | `60s` | fixed | Matches PAPER-07 1-minute peak-rate measurement window |
| [D: UE Scale] | `MMTC_TOTAL_UES=29` | fixed for true 256QAM run | Keeps test inside the project RedCap mMTC scenario while measuring UE1 |
| [E: Measurement UE] | `MMTC_IPERF_SAMPLE_UES=1` | fixed | Keeps iperf measurement deterministic and easy to trace |
| [F: MAC Evidence] | `nrMAC_stats.log` sampled during iperf | fixed | Prevents false pass based only on Mbps |

## 6. Parameter Explanation

### 6.1 Traffic Parameters
| Parameter | Value | Explanation |
|---|---:|---|
| `MMTC_IPERF_ENABLE` | `1` | Enables iperf3 traffic after UE readiness checks |
| `MMTC_IPERF_UDP` | `1` | Uses UDP mode, matching the PAPER-07 UDP peak-rate test |
| `MMTC_IPERF_RATE` | `26M` / `35M` | Offered UL traffic rate; `26M` maps to 64QAM point, `35M` maps to 256QAM point |
| `MMTC_IPERF_DURATION` | `60` | Runs traffic for 60 seconds, matching the paper test duration |
| `MMTC_IPERF_SAMPLE_UES` | `1` | Runs iperf on one sampled UE to isolate the metric |

### 6.2 Scenario Parameters
| Parameter | Value | Explanation |
|---|---:|---|
| `MMTC_TOTAL_UES` | `29` | Starts the mMTC RedCap scenario with 29 UE services for the true 256QAM run |
| `MMTC_SAMPLE_UES` | `1` | Performs readiness checks on one sampled UE |
| `MMTC_UE_START_GAP` | `0` | Starts selected UEs without extra launch delay |
| `MMTC_GNB_WARMUP` | `5` | Gives gNB time to initialize before UE checks |
| `MMTC_SLEEP_AFTER_UP` | `25` | Allows post-start attach/PDU/tunnel stabilization |
| `MMTC_FORWARD_PING_MODE` | `parallel` | Runs forward ping checks in parallel mode |
| `MMTC_RUN_REVERSE_PING` | `0` | Disables reverse ping to keep this report focused on UL iperf |
| `MMTC_PING_COUNT` | `10` | Sends 10 ICMP packets for readiness/latency proxy |

### 6.3 RedCap / 256QAM Parameters
| Parameter | Value | Explanation |
|---|---:|---|
| `MMTC_PUSCH_256QAM` | `0` for 64QAM baseline, `1` for true 256QAM | Routes into `nrue_recap.pusch_256qam` in UE YAML |
| `nrue_recap.pusch_256qam` | `0` / `1` | Controls whether UE capability advertises `BandNR.pusch_256QAM` |
| `MMTC_PUCCH_COMMON_FALLBACK_BWP0` | `1` | Keeps PUCCH common fallback behavior stable for the scenario |
| `support_of_redcap_r17` | `1` | Ensures the UE is treated as RedCap-capable |
| `number_of_rx_redcap_r17` | `1` | Uses 1Rx RedCap capability behavior |

## 7. Step-By-Step Test Flow

### Step 1: Extract PAPER-07 Test Target
- Read PAPER-07 Table IV.
- Extract two target points:
  - [64QAM]: PDCP UL `25.5 Mbps`, PHY UL `26.4 Mbps`.
  - [256QAM]: PDCP UL `34.7 Mbps`, PHY UL `35.4 Mbps`.
- Decide simulator response metrics:
  - receiver throughput,
  - sender throughput,
  - UDP jitter,
  - UDP loss,
  - ping RTT,
  - gNB MAC `MCS`, `Qm`, `NPRB`.

### Step 2: Define Pass Criteria
- [Platform Health Pass]:
  - attach success = 100%.
  - PDU session success = 100%.
  - UE tunnel exists.
  - forward ping succeeds.
  - `gnb_restart_count = 0`.
  - `failure_count = 0`.
- [PAPER-07 Throughput Pass]:
  - 64QAM measured receiver throughput should reach or exceed `25.5 Mbps`.
  - 256QAM measured receiver throughput should reach or exceed `34.7 Mbps`.
- [QAM Evidence Pass]:
  - 64QAM must show `MCS (0)` and `Qm 6`.
  - 256QAM must show `MCS (1)` and `Qm 8`.

### Step 3: Run 64QAM Baseline
- Use `MMTC_PUSCH_256QAM=0`.
- Use UDP UL offered rate `26M`.
- Run 60-second iperf3 UL traffic from UE to `oai-ext-dn`.
- Sample `rfsim5g-oai-gnb_redcap:/opt/oai-gnb/nrMAC_stats.log` during active iperf.
- Observed result:
  - receiver throughput: `26.0 Mbps`.
  - jitter: `0.562 ms`.
  - UDP loss: `0%`.
  - gNB MAC: `MCS (0) 28`, `Qm 6`.
- Interpretation:
  - The 64QAM point passed both throughput and modulation evidence checks.

### Step 4: Run Initial 35M Check Before 256QAM Capability Fix
- Use UDP UL offered rate `35M`.
- The initial run reached receiver throughput `35.0 Mbps`, but gNB still showed `MCS (0) 28` and `Qm 6`.
- Interpretation:
  - This was a [throughput-compatible] result, but not a [true 256QAM] result.
  - Root cause: UE capability did not advertise PUSCH 256QAM, so gNB did not switch to the 256QAM MCS table.

### Step 5: Enable True PUSCH 256QAM Capability
- Add `nrue_recap.pusch_256qam` to the RedCap UICC YAML config.
- Add `MMTC_PUSCH_256QAM` routing in the mMTC entrypoint and overlay generator.
- In UE capability construction, set `BandNR.pusch_256QAM = supported` when enabled.
- Existing gNB logic then selects `mcs_Table = qam256` through `set_ul_mcs_table()`.

### Step 6: Rebuild And Restart Scenario
- Build validation:

```bash
CCACHE_DIR=/tmp/oai-ccache CCACHE_TEMPDIR=/tmp/oai-ccache-tmp cmake --build --preset default --target nr-uesoftmodem
```

- Image rebuild validation:

```bash
ci-scripts/redcap_rebuild_local_oai_images.sh
```

- True 256QAM smoke/test command:

```bash
MMTC_TOTAL_UES=29 MMTC_SAMPLE_UES=1 MMTC_IPERF_SAMPLE_UES=1 MMTC_IPERF_ENABLE=1 MMTC_IPERF_UDP=1 MMTC_IPERF_RATE=35M MMTC_IPERF_DURATION=60 MMTC_FORWARD_PING_MODE=parallel MMTC_RUN_REVERSE_PING=0 MMTC_PING_COUNT=10 MMTC_GNB_WARMUP=5 MMTC_SLEEP_AFTER_UP=25 MMTC_UE_START_GAP=0 MMTC_PUCCH_COMMON_FALLBACK_BWP0=1 MMTC_PUSCH_256QAM=1 ci-scripts/redcap_mmtc_smoke_validation.sh
```

### Step 7: Verify Runtime UE Capability
- Check generated UE YAML:

```text
nrue_recap:
  support_of_redcap_r17: 1
  number_of_rx_redcap_r17: 1
  half_duplex_fdd_type_a_redcap_r17: 1
  pusch_256qam: 1
```

- Check UE log:

```text
nrue_recap RedCap config: band=n78 RedCap=1 ... PUSCH256QAM=1
```

### Step 8: Verify gNB MAC Uses 256QAM During Active UL
- Sample gNB MAC stats while iperf is still running.
- Required evidence:

```text
MCS (1) ... (Qm 8 ...)
```

- Observed evidence:

```text
UE 6cd3: ulsch_rounds 27059/0/0/0, ulsch_errors 0, ulsch_DTX 0, BLER 0.00000 MCS (1) 27 (Qm 8 deltaMCS 0 dB) NPRB 106  SNR 50.0 dB CCE fail 0
```

### Step 9: Collect Traffic Metrics
- Read iperf3 UL log from:
  - `test_log/compiler_logs/mmtc_smoke_2026-05-21_18-04-58_ue1_iperf3_ul.log`.
- Read ping log from:
  - `test_log/compiler_logs/mmtc_smoke_2026-05-21_18-04-58_ue1_ping.log`.
- Store parsed results in:
  - `analysis/data/paper07_true_256qam_retest.csv`.
- Generate plot:
  - `analysis/plots/paper07_true_256qam_retest.png`.
  - `analysis/plots/paper07_true_256qam_retest.pdf`.

## 8. Results
| Run | PAPER-07 Point | Paper PDCP UL Mbps | Offered Rate | Receiver Mbps | Jitter ms | UDP Loss | gNB Evidence | Verdict |
|---|---|---:|---:|---:|---:|---:|---|---|
| PAPER07-QAM-64-OBSERVED | 64QAM | 25.5 | 26M | 26.0 | 0.562 | 0% | `MCS (0) 28`, `Qm 6` | PASS |
| PAPER07-QAM-256-TRUE | 256QAM | 34.7 | 35M | 35.0 | 0.326 | 0% | `MCS (1) 27`, `Qm 8` | PASS |

## 9. Parameter-To-Outcome Explanation
- `MMTC_IPERF_RATE=26M`:
  - Purpose: stress the UL path near PAPER-07 64QAM PDCP target.
  - Result: receiver `26.0 Mbps`, above paper PDCP target `25.5 Mbps`.
- `MMTC_IPERF_RATE=35M`:
  - Purpose: stress the UL path near PAPER-07 256QAM PDCP target.
  - Result: receiver `35.0 Mbps`, above paper PDCP target `34.7 Mbps`.
- `MMTC_PUSCH_256QAM=0`:
  - Purpose: preserve 64QAM capability behavior.
  - Result: gNB reported `MCS (0)` and `Qm 6`.
- `MMTC_PUSCH_256QAM=1`:
  - Purpose: make UE capability expose PUSCH 256QAM support.
  - Result: gNB reported `MCS (1)` and `Qm 8`.
- `MMTC_IPERF_DURATION=60`:
  - Purpose: align with PAPER-07 one-minute measurement window.
  - Result: stable receiver report and zero UDP loss.
- `MMTC_TOTAL_UES=29`:
  - Purpose: keep the test inside the project mMTC RedCap scenario.
  - Result: true 256QAM test passed with `gnb_restart=0` and `failures=0`.

## 10. Limitations
- [RF Equivalence Limitation]: RFsim AWGN does not reproduce PAPER-07 physical RSRP `-65 dBm` exactly.
- [RB Equivalence Limitation]: PAPER-07 uses 51 RB. The simulator carrier is `N_RB_DL=106`; logs show RedCap initial BWP size 51, but active UL MAC stats observed `NPRB 106`.
- [Latency Limitation]: ping RTT is used only as a simulator data-path proxy, not as full 5G E2E latency equivalence.
- [Single-UE Measurement Limitation]: iperf measurement was collected from UE1 only. This is acceptable for PAPER-07 peak-rate reproduction, but not sufficient for UE-scale fairness claims.
- [Sampling Timing Limitation]: `Qm 8` must be sampled during active full-buffer UL traffic. After iperf ends, MAC stats may return to idle low-MCS values.

## 11. Conclusion
- The simulator reproduced the PAPER-07 64QAM UL peak-rate point:
  - paper PDCP target `25.5 Mbps`,
  - measured receiver throughput `26.0 Mbps`,
  - correct MAC evidence `MCS (0)` and `Qm 6`.
- The simulator reproduced the PAPER-07 256QAM UL peak-rate point after enabling UE PUSCH 256QAM capability:
  - paper PDCP target `34.7 Mbps`,
  - measured receiver throughput `35.0 Mbps`,
  - correct MAC evidence `MCS (1)` and `Qm 8`.
- Final assessment:
  - [PASS] for PAPER-07 UL peak-rate functional reproduction.
  - [PASS] for true 256QAM MAC evidence.
  - [LIMITED] for exact RF/channel equivalence because RFsim cannot fully reproduce PAPER-07 physical-layer field conditions without additional channel calibration and RB/BWP alignment.
