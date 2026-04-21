# Work Daily Log
## Session Metadata
- Date: 2026-04-21 11:42
- Agent Session ID: N/A
- Task Slug: redcap-m5-stage60-64-validation

## Milestone & Sub-task Reference
- Milestone: M5 RCA (mMTC staged load)
- Sub-task: Validate stage60/stage64 after PUCCH oversubscription patch
- Status: [COMPLETED]

## What Was Done
- Executed `MMTC_STAGE_LIST=60,64` stage scan using existing rebuilt images.
- First attempt failed due Docker socket sandbox permission; reran with escalated Docker access.
- Collected stage summaries from `mmtc_stage_scan_2026-04-21_11-35-06_summary.log`.
- Collected gNB/UE state logs for both stages (`mmtc_smoke_2026-04-21_11-35-06_*`, `mmtc_smoke_2026-04-21_11-38-14_*`).

## 3GPP Spec Clauses Referenced
- TS 38.331 Section 5.3.3.1 — RRC connection establishment stability under high attach load.
- TS 38.321 Section 5.1.4 — RA completion context used to interpret attach counts before service collapse.

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| Stage scan UE=60 | Fail | Runtime stage smoke | `[SUMMARY] sample=60 running=2 attach=49 pdu=48 tun=0 forward_ping_ok=0 gnb_restart=1 failures=61` |
| Stage scan UE=64 | Fail | Runtime stage smoke | `[SUMMARY] sample=64 running=6 attach=49 pdu=49 tun=0 forward_ping_ok=0 gnb_restart=1 failures=65` |
| gNB restart monitor | Fail | Runtime stability | `gnb_restart=1` in both stage60 and stage64 |
| UE container state check | Fail | Runtime diagnostics | UE containers mostly `Status=exited`, `ExitCode=1` after gNB restart window |

## Known Issues / Blockers
- Hard PUCCH budget gate issue is fixed for stage52/56, but stage60/64 still collapse due restart-class instability.
- Current logs show restart happened, but direct crash reason marker is not explicit in saved gNB logs.

## Next Step
- Add minimal crash-cause instrumentation around gNB restart window (startup + first 120s), then rerun stage60 only for focused RCA.
