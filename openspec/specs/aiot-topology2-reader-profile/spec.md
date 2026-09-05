## Purpose

Define the bounded Topology 2 role separation, experimental D2R profile, and
single-tag transaction contract for RedCap UE Readers.

## Requirements

### Requirement: Topology 2 role separation
The experiment SHALL use a RedCap UE as UE Reader over NR Uu. The gNB or an independent CW node SHALL provide continuous tag-directed CW. The UE SHALL NOT provide continuous CW.

#### Scenario: UE Reader receives a bounded R2D operation
- **WHEN** the gNB grants an R2D operation window to a UE Reader
- **THEN** the UE wakes for the window, sends R2D, and returns to its configured inactive/sleep behaviour afterwards.

### Requirement: Experimental D2R Manchester profile
The experiment SHALL identify D2R Manchester as an experimental profile. The encoder SHALL map `0` to `10` and `1` to `01`; the decoder SHALL reject `00` and `11`.

#### Scenario: Invalid Manchester pair
- **WHEN** the UE Reader receives a D2R encoded stream containing `00` or `11`
- **THEN** it rejects the D2R payload and records an invalid-line-code outcome.

### Requirement: Bounded initial scope
Each radio transaction SHALL support one tag and one short Inventory Report only. A bounded multi-tag inventory SHALL reuse this transaction through deterministic serialization. It SHALL NOT claim concurrent multi-tag collision handling or 3GPP conformance.

#### Scenario: Bounded multi-tag request
- **WHEN** the profile receives an inventory request for Tags 1-60
- **THEN** AIOTF schedules one single-tag radio transaction per Tag and does not place two Tags in the same initial response slot.

#### Scenario: Request exceeds the bounded population
- **WHEN** the profile receives an unknown Tag or more than 60 distinct Tags
- **THEN** it rejects the unsupported Tag entries without silently expanding the configured population.
