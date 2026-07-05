# A/B SDT Fast Access Demo

- [Run ID]: `parser_check_2026-06-13_gate3`
- [Generated At]: `2026-06-13T15:14:05+08:00`
- [Output Dir]: `/home/tonywang/OAI/Red_cap_openairinterface5g/test_log/ab_sdt_fast_access`
- [Run Experiments]: `0`
- [Case A]: [Connected UE], Gate1/2/3 off
- [Case B]: [SDT UE], Gate1 on, Gate2 off, Gate3 on
- [Total UEs]: `29`
- [Sample UEs]: `1`
- [First Sample UE For UE/Ping Logs]: `1`

## Measurement Definition
- [Case A data_path_ms]: UE `Received NR_RRCSetup` -> UE `Interface oaitun_ue1 successfully configured`.
- [Case A packet_bytes]: UE `RRCSetupComplete` encoded bytes when available; otherwise first ping reply bytes.
- [Case B data_path_ms]: UE `RRC_INACTIVE entered` -> UE `cg-SDT PUSCH tx`.
- [Case B packet_bytes/TBS]: first UE `cg-SDT autonomous CG PUSCH scheduled` after inactive.
- [gNB rx bytes]: first gNB `cg-SDT PUSCH rx candidate` selected after the UE inactive timestamp when possible.
- [Caution]: UE and gNB timestamps are not used for hard cross-container latency unless clock alignment is proven.

## A/B Table

| Case | Name | Status | Data path ms | Packet bytes | TBS | gNB rx bytes | Ping avg ms | Reason |
|---|---|---|---:|---:|---:|---:|---:|---|
| `B` | `sdt-inactive` | `PASS` | `0.323` | `53` | `72` | `4` | `9.664` | `ok` |

## Evidence Logs
- [Case A gNB log]: `NA`
- [Case A UE log]: `NA`
- [Case A ping log]: `NA`
- [Case A console log]: `NA`
- [Case B gNB log]: `test_log/compiler_logs/mmtc_smoke_2026-06-13_14-52-24_gnb.log`
- [Case B UE log]: `test_log/compiler_logs/mmtc_smoke_2026-06-13_14-52-24_ue1_docker.log`
- [Case B ping log]: `test_log/compiler_logs/mmtc_smoke_2026-06-13_14-52-24_ue1_ping.log`
- [Case B console log]: `NA`

## Output Files
- [Summary]: `/home/tonywang/OAI/Red_cap_openairinterface5g/test_log/ab_sdt_fast_access/parser_check_2026-06-13_gate3_summary.md`
- [Metrics CSV]: `/home/tonywang/OAI/Red_cap_openairinterface5g/test_log/ab_sdt_fast_access/parser_check_2026-06-13_gate3_metrics.csv`
