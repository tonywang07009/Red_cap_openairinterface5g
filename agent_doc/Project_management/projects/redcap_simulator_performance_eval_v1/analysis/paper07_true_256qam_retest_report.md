# PAPER-07 True 256QAM UL Retest

## Status
- [Completed]
- Paper: `redcap_doc/evaluation_papers/paper_07Research_on_5G_RedCap_Standard_and_Key_Technologies.pdf`
- Paper evidence: PDF page 4, Table IV, RedCap uplink peak-rate test.
- Retest purpose: verify that the 35 Mbps UL point is not only a throughput proxy, but actually runs with [PUSCH 256QAM].

## Why This Retest Was Needed
- Previous 35M run reached the paper throughput target, but gNB MAC stats still showed `MCS (0) 28` and `Qm 6`.
- In OAI MAC stats, `MCS (0)` maps to the 64QAM table and `MCS (1)` maps to the 256QAM table.
- Therefore the previous 35M result was [throughput-compatible] but not [true 256QAM].

## Configuration Change
- Added optional RedCap YAML field: `nrue_recap.pusch_256qam`.
- Routed `MMTC_PUSCH_256QAM=1` from the mMTC overlay into the generated UE UICC YAML.
- UE capability generation now advertises `BandNR.pusch_256QAM = supported` when the field is enabled.
- gNB-side existing logic in `set_ul_mcs_table()` then selects PUSCH `mcs_Table = qam256`.

## Test Command
```bash
MMTC_TOTAL_UES=29 MMTC_SAMPLE_UES=1 MMTC_IPERF_SAMPLE_UES=1 MMTC_IPERF_ENABLE=1 MMTC_IPERF_UDP=1 MMTC_IPERF_RATE=35M MMTC_IPERF_DURATION=60 MMTC_FORWARD_PING_MODE=parallel MMTC_RUN_REVERSE_PING=0 MMTC_PING_COUNT=10 MMTC_GNB_WARMUP=5 MMTC_SLEEP_AFTER_UP=25 MMTC_UE_START_GAP=0 MMTC_PUCCH_COMMON_FALLBACK_BWP0=1 MMTC_PUSCH_256QAM=1 ci-scripts/redcap_mmtc_smoke_validation.sh
```

## Runtime Evidence
- UE generated config: `pusch_256qam: 1`.
- UE log: `nrue_recap RedCap config: ... PUSCH256QAM=1`.
- gNB active stats during iperf:

```text
UE 6cd3: ulsch_rounds 27059/0/0/0, ulsch_errors 0, ulsch_DTX 0, BLER 0.00000 MCS (1) 27 (Qm 8 deltaMCS 0 dB) NPRB 106  SNR 50.0 dB CCE fail 0
```

## Result Table
| Run | Paper point | UE PUSCH 256QAM | Observed Qm/table/MCS | Paper PDCP UL Mbps | Receiver Mbps | Jitter ms | UDP Loss % | Verdict |
|---|---|---:|---:|---:|---:|---:|---:|---|
| PAPER07-QAM-64-OBSERVED | 64QAM | 0 | Qm 6 / table 0 / MCS 28 | 25.5 | 26.0 | 0.562 | 0.0 | MATCH_64QAM |
| PAPER07-QAM-256-TRUE | 256QAM | 1 | Qm 8 / table 1 / MCS 27 | 34.7 | 35.0 | 0.326 | 0.0 | MATCH_TRUE_256QAM |

## Validation
- `git diff --check`: passed for modified files.
- `cmake --build --preset default --target nr-uesoftmodem`: passed with `CCACHE_DIR=/tmp/oai-ccache CCACHE_TEMPDIR=/tmp/oai-ccache-tmp`.
- `ci-scripts/redcap_rebuild_local_oai_images.sh`: passed after Docker escalation.
- `ci-scripts/redcap_mmtc_smoke_validation.sh`: passed with `failures=0`, `gnb_restart=0`, `iperf_ul_ok=1`.

## Logs
- Build log: `redcap_library/library_build_evidence/build_nr_uesoftmodem_redcap_pusch256qam_final.log`
- UE log: `redcap_library/library_runtime_probe/paper07_tdd_ue_docker_256qam_final.log`
- iperf3 UL log: `redcap_library/library_runtime_probe/paper07_tdd_ul_iperf_256qam_final.log`
- ping log: `redcap_library/library_runtime_probe/paper07_tdd_ping_256qam_final.log`

## Outputs
- CSV: `analysis/data/paper07_true_256qam_retest.csv`
- PNG: `analysis/plots/paper07_true_256qam_retest.png`
- PDF: `analysis/plots/paper07_true_256qam_retest.pdf`

## Interpretation
- The new run satisfies the paper 256QAM PDCP UL target: measured receiver throughput was `35.0 Mbps` versus paper target `34.7 Mbps`.
- The run also satisfies the modulation evidence requirement: active gNB stats showed `MCS (1)` and `Qm 8`.
- The simulator can now reproduce PAPER-07 64QAM and 256QAM UL peak-rate points at the traffic and MAC-stat evidence level.
- Note: after iperf ends, `nrMAC_stats.log` returns to idle scheduling and may show lower `MCS/Qm`; the `Qm 8` evidence must be sampled during active full-buffer UL traffic.
