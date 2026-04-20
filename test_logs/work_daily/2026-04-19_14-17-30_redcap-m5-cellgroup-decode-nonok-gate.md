# Work Daily Log
## Session Metadata
- Date: 2026-04-19 14:17
- Agent Session ID: N/A
- Task Slug: redcap-m5-cellgroup-decode-nonok-gate

## Milestone & Sub-task Reference
- Milestone: [Milestone 5: Compose Rebase & mMTC Scaling]
- Sub-task: [UE CellGroupConfig decode gate hardening in RRC->MAC first-apply path]
- Status: [COMPLETED]

## What Was Done
- Applied a minimal behavior fix in `openair2/RRC/NR_UE/rrc_UE.c` (`nr_rrc_ue_process_masterCellGroup()`):
  - changed policy from [allow partial decode when `consumed > 0`] to [reject any `dec_rval.code != RC_OK`].
  - added explicit reject marker:
    `[CGDBG][UE x] reject CellGroupConfig decode (...)`.
  - added `ASN_STRUCT_FREE(asn_DEF_NR_CellGroupConfig, cellGroupConfig)` before return on reject path to avoid leak.
- Kept the prior [CGDBG] instrumentation unchanged in:
  - `openair2/RRC/NR_UE/L2_interface_ue.c`
  - `openair2/LAYER2/NR_MAC_UE/config_ue.c`
  so next runtime can correlate decode quality with MAC-entry state.

## 3GPP Spec Clauses Referenced
- TS 38.331 Section 5.3.3.4 — [Reception of the RRCSetup by the UE], first `masterCellGroup` apply stage.
- TS 38.331 Section 5.3.5 — [RRCReconfiguration procedure] context for `masterCellGroup` update handling.

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| Build `cmake --build --preset default --target nr-uesoftmodem` | Pass | Build-only | `rrc_UE.c` rebuilt; `nr-uesoftmodem` linked |
| Runtime 64-UE replay with new decode gate | Not Run | N/A | Pending host/container rerun |

## Known Issues / Blockers
- Runtime root-cause confirmation still needs one fresh 64-UE run with [CGDBG] markers.
- This patch may convert some former [late SIGSEGV] cases into [early decode reject] cases; expected and useful for triage.

## Next Step
- Re-run the existing 64-UE harness and classify failing UEs into:
  - `[CGDBG decode reject]`,
  - `[CGDBG current_UL_BWP NULL]`,
  - `[other assert / crash]`.
- If failures concentrate on decode reject:
  - compare failing UE `masterCellGroup` payload quality/timing against surviving UEs, then decide whether to add guarded retry or stricter decode diagnostics upstream.
