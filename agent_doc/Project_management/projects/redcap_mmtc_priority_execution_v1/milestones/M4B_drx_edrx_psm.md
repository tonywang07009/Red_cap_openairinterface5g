# M4B DRX eDRX PSM

## Scope
- Connected DRX behavior.
- Idle and inactive eDRX support.
- PSM/NAS timer interface hooks and documentation.

## Out of Scope
- Full AMF/CN feature development unless explicitly promoted.
- xApp/rApp/dApp SDK implementation.
- mMTC scaling fixes unrelated to low-power behavior.

## 3GPP Spec Mapping
- TS 38.321 Section 5.7 — Connected DRX.
- TS 38.331 eDRX SIB1/RRC clauses: [Needs Verification].
- TS 24.501 T3324 / periodic registration / PSM behavior: [Needs Verification].

## Target Files
- `openair2/LAYER2/NR_MAC_UE/config_ue.c`
- `openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_dlsch.c`
- `openair2/LAYER2/NR_MAC_gNB/gNB_scheduler.c`
- `openair2/RRC/NR/rrc_gNB.c`
- `openair2/RRC/NR_UE/rrc_UE.c`
- RedCap gNB and UE YAML files referenced by `5g_rfsimulator_flexric_redcap/`.

## Implementation Tasks
- `M4B-T1`: Connected DRX config parse and runtime gating.
- `M4B-T2`: eDRX SIB1 encode/decode and UE state gating.
- `M4B-T3`: PSM timer hooks and CN dependency report.

## Flow Validation
- UE no longer logs `DRX not implemented! Configuration not handled!` when DRX is configured.
- DRX active/inactive periods are visible in logs.
- eDRX and PSM behavior must be marked as [compile-level], [flow-level], or [runtime-level].

## System Unit Tests
- `UT-M4B-001`: DRX config parse.
- `UT-M4B-002`: eDRX SIB1 encode/decode.
- `UT-M4B-003`: PSM timer hook state tracking.

## RFsim Runtime Tests
- `RT-M4B-001`: Connected DRX runtime smoke.
- `RT-M4B-002`: eDRX/PSM compile-level plus log-level validation until CN support is defined.

## Completion Criteria
- [source build PASS]
- [unit test PASS]
- [runtime or compile-level boundary stated]
- [spec traceability updated]
