# Work Daily Log
## Session Metadata
- Date: 2026-04-20 13:29
- Agent Session ID: N/A
- Task Slug: redcap-m5-pdcp-sn12-fix-and-64ue-rerun

## Milestone & Sub-task Reference
- Milestone: RedCap mMTC [M5] CellGroupConfig / UE attach stability
- Sub-task: [PDCP SN-size alignment] fix verification + [64 UE full rerun] failure re-classification
- Status: [COMPLETED]

## What Was Done
- Applied and validated [gNB RRC PDCP SN-size force-12bits] path:
  - `openair2/RRC/NR/rrc_gNB_asn1.h`
  - `openair2/RRC/NR/rrc_gNB_asn1.c`
  - `openair2/RRC/NR/rrc_gNB.c`
  - `openair2/RRC/NR/rrc_gNB_nsa.c`
- Retained/used PDCP diagnostics:
  - `openair2/LAYER2/nr_pdcp/nr_pdcp_entity.c`
  - `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/scripts/generate_mmtc_overlay.sh`
- Used `symdex` to re-check call sites of `nr_rrc_build_pdcp_config_ie(...)` and confirm caller alignment.
- Runtime validation:
  - Single UE (`UE36`) smoke run: ping `10/10` success.
  - Targeted set (`UE33,34,36,37,38,39,40`) smoke run: `7/7` each ping `10/10` success.
  - Full set (`UE1..UE64`) smoke run: reported `60` failures.
- Full 64-UE run evidence extraction:
  - `58` UE containers show `[HW] W Lost socket` then exit status `1`.
  - `6` UE containers remain running (`UE59..UE64`), with ping success on `UE61..UE64` and ping fail on `UE59/UE60`.
  - gNB log shows process restart in same run:
    - `Main child exited with signal 'Killed'`
    - second `== Starting gNB soft modem`
    - pre/post restart RFsim client connects: `58/6`.

## 3GPP Spec Clauses Referenced
- TS 38.331 Section 5.3.5 — RRC reconfiguration and UE-side application behavior.
- TS 38.331 Section 6.3.2 — DRB `PDCP-Config` signaling in RRC.
- TS 38.323 Section 6.x (⚠ Needs Verification) — PDCP SN/COUNT behavior and receive window implications.

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| Single UE smoke (`12-44-04`, UE36) | Pass | UE36 | Ping `10/10`; UPF `tun0 RX` increased from `0` to `10` pkts |
| Targeted smoke (`12-54-19`, UE33/34/36/37/38/39/40) | Pass | 7 UEs | All `7/7` ping `10/10`; no PDCP RX drop marker in gNB log |
| Full smoke (`13-02-11`, UE1..64) | Fail | 64 UEs | `60` failures; only `UE59..64` kept running at TUN-check stage |
| gNB lifecycle in full smoke | Fail | gNB | gNB main child killed once, then auto-restarted during same run |

## Known Issues / Blockers
- [PDCP SN-size mismatch] issue appears mitigated for the targeted failing cluster (`UE33/34/36+`) when load is moderate.
- [64 UE full load] still fails primarily due [gNB process killed + RFsim socket drop cascade], not the earlier PDCP drop signature.
- Need dedicated RCA for gNB kill trigger (resource pressure / scheduler overload / RFsim scaling bottleneck).

## Next Step
- Add [gNB lifecycle + memory/restart telemetry] in harness (sampled `docker inspect`/`docker stats`) during full-load run.
- Re-run staged load (e.g., 16 -> 32 -> 48 -> 64) to identify kill threshold and correlate with RFsim client count.
- Keep PDCP SN-size fix in place while moving RCA focus to [gNB process kill / RFsim connection stability].
