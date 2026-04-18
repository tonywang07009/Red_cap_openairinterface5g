# Work Daily Log
## Session Metadata
- Date: 2026-04-19 00:26
- Agent Session ID: N/A
- Task Slug: 64ue-full-attach-parallel-ping-validation

## Milestone & Sub-task Reference
- Milestone: [Milestone 5: Compose Rebase & mMTC Scaling]
- Sub-task: [Scalable mMTC path - 64-UE full attach and parallel ping validation]
- Status: [COMPLETED]

## What Was Done
- Reused the staged-launch validation harness in `[ci-scripts/redcap_mmtc_smoke_validation.sh]` with:
  `[MMTC_GNB_WARMUP=10]`,
  `[MMTC_UE_START_GAP=10]`,
  `[MMTC_FORWARD_PING_MODE=parallel]`,
  `[MMTC_RUN_REVERSE_PING=0]`.
- Executed the full [UE1..UE64] validation run and collected logs under:
  `test_log/compiler_logs/mmtc_smoke_2026-04-19_00-11-51_*`.
- Aggregated success counts for:
  `[RNTI]`,
  `[Registration Accept]`,
  `[PDU Session Establishment Accept]`,
  `[TUN creation]`,
  and `[parallel uplink ping]`.
- Classified the [59 failed UE] into:
  `[pre-RRCSetup crash]` and `[post-CellGroupConfig crash]`.
- Compared the new [wide-gap run] against the earlier [23:54:19 full-64 run] and confirmed that [launch pacing changes survivor distribution] but does not remove the root failure mode.

## 3GPP Spec Clauses Referenced
- [TS 38.321 Section 5.1] — [Random Access procedure]; used as the attach-stage reference for [RNTI] progression.
- [TS 38.331 Section 5.3.3] — [RRC connection establishment procedure]; used to map `RRCSetupRequest` / `RRCSetup` / `RRCSetupComplete`.
- [TS 38.331 Section 5.3.3.4] — [Reception of the RRCSetup by the UE]; used to split [pre-RRCSetup] versus [post-RRCSetup / CellGroupConfig] failures.

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| [64-UE launch with 10s warmup + 10s gap] | [Fail] | [N/A - runtime smoke] | Script finished with [59 failure(s)] |
| [RNTI evidence in UE logs] | [Fail] | [N/A - runtime smoke] | [5/64] success: [UE1, UE2, UE31, UE32, UE35] |
| [Registration Accept] | [Fail] | [N/A - runtime smoke] | [5/64] success: [UE1, UE2, UE31, UE32, UE35] |
| [PDU Session Establishment Accept] | [Fail] | [N/A - runtime smoke] | [5/64] success: [UE1, UE2, UE31, UE32, UE35] |
| [`oaitun_ue1` created] | [Fail] | [N/A - runtime smoke] | [5/64] success: [UE1, UE2, UE31, UE32, UE35] |
| [Parallel uplink ping] | [Fail] | [N/A - runtime smoke] | [5/64] success with [0% packet loss] |
| [Failure classification] | [Pass] | [N/A - runtime smoke] | [28] pre-RRCSetup crash; [31] post-CellGroupConfig crash |

## Known Issues / Blockers
- [Wide-gap staged launch] still leaves the system at [5/64] effective success, far below the target [64/64].
- [28 UE] crash before `Received NR_RRCSetup`, showing that some failures occur before the UE enters the explicit RRC setup success path.
- [31 UE] crash immediately after the first `Applying CellGroupConfig from gNodeB`, strongly pointing to the UE [RRC -> MAC] configuration handoff path.
- [⚠ Needs Verification]:
  The exact [C-level backtrace], offending pointer, or race window inside `nr_rrc_mac_config_req_cg()` and its caller chain is not yet captured.

## Next Step
- Instrument the UE [RRC -> MAC CellGroupConfig] path with focused diagnostics around:
  `nr_rrc_ue_process_masterCellGroup()`,
  `process_msg_rcc_to_mac()`,
  `nr_rrc_mac_config_req_cg()`,
  and `NR_UE_MAC_INST_t` state validity.
- Target the first proof point:
  explain why [UE33 / UE34 / UE36+] die immediately after the first `Applying CellGroupConfig from gNodeB` while [UE31 / UE32 / UE35] survive the same stage.
