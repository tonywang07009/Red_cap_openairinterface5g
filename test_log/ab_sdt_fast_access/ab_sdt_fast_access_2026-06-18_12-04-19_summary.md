# A/B SDT Fast Access Demo

- [Run ID]: `ab_sdt_fast_access_2026-06-18_12-04-19`
- [Generated At]: `2026-06-18T12:04:19+08:00`
- [Output Dir]: `/home/tonywang/OAI/Red_cap_openairinterface5g/test_log/ab_sdt_fast_access`
- [Run Experiments]: `1`
- [Case A]: [Connected UE], Gate1/2/3 off
- [Case B]: [SDT UE], Gate1 on, Gate2 off, Gate3 on
- [Total UEs]: `29`
- [Sample UEs]: `1`
- [First Sample UE For UE/Ping Logs]: `1`

## Measurement Definition
- [Case A data_path_ms]: UE `Received NR_RRCSetup` -> UE `Interface oaitun_ue1 successfully configured`.
- [Case A packet_bytes]: UE `RRCSetupComplete` encoded bytes when available; otherwise first ping reply bytes.
- [Case B data_path_ms]: UE `cg-SDT autonomous CG PUSCH scheduled` -> UE `cg-SDT PUSCH tx`.
- [Case B inactive_wait_ms]: UE `RRC_INACTIVE entered` -> UE `cg-SDT PUSCH tx`; this includes inactive dwell time before small data arrives.
- [Case B packet_bytes/TBS]: first UE `cg-SDT autonomous CG PUSCH scheduled` after inactive.
- [gNB rx bytes]: first gNB `cg-SDT PUSCH rx candidate` selected after the UE inactive timestamp when possible.
- [Caution]: UE and gNB timestamps are not used for hard cross-container latency unless clock alignment is proven.

## A/B Table

| Case | Name | Status | Data path ms | Inactive wait ms | Packet bytes | TBS | gNB rx bytes | Ping avg ms | Reason |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| `A` | `connected` | `PASS` | `62.603` | `NA` | `33` | `NA` | `NA` | `3.761` | `ok` |
| `B` | `sdt-inactive` | `PASS` | `0.006` | `3967.349` | `53` | `72` | `20` | `3.865` | `ok` |

## Evidence Logs
- [Case A gNB log]: `/home/tonywang/OAI/Red_cap_openairinterface5g/test_log/compiler_logs/mmtc_smoke_2026-06-18_12-04-19_gnb.log`
- [Case A UE log]: `/home/tonywang/OAI/Red_cap_openairinterface5g/test_log/compiler_logs/mmtc_smoke_2026-06-18_12-04-19_ue1_docker.log`
- [Case A ping log]: `/home/tonywang/OAI/Red_cap_openairinterface5g/test_log/compiler_logs/mmtc_smoke_2026-06-18_12-04-19_ue1_ping.log`
- [Case A console log]: `/home/tonywang/OAI/Red_cap_openairinterface5g/test_log/ab_sdt_fast_access/ab_sdt_fast_access_2026-06-18_12-04-19_A_console.log`
- [Case B gNB log]: `/home/tonywang/OAI/Red_cap_openairinterface5g/test_log/compiler_logs/mmtc_smoke_2026-06-18_12-05-31_gnb.log`
- [Case B UE log]: `/home/tonywang/OAI/Red_cap_openairinterface5g/test_log/compiler_logs/mmtc_smoke_2026-06-18_12-05-31_ue1_docker.log`
- [Case B ping log]: `/home/tonywang/OAI/Red_cap_openairinterface5g/test_log/compiler_logs/mmtc_smoke_2026-06-18_12-05-31_ue1_ping.log`
- [Case B console log]: `/home/tonywang/OAI/Red_cap_openairinterface5g/test_log/ab_sdt_fast_access/ab_sdt_fast_access_2026-06-18_12-04-19_B_console.log`

## Output Files
- [Summary]: `/home/tonywang/OAI/Red_cap_openairinterface5g/test_log/ab_sdt_fast_access/ab_sdt_fast_access_2026-06-18_12-04-19_summary.md`
- [Metrics CSV]: `/home/tonywang/OAI/Red_cap_openairinterface5g/test_log/ab_sdt_fast_access/ab_sdt_fast_access_2026-06-18_12-04-19_metrics.csv`
