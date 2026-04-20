# Work Daily Log
## Session Metadata
- Date: 2026-04-20 21:19
- Agent Session ID: N/A
- Task Slug: redcap-m5-stage-scan-summary-markers

## Milestone & Sub-task Reference
- Milestone: M5 - 64UE mMTC Stability & RCA
- Sub-task: Add smoke summary markers and execute staged threshold scan (52/56/60/64)
- Status: [COMPLETED]

## What Was Done
- Updated `ci-scripts/redcap_mmtc_smoke_validation.sh`.
- Added counters: `running/attach/pdu/tun/forward_ping_ok/reverse_ping_ok/gnb_restart`.
- Added one-line marker: `[SUMMARY] sample=... running=... attach=... pdu=... tun=... forward_ping_ok=... reverse_ping_ok=... gnb_restart=... failures=... mode=...`.
- Added `ci-scripts/redcap_mmtc_stage_scan.sh` for staged runs and summary extraction.
- Executed staged scan with fast setting: `MMTC_UE_START_GAP=0`, stages `52/56/60/64`.
- Captured summary report: `test_log/compiler_logs/mmtc_stage_scan_2026-04-20_21-09-33_summary.log`.

## 3GPP Spec Clauses Referenced
- TS 38.331 Section 5.3.5 — UE RRC connection/reconfiguration procedure context for attach/reconfig stage.
- TS 38.321 Section 5.11 — MAC behavior context when UE transitions into configured operation.

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| `bash -n ci-scripts/redcap_mmtc_smoke_validation.sh` | Pass | N/A | Script syntax OK after summary marker patch |
| `bash -n ci-scripts/redcap_mmtc_stage_scan.sh` | Pass | N/A | New scan helper syntax OK |
| `env MMTC_UE_START_GAP=0 MMTC_GNB_WARMUP=10 MMTC_SLEEP_AFTER_UP=25 bash ci-scripts/redcap_mmtc_stage_scan.sh` | Pass (execution) | Stage 52/56/60/64 | All stages executed and summary lines captured; each stage functional result is FAIL by design due UE failures |

## Known Issues / Blockers
- Stage results show severe collapse already at stage 52:
  - `52`: running=4, attach=4, tun=4, ping=4, restart=1, failures=49
  - `56`: running=5, attach=5, tun=5, ping=5, restart=0, failures=51
  - `60`: running=5, attach=5, tun=5, ping=5, restart=0, failures=55
  - `64`: running=5, attach=5, tun=5, ping=5, restart=0, failures=59
- Indicates primary bottleneck is pre-ping UE survival/attach scale collapse; gNB restart is intermittent, not the only limiting factor.

## Next Step
- Focus next RCA slice on per-UE early death correlation (`running=0`) using UE/gNB logs at stage 52 and 56:
  - compare survivors vs failed cohort around first `CellGroupConfig` apply and immediate post-apply window.
