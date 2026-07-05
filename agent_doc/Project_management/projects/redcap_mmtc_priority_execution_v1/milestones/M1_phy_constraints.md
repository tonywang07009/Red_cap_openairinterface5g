# M1 PHY Constraints

## Scope
- Enforce RedCap FR1 bandwidth, PRB, antenna, and half-duplex guard behavior.
- Keep this milestone focused on PHY/MAC constraint helpers and tests.

## Out of Scope
- RRC SIB1 RedCap IE encoding.
- RFsim multi-UE scaling.
- O-RAN xApp/rApp/dApp SDK work.

## 3GPP Spec Mapping
- TS 38.306 Section 4 — RedCap UE capability constraints. Exact subsection: [Needs Verification].
- TS 38.101-1 Section 5.3 — FR1 channel bandwidth and PRB limits. Exact subsection: [Needs Verification].

## Target Files
- `openair1/PHY/NR_TRANSPORT/`
- `openair2/LAYER2/NR_MAC_gNB/nr_mac_redcap*`
- Closest CTest targets for RedCap BWP/PHY helpers.

## Implementation Tasks
- `M1-T1`: Define FR1 RedCap PRB caps for 15 kHz and 30 kHz SCS.
- `M1-T2`: Enforce 1Rx/2Rx and single-Tx assumptions.
- `M1-T3`: Harden HD-FDD Tx/Rx gap guard.

## Flow Validation
- Verify invalid PRB and antenna combinations are rejected before runtime attach.
- Verify valid 20 MHz RedCap parameters pass initialization.

## System Unit Tests
- `UT-M1-001`: RedCap PRB cap helper test.
- `UT-M1-002`: HD-FDD guard helper test.

## RFsim Runtime Tests
- Runtime is not the primary gate for this milestone.
- Use `RT-M3-CASEA` and `RT-M3-CASEB` after M3 wiring.

## Completion Criteria
- [source build PASS]
- [unit test PASS]
- [spec mapping reviewed]
- [no unrelated runtime YAML/XML edits]
