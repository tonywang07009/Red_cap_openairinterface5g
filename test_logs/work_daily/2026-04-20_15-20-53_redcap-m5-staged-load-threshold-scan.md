# Work Daily Log
## Session Metadata
- Date: 2026-04-20 15:20
- Agent Session ID: N/A
- Task Slug: redcap-m5-staged-load-threshold-scan

## Milestone & Sub-task Reference
- Milestone: RedCap mMTC [M5] CellGroupConfig / UE attach stability
- Sub-task: [staged load scan] quantify threshold and classify failure mode under 16/32/48/64 UE
- Status: [COMPLETED]

## What Was Done
- Executed staged smoke validation with fixed runtime knobs:
  - `MMTC_FORWARD_PING_MODE=parallel`
  - `MMTC_RUN_REVERSE_PING=0`
  - `MMTC_GNB_WARMUP=10`
  - `MMTC_UE_START_GAP=10`
  - `MMTC_CGCFG_NOFREE=1`
  - `MMTC_CGCFG_DEFER_FREE_SLOTS=0`
  - `MMTC_PUCCH_COMMON_FALLBACK_BWP0=1`
  - `MMTC_PDCP_TRACE=0`
- Ran four sets:
  - `UE1..16` (`mmtc_smoke_2026-04-20_13-51-26_*`)
  - `UE1..32` (`mmtc_smoke_2026-04-20_14-48-49_*`)
  - `UE1..48` (`mmtc_smoke_2026-04-20_14-56-39_*`)
  - `UE1..64` (`mmtc_smoke_2026-04-20_15-07-25_*`)
- Used new harness telemetry (`gnb_state.log`) to capture `gNB RestartCount` per run.
- Verified surviving UE set for 64-UE run from state logs: `UE60..UE64`.

## 3GPP Spec Clauses Referenced
- TS 38.331 Section 5.3.5 — RRC reconfiguration context during attach/re-attach loops.
- TS 38.321 Section 5.1 — Random Access procedure and repeated `RAR reception failed` symptoms.
- TS 38.300 Section 10.x (⚠ Needs Verification) — system-level scalability context (non-code assertion).

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| Staged run `UE1..16` | Fail | 16 UE | `gNB restart=0`, `FAILURES=13`, ping success `3/16` |
| Staged run `UE1..32` | Fail | 32 UE | `gNB restart=0`, `FAILURES=29`, ping success `3/32` |
| Staged run `UE1..48` | Fail | 48 UE | `gNB restart=0`, `FAILURES=44`, ping success `4/48` |
| Staged run `UE1..64` | Fail | 64 UE | `gNB restart=1`, `FAILURES=60`, ping success `5/64`, running UE=`5` (`UE60..64`) |

## Known Issues / Blockers
- Under `<=48` UE: no gNB restart, but most UEs still fail at TUN/ping stage.
- At `64` UE: gNB restart reappears and failure pattern becomes clustered (front block exits, tail UEs survive).
- Current primary bottleneck is not the earlier PDCP SN mismatch; it is [scale-dependent lifecycle instability + RA/tunnel availability collapse].

## Next Step
- Add per-phase counters in harness (attach-ok / tun-ok / ping-ok / running) as explicit summary lines.
- Run binary-search load scan around threshold (`52/56/60/64`) to isolate restart boundary.
- Correlate restart boundary with `gNB.log` (process kill point), and UE-side `Lost socket` timestamps.
