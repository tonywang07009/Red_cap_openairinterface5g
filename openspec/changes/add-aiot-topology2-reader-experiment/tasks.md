## 1. Review and Contract Gate

- [x] 1.1 Trace existing gNB, UE, RFsim, and container owners with `symdex`; classify each required CW, backscatter, R2D, D2R, and UE-to-gNB hook as implemented, partial, dormant, or missing.
- [x] 1.2 Extract and record exact local clauses for Topology 2, UE Reader, R2D/D2R PHY/MAC, CW, and AIOTF; retain `[Needs Verification]` for unresolved mappings.
- [x] 1.3 Freeze `aiot-topology2-reader-profile-v1`: one tag, Beam A Uu, Beam B CW, UE-bounded R2D, experimental D2R Manchester plus SFS, payload limit, CRC, timeout, and fault cases.
- [x] 1.4 Select the smallest existing RFsim integration owner or stop with a documented missing-seam finding; do not create a parallel radio implementation.
- [x] 1.5 Define Gate 1 evidence: valid Manchester round-trip, invalid `00`/`11`, CRC failure, CW-on acceptance, CW-off rejection, and no R2D while UE is asleep.
- [x] 1.6 Freeze the bounded AIOTF extension: 60 Tags, two stable reader handles, binding ranges 1-20/21-40/41-60, balanced 30/30 default primary load, normal/diversity modes, and one primary R2D sender per transaction.
- [x] 1.7 Freeze report arbitration and scheduling: binding epoch, deterministic one-Tag-per-response-slot ordering, first binding-valid CRC-valid result, duplicate/conflict evidence, and no MRC/soft combining.

## 2. Implementation and Runtime Gate

- [x] 2.1 Add the smallest deterministic single-tag simulator/container through an existing project owner; implement explicit CW-present state, bounded R2D input, D2R output, and deterministic valid/invalid/CRC fault modes.
- [x] 2.2 Implement the experimental R2D and D2R profile in the selected owners: `0 -> 10`, `1 -> 01`, invalid-pair rejection, CRC validation, and retained D2R SFS.
- [x] 2.3 Implement the selected CW/backscatter seam from gNB or CW node through tag reflection to UE Reader; retain a disable switch and leave normal NR behaviour unchanged.
- [x] 2.4 Implement UE Reader wake-window gating, short R2D transmission, D2R detection, and UE-to-gNB report forwarding.
  - [x] 2.4.1 Add a bounded RFsim R2D control-send and D2R control-receive seam; keep it disabled outside the `aiot_t2` profile.
  - [x] 2.4.2 Gate one short Inventory R2D transmission on connected MAC state, active DRX state, and an explicit bounded Reader window.
  - [x] 2.4.3 Decode captured D2R Manchester plus SFS, reject invalid line code/CRC/length, and emit a report-ready marker.
  - [x] 2.4.4 Select and implement the experimental UE-to-gNB report transport without overloading an unrelated RRC or NAS message.
- [x] 2.5 Implement the minimal AIOTF correlation boundary only after task 2.4 passes: request validation, Correlation ID, completed/rejected/timeout result, and report association.
- [x] 2.6 Extend the existing AIOTF owner with the 60-Tag binding table; validate stable reader handles, eligible/active/primary roles, binding epoch, and the exact UE1/UE2 ranges without storing reader membership in the Tag.
- [x] 2.7 Implement normal-mode reader selection with one active primary and diversity-mode selection with one R2D primary plus an optional D2R observer for Tags 21-40.
- [x] 2.8 Implement deterministic serialization of the 60-Tag inventory as single-tag transactions; do not implement concurrent anti-collision until runtime evidence requires it.
- [x] 2.9 Implement report arbitration: validate correlation/session/Tag/epoch/reader/deadline/CRC, complete on the first valid report, retain duplicates and invalid reports as evidence, and mark conflicting valid payloads.
- [x] 2.10 Implement shared-tag failover before R2D transmission by selecting the other eligible reader and incrementing binding epoch; reject silent failover for exclusive bindings.
- [x] 2.11 Add the nearest focused checks and run affected UE/gNB builds. Validate zero/one/60/61 Tags, ranges 20/21 and 40/41, empty eligible-reader sets, primary membership, stale epochs, duplicate and conflicting valid reports, wake/timeout boundaries N-1/N/N+1, simultaneous Tag arrival, failover/report races, and timer expiry at a paging occasion.
  - [x] 2.11.1 Validate all listed Tag, binding, report, wake/timeout, simultaneous-arrival, and failover/report-race boundaries; run affected UE/gNB/RFsim/AIOTF builds.
  - [x] 2.11.2 Validate experimental AIOTF timer expiry coinciding with an NR paging occasion after a real NR paging occasion owner is implemented or exposed; the existing NR RRC message owner now exposes PF/PO identity, while exact NR MAC PCCH/PDCCH delivery remains `[Needs Verification]`.
    - Evidence: `review/continuation_review_evidence.md` records the focused PF/PO seam, timer boundary, affected builds, and the remaining over-the-air paging limitation.
- [x] 2.12 Run the runtime ladder: single-tag protocol simulator, baseband/CW proof, single-reader RFsim evidence, two-reader diversity evidence, then serialized 60-Tag evidence. Stop at the first failed layer and report it without a PASS claim.

## 3. Documentation and Evidence Gate

- [x] 3.1 Record the finalized profile, all non-standard D2R Manchester decisions, CW assumptions, and known non-goals in the A-IoT reference route.
- [x] 3.2 Produce a reproducible operator guide for the single-tag scenario, including inputs, commands, expected UE/gNB/tag/AIOTF markers, failure markers, and rollback/disable action.
- [x] 3.3 Produce a validation report that separates protocol, baseband, source-build, container-image, and RFsim evidence; label unsupported claims `[Needs Verification]`.
- [x] 3.4 Produce the final trace-code guide: source symbol, input/output, state owner, expected marker, next trace point, and implemented/partial/dormant/missing status.
- [x] 3.5 Document the AIOTF binding schema, 60-Tag mapping, normal/diversity wake policy, failover epoch, serialized resource policy, report evidence fields, and explicit no-combining boundary.
- [x] 3.6 Report UE1/UE2 primary load, per-reader observations, duplicate/conflict counts, timeouts, and stale-epoch reports without converting protocol-only evidence into RF/backscatter PASS.
- [x] 3.7 Run `openspec validate add-aiot-topology2-reader-experiment --strict` and resolve change-artifact failures before implementation handoff.
