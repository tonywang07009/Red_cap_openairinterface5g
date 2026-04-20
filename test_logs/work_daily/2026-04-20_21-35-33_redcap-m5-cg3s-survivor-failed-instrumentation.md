# Work Daily Log
## Session Metadata
- Date: 2026-04-20 21:35
- Agent Session ID: N/A
- Task Slug: redcap-m5-cg3s-survivor-failed-instrumentation

## Milestone & Sub-task Reference
- Milestone: M5 - 64UE mMTC Stability & RCA
- Sub-task: Survivor vs failed diagnostics around first CellGroupConfig apply window and minimal instrumentation patch
- Status: [COMPLETED]

## What Was Done
- Reviewed project milestone context in `agent_doc/Project_management/Simluation_v2.md` (M5 section) and prior `test_logs/work_daily` RCA logs.
- Mapped likely crash window to first `CellGroupConfig` apply path and immediate scheduler/PHY follow-up path.
- Added minimal instrumentation and safety guards in:
  - `openair2/LAYER2/NR_MAC_UE/config_ue.c`
  - `openair2/LAYER2/NR_MAC_UE/nr_ue_scheduler.c`
  - `openair1/PHY/NR_UE_TRANSPORT/pucch_nr.c`
- New markers:
  - `[CGDBG][LC]` before/after `configure_logicalChannelBearer` and null entries in LC list/qsort path
  - `[CGDBG][PUCCH-UCI]` for missing initial common PUCCH resource in overlap-check path
  - `[CGDBG][PUCCHPHY]` for invalid/suspicious format0 RE offset and symbol/input bounds
- Rebuilt `nr-uesoftmodem` with escalated build command and stored log at:
  - `test_log/build_logs/build_nr-uesoftmodem_2026-04-20_21-33-22_cgtrace-pucch-guard_escalated.log`

## 3GPP Spec Clauses Referenced
- TS 38.331 Section 5.3.5 — UE behavior during [RRCReconfiguration] and [masterCellGroup] apply sequence.
- TS 38.321 Section 5.11 — MAC behavior under configured operation and scheduler interaction post-reconfiguration.
- TS 38.213 Section 9.2.1 — Common PUCCH resource dependency for initial UCI transmission.
- TS 38.211 Section 6.3.2 — PUCCH format 0 symbol/resource mapping constraints.

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| `cmake --build --preset default --target nr-uesoftmodem` (sandbox) | Fail | Build infra | Failed due sandbox ccache temp path permission (`/run/user/1000/ccache-tmp`) |
| `cmake --build --preset default --target nr-uesoftmodem` (escalated) | Pass | Edited modules compile path | Build succeeded; log archived under `test_log/build_logs/` |
| Marker presence check (`rg` on edited files) | Pass | Instrumentation markers | All new `[CGDBG][LC]`, `[CGDBG][PUCCH-UCI]`, `[CGDBG][PUCCHPHY]` markers confirmed |

## Known Issues / Blockers
- Stage scan logs in `test_log/compiler_logs/mmtc_stage_scan_2026-04-20_21-09-33_ue*.log` are harness-centric and do not directly include detailed UE container `CellGroupConfig` traces.
- ⚠ Needs Verification: additional runtime run is needed to correlate new markers against survivor/failed cohorts in the exact first-3-second post-apply window.

## Next Step
- Run focused stage (`52` then `56`) with new binary + `MMTC_SEGV_BACKTRACE=1` and extract marker correlation timeline:
  - first `[CGDBG][LC] after configure_logicalChannelBearer`
  - first `[CGDBG][PUCCH-UCI] skip overlap check`
  - first `[CGDBG][PUCCHPHY] suspicious RE offset`
- Use timeline to choose the next minimal fix point (likely gating unsafe UCI scheduling branch until valid common resource is observed).
