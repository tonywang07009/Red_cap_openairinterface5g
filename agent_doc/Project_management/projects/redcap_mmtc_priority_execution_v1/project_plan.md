# RedCap mMTC Priority Execution Project (v1)

## Project Metadata
- Project Path: `agent_doc/Project_management/projects/redcap_mmtc_priority_execution_v1/project_plan.md`
- Created Date: 2026-04-25
- Updated Date: 2026-05-08
- Baseline Archive: `agent_doc/Project_management/Simluation_v2.md`
- Milestone Directory: `agent_doc/Project_management/projects/redcap_mmtc_priority_execution_v1/milestones/`
- Validation Directory: `agent_doc/Project_management/projects/redcap_mmtc_priority_execution_v1/validation/`
- Daily Log Path: `test_log/work_daily/`
- Curated Evidence Library: `redcap_library/`
- Objective: Execute RedCap/mMTC work through small, spec-traceable, testable milestone files.

## Document Model
- `project_plan.md` is the active index and status source.
- `Simluation_v2.md` is retained as the baseline archive only.
- Each milestone has one execution contract under `milestones/`.
- Shared test definitions live under `validation/`.
- Before implementation or runtime validation, read only:
  - this file,
  - the target milestone file,
  - the relevant validation file,
  - the latest work daily log.

## Prioritization Method
- Score Formula: `[Priority Score] = [Feasibility] + [Ease] - [Implementation Difficulty]`
- Scale: `1..5` (`5 = highest`)
- Status Legend: `[ ] Not Started`, `[~] In Progress`, `[x] Completed`, `[!] Blocked`

## Milestone Index
| Milestone | File | Purpose | Status |
|---|---|---|---|
| M1 | `milestones/M1_phy_constraints.md` | RedCap PHY limits, antenna limits, HD-FDD guard | [x] |
| M2 | `milestones/M2_rrc_sib1_redcap.md` | RedCap SIB1 encode/decode and barring gates | [x] |
| M3 | `milestones/M3_bwp_coreset_ra.md` | RedCap initial BWP, CORESET#0 Case A/B, RA Msg2 path | [x] |
| M4 | `milestones/M4_sdt_inactive.md` | SDT and RRC_INACTIVE FSM wiring | [x] |
| M4-B | `milestones/M4B_drx_edrx_psm.md` | Connected DRX, eDRX, PSM low-power behavior | [x] |
| M5 | `milestones/M5_mmtc_runtime_scaling.md` | Compose-based mMTC runtime, 30/32/64 UE scaling | [x] |
| M6 | `milestones/M6_docs_automation.md` | Automation, tutorial, reference, evidence packaging | [x] |
| M7 | `milestones/M7_repo_hygiene.md` | Clean code, unused script/doc inventory, approved removals | [x] |

## Validation Index
| File | Purpose |
|---|---|
| `validation/test_matrix.md` | Unit, flow, and runtime test IDs shared by all milestones |
| `validation/runtime_checklist.md` | RFsim Docker validation checklist and log markers |
| `validation/spec_traceability_matrix.md` | 3GPP clause mapping and verification status |
| `redcap_parameter_implementation_validation_tutorial.md` | Traditional Chinese RedCap parameter / implementation logic / spec validation tutorial |

## Execution Batches
- [Batch A: Immediate / local-first]
  - `M6C-T1` Automation scripts baseline
  - `M2-T1` RedCap SIB1 encode/decode + 1Rx barring gate completion
  - `M4-T1` SDT FSM wiring to scheduler path
  - `M1-T3` HD-FDD Tx/Rx gap enforcement hardening
- [Batch B: Host Docker required]
  - `M3-T2` CORESET#0 Case A/B host runtime evidence
  - `M5-T1` fixed-UE UE2 user-plane blocker RCA
  - `M5-T2` scalable mMTC staged validation
