## Why

The RedCap UE must preserve its DRX/sleep behaviour and cannot be the continuous carrier-wave source for an Ambient IoT tag. A bounded Topology 2 experiment is needed to prove the gNB/CW-node to tag to UE-Reader path before any claim about A-IoT support is made. After the single-tag radio transaction is proven, the same transaction must support a bounded 60-tag, two-reader inventory without moving reader binding into the tag.

## What Changes

- Define an experimental Topology 2 profile: gNB or independent CW node supplies tag-directed continuous wave; the RedCap UE wakes only for R2D and D2R reader operations.
- Add a deterministic single-tag simulator contract, including R2D/D2R framing, CRC handling, CW state, and a tag Inventory Report.
- Add a bistatic CW/backscatter validation path from CW source through tag reflection to UE Reader, followed by UE-to-gNB reporting.
- Define a minimal AIOTF inventory correlation boundary after radio-path evidence exists.
- Extend AIOTF with a network-owned binding table for 60 tags and two UE Readers; keep each radio transaction single-tag and deterministically serialized.
- Select one primary R2D sender per tag transaction, optionally activate a second eligible UE as a D2R observer, accept the first binding-valid CRC-valid report, and retain other reports as evidence without MRC or soft combining.
- Mark Manchester encoding on D2R as experimental; it is not presented as current TS 38.291 behaviour.

## Capabilities

### New Capabilities

- `aiot-topology2-reader-profile`: Defines the bounded gNB-CW, RedCap UE Reader, single-tag radio transaction, and serialized multi-tag inventory contract.
- `aiot-bistatic-backscatter-validation`: Defines the evidence required to validate CW-dependent D2R detection, independent multi-reader decoding, and UE-to-gNB reporting.
- `aiotf-minimal-inventory-correlation`: Defines AIOTF request correlation, network-owned reader binding, per-session reader selection, report arbitration, failover, result, and timeout boundaries.

### Modified Capabilities

- None.

## Impact

- Expected affected areas: existing owners in `openair1/` for waveform/detection work, `openair2/` for UE Reader MAC/RRC control and reporting, and existing RFsim runtime configuration.
- `oai-cn5g/` or an existing core-network owner is affected only after the minimal AIOTF boundary is selected.
- A tag simulator/container is test support, not an A-IoT implementation claim.
- Exact OAI source owners, RFsim capability, and the gNB CW-beam implementation remain [Needs Verification].
