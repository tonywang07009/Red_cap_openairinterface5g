# Work Daily Log
## Session Metadata
- Date: 2026-04-20 11:55
- Agent Session ID: N/A
- Task Slug: redcap-m5-pucch-fallback-gate-validation

## Milestone & Sub-task Reference
- Milestone: RedCap mMTC [M5] CellGroupConfig / UE attach stability
- Sub-task: [PUCCH common fallback gate] implementation + [runtime A/B validation]
- Status: [COMPLETED]

## What Was Done
- Added [minimal behavioral gate] in `openair2/LAYER2/NR_MAC_UE/nr_ue_procedures.c`:
  - new env gate: `MMTC_PUCCH_COMMON_FALLBACK_BWP0`
  - new helper: search UL BWP by `bwp_id`
  - on initial PUCCH path, if current BWP has no `pucch_ResourceCommon`, fallback to BWP0 common config
  - added markers:
    - `[CGDBG][PUCCH-FALLBACK] use BWP0 common resource ...`
    - enriched NULL marker with `bwp_id` and `fallback` state
  - added range check for `pucch_ResourceCommon` index.
- Fixed logging format warnings (`NR_BWP_Id_t` uses `%ld`) and rebuilt `nr-uesoftmodem`.
- Found harness gap: env var was not forwarded into UE containers.
- Added env pass-through in `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/scripts/generate_mmtc_overlay.sh`:
  - `MMTC_PUCCH_COMMON_FALLBACK_BWP0: ${MMTC_PUCCH_COMMON_FALLBACK_BWP0:-0}`.
- Rebuilt local runtime images and reran `MMTC_SAMPLE_UES=33..40` validation.

## 3GPP Spec Clauses Referenced
- TS 38.331 Section 5.3.5 — [masterCellGroup] / [ServingCellConfig] reconfiguration path.
- TS 38.213 Section 9.2.1 — [initial PUCCH resource] selection dependency on common config.
- TS 38.321 Section 5.4.4 — UL control/procedure continuity impact when HARQ feedback signaling is broken.

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| `nr-uesoftmodem` build after fallback patch | Pass | Edited MAC file | Build success; format warnings fixed |
| Runtime smoke (`11-47-56`, gate set but env not forwarded) | Fail | UE33-40 | Marker shows `fallback=0`; TUN `3/8` |
| Runtime smoke (`11-51-37`, env forwarded) | Fail | UE33-40 | `PUCCH-FALLBACK use BWP0` hit on UE36-40; TUN `8/8`; ping still `0/8` |
| `pucch_ResourceCommon NULL` on UE36-40 after effective gate | Pass | UE36-40 docker logs | Count reduced from `{89,69,52,39,13}` to `0` |
| `configure failed` on UE36-40 after effective gate | Pass | UE36-40 docker logs | Count reduced to `0` |

## Known Issues / Blockers
- Current blocker moved to [UPF / user-plane path]:
  - all sampled UEs have TUN IP, but forward ping still `0/8`.
- Need next RCA on PDR/FAR/route path and gNB-UPF tunnel handling for multi-UE.

## Next Step
- Run targeted [UPF/N3/N4] RCA for UE33-40:
  - correlate gNB GTP-U tunnel setup and UPF PDR/FAR entries,
  - verify ext-dn return path and per-UE route consistency,
  - keep `MMTC_PUCCH_COMMON_FALLBACK_BWP0=1` as control baseline.
