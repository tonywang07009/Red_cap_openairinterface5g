# Work Daily Log
## Session Metadata
- Date: 2026-04-19 16:37
- Agent Session ID: N/A
- Task Slug: redcap-m5-cgcfg-nofree-defer-guard

## Milestone & Sub-task Reference
- Milestone: RedCap mMTC M5 [UE CellGroupConfig SIGSEGV RCA]
- Sub-task: Implement staged diagnostic hardening for CellGroupConfig free/guard path
- Status: [COMPLETED]

## What Was Done
- Added [MMTC_CGCFG_NOFREE] gate in `process_msg_rcc_to_mac()` to optionally skip `CellGroupConfig` free for diagnostics.
- Added [MMTC_CGCFG_DEFER_FREE_SLOTS] deferred-free mechanism (tick-based queue) in `L2_interface_ue.c`.
- Added guarded/null-safe checks for [current_UL_BWP/current_DL_BWP] in:
  - `configure_maccellgroup()`
  - `handle_mac_uecap_info()`
  - `nr_rrc_mac_config_req_cg()` tag-timer / UE capability apply path
- Added explicit `[CGDBG]` guard-path logs to distinguish normal vs guarded apply.
- Kept default behavior unchanged when env vars are unset (`nofree=0`, `defer=0` => immediate free).

## 3GPP Spec Clauses Referenced
- TS 38.331 Section 5.3.5 — RRC Reconfiguration / CellGroupConfig handling sequence
- TS 38.321 Section 5.x (MAC configuration application timing) — MAC-side config safety during reconfiguration

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| Build `nr-uesoftmodem` after patch | Pass | compile only | `test_log/build_logs/build_nr-uesoftmodem_2026-04-19_16-37-15_escalated.log` |
| In-sandbox build attempt | Fail | compile only | ccache tmp write denied in sandbox (`/run/user/1000/...`), resolved by escalated build |

## Known Issues / Blockers
- Runtime validation for new env gates (`MMTC_CGCFG_NOFREE` / `MMTC_CGCFG_DEFER_FREE_SLOTS`) not executed in this step.
- Deferred free currently uses message-processing tick; if no later MAC messages arrive, deferred nodes may remain until process exit.

## Next Step
- Run focused runtime validation with local image (`REGISTRY=`, `TAG=latest`) and set:
  - `MMTC_CGCFG_NOFREE=1` (A/B test)
  - `MMTC_CGCFG_DEFER_FREE_SLOTS=8` (or 16)
- Compare SIGSEGV stage distribution against baseline (`2026-04-19_15-17-13`) to confirm/deny UAF hypothesis.
