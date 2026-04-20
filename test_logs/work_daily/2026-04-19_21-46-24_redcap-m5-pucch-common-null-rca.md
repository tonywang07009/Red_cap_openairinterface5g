# Work Daily Log
## Session Metadata
- Date: 2026-04-19 21:46
- Agent Session ID: N/A
- Task Slug: redcap-m5-pucch-common-null-rca

## Milestone & Sub-task Reference
- Milestone: RedCap mMTC [M5] CellGroupConfig / UE attach stability
- Sub-task: [CellGroupConfig->MAC->PUCCH] code-level RCA + minimal safety/instrumentation patch
- Status: [COMPLETED]

## What Was Done
- Added [dangling pointer safety] in `configure_dedicated_BWP_ul()`:
  - release after free now sets `bwp->pucch_Config = NULL`, `bwp->pusch_Config = NULL`, `bwp->srs_Config = NULL`.
- Added [PUCCH PHY boundary guard]:
  - `openair1/SCHED_NR_UE/pucch_uci_ue_nr.c`: drop invalid PUCCH symbol range with `[CGDBG][PUCCHPHY]`.
  - `openair1/PHY/NR_UE_TRANSPORT/pucch_nr.c`: guard format0 `nr_of_symbols`/symbol window before generation.
- Added [PUCCH scheduler RCA marker]:
  - `openair2/LAYER2/NR_MAC_UE/nr_ue_scheduler.c`: when `nr_ue_configure_pucch()` fails, log `init_id/res/O_ACK/O_SR/O_CSI/pdu fields`.
- Added [BWP null defensive log]:
  - `openair2/LAYER2/NR_MAC_UE/nr_ue_scheduler.c`: skip CSI-IM when `current_DL_BWP == NULL`.
- Added [PUCCH common source markers]:
  - `openair2/LAYER2/NR_MAC_UE/config_ue.c`: log `ul_common->pucch_ConfigCommon` and resulting `bwp->pucch_ConfigCommon->pucch_ResourceCommon`.
  - `openair2/RRC/NR_UE/rrc_UE.c`: log decoded `scd/ul_cfg/initialUplinkBWP` PUCCH setup-release presence.
- Rebuilt local images and validated runtime with `MMTC_SAMPLE_UES=33..40`, `MMTC_CGCFG_NOFREE=1`, `MMTC_SEGV_BACKTRACE=1`.

## 3GPP Spec Clauses Referenced
- TS 38.331 Section 5.3.5 — [RRCReconfiguration] and [masterCellGroup] processing.
- TS 38.213 Section 9.2.1 — [PUCCH resource selection] procedure.
- TS 38.211 Section 6.3.2 — [PUCCH format 0/1] sequence/resource mapping constraints.

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| `nr-uesoftmodem` local build (new patch) | Pass | Edited files compiled | No compile error after patch refinement |
| Runtime smoke `UE33-40` (prefix `21-35-18`) | Fail | Target path + markers | No SIGSEGV; TUN only `UE33-35` |
| Runtime smoke `UE33-40` (prefix `21-42-45`) | Fail | Target path + new source markers | No SIGSEGV; TUN only `UE33-35` |
| Crash regression (`SIGSEGV`, `nr_generate_pucch0`) | Pass | UE33-40 logs | No `caught SIGSEGV` / no backtrace hit |
| PUCCH failure marker correlation | Fail | UE36-40 | `pucch_ResourceCommon is NULL` count matches `configure failed` count |

## Known Issues / Blockers
- UE36~UE40 repeatedly hit:
  - `[CGDBG][PUCCH] pucch_ResourceCommon is NULL for initial PUCCH`
  - `[CGDBG][PUCCH] configure failed ... init_id=0 res=(nil) O_ACK=1`
- `configure_common_BWP_ul()` logs show `bwp_id=1` path repeatedly has `resourceCommon=(nil)` while `bwp_id=0` has valid `resourceCommon`.
- This causes [initial PUCCH cannot be configured] -> [UL control failure] -> [no stable attach/ping].

## Next Step
- Implement minimal [behavioral fix proposal] in `nr_ue_configure_pucch()`:
  - when `current_UL_BWP->pucch_ConfigCommon->pucch_ResourceCommon == NULL` on initial PUCCH path, attempt controlled fallback to [UL BWP0 common resourceCommon] with explicit `[CGDBG][PUCCH-FALLBACK]` marker.
- Re-run `UE33-40` and compare:
  - fallback hit count,
  - `configure failed` count,
  - TUN + ping success deltas.