- [Batch C: High-difficulty spec gap closure]
  - `M4B-T1` DRX/eDRX/PSM closure
  - `M6-A/B` Tutorial + reference manuals finalization
- [Batch D: Repository hygiene / cleanup]
  - `M7-T1` Inventory unused Bash and Markdown files
  - `M7-T2` Remove confirmed-unused files after explicit approval
  - `M7-T3` Clean documentation links and references after removals

## Priority Backlog
| Task ID | Milestone | Task Name | File | Feasibility | Ease | Difficulty | Priority Score | Prerequisite Tasks | Current Status |
|---|---|---|---|---:|---:|---:|---:|---|---|
| M6C-T1 | M6 | Automation scripts baseline | `milestones/M6_docs_automation.md` | 5 | 5 | 2 | 8 | None | [x] |
| M2-T1 | M2 | RedCap SIB1 encode/decode + 1Rx barring gate completion | `milestones/M2_rrc_sib1_redcap.md` | 5 | 4 | 2 | 7 | M1 baseline constraints | [x] |
| M6AB-T1 | M6 | Tutorial/reference manuals finalization | `milestones/M6_docs_automation.md` | 5 | 4 | 2 | 7 | M1/M2/M3/M4/M5 evidence ready | [x] |
| M4-T1 | M4 | SDT FSM scheduler wiring and transition logging | `milestones/M4_sdt_inactive.md` | 5 | 3 | 3 | 5 | M2, M3 | [x] |
| M1-T3 | M1 | HD-FDD Tx/Rx gap guard hardening | `milestones/M1_phy_constraints.md` | 4 | 3 | 3 | 4 | None | [x] |
| M3-T2 | M3 | CORESET#0 Case A/B host runtime evidence completion | `milestones/M3_bwp_coreset_ra.md` | 2 | 3 | 4 | 1 | M2-T1, M1-T3 | [x] |
| M5-T1 | M5 | fixed-UE UE2 user-plane blocker RCA | `milestones/M5_mmtc_runtime_scaling.md` | 2 | 2 | 5 | -1 | M3-T2 | [x] |
| M5-T2 | M5 | scalable mMTC staged validation | `milestones/M5_mmtc_runtime_scaling.md` | 2 | 2 | 5 | -1 | M5-T1 | [x] |
| M4B-T1 | M4-B | DRX/eDRX/PSM end-to-end implementation closure | `milestones/M4B_drx_edrx_psm.md` | 3 | 1 | 5 | -1 | M2-T1, M4-T1, M5-T1 | [x] |
| M7-T1 | M7 | Inventory unused Bash and Markdown files | `milestones/M7_repo_hygiene.md` | 5 | 3 | 2 | 6 | None | [x] |
| M7-T2 | M7 | Remove confirmed-unused files after explicit approval | `milestones/M7_repo_hygiene.md` | 4 | 3 | 3 | 4 | M7-T1, user approval | [NA] |
| M7-T3 | M7 | Clean stale references after approved removals | `milestones/M7_repo_hygiene.md` | 4 | 2 | 3 | 3 | M7-T2 | [NA] |

## Active Focus
- Current batch: [Closure / evidence packaging]
- Current milestone: [M5/M6/M7 closure complete]
- Current validation focus:
  - `RT-M5-032`: passed 32 UE staged mMTC stability after Case B 30 UE pass.
  - `RT-M5-048`: passed 48 UE staged mMTC stability with higher transient Msg2 window pressure.
  - `RT-M5-056`: first run classified [CN/NAS/PDU late-stage failure]; static CN discovery mitigation rerun passed 56/56 attach/PDU/tunnel/forward ping.
  - `RT-M5-064`: user-promoted upper-bound check classified 64 UE as [gNB runtime restart / SIGKILL threshold].
  - `RT-M5-060`: [NA] after user accepted 56 UE as sufficient simulation capacity.
  - `RT-M5-CASEB-030`: keep Case B comparison for RA/Msg4 and PUCCH fallback counters.
