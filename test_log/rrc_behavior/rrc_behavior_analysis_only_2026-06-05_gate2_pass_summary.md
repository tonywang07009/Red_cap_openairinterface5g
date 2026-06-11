# RRC Behavior Comparison

- [Run ID]: `rrc_behavior_analysis_only_2026-06-05_gate2_pass`
- [Generated At]: `2026-06-06T10:15:35+08:00`
- [Output Dir]: `/home/tonywang/OAI/Red_cap_openairinterface5g/test_log/rrc_behavior`
- [Run Experiments]: `0`
- [Total UEs]: `29`
- [Sample UEs]: `1`
- [First Sample UE For UE Log]: `1`

## Measurement Definition
- [IDLE ra_to_connected_ms]: gNB `Initiating RA procedure` -> gNB `Received RRCSetupComplete`.
- [IDLE rrc_setup_to_connected_ms]: gNB `Send RRC Setup` -> gNB `Received RRCSetupComplete`.
- [INACTIVE ra_to_connected_ms]: gNB resume RA `Initiating RA procedure` -> gNB `RRCResumeComplete received`.
- [INACTIVE rrc_resume_request_to_connected_ms]: gNB `RRCResumeRequest received` -> gNB `RRCResumeComplete received`.

## Metrics

| Mode | Metric | Start Marker | End Marker | Duration ms | Status | Smoke RC |
|---|---|---|---|---:|---|---:|
| `idle` | `ra_to_connected_ms` | `gNB Initiating RA procedure` | `gNB Received RRCSetupComplete` | `6.688` | `PASS` | `NA` |
| `idle` | `rrc_setup_to_connected_ms` | `gNB Send RRC Setup` | `gNB Received RRCSetupComplete` | `4.336` | `PASS` | `NA` |
| `idle` | `ue_setupcomplete_to_gnb_connected_ms` | `UE Generating RRCSetupComplete` | `gNB Received RRCSetupComplete` | `2.974` | `PASS` | `NA` |
| `inactive` | `release_to_connected_ms` | `gNB Send RRC Release suspendConfig` | `gNB RRCResumeComplete received` | `22.503` | `PASS` | `NA` |
| `inactive` | `ra_to_connected_ms` | `gNB resume RA Initiating RA procedure` | `gNB RRCResumeComplete received` | `13.668` | `PASS` | `NA` |
| `inactive` | `rrc_resume_request_to_connected_ms` | `gNB RRCResumeRequest received` | `gNB RRCResumeComplete received` | `12.204` | `PASS` | `NA` |
| `inactive` | `rrc_resume_sent_to_connected_ms` | `gNB RRCResume sent` | `gNB RRCResumeComplete received` | `12.192` | `PASS` | `NA` |
| `inactive` | `ue_inactive_to_ue_resumecomplete_sent_ms` | `UE RRC_INACTIVE entered` | `UE RRCResumeComplete sent` | `3.156` | `PASS` | `NA` |

## IDLE Evidence
- [gNB log]: `test_log/compiler_logs/mmtc_smoke_2026-06-05_23-34-44_gnb.log`
- [UE log]: `/home/tonywang/OAI/Red_cap_openairinterface5g/test_log/compiler_logs/mmtc_smoke_2026-06-05_23-34-44_ue1_docker.log`
- [Console log]: `NA`
- [Note]: This is an [RRC_IDLE initial access] proxy unless the supplied log is from a true release-to-idle reconnect run.

## INACTIVE Evidence
- [gNB log]: `test_log/compiler_logs/mmtc_smoke_2026-06-05_23-34-44_gnb.log`
- [UE log]: `/home/tonywang/OAI/Red_cap_openairinterface5g/test_log/compiler_logs/mmtc_smoke_2026-06-05_23-34-44_ue1_docker.log`
- [Console log]: `NA`
- [Note]: [RRC_INACTIVE resume] uses Gate 1/2 markers when this script runs the experiment.

## Delta

| Comparison | Formula | Delta ms | Interpretation |
|---|---:|---:|---|
| RA-to-connected | inactive.ra_to_connected_ms - idle.ra_to_connected_ms | `6.980` | `idle_faster` |
| RRC-message-to-connected | inactive.rrc_resume_request_to_connected_ms - idle.rrc_setup_to_connected_ms | `7.868` | `idle_faster` |

## Output Files
- [Summary]: `/home/tonywang/OAI/Red_cap_openairinterface5g/test_log/rrc_behavior/rrc_behavior_analysis_only_2026-06-05_gate2_pass_summary.md`
- [Metrics CSV]: `/home/tonywang/OAI/Red_cap_openairinterface5g/test_log/rrc_behavior/rrc_behavior_analysis_only_2026-06-05_gate2_pass_metrics.csv`
