## Context

The active BWP/SDT validation project has a reproducible BWP Gate 5 blocker: the eight-row RFsim matrix runs to the BWP trigger point, but every BWP 1 -> 0 telnet trigger crashes the gNB in `update_cellGroupConfig_for_BWP_switch()`. The current call chain is `trigger_bwp_switch()` -> `nr_trigger_bwp_switch()` -> `nr_mac_trigger_reconfiguration()` -> `update_cellGroupConfig_for_BWP_switch()`.

The BWP reconfiguration path crosses multiple ownership boundaries: gNB MAC UE state, ASN.1 `NR_CellGroupConfig_t` trees, RRC/F1AP reconfiguration payload encoding, and the later ACK path that applies `UE->reconfigCellGroup` to `UE->CellGroup`. The fix must therefore make the reconfiguration candidate safe before any pending state is committed.

## Goals / Non-Goals

**Goals:**

- Stop the gNB crash when switching from additional BWP 1 back to initial BWP 0.
- Keep live `UE->CellGroup` unchanged until a BWP reconfiguration candidate has been built and encoded.
- Avoid stale `UE->local_bwp_id` changes when candidate creation or ASN.1 encoding fails.
- Preserve the existing telnet command syntax and project CSV schemas.
- Add an explicit project code-review gate before Gate 7 reporting.

**Non-Goals:**

- Do not implement real `MMTC_BWP_TRAFFIC_PROFILE`, `MMTC_BWP_INACTIVITY_TIMER_MS`, or `MMTC_BWP_SWITCH_DELAY_MS` runtime hooks in this change.
- Do not change SDT Gate 6 aggregation behavior.
- Do not claim paper-comparable Gate 5 PASS unless the fixed runtime matrix produces the required numeric evidence.
- Do not generalize multi-additional-BWP support beyond the current BWP 0 and BWP 1 validation path.

## Decisions

- Use a clone-first reconfiguration model.
  - Rationale: the existing flow mutates the live `UE->CellGroup` before cloning the reconfiguration payload. If candidate generation crashes or encode fails, the gNB can retain partially modified state.
  - Alternative considered: add null checks in the existing in-place update. This is weaker because it does not solve premature live-state mutation or ASN.1 subtree ownership hazards.

- Encode the candidate before assigning it to UE pending state.
  - Rationale: `UE->reconfigCellGroup` is applied later by `ack_reconfig()`. The candidate should become pending only after ASN.1 encoding proves that the tree is structurally usable.
  - Alternative considered: assign first and encode second. This keeps the current failure mode where pending state can be stale or invalid.

- Keep `UE->local_bwp_id` update after candidate success.
  - Rationale: the local BWP ID is operational state. Updating it before candidate success makes a failed trigger look like it partially succeeded.
  - Alternative considered: update early to preserve current ordering. This was rejected because the crash evidence shows the current ordering is not failure-safe.

- Preserve the existing BWP ID mapping.
  - Rationale: the validation project only exercises initial BWP 0 and one additional BWP 1. Changing ID mapping semantics would expand the behavior surface and make the runtime evidence harder to interpret.

## Risks / Trade-offs

- [Risk] Candidate cloning can expose pre-existing ASN.1 ownership bugs. -> Mitigation: validate with single trigger0, bidirectional trigger sequence, and the full BWP matrix before claiming Gate 5 progress.
- [Risk] The C fix can remove the crash but still leave missing paper hooks. -> Mitigation: keep traffic/timer/switch-delay fields marked as runner labels until real hooks are implemented.
- [Risk] Docker runtime validation may be blocked by workspace resources. -> Mitigation: complete static/build validation and record runtime validation as blocked only if the same external blocker repeats.
- [Risk] Existing dirty worktree changes can be overwritten accidentally. -> Mitigation: inspect diffs before edits and only patch the targeted OpenSpec, BWP C code, and review-gate records.
