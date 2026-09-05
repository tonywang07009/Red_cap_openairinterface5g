## Context

The experiment uses Ambient IoT Topology 2 with RedCap UEs as UE Readers. A UE cannot be the continuous carrier-wave (CW) source because its DRX/sleep behaviour is in scope. A gNB or independent CW node therefore supplies a tag-directed CW beam, while a selected UE wakes only for R2D and D2R operations. The radio baseline remains one tag and one primary R2D sender per transaction; AIOTF serializes those transactions across 60 tags and two UE Readers. The implementation is an explicit, disabled-by-default RFsim profile and does not claim standard A-IoT PHY/MAC/RRC support.

## Goals / Non-Goals

**Goals:**

- Prove a deterministic single-tag bistatic path: CW source to tag to UE Reader.
- Keep R2D short and UE-triggered, preserving observable UE sleep intervals.
- Use a single, versioned experimental profile for D2R Manchester plus SFS.
- Forward an accepted tag Inventory Report from UE to gNB and then through a minimal AIOTF correlation boundary.
- Add a bounded 60-tag, two-reader inventory using AIOTF-owned binding and deterministic single-tag transactions.
- Preserve RedCap sleep by activating one eligible reader normally and both readers only for an explicit diversity session.

**Non-Goals:**

- Claiming full 3GPP A-IoT compliance.
- Concurrent multi-tag anti-collision, production RF calibration, beamforming optimisation, ADM/NEF integration, or complete AIoT NAS security.
- Treating Docker startup, NR attach, or ping success as backscatter validation.

## Decisions

### Separate CW2D from R2D

The gNB/CW node continuously transmits Beam B toward the tag. The UE Reader receives Beam A over NR Uu and sends only bounded R2D control windows. This avoids making an energy-constrained RedCap UE a permanent CW source. An alternative in which gNB sends both CW and R2D was rejected for the first profile because it changes the gNB into the reader and leaves the UE only as a collector.

### Keep a deterministic tag simulator before RF integration

The first tag Docker process is a protocol and state simulator with explicit CW-present input, R2D input, D2R output, and deterministic faults. It is not evidence of RF propagation. This isolates framing and state failures before cross-layer work.

### Make D2R Manchester explicit and reversible

R2D uses Manchester `0 -> 10`, `1 -> 01`. The experimental D2R profile uses the same mapping after CRC and before OOK/BPSK plus small-frequency-shift modulation. The UE rejects `00`, `11`, and CRC-invalid payloads. TS 38.291 D2R does not mandate this line encoding; the profile is therefore namespaced and never advertised as standard behaviour.

### Gate AIOTF behind radio evidence

The minimal AIOTF owns request validation, Correlation ID, accepted/rejected/timeout state, and Inventory Report aggregation. It is added only after the UE Reader proves a CW-dependent D2R decode and Uu forwarding. This avoids concealing a missing PHY path behind core-network messages.

### Keep the radio transaction single-tag

A 60-tag inventory is decomposed into deterministic single-tag transactions. The first scheduler assigns one response slot to one tag and makes no anti-collision or concurrent-capacity claim. This reuses the proven Manchester, CRC, CW, and timeout path instead of adding a second PHY profile.

### Keep binding outside the tag

AIOTF owns `eligible_readers`, `active_readers`, `primary_reader`, a stable `reader_handle`, and `binding_epoch`. A tag carries no UE list and does not select its reader. The bounded initial binding is:

| Tag range | Eligible readers | Default primary |
|---|---|---|
| 1-20 | UE1 | UE1 |
| 21-30 | UE1, UE2 | UE1 |
| 31-40 | UE1, UE2 | UE2 |
| 41-60 | UE2 | UE2 |

Normal mode activates only the primary reader. Diversity mode activates both eligible readers for tags 21-40, but exactly one UE sends R2D and the other is a D2R observer. An exclusive binding does not silently fail over to an ineligible UE.

### Arbitrate reports without sample combining

AIOTF validates `correlation_id`, `session_id`, `tag_id`, `binding_epoch`, active-reader membership, deadline, and CRC outcome before accepting a report. The first valid report completes the tag result; later reports remain measurement evidence until the session deadline. Identical valid payloads are duplicates. Different valid payloads for the same result key create a conflict marker. AIOTF does not perform MRC, soft combining, or IQ combining.

### Keep UE report transport separate from AIOTF state

The UE sends a fixed 40-byte UDP report through its PDU-session TUN. This proves the UE-to-gNB/UPF forwarding path without overloading RRC or NAS. The current wire record contains reader, Tag, frame, slot, CRC-valid flag, and payload, but not `correlation_id`, `session_id`, or `binding_epoch`. The AIOTF endpoint must therefore add pending-transaction context before invoking full arbitration. Direct UDP-to-AIOTF correlation remains `[Needs Verification]`; the source-level AIOTF state machine and UE report transport are validated separately.

### Keep observer reception physically independent

`--aiot-t2-reader` and `--aiot-t2-observer` are mutually exclusive UE roles. Both roles may decode D2R and emit reports, but only the reader executes the R2D send branch. RFsim relays one Tag D2R packet independently to both default UE peers. No receiver result, IQ buffer, or soft information is shared between the UEs.

## Risks / Trade-offs

- [RFsim has no bistatic CW/backscatter seam] -> Inspect existing RFsim ownership before code. Stop at a baseband harness if no existing integration owner is available.
- [Strong CW leakage masks D2R] -> Require CW-on/CW-off and leakage-level test cases; retain SFS rather than relying on Manchester alone.
- [UE DRX timing drops R2D] -> Gate R2D transmission on explicit UE wake state and test before/during/after the window.
- [D2R Manchester doubles chips/effective bandwidth] -> Bound the first payload and record chip rate, SFS, and duration in the profile.
- [AIOTF scope expands into a new 5GC] -> Limit first implementation to one local inventory correlation contract; defer ADM, NEF, and security.
- [Both readers remain awake for every shared tag] -> Default to one active reader and require an explicit diversity policy for dual reception.
- [A stale report wins after failover] -> Increment `binding_epoch` and retain epoch-mismatched reports only as evidence.
- [Multiple tags collide in one response resource] -> Serialize one tag per response slot; add parallel resources only after measured evidence requires them.

## Enable and Rollback Plan

1. Keep the profile disabled by default; normal NR/RFsim uses no A-IoT option.
2. Enable RFsim with `--rfsimulator.options aiot_t2` on the gNB and participating UEs.
3. Select one reader or observer role per UE and provide bounded Tag/window/report parameters.
4. Run the single-tag radio path before using the 60-tag AIOTF scheduler.
5. Roll back by recreating gNB/UE services without the A-IoT options; no persistent CN schema is replaced.

## Remaining Questions

- The current logical CW node proves deterministic multiplication and routing, not calibrated RF power or two physical beams. Physical Beam A/Beam B isolation remains `[Needs Verification]`.
- The 100 ms experimental AIOTF timeout has no shared state with OAI paging. The existing NR RRC message owner exposes TS 38.304 PF/PO identity, but no NR MAC PCCH/PDCCH runtime consumer is connected. Timeout expiry coinciding with an over-the-air paging transmission remains `[Needs Verification]`.
- A future AIOTF UDP endpoint must define how it injects `correlation_id`, `session_id`, and `binding_epoch` into the current UE wire report before full arbitration.
