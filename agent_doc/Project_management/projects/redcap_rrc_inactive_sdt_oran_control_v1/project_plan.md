# RedCap RRC_INACTIVE + SDT + O-RAN Control Project (v1)

## Project Metadata
- [Project Path]: `agent_doc/Project_management/projects/redcap_rrc_inactive_sdt_oran_control_v1/project_plan.md`
- [Created Date]: 2026-06-03
- [Milestone Directory]: `agent_doc/Project_management/projects/redcap_rrc_inactive_sdt_oran_control_v1/milestones/`
- [Validation Directory]: `agent_doc/Project_management/projects/redcap_rrc_inactive_sdt_oran_control_v1/validation/`
- [Runtime Source of Truth]: `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/`
- [Daily Log Path]: `test_log/work_daily/`
- [Curated Evidence Library]: `redcap_library/`
- [Objective]: Implement [RRC_INACTIVE + SDT] in full-protocol direction, validate it gate-by-gate in RFsim, then add [Case B] O-RAN policy control without weakening the [Case A] baseline.

## Summary
- [Goal]: Use [完整協定版] for [RRC_INACTIVE + SDT], but execute through [逐 gate 推進].
- [Case A]: fixed YAML baseline; AI, xApp, rApp, and dApp dynamic control are disabled.
- [Case B]: KPM-driven policy/control path; dApp/xApp/rApp may adjust whitelisted parameters through a bounded control contract.
- [MUST]: Each gate must pass before the next gate starts.
- [SHOULD]: Every gate should preserve RFsim logs, build logs, packet/log markers, and parameter snapshots.
- [MAY]: T2-4 may use a deterministic RFsim test hook for RSRP/TA threshold validation.

## Confirmed Current State
- OAI currently has partial [RRC_INACTIVE] hooks.
- UE `RRCRelease.suspendConfig` no longer reaches `AssertFatal("Inactive State not supported")` in the current worktree;
  it now enters a controlled [RRC_INACTIVE] transition. [Gate 1 RFsim PASS on 2026-06-04]
- gNB `RRCResumeRequest` handling has a Gate 2 validation path that preserves/looks up the retained RRC UE context by `shortI-RNTI`,
  emits `RRCResume`, and receives `RRCResumeComplete` after UE active BWP restoration. [Gate 2 RFsim PASS on 2026-06-05]
- UE `configuredGrantConfig` parse/store smoke is implemented, and Gate 3 now has a source-build PASS slice for
  [UE autonomous CG PUSCH scheduler], [RRC-to-MAC inactive indication], and [gNB CG PUSCH RX classifier].
  [Gate 3 RFsim sampled multi-UE PASS on 2026-06-13] confirms `configuredGrantConfig parsed`,
  `cg-SDT PUSCH tx`, and `cg-SDT PUSCH rx candidate` for UE1-3 with no `exit 139`.
- `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/` already hosts the RedCap RFsim + FlexRIC compose path.

## Document Model
- `project_plan.md` is the active project index and status source.
- `agent_rules.md` defines token-efficient context and implementation boundaries.
- `milestones/T2_rrc_inactive_sdt_protocol.md` owns [Case A] protocol gates.
- `milestones/T2B_oran_policy_control.md` owns [Case B] O-RAN policy/control gates.
- `validation/runtime_checklist.md` defines RFsim log and failure markers.
- `validation/control_contract_checklist.md` defines O-RAN dynamic control safety checks.
- `validation/spec_traceability_matrix.md` records clause mappings and uncertainty.

## Runtime YAML Model
- [MUST] `docker-compose.mmtc.yml` remains a runtime entrypoint and must only mount/select policy files.
- [MUST NOT] Embed policy content directly inside `docker-compose.mmtc.yml`.
- [MUST] Case policies live under `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/control/`.
- [SHOULD] `redcap_library/` should receive only final reusable configs, reports, and evidence after validation.

## Milestone Index
| Milestone | File | Purpose | Status |
|---|---|---|---|
| T2 | `milestones/T2_rrc_inactive_sdt_protocol.md` | RRC_INACTIVE, RRCResume, CG-SDT, TA fallback protocol baseline | [~] Gates 1-3 PASS; Gate 4 pending |
| T2B | `milestones/T2B_oran_policy_control.md` | KPM-driven O-RAN policy/control over validated RedCap parameters | [ ] |

## Gate Index
| Gate | Task | Primary Output Checkpoint | Status |
|---|---|---|---|
| Gate 0 | Protocol/code inventory | Existing branches and 3GPP mapping confirmed | [x] |
| Gate 1 | T2-1 `RRCRelease.suspendConfig` to UE INACTIVE | UE log: `RRC_INACTIVE entered`; no `exit 139` | [x] C build PASS; local images rebuilt; RFsim PASS 2026-06-04 |
| Gate 2 | T2-2 RRCResume / RRCReestablishment | RFsim or Wireshark captures `RRCResumeRequest` | [x] RFsim PASS 2026-06-05 |
| Gate 3 | T2-3 `configuredGrantConfig` + `cg-SDT` | UE uses CG PUSCH for small data | [x] RFsim sampled multi-UE PASS 2026-06-13 |
| Gate 4 | T2-4 TA / RSRP threshold fallback | Threshold exceed triggers 4-step RA | [ ] |
| Gate 5 | T2B O-RAN policy control | KPM snapshot, control request, ACK/NACK, applied snapshot logged | [ ] |

## Active Focus
- [Current Batch]: [T2 protocol baseline]
- [Current Milestone]: [T2 Gate 4 TA / RSRP threshold fallback pending]
- [Current Runtime Policy Default]: [Case A]
- [Current Implementation Status]: [Gate 1 RFsim PASS; Gate 2 RFsim PASS; Gate 3 RFsim sampled multi-UE PASS; Gate 4 pending]

## Daily Log Follow Rules
- Every new `test_log/work_daily/*.md` entry for this project must include:
  - `Project Path: agent_doc/Project_management/projects/redcap_rrc_inactive_sdt_oran_control_v1/project_plan.md`
  - [Case]: `A` or `B`
  - [Gate]: `0..5`
  - [source build PASS/FAIL/NA]
  - [unit test PASS/FAIL/NA]
  - [RFsim runtime PASS/FAIL/NA]
  - [exit 139]: present or absent
