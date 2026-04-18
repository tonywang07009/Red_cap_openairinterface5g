# Work Daily Log
## Session Metadata
- Date: 2026-04-18 23:13
- Agent Session ID: N/A
- Task Slug: mmtc-smoke-staggered-ue-launch

## Milestone & Sub-task Reference
- Milestone: Compose Rebase & mMTC Scaling
- Sub-task: Stabilize the fixed-UE smoke validation path by staging sampled UE startup and re-validating UE1 baseline plus RedCap UE2/UE32
- Status: COMPLETED

## What Was Done
- Re-read [Milestone 5] in `agent_doc/Project_management/Simluation_v2.md` and kept the scope on the [fixed-UE validation path] and [scalable mMTC compose] track.
- Re-ran the aligned smoke flow with `MMTC_SAMPLE_UES=1,2,32` and confirmed the previous [RedCap-common user-plane blockage] no longer reproduced.
- Localized the new failure shape:
  - [UE2] and [UE32] completed [Registration Accept] / [PDU Session Establishment Accept] / [bidirectional ping].
  - [UE1] exited with [ExitCode 139] immediately after the [CellGroupConfig] application phase.
- Correlated the failure with gNB-side attach pressure:
  - latest failing run showed [Cannot find free vrb_map], [exceeded RA window], and forced [RRC Release] markers in `mmtc_smoke_2026-04-18_22-59-30_gnb.log`.
- Ran an [A/B isolation] smoke using `MMTC_SAMPLE_UES=1` and proved [UE1-only] passes [attach + bidirectional ping], ruling out a baseline-only YAML incompatibility.
- Patched `ci-scripts/redcap_mmtc_smoke_validation.sh` to:
  - add [GNB_WARMUP] and [UE_START_GAP] environment knobs,
  - start [nearRT-RIC + gNB] first,
  - then launch sampled UE services sequentially.
- Re-ran the full `MMTC_SAMPLE_UES=1,2,32` smoke after the patch and verified:
  - [UE1] got `10.0.0.2`,
  - [UE2] got `10.0.0.3`,
  - [UE32] got `10.0.0.4`,
  - all three passed [forward ping] and [reverse ping].
- Generated a unit-test learning report at `test_log/report/redcap_mmtc_smoke_staggered_launch_report_2026-04-18_23-13-12.md`.

## 3GPP Spec Clauses Referenced
- TS 38.321 Section 5.1 — [Random Access procedure]; relevant to the observed [ra-ResponseWindow] / concurrent attach pressure.
- TS 38.321 Section 5.1.5 — [Contention Resolution]; relevant to [Msg3] completion and unstable concurrent RA behavior.
- TS 38.331 Section 5.3.3 — [RRC connection establishment]; relevant to [RRCSetup] / [RRCSetupComplete] around the UE1 crash window.
- TS 38.331 Section 5.3.5.5 — [Cell group configuration]; relevant to the [masterCellGroup] / [CellGroupConfig] application path.
- TS 38.331 Section 6.3.1 — [SIB1 / RedCap-ConfigCommonSIB-r17]; relevant to preserving the RedCap attach path while fixing validation determinism.
- TS 38.306 Section 4.2.21.1 — [Definition of RedCap UE]; relevant to RedCap capability boundaries kept intact during this mitigation.

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| Focused smoke before mitigation `MMTC_SAMPLE_UES=1,2,32` | Fail | N/A | [UE1] crashed with [ExitCode 139]; [UE2/UE32] passed attach and ping; gNB showed [vrb_map] / [RA window] pressure |
| Isolation smoke `MMTC_SAMPLE_UES=1` | Pass | N/A | [UE1-only] passed [attach + bidirectional ping], proving the failure needs concurrent startup |
| `bash -n ci-scripts/redcap_mmtc_smoke_validation.sh` | Pass | N/A | Sequential launch patch has valid shell syntax |
| Focused smoke after mitigation `MMTC_SAMPLE_UES=1,2,32` | Pass | N/A | [UE1/UE2/UE32] all passed [Registration Accept] / [PDU Session Establishment Accept] / [TUN bring-up] / [forward+reverse ping] |

## Known Issues / Blockers
- The [concurrent UE1 SIGSEGV] is mitigated for validation by staged startup, but its exact [C-level root cause] is still not proven with a backtrace.
- The mitigation is currently tuned for the sampled validation set [UE1/UE2/UE32]; larger concurrent sets may need a different [GNB_WARMUP] or [UE_START_GAP].
- No PHY/MAC/RRC behavior-changing patch was applied in this sub-task; the change is confined to the validation harness.

## Next Step
- Re-run the smoke with a slightly tighter [UE_START_GAP] to determine the minimum stable attach spacing for [UE1/UE2/UE32].
- If strict concurrent startup is still a project requirement, add targeted diagnostics around the [RRCSetup -> CellGroupConfig -> MAC handoff] path to capture a backtrace for the original [ExitCode 139].
- Extend the staged validation pattern to a larger sampled set before scaling the same harness back toward [32 UE] and [64 UE] smoke evidence.
