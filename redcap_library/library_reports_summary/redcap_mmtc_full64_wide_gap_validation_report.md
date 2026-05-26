# RedCap mMTC 64-UE Wide-Gap Validation Report

## Session Metadata
- Date: 2026-04-19 00:26
- Milestone: [Milestone 5: Compose Rebase & mMTC Scaling]
- Sub-task: [64-UE full attach and parallel ping validation]
- Validation Command:
  `env MMTC_TOTAL_UES=64 MMTC_SAMPLE_UES=1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64 MMTC_START_XAPP=0 MMTC_FORWARD_PING_MODE=parallel MMTC_RUN_REVERSE_PING=0 MMTC_GNB_WARMUP=10 MMTC_UE_START_GAP=10 redcap_interface/redcap_mmtc_smoke_validation.sh`
- Primary Log Prefix:
  `test_log/compiler_logs/mmtc_smoke_2026-04-19_00-11-51_*`

## 1. Technical Background
- [Goal]:
  Validate whether the [scalable mMTC path] can reach the Milestone 5 [64 UE] follow-up target with [attach], [PDU session], and [simultaneous uplink ping] stability.
- [Observed Runtime Shape]:
  The [gNB warmup] and [10-second inter-UE launch gap] reduce startup burst pressure, but they do not remove the dominant failure mode.
- [Current Failure Signature]:
  Most failing UEs terminate with [ExitCode 139].
  The failures split into:
  [pre-RRCSetup crash] and [post-CellGroupConfig crash].
- [Implication]:
  The limiting factor is no longer the [Compose launch harness] alone.
  The evidence points to a [UE-side runtime / configuration application crash] during multi-UE attach, especially near the first [CellGroupConfig] handoff.

## 2. Key C Functions / Data Structures Utilized In This Module
- `[openair2/RRC/NR_UE/rrc_UE.c]` → `nr_rrc_process_rrcsetup()`
- `[openair2/RRC/NR_UE/rrc_UE.c]` → `nr_rrc_ue_process_masterCellGroup()`
- `[openair2/RRC/NR_UE/L2_interface_ue.c]` → `process_msg_rcc_to_mac()`
- `[openair2/LAYER2/NR_MAC_UE/config_ue.c]` → `nr_rrc_mac_config_req_cg()`
- `[openair2/LAYER2/NR_MAC_UE/main_ue_nr.c]` → `get_mac_inst()`
- `[NR_CellGroupConfig_t]` → UE-side decoded cell-group configuration payload
- `[NR_UE_MAC_INST_t]` → UE MAC runtime state used during `CellGroupConfig` application

## 3. Test Results Summary Table
| Test Item | Pass / Fail | Code Coverage | Notes |
|-----------|-------------|---------------|-------|
| [64-UE staged launch with 10s warmup + 10s gap] | [Fail] | [N/A - runtime smoke] | Script completed with [59 failures] |
| [RNTI acquisition] | [Fail] | [N/A - runtime smoke] | Only [UE1, UE2, UE31, UE32, UE35] showed `RNTI ... stats` |
| [Registration Accept] | [Fail] | [N/A - runtime smoke] | Same [5 UE] reached NAS registration success |
| [PDU Session Establishment Accept] | [Fail] | [N/A - runtime smoke] | Same [5 UE] obtained UE IPv4 |
| [TUN interface creation] | [Fail] | [N/A - runtime smoke] | Same [5 UE] created `oaitun_ue1` |
| [Parallel uplink ping to gNB / core-side 10.0.0.1] | [Fail] | [N/A - runtime smoke] | [5 UE] succeeded concurrently with [0% packet loss] |
| [Failure-layer classification] | [Pass] | [N/A - runtime smoke] | [28 UE] crashed before `Received NR_RRCSetup`; [31 UE] crashed after first `Applying CellGroupConfig from gNodeB` |

## 4. 3GPP Specification Mapping
- `[TS 38.321 Section 5.1]`:
  [Random Access procedure].
  Relevance: used here as the validation reference for whether the UE progresses far enough to obtain a working radio identity and continue attach.
- `[TS 38.331 Section 5.3.3]`:
  [RRC connection establishment procedure].
  Relevance: aligns with the observed `RRCSetupRequest` / `RRCSetup` / `RRCSetupComplete` flow in UE logs.
- `[TS 38.331 Section 5.3.3.4]`:
  [Reception of the RRCSetup by the UE].
  Relevance: this is the transition point immediately before the failing branch splits into [success path] versus [post-CellGroupConfig crash].

## 5. Practice Exercises
- [Basic]:
  Explain why a UE can reach `Received NR_RRCSetup` but still fail before `Received Registration Accept`.
- [Applied]:
  Design one additional runtime marker inside `nr_rrc_mac_config_req_cg()` that would help distinguish [null state], [decode issue], and [race condition].
- [Advanced]:
  Propose a minimal multi-UE experiment matrix that can separate [launch-order sensitivity], [UE capability sensitivity], and [CellGroupConfig application sensitivity] without changing CN topology.

## Modification Logs
- `[redcap_interface/redcap_mmtc_smoke_validation.sh]`:
  Added `[MMTC_GNB_WARMUP]` and `[MMTC_UE_START_GAP]` controls for staged UE startup.
- `[redcap_interface/redcap_mmtc_smoke_validation.sh]`:
  Added `[MMTC_FORWARD_PING_MODE=parallel]` and `[MMTC_RUN_REVERSE_PING]` controls for concurrent ping validation.
- `[redcap_interface/redcap_mmtc_smoke_validation.sh]`:
  Added shared user-plane snapshots and per-UE state capture to improve runtime evidence collection.

## Conclusion
- [Validated]:
  The current harness can now prove exactly which UE subset survives a [64-UE] run and can perform [parallel uplink ping].
- [Not Validated]:
  The system does not meet the [64/64 attach + PDU + simultaneous ping] target.
- [Decision]:
  The next engineering step should move to [code-level crash diagnosis] in the UE [RRC -> MAC CellGroupConfig] path, not further launch-gap tuning alone.
