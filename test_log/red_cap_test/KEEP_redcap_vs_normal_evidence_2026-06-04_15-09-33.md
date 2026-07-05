# KEEP: RedCap vs Normal Runtime Evidence 2026-06-04_15-09-33

## Retention Decision

- [Decision]: Keep this evidence batch.
- [Reason]: This is the first successful runtime proof that compares [UE1 normal] and [UE2 RedCap] under the same [106PRB] gNB/CN profile.
- [Scope]: Preserve the readable `.txt` evidence files generated from Docker runtime logs.
- [Cleanup Rule]: Do not delete, move, or overwrite this batch during `test_log/` cleanup unless the owner explicitly approves a later archival/promotion step.

## Files To Preserve

- `test_log/red_cap_test/redcap_vs_normal_final_summary_2026-06-04_15-09-33.txt`
- `test_log/red_cap_test/normal_ue_capability_evidence_2026-06-04_15-09-33.txt`
- `test_log/red_cap_test/redcap_ue_capability_evidence_2026-06-04_15-09-33.txt`
- `test_log/red_cap_test/gnb_redcap_parser_scheduler_evidence_2026-06-04_15-09-33.txt`

## Evidence Summary

- [UE1 normal]: `cap=no`, `10.0.0.2`, legacy/minimal capability, [redCapParameters-r17 absent].
- [UE2 RedCap]: `cap=yes`, `10.0.0.3`, Rel-17 capability, [redCapParameters-r17/supportOfRedCap-r17].
- [gNB]: parses UE2 [redCapParameters-r17] successfully and logs RedCap MAC/scheduler evidence.
- [BWP]: RedCap initial DL/UL BWP is [51PRB] while full serving-cell carrier remains [106PRB].

