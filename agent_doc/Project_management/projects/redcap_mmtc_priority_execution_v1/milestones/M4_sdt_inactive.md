# M4 SDT Inactive

## Scope
- RedCap SDT scheduler FSM.
- RRC_INACTIVE state tracking hooks.
- Transition logging for educational and validation reports.

## Out of Scope
- DRX/eDRX/PSM timer implementation.
- mMTC scaling performance.
- O-RAN SDK work.

## 3GPP Spec Mapping
- TS 38.321 SDT procedure clause: [Needs Verification].
- TS 38.331 RRC_INACTIVE state behavior: [Needs Verification].

## Target Files
- `openair2/LAYER2/NR_MAC_gNB/nr_mac_sdt_fsm.c`
- `openair2/LAYER2/NR_MAC_gNB/nr_mac_sdt_fsm.h`
- `openair2/RRC/NR/`
- `openair2/RRC/NR_UE/`
- Closest SDT FSM test target.

## Implementation Tasks
- `M4-T1`: Wire `sdt_scheduler_fsm()` into scheduler data path with transition logs.
- `M4-T2`: Add MsgA/Msg3 path selection tests.

## Flow Validation
- FSM sequence: `IDLE -> SDT_TRIGGER -> MsgA_PATH | Msg3_PATH -> SDT_ACTIVE -> INACTIVE`.
- Transition log must match expected path.

## System Unit Tests
- `UT-M4-001`: SDT FSM MsgA path.
- `UT-M4-002`: SDT FSM Msg3 fallback path.

## RFsim Runtime Tests
- Runtime validation is deferred until M5 user-plane baseline is stable.

## Completion Criteria
- [source build PASS]
- [unit test PASS]
- [transition log evidence preserved]
- [spec uncertainty marked]
