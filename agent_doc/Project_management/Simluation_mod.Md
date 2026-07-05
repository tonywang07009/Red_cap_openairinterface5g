# RedCap mMTC Project Plan

## Milestone 1: Hardware / PHY Constraints
- Define FR1 bandwidth & PRB limits for RedCap (<= 20 MHz, SCS 15 kHz and 30 kHz).
- Antenna config: 1Rx mandatory, optional 2Rx, DL layers <= 2, no UL MIMO.
- Half-duplex FDD Type A timing assumptions.

## Milestone 2: RRC / SIB1 Support
- Design `RedCap_SIB1` struct (`redCap-ConfigCommon-r17`, `halfDuplexRedCapAllowed`, `cellBarredRedCap1Rx/2Rx`).
- Map each field to 3GPP clauses (TS 38.331).
- Integrate SIB1 handling into OAI RRC code.

## Milestone 3: BWP & CORESET#0
- Define RedCap BWP structs for DL/UL initial BWPs.
- Handle CORESET#0 special cases (Case A: full-cell; Case B: edge-only with `commonControlResourceSet`).
- Validate scheduler changes in simulation.

## Milestone 4: SDT / RRC_INACTIVE
- Add flags for RRC_INACTIVE support in gNB and UE.
- Design scheduler state machine for SDT (MsgA/Msg3 path).
- Add basic unit tests / simulation scenarios.

## Milestone 5: Integration & Throughput Targets
- Configure scenarios to hit 50–120 Mbps range under RedCap constraints.
- Run end-to-end simulations and log results.
- Document open gaps vs. full 3GPP RedCap compliance.