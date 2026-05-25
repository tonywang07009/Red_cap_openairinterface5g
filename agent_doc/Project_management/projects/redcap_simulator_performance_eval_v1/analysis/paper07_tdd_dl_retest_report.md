# PAPER-07 TDD Downlink Retest Report

## Status
- [Completed]
- Scope: [TDD DL] only.
- FDD: [Deferred] for later project-management planning.
- Paper source: `redcap_doc/evaluation_papers/paper_07Research_on_5G_RedCap_Standard_and_Key_Technologies.pdf`.
- Paper target used: TDD downlink 105/140 Mbps-level capability from Table I and downlink peak-rate result section [Needs Verification: local PDF OCR mixes Table IV/Table V ordering].

## Purpose
- Verify whether the current TDD RedCap RFsim platform can run downlink traffic.
- Separate [DL throughput pass] from [true DL 256QAM pass].
- Avoid the same mistake seen earlier in UL testing, where Mbps alone could pass while the scheduler still used the wrong MCS table.

## Environment
| Item | Value |
|---|---|
| Simulator mode | TDD RFsim |
| gNB container | `rfsim5g-oai-gnb_redcap` |
| UE container | `rfsim5g-oai-nr-ue1_redcap` |
| Data network | `oai-ext-dn` |
| UE tunnel IP | `10.0.0.2` |
| ext-dn IP | `192.168.72.135` |
| gNB/UE images after rebuild | `oai-gnb:latest`, `oai-nr-ue:latest` |
| gNB restart count | `0` |

## Step-By-Step Test Flow

### Step 1: Confirm TDD User Plane
- Restarted existing TDD RedCap UE1.
- Confirmed `oaitun_ue1` exists with `10.0.0.2/24`.
- Confirmed RedCap runtime config:
  - `support_of_redcap_r17: 1`
  - `number_of_rx_redcap_r17: 1`
  - `half_duplex_fdd_type_a_redcap_r17: 1`
  - `pusch_256qam: 1`
- Confirmed bidirectional ping:
  - UE to ext-dn: `0%` loss, RTT avg `4.822 ms`.
  - ext-dn to UE: `0%` loss, RTT avg `4.678 ms`.

### Step 2: Run TDD DL 106M Baseline
- Started iperf3 server on `oai-ext-dn`.
- Ran UE-side reverse UDP iperf:

```bash
docker exec rfsim5g-oai-nr-ue1_redcap iperf3 -c 192.168.72.135 -B 10.0.0.2 -t 60 -u -b 106M -R
```

- Result:
  - receiver throughput: `106 Mbit/s`.
  - jitter: `0.028 ms`.
  - UDP loss: `284/549831`, `0.052%`.
  - active gNB DLSCH stats: `MCS (0) 28`.
- Interpretation:
  - [PASS] for 64QAM-level TDD DL throughput.
  - MAC evidence remained DL MCS table 0, as expected before DL 256QAM capability was enabled.

### Step 3: Run TDD DL 141M Before DL 256QAM Capability
- Ran UE-side reverse UDP iperf:

```bash
docker exec rfsim5g-oai-nr-ue1_redcap iperf3 -c 192.168.72.135 -B 10.0.0.2 -t 60 -u -b 141M -R
```

- Result:
  - receiver throughput: `141 Mbit/s`.
  - jitter: `0.033 ms`.
  - UDP loss: `422/731598`, `0.058%`.
  - active gNB DLSCH stats: `MCS (0) 28`.
- Interpretation:
  - [PASS] for 141M downlink throughput.
  - [FAIL] for true DL 256QAM evidence because DLSCH remained `MCS (0)`.

### Step 4: Add RedCap PDSCH 256QAM Capability
- Added `nrue_recap.pdsch_256qam`.
- Added `MMTC_PDSCH_256QAM` routing through:
  - `ue_mmtc_entrypoint.sh`
  - `generate_mmtc_overlay.sh`
- Updated UE capability generation:
  - when `pdsch_256qam=1`, set `phy_ParametersFR1.pdsch_256QAM_FR1 = supported`.
- Reason:
  - OAI gNB `set_dl_mcs_table()` selects PDSCH `qam256` only when UE capability exposes `pdsch_256QAM_FR1`.

