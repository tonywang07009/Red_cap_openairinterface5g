# Work Daily Log
## Session Metadata
- Date: 2026-04-19 19:44
- Agent Session ID: N/A
- Task Slug: redcap-m5-fifo-crash-window-markers

## Milestone & Sub-task Reference
- Milestone: RedCap mMTC runtime stabilization (M5)
- Sub-task: Add minimal FIFO crash-window markers around `process_msg_rcc_to_mac()` callsites
- Status: [COMPLETED]

## What Was Done
- Added [before/after/del] FIFO markers at `process_msg_rcc_to_mac()` callsite in:
  - `executables/nr-ue.c` (`UE_dl_preprocessing`)
  - `executables/nr-ue.c` (`UE_thread` sync/MIB path)
  - `executables/nr-uesoftmodem.c` (UE init drain path)
- Marker payload includes:
  - `elt` pointer snapshot
  - `data` pointer snapshot
  - `payload_type` snapshot
- Markers use `[CGDBG][UE x][FIFO] ...` prefix and avoid post-free dereference.
- Built target `nr-uesoftmodem` successfully after patch.

## 3GPP Spec Clauses Referenced
- ⚠ Needs Verification: TS 38.331 Section 5.3.5 (RRC reconfiguration apply sequence context)
- ⚠ Needs Verification: TS 38.321 (MAC processing timing/context after RRC signaling)

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| `cmake --build --preset default --target nr-uesoftmodem` | Pass | Compile/link | New markers compiled in `nr-ue.c` and `nr-uesoftmodem.c` |

## Known Issues / Blockers
- Docker runtime logs will only show these new markers after runtime image rebuild with latest workspace code.

## Next Step
- Rebuild local runtime images, run focused UE33-36 smoke, and confirm `[CGDBG][FIFO]` marker ordering relative to post-apply SIGSEGV.
