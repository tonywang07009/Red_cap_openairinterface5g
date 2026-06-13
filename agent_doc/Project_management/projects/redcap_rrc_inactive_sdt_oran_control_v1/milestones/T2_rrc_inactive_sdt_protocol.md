# T2 RRC_INACTIVE + SDT Protocol Baseline

## Scope
- [Case A] fixed RFsim baseline for [RRC_INACTIVE + SDT].
- UE/gNB RRC state transition for `RRCRelease.suspendConfig`.
- RRCResume and RRCReestablishment fallback separation.
- Configured grant and CG-SDT path.
- TA / RSRP threshold fallback to 4-step RA.

## Out of Scope
- xApp/rApp/dApp runtime parameter control.
- Non-RT RIC SDK implementation.
- Performance optimization beyond protocol correctness.

## 3GPP Spec Mapping
- [RRC_INACTIVE]: TS 38.331 `[Needs Verification]`.
- [RRCRelease suspendConfig]: TS 38.331 `[Needs Verification]`.
- [RRCResume]: TS 38.331 `[Needs Verification]`.
- [SDT]: TS 38.321 / TS 38.331 `[Needs Verification]`.
- [RedCap capability]: TS 38.306 `[Needs Verification]`.

## Current OAI Status
- UE `RRCRelease.suspendConfig` no longer reaches `AssertFatal("Inactive State not supported")` in the current worktree;
  [Gate 1 RFsim PASS] confirms controlled `[RRC_INACTIVE]` entry on 2026-06-04.
- gNB has a validation-only `MMTC_RRC_INACTIVE_GATE1_TRIGGER` path, default disabled, to emit `RRCRelease.suspendConfig` after PDU session setup.
- gNB `rrcResumeRequest` handling has a Gate 2 validation path that keeps the retained UE RRC context and resumes it by `shortI-RNTI`.
- UE `RRCResume` DL-DCCH handling has a Gate 2 validation path that returns UE state to `[RRC_CONNECTED]` and sends `RRCResumeComplete`.
- UE `configuredGrantConfig` assert path has been replaced by a parse/store/release slice for Gate 3 validation.
- UE now has a validation-oriented autonomous CG PUSCH scheduler slice, a RRC-to-MAC inactive indication,
  and gNB has a CG-SDT RX classifier candidate.
- Gate 3 RFsim now has a repeat sample UE1 PASS and sampled UE1-3 PASS on 2026-06-13, proving
  `configuredGrantConfig parsed`, `cg-SDT PUSCH tx`, and `cg-SDT PUSCH rx candidate` together with no `exit 139`.
- Existing MAC SDT FSM hooks are not a complete RRC_INACTIVE + SDT protocol implementation.

## Gate 0: Protocol and Code Inventory
- [Status] [x] Completed on 2026-06-03.
- [MUST] Reconfirm existing branches for `RRC_INACTIVE`, `suspendConfig`, `RRCResumeRequest`, and `configuredGrantConfig`.
- [MUST] Confirm whether `cg-SDT` ASN.1 fields exist in current generated types.
- [MUST] Record exact files and unsupported branches before editing.
- [Output Checkpoint] Inventory note in work daily log.
- [Inventory Result] UE and gNB have partial state/ASN.1 hooks, but full RRC_INACTIVE / Resume / CG-SDT protocol paths are not implemented.
- [Inventory Log] `test_log/work_daily/2026-06-03_rrc_inactive_sdt_gate0_inventory.md`

## Gate 1: T2-1 RRCRelease suspendConfig to UE INACTIVE
- [Status] [x] Completed on 2026-06-04.
- [Modification Point] -> `nr_rrc.c` / UE RRC release handling path.
- [Reason] -> UE currently crashes when receiving `suspendConfig`; the path must become a controlled state transition.
- [Before vs. After Comparison] -> Before: `AssertFatal`; After: UE stores needed AS context and enters `[RRC_INACTIVE]`.
- [Discussion Point] -> gNB context purge must be disabled or extended; PDCP counter must not reset.
- [MUST] UE log includes `RRCRelease suspendConfig received`.
- [MUST] UE log includes `RRC_INACTIVE entered`.
- [MUST] No `exit 139`.
- [Validation Log] `test_log/work_daily/2026-06-04_rrc_inactive_sdt_gate1_rfsim_validation.md`

