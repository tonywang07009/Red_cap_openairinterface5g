# RedCap mMTC Priority Execution Project (v1)

## Project Metadata
- Project Path: `agent_doc/Project_management/projects/redcap_mmtc_priority_execution_v1/project_plan.md`
- Created Date: 2026-04-25
- Baseline Milestone File: `agent_doc/Project_management/Simluation_v2.md`
- Daily Log Path: `test_logs/work_daily/`
- Objective: Execute remaining RedCap/mMTC work in a pragmatic order based on [Feasibility], [Ease], and [Implementation Difficulty].

## Prioritization Method
- Score Formula: `[Priority Score] = [Feasibility] + [Ease] - [Implementation Difficulty]`
- Scale: `1..5` (`5 = highest`)
- Status Legend: `[ ] Not Started`, `[~] In Progress`, `[x] Completed`, `[!] Blocked`

## Execution Batches
- [Batch A: Immediate / local-first]
  - `M6-C` Automation scripts baseline
  - `M2-T1` RedCap SIB1 encode/decode + 1Rx barring gate completion
  - `M4-T1` SDT FSM wiring to scheduler path
  - `M1-T3` HD-FDD Tx/Rx gap enforcement hardening
- [Batch B: Host Docker required]
  - `M3-T2` CORESET#0 Case A/B host runtime evidence
  - `M5-T1` fixed-UE UE2 user-plane blocker RCA
  - `M5-T2` scalable mMTC 32->64 staged validation
- [Batch C: High-difficulty spec gap closure]
  - `M4B-T1` DRX/eDRX/PSM closure
  - `M6-A/B` Tutorial + Reference manuals finalization

## Priority Backlog
| Task ID | Milestone | Task Name | Feasibility | Ease | Difficulty | Priority Score | Prerequisite Tasks | Current Status |
|---|---|---|---:|---:|---:|---:|---|---|
| M6C-T1 | M6-C | Automation scripts baseline (`redcap_tput_logger.py`, `gen_function_index.py`, `gen_doc_skeleton.py`) | 5 | 5 | 2 | 8 | None | [x] |
| M2-T1 | M2 | RedCap SIB1 encode/decode + 1Rx barring gate completion | 5 | 4 | 2 | 7 | M1 baseline constraints | [x] |
| M6AB-T1 | M6-A/B | Tutorial/reference manuals finalization | 5 | 4 | 2 | 7 | M1/M2/M3/M4/M5 evidence ready | [ ] |
| M4-T1 | M4 | SDT FSM scheduler wiring and transition logging | 5 | 3 | 3 | 5 | M2, M3 | [x] |
| M1-T3 | M1 | HD-FDD Tx/Rx gap guard hardening | 4 | 3 | 3 | 4 | None | [x] |
| M3-T2 | M3 | CORESET#0 Case A/B host runtime evidence completion | 2 | 3 | 4 | 1 | M2-T1, M1-T3 | [ ] |
| M5-T1 | M5 | fixed-UE path UE2 user-plane blocker RCA (stage60/64 instability) | 2 | 2 | 5 | -1 | M3-T2 | [ ] |
| M5-T2 | M5 | scalable mMTC staged validation (32/50/56/60/64) | 2 | 2 | 5 | -1 | M5-T1 | [ ] |
| M4B-T1 | M4-B | DRX/eDRX/PSM end-to-end implementation closure | 3 | 1 | 5 | -1 | M2-T1, M4-T1, M5-T1 | [ ] |

## Task Cards (Execution Contract)
- [M6C-T1] [Modification Point] -> [Implement baseline automation scripts and output contracts] -> [Reason] [Fastest leverage for test/doc throughput] -> [Before vs. After Comparison] [Before: manual parsing and indexing] [After: reproducible script outputs] -> [Discussion Point] [No direct 3GPP clause dependency]
- [M2-T1] [Modification Point] -> [Complete RedCap SIB1 wiring + barring behavior tests] -> [Reason] [Foundation for attach and later runtime validation] -> [Before vs. After Comparison] [Before: partial M2 coverage] [After: complete encode/decode and attach gate behavior] -> [Discussion Point] [TS 38.331 Section 5.3.1; exact RedCap IE clause: ⚠ Needs Verification]
- [M4-T1] [Modification Point] -> [Wire `sdt_scheduler_fsm()` into scheduler data path with state-transition logs] -> [Reason] [Current FSM is skeleton-level] -> [Before vs. After Comparison] [Before: compile-only FSM] [After: executable state flow with checks] -> [Discussion Point] [TS 38.321 SDT procedure clause: ⚠ Needs Verification]
- [M1-T3] [Modification Point] -> [Strengthen HD-FDD switching gap enforcement guards] -> [Reason] [Critical for RedCap constraints and runtime stability] -> [Before vs. After Comparison] [Before: partial guard behavior] [After: deterministic enforcement and assertions] -> [Discussion Point] [TS 38.306 / TS 38.101-1 exact clause mapping: ⚠ Needs Verification]
- [M3-T2] [Modification Point] -> [Collect host runtime evidence for Case A/B CORESET#0 operation] -> [Reason] [Current M3 completion blocked by host-runtime evidence gap] -> [Before vs. After Comparison] [Before: local dry-run only] [After: host log evidence for both cases] -> [Discussion Point] [TS 38.331 CORESET/BWP exact clause mapping: ⚠ Needs Verification]
- [M5-T1] [Modification Point] -> [RCA for gNB `Killed` and UE2 user-plane blockage at higher loads] -> [Reason] [Primary blocker for M5 completion] -> [Before vs. After Comparison] [Before: stage50 stable only] [After: fixed-UE path stability at higher staged loads] -> [Discussion Point] [TS 38.321 Section 5.1, TS 38.331 Section 5.3.1]
- [M5-T2] [Modification Point] -> [Execute staged mMTC validation and preserve xApp control checks] -> [Reason] [Hard deliverable for scaling architecture] -> [Before vs. After Comparison] [Before: partial staged pass] [After: reproducible staged validation reports] -> [Discussion Point] [UL scheduling behavior per TS 38.321; O-RAN E2 path is non-3GPP]
- [M4B-T1] [Modification Point] -> [Close DRX/eDRX/PSM gaps end-to-end] -> [Reason] [Largest compliance gap for low-power mMTC behavior] -> [Before vs. After Comparison] [Before: not implemented/partial paths] [After: minimum closed-loop implementation and runtime validation] -> [Discussion Point] [TS 38.321 Section 5.7; TS 38.331 eDRX clauses: ⚠ Needs Verification; TS 24.501 PSM timers: ⚠ Needs Verification]
- [M6AB-T1] [Modification Point] -> [Finalize tutorial/reference/compliance-gap docs against final code+evidence] -> [Reason] [Avoid repeated rewrites before technical baseline stabilizes] -> [Before vs. After Comparison] [Before: pending documentation] [After: review-ready final documentation package] -> [Discussion Point] [Clause citations must be revalidated against final implementation]

## Daily Log Follow Rules for This Project
- Every new `test_logs/work_daily/*.md` entry for this project must include:
  - `Project Path: agent_doc/Project_management/projects/redcap_mmtc_priority_execution_v1/project_plan.md`
  - `Task ID: <one item from Priority Backlog>`
  - `Batch: A / B / C`
- Task slug format recommendation:
  - `px-v1-<task-id-lowercase>-<short-action>`

## Next Action
- Move to [Batch B] on a Docker-enabled host in this order:
  1. `M3-T2`
  2. `M5-T1`
  3. `M5-T2`