- Recently closed:
  - `M3-T2`: Case A and Case B RFsim runtime evidence passed; retained summaries/configs are now curated under `redcap_library/`.
  - `M4B-T1`: DRX/eDRX/PSM support boundary is documented as [DRX unit/flow-level], [eDRX runtime log-level], and [PSM runtime log-level].
- Current M5 status:
  - Case B staged runtime now reached `56/56` attach/PDU/tunnel/forward ping after static CN discovery mitigation.
  - CN pressure mitigation changed `/home/tonywang/OAI/oai-cn5g/conf/config.yaml`: `register_nf.general=no`, `amf.support_features_options.enable_smf_selection=no`, and static SMF UPF `port=8805`.
  - Pre-mitigation 56 UE failed UEs were CN/NAS/PDU-side: `UE54` and `UE55` received Registration Reject after AMF `Request Authentication Vectors failure`; `UE56` registered but hit AMF `SMF Selection, no SMF candidate is available`.
  - Post-mitigation 56 UE cleared those blockers: `Request Authentication Vectors failure=0`, `Registration Reject=0`, `SMF Selection, no SMF candidate=0`, NRF response/HTTP registration errors `0`.
  - 56 UE RAN success counters: Msg2 DCI `56`, Msg2/Msg4 `vrb_map` fail `0`, contention timer expired `0`, Msg4 ACK / CBRA success `56`, gNB restart count `0`.
  - 56 UE RA retry pressure remains visible: Msg2 window fail `55`, UE `RAR reception failed=55`, with all affected UEs finally reaching RRCSetup/PDU/tunnel/ping.
  - 64 UE static CN run reached `59/64` Registration Accept and PDU Session Establishment Accept before gNB restart, but final validation reported `4/64` running, `0/64` tunnel, `0/64` forward ping because the gNB container restarted before validation.
  - 64 UE restart evidence: gNB `restart_count=1`; gNB log contains `[tini] Main child exited with signal 'Killed'`; Docker state reports `OOMKilled=false`, `ExitCode=0`, container restarted and is healthy after restart.
  - 64 UE CN blockers remained absent: auth-vector failure, Registration Reject, empty SMF candidate, and NRF/HTTP registration pressure markers were all `0`.
  - 64 UE RAN pre-restart counters: Msg2 DCI `64`, Msg2 window fail `53`, Msg2/Msg4 `vrb_map` fail `0`, contention timer expired `0`, Msg4 ACK / CBRA success `63`.
  - Case A staged runtime previously reached `26/30`; normal 30 UE Case A remains a separate comparison if needed.
  - 60 UE upper-bound threshold remains unclassified.
- M5 closure decision:
  - User accepted the 56 UE Case B static CN run as sufficient for simulation scope.
  - Therefore M5 closes on `56/56` attach/PDU/tunnel/forward ping plus documented 64 UE upper-bound failure classification.
- M6 closure decision:
  - Evidence package summary, report existence check, and spec traceability review completed.
- M7 closure decision:
  - Inventory-only repo hygiene completed; no files were deleted because removals require explicit user approval.

## Daily Log Follow Rules
- Every new `test_log/work_daily/*.md` entry for this project must include:
  - `Project Path: agent_doc/Project_management/projects/redcap_mmtc_priority_execution_v1/project_plan.md`
  - `Milestone File: milestones/<target>.md`
  - `Validation File: validation/<target>.md`
  - `Task ID: <one item from Priority Backlog>`
  - `Batch: A / B / C`
- Task slug format recommendation:
  - `px-v1-<task-id-lowercase>-<short-action>`

## Next Action
- No remaining required milestone work in the current RedCap mMTC priority execution v1 scope.
- Optional follow-up only:
  1. Rerun 64 UE with host resource telemetry if the user later wants upper-bound tuning beyond the accepted 56 UE capacity.
  2. Promote explicit removal candidates from the M7 inventory only after user approval.