## Code Modification Summary
| Modification Point | Reason | Outcome |
|---|---|---|
| `nr_redcap_cfg_t.pdsch_256qam` | Add explicit DL 256QAM capability knob | RedCap YAML can control DL 256QAM advertisement |
| `nr_redcap_config.c` | Parse and log `pdsch_256qam` | Runtime log/config can prove requested capability |
| `rrc_ue_redcap.c` | Add `pdsch_256QAM_FR1` to UE capability | gNB can select PDSCH qam256 MCS table |
| `nrue1.uicc.yaml` / example YAML | Default to disabled | Avoid changing baseline behavior |
| mMTC entrypoint and overlay | Route `MMTC_PDSCH_256QAM` | Scenario can enable DL 256QAM without editing files |

## Build And Restart Validation
- `git diff --check`: passed.
- `CCACHE_DIR=/tmp/oai-ccache CCACHE_TEMPDIR=/tmp/oai-ccache-tmp cmake --build --preset default --target nr-uesoftmodem`: passed.
- `ci-scripts/redcap_rebuild_local_oai_images.sh`: passed.
- Smoke command used `MMTC_PDSCH_256QAM=1`.
- Smoke result:
  - `sample=1`
  - `running=1`
  - `attach=1`
  - `pdu=1`
  - `tun=1`
  - `forward_ping_ok=1`
  - `gnb_restart=0`
  - `failures=0`
- Runtime UE YAML confirmed:

```text
pusch_256qam: 1
pdsch_256qam: 1
```

## Step 5: Run True TDD DL 256QAM Retest
- Ran UE-side reverse UDP iperf:

```bash
docker exec rfsim5g-oai-nr-ue1_redcap iperf3 -c 192.168.72.135 -B 10.0.0.2 -t 60 -u -b 141M -R
```

- Active gNB evidence:

```text
UE 123c: dlsch_rounds 16157/0/0/0, dlsch_errors 0, pucch0_DTX 0, BLER 0.00000 MCS (1) 27 CCE fail 0
```

- iperf result:
  - sender throughput: `141 Mbit/s`.
  - receiver throughput: `141 Mbit/s`.
  - jitter: `0.084 ms`.
  - UDP loss: `422/731299`, `0.058%`.
- Interpretation:
  - [PASS] for TDD DL 141M throughput.
  - [PASS] for true DL 256QAM table evidence via DLSCH `MCS (1)`.

## Result Table
| Run | Direction | Target | Offered Rate | Receiver Mbps | Jitter ms | UDP Loss % | DLSCH MCS Evidence | Verdict |
|---|---|---:|---:|---:|---:|---:|---|---|
| PAPER07-TDD-DL-106M-PRE-PDSCH | DL | 106.6 | 106M | 106 | 0.028 | 0.052 | `MCS (0) 28` | PASS_TDD_DL_64QAM_LEVEL |
| PAPER07-TDD-DL-141M-PRE-PDSCH | DL | 141.3 | 141M | 141 | 0.033 | 0.058 | `MCS (0) 28` | THROUGHPUT_PASS_QAM_MISMATCH |
| PAPER07-TDD-DL-141M-TRUE-PDSCH256 | DL | 141.3 | 141M | 141 | 0.084 | 0.058 | `MCS (1) 27` | PASS_TRUE_TDD_DL_256QAM |

## Limitations
- The paper table extraction should be rechecked visually because local PDF OCR mixes Table IV/Table V text.
- RFsim AWGN does not reproduce paper RSRP/channel conditions exactly.
- gNB DLSCH stats expose `MCS (table) index`, but unlike ULSCH they do not print `Qm`; therefore DL 256QAM evidence is based on `MCS (1)` and OAI `set_dl_mcs_table()` behavior.
- The current test is one UE only. It proves TDD DL direction and DL 256QAM table selection, not multi-UE DL fairness.
- FDD remains out of scope for this run.

## Conclusion
- TDD DL is measurable in the current simulator using iperf3 reverse mode.
- TDD DL 106M passed with DLSCH table 0.
- TDD DL 141M initially passed throughput but failed true 256QAM evidence.
- After adding `pdsch_256qam`, TDD DL 141M passed with DLSCH `MCS (1) 27`.
- Final status: [TDD UL + TDD DL] are now both validated at throughput and MAC-table evidence level for the selected PAPER-07-style peak-rate points.
