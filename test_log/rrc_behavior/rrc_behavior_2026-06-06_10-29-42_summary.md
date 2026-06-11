# RRC Behavior Comparison

- [Run ID]: `rrc_behavior_2026-06-06_10-29-42`
- [Generated At]: `2026-06-06T10:29:42+08:00`
- [Output Dir]: `/home/tonywang/OAI/Red_cap_openairinterface5g/test_log/rrc_behavior`
- [Run Experiments]: `1`
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
| `idle` | `ra_to_connected_ms` | `gNB Initiating RA procedure` | `gNB Received RRCSetupComplete` | `6.748` | `PASS` | `0` |
| `idle` | `rrc_setup_to_connected_ms` | `gNB Send RRC Setup` | `gNB Received RRCSetupComplete` | `4.041` | `PASS` | `0` |
| `idle` | `ue_setupcomplete_to_gnb_connected_ms` | `UE Generating RRCSetupComplete` | `gNB Received RRCSetupComplete` | `2.481` | `PASS` | `0` |
| `inactive` | `release_to_connected_ms` | `gNB Send RRC Release suspendConfig` | `gNB RRCResumeComplete received` | `20.476` | `PASS` | `0` |
| `inactive` | `ra_to_connected_ms` | `gNB resume RA Initiating RA procedure` | `gNB RRCResumeComplete received` | `12.433` | `PASS` | `0` |
| `inactive` | `rrc_resume_request_to_connected_ms` | `gNB RRCResumeRequest received` | `gNB RRCResumeComplete received` | `11.125` | `PASS` | `0` |
| `inactive` | `rrc_resume_sent_to_connected_ms` | `gNB RRCResume sent` | `gNB RRCResumeComplete received` | `11.113` | `PASS` | `0` |
| `inactive` | `ue_inactive_to_ue_resumecomplete_sent_ms` | `UE RRC_INACTIVE entered` | `UE RRCResumeComplete sent` | `2.951` | `PASS` | `0` |

## IDLE Evidence
- [gNB log]: `/home/tonywang/OAI/Red_cap_openairinterface5g/test_log/compiler_logs/mmtc_smoke_2026-06-06_10-29-42_gnb.log`
- [UE log]: `/home/tonywang/OAI/Red_cap_openairinterface5g/test_log/compiler_logs/mmtc_smoke_2026-06-06_10-29-42_ue1_docker.log`
- [Console log]: `/home/tonywang/OAI/Red_cap_openairinterface5g/test_log/rrc_behavior/rrc_behavior_2026-06-06_10-29-42_idle_console.log`
- [Note]: This is an [RRC_IDLE initial access] proxy unless the supplied log is from a true release-to-idle reconnect run.

## INACTIVE Evidence
- [gNB log]: `/home/tonywang/OAI/Red_cap_openairinterface5g/test_log/compiler_logs/mmtc_smoke_2026-06-06_10-31-12_gnb.log`
- [UE log]: `/home/tonywang/OAI/Red_cap_openairinterface5g/test_log/compiler_logs/mmtc_smoke_2026-06-06_10-31-12_ue1_docker.log`
- [Console log]: `/home/tonywang/OAI/Red_cap_openairinterface5g/test_log/rrc_behavior/rrc_behavior_2026-06-06_10-29-42_inactive_console.log`
- [Note]: [RRC_INACTIVE resume] uses Gate 1/2 markers when this script runs the experiment.

## Delta

| Comparison | Formula | Delta ms | Interpretation |
|---|---:|---:|---|
| RA-to-connected | inactive.ra_to_connected_ms - idle.ra_to_connected_ms | `5.685` | `idle_faster` |
| RRC-message-to-connected | inactive.rrc_resume_request_to_connected_ms - idle.rrc_setup_to_connected_ms | `7.084` | `idle_faster` |

## Output Files
- [Summary]: `/home/tonywang/OAI/Red_cap_openairinterface5g/test_log/rrc_behavior/rrc_behavior_2026-06-06_10-29-42_summary.md`
- [Metrics CSV]: `/home/tonywang/OAI/Red_cap_openairinterface5g/test_log/rrc_behavior/rrc_behavior_2026-06-06_10-29-42_metrics.csv`
