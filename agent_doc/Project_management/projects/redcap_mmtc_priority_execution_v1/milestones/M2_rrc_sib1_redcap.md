# M2 RRC SIB1 RedCap

## Scope
- Encode and decode RedCap SIB1 support fields.
- Gate RedCap UE cell access from SIB1 barring fields.

## Out of Scope
- CORESET#0 Case A/B scheduler behavior.
- mMTC scaling and user-plane throughput.
- O-RAN SDK implementation.

## 3GPP Spec Mapping
- TS 38.331 Section 6.3.1 — system information structure. Exact RedCap IE mapping: [Needs Verification].
- TS 38.331 Section 6.3.2 — SIB1 and RedCap-related fields. Exact clause: [Needs Verification].

## Target Files
- `openair2/RRC/NR/`
- `openair2/RRC/NR_UE/`
- `openair2/LAYER2/NR_MAC_gNB/nr_radio_config.c`
- RedCap gNB and UE YAML files referenced by `5g_rfsimulator_flexric_redcap/`.

## Implementation Tasks
- `M2-T1`: Complete RedCap SIB1 encode/decode and 1Rx barring gate.
- `M2-T2`: Confirm UE-side SIB1 parse logs and cell selection behavior.

## Flow Validation
- SIB1 advertises RedCap support.
- UE parses RedCap SIB1 fields.
- 1Rx barring blocks attachment when configured.

## System Unit Tests
- `UT-M2-001`: RedCap SIB1 encode/decode.
- `UT-M2-002`: RedCap barring decision helper.

## RFsim Runtime Tests
- `RT-M2-001`: Single RedCap UE attach with SIB1 RedCap support.
- `RT-M2-002`: 1Rx barred UE rejects cell.

## Completion Criteria
- [source build PASS]
- [unit test PASS]
- [RFsim single-UE SIB1 flow PASS]
- [spec traceability updated]
