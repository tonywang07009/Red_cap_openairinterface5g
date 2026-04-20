# Work Daily Log
## Session Metadata
- Date: 2026-04-19 14:00
- Agent Session ID: N/A
- Task Slug: redcap-m5-cellgroupconfig-cgdbg-rca

## Milestone & Sub-task Reference
- Milestone: [Milestone 5: Compose Rebase & mMTC Scaling]
- Sub-task: [Code-level RCA instrumentation on UE RRC -> MAC CellGroupConfig first-apply path]
- Status: [COMPLETED]

## What Was Done
- Added [CGDBG] decode/structure markers in `openair2/RRC/NR_UE/rrc_UE.c` at `nr_rrc_ue_process_masterCellGroup()`:
  - decode result (`dec_rval.code`, `consumed`, payload size)
  - decoded pointer summary (`spCellConfig`, `spCellConfigDedicated`, `mac_CellGroupConfig`, RLC bearer lists)
  - enqueue marker with queue pointer and `hfn/frame`.
- Added [CGDBG] handoff/free markers in `openair2/RRC/NR_UE/L2_interface_ue.c` at `process_msg_rcc_to_mac()`:
  - dequeue marker (`cfg`, `UE_NR_Capability`, `hfn/frame`)
  - explicit non-null assert before invoking MAC config
  - free marker after `nr_rrc_mac_config_req_cg()`.
- Added [CGDBG] entry/exit and guard assertions in `openair2/LAYER2/NR_MAC_UE/config_ue.c` at `nr_rrc_mac_config_req_cg()`:
  - `cell_group_config != NULL`
  - `get_mac_inst(module_id) != NULL`
  - post-BWP marker (`current_UL_BWP`, `current_DL_BWP`, `tag_Id`)
  - assert on `current_UL_BWP` before TAG timer access
  - assert on `TAG_list.array[j] != NULL`.
- Collected one failing-vs-surviving evidence pair from existing runtime logs:
  - failing UE sample (`ue33`) exits right after first `Applying CellGroupConfig from gNodeB`
  - surviving UE sample (`ue31`) continues through reconfiguration and long-run UL stats.

## 3GPP Spec Clauses Referenced
- TS 38.331 Section 5.3.3.4 — [Reception of the RRCSetup by the UE]; used to bound the first `masterCellGroup` apply stage.
- TS 38.331 Section 5.3.5 — [RRCReconfiguration procedure] and `masterCellGroup` handling context. (⚠ Needs Verification: exact subclause index to be pinned in next pass)
- TS 38.321 Section 5.2 — [Time Alignment Timer behavior], relevant to `TAG_list` / `current_UL_BWP->scs` timer application path.

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| Focused build `cmake --build --preset default --target nr-uesoftmodem` (sandbox run) | Fail | N/A | Blocked by sandbox FS restriction: `ccache` could not write `/run/user/1000/ccache-tmp` |
| Focused build `cmake --build --preset default --target nr-uesoftmodem` (escalated rerun) | Pass | Build-only | Touched objects compiled, `nr-uesoftmodem` linked successfully |
| Runtime repro with new [CGDBG] markers | Not Run | N/A | Pending host/container rerun with 64-UE scenario |

## Known Issues / Blockers
- Runtime RCA is still pending one new 64-UE rerun to capture [CGDBG] markers at crash point.
- Most suspicious path currently:
  - `nr_rrc_ue_process_masterCellGroup()` accepts non-`RC_OK` decode results when `consumed > 0`,
  - then forwards potentially partial `CellGroupConfig` into MAC.
- Second suspicious path:
  - `nr_rrc_mac_config_req_cg()` previously dereferenced `mac->current_UL_BWP->scs` without explicit guard when TAGs exist.

## Next Step
- Run the existing 64-UE validation harness once with this patch and collect markers for:
  - `[CGDBG] decode non-OK`
  - `[CGDBG] post-BWP ... curUL=(nil)`
  - any `AssertFatal` from `get_mac_inst == NULL` / `current_UL_BWP == NULL` / `TAG_list.array[j] == NULL`.
- If `decode non-OK` appears for failing UEs, propose the smallest behavior fix:
  - reject non-OK decode before forwarding to MAC (`dec_rval.code != RC_OK` early return with counter/log).
