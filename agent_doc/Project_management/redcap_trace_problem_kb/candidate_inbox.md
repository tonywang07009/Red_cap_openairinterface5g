# RedCap Trace / Problem Candidate Inbox

## Purpose
- Collect lightweight candidates during sub-task closeout.
- Promote only reusable entries during the every-5-sub-task review.
- Keep candidates short; detailed raw evidence belongs in logs or `redcap_library/`.

## Candidate Format

### [Candidate ID] CAND-YYYYMMDD-NN
- [Type]: trace / problem
- [Sub-task]:
- [Project]:
- [Gate or Milestone]:
- [Why It May Be Reusable]:
- [Source Evidence]:
- [Status]: pending-review

#### [Step-by-step Draft]
1. [TBD]

#### [Review Decision]
- [Promote To]: trace_steps.md / problem_set.md / none
- [Reason]:

## Pending Candidates

### [Candidate ID] CAND-20260611-01
- [Type]: trace
- [Sub-task]: Gate 3 UE autonomous CG PUSCH scheduler + gNB CG-SDT RX classifier
- [Project]: `redcap_rrc_inactive_sdt_oran_control_v1`
- [Gate or Milestone]: Gate 3 / T2-3
- [Why It May Be Reusable]: Separates `configuredGrantConfig parsed`, `cg-SDT PUSCH tx`, and `cg-SDT PUSCH rx candidate` so future debugging does not mistake parse success for full Gate 3 PASS.
- [Source Evidence]: `test_log/work_daily/2026-06-11_20-52-52_rrc_inactive_sdt_gate3_cg_scheduler_classifier.md`
- [Status]: pending-review

#### [Step-by-step Draft]
1. Confirm `MMTC_RRC_INACTIVE_GATE3_CG_CONFIG=1` reaches the gNB runtime.
2. Confirm UE log has `configuredGrantConfig parsed`.
3. Confirm UE log has `cg-SDT autonomous CG PUSCH scheduled`.
4. Confirm UE log has `cg-SDT PUSCH tx`.
5. Confirm gNB log has `cg-SDT PUSCH rx candidate`.
6. If UE TX exists but gNB RX is absent, inspect whether gNB created a matching UL_TTI/PUSCH expectation for the configured grant occasion.

#### [Review Decision]
- [Promote To]: trace_steps.md
- [Reason]: Pending RFsim validation; promote only after runtime confirms the marker sequence.

### [Candidate ID] CAND-20260611-02
- [Type]: problem
- [Sub-task]: Gate 3 inactive CG scheduler RFsim rerun
- [Project]: `redcap_rrc_inactive_sdt_oran_control_v1`
- [Gate or Milestone]: Gate 3 / T2-3
- [Why It May Be Reusable]: Prevents future audits from treating gNB `cg-SDT PUSCH rx candidate` as PASS when UE-side `cg-SDT PUSCH tx` is absent.
- [Source Evidence]: `test_log/work_daily/2026-06-11_20-52-52_rrc_inactive_sdt_gate3_cg_scheduler_classifier.md`
- [Status]: pending-review

#### [Step-by-step Draft]
1. Check UE log for `configuredGrantConfig parsed`.
2. Check UE log for `[RRC_INACTIVE Gate 3][UE MAC] entered inactive`.
3. Check UE log for `cg-SDT autonomous CG PUSCH scheduled`.
4. Check UE log for `cg-SDT PUSCH tx`.
5. Check gNB log for `cg-SDT PUSCH rx candidate`.
6. Classify as PASS only if UE TX and gNB RX evidence both exist; otherwise keep Gate 3 `[in progress]`.

#### [Review Decision]
- [Promote To]: problem_set.md
- [Reason]: Pending RFsim rerun with the inactive CG flag binary; promote after confirming which marker is still absent.