## Gate 2: T2-2 RRCResume / RRCReestablishment
- [Status] [x] RFsim PASS on 2026-06-05.
- [Modification Point] -> gNB `rrcResumeRequest` handler and UE `RRCResume` DL-DCCH handler.
- [Reason] -> INACTIVE must have a normal path back to CONNECTED.
- [Before vs. After Comparison] -> Before: gNB/UE log unsupported; After: UE sends `RRCResumeRequest`, gNB sends `RRCResume`, UE sends `RRCResumeComplete`.
- [Discussion Point] -> `RRCReestablishment` is fallback only and must not mask normal Resume behavior.
- [Discussion Point] -> `resumeMAC-I` is currently deterministic zero in the validation helper; formal integrity behavior remains `[Needs Verification]`.
- [MUST] RFsim log or Wireshark shows `RRCResumeRequest`.
- [MUST] UE returns to `[RRC_CONNECTED]`.
- [MUST] PDCP SN preservation is checked or marked `[Needs Verification]`.
- [Validation Log] `test_log/work_daily/2026-06-04_rrc_inactive_sdt_gate2_c_implementation.md`
- [RFsim Validation Log] `test_log/work_daily/2026-06-05_rrc_inactive_sdt_gate2_rfsim_validation.md`
- [RFsim Evidence] `test_log/compiler_logs/rrc_inactive_gate2_bwp_restore_rfsim_2026-06-05_23-34-44.log`

## Gate 3: T2-3 configuredGrantConfig + cg-SDT
- [Status] [x] RFsim sampled multi-UE PASS on 2026-06-13; full-scale stress is optional follow-up, not required before Gate 4 planning.
- [Modification Point] -> SIB1 / UL BWP / MAC UE configured grant parse path.
- [Reason] -> UE configured grant support must exist before CG-SDT validation.
- [Before vs. After Comparison] -> Before: configured grant assert and no CG scheduler; After: UE parses/stores CG resources and can schedule a validation-only autonomous CG PUSCH occasion.
- [Discussion Point] -> gNB classifier currently marks `cg-SDT PUSCH rx candidate`; this is the accepted Gate 3 validation marker, while formal configured-grant classifier behavior remains `[Needs Verification]`.
- [MUST] UE uses CG PUSCH for small data.
- [MUST] UE log includes `configuredGrantConfig parsed`.
- [MUST] UE log includes `cg-SDT PUSCH tx`.
- [SHOULD] gNB log includes `cg-SDT PUSCH rx candidate`.
- [Validation Log] `test_log/work_daily/2026-06-12_rrc_inactive_sdt_gate3_rebuilt_rfsim_gate2off.md`
- [Repeat / Sampled Multi-UE Log] `test_log/work_daily/2026-06-13_rrc_inactive_sdt_gate3_repeat_sampled_multiue.md`

## Gate 4: T2-4 TA / RSRP Threshold to 4-Step RA
- [Modification Point] -> UE SDT trigger decision and TA validity check.
- [Reason] -> RFsim `cg-SDT-TimeAlignmentTime = infinity` is safe for smoke testing but does not validate fallback.
- [Before vs. After Comparison] -> Before: no deterministic threshold validation; After: RFsim test hook can force re-RA.
- [Discussion Point] -> Test hook is validation-only; formal behavior follows `cg-SDT-RSRP-ChangeThreshold`.
- [MUST] Threshold exceed triggers 4-step RA.
- [MAY] Use deterministic RFsim hook for repeatable PASS.

## Completion Criteria
- [MUST] T2-1 through T2-4 pass in order.
- [MUST] `nr-softmodem` and `nr-uesoftmodem` build after relevant C changes.
- [MUST] RFsim log markers in `validation/runtime_checklist.md` are satisfied.
- [MUST NOT] `exit 139` appears.
- [MUST] Final Case A reusable config/evidence is promoted to `redcap_library/` only after validation.
