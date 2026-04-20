# Work Daily Log
## Session Metadata
- Date: 2026-04-20 13:32
- Agent Session ID: N/A
- Task Slug: redcap-m5-gnb-restart-telemetry-gate

## Milestone & Sub-task Reference
- Milestone: RedCap mMTC [M5] CellGroupConfig / UE attach stability
- Sub-task: [harness telemetry] detect gNB restart during smoke validation
- Status: [COMPLETED]

## What Was Done
- Updated smoke harness script:
  - `ci-scripts/redcap_mmtc_smoke_validation.sh`
- Added output log:
  - `mmtc_smoke_<timestamp>_gnb_state.log`
  - content includes `restart_count` and full gNB `.State` JSON.
- Added runtime marker:
  - `[INFO] gNB restart count : <N> (state log: ...)`
- Added failure gate:
  - If gNB `RestartCount != 0`, harness emits warning and increments `FAILURES`.
- Added new diagnostic log path to failure summary output list.
- Verified script syntax by `bash -n`.
- Ran single-UE smoke to validate behavior and marker output.

## 3GPP Spec Clauses Referenced
- TS 38.331 Section 5.3.5 — UE/gNB reconfiguration lifecycle context for stability analysis.
- TS 38.300 Section 9.x (⚠ Needs Verification) — NG-RAN functional behavior context (non-normative here).

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| `bash -n ci-scripts/redcap_mmtc_smoke_validation.sh` | Pass | Script syntax | No syntax error |
| Smoke run (`13-31-27`, sample UE1) | Pass | UE1 | Forward ping `10/10`, reverse ping `3/3` |
| New marker output | Pass | Harness | `gNB restart count : 0` printed and `gnb_state.log` generated |

## Known Issues / Blockers
- Full 64-UE run still has gNB restart under heavy load; this patch is diagnostic and classification-only, not a root-cause fix.

## Next Step
- Use new `gnb_state.log` + `RestartCount` gate in staged-load runs (16/32/48/64) to identify deterministic kill threshold.
- Correlate restart point with per-UE socket drop and RAR-failure windows to locate gNB-side bottleneck.
