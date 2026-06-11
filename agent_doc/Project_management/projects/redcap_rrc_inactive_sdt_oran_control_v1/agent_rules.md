# RedCap RRC_INACTIVE + SDT + O-RAN Control Agent Rules

## Project Entry
- [Project Plan]: `agent_doc/Project_management/projects/redcap_rrc_inactive_sdt_oran_control_v1/project_plan.md`
- [Milestones]: `agent_doc/Project_management/projects/redcap_rrc_inactive_sdt_oran_control_v1/milestones/`
- [Validation]: `agent_doc/Project_management/projects/redcap_rrc_inactive_sdt_oran_control_v1/validation/`
- [Runtime Source of Truth]: `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/`
- [Control YAML]: `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/control/`

## Token-Efficient Context Pack
- [MUST] For protocol implementation, read only:
  - `project_plan.md`
  - `agent_rules.md`
  - `milestones/T2_rrc_inactive_sdt_protocol.md`
  - relevant validation file
  - latest project work daily log if resuming runtime work
- [MUST] For O-RAN control work, add only:
  - `milestones/T2B_oran_policy_control.md`
  - `validation/control_contract_checklist.md`
  - target `control/*.yaml`
- [MUST NOT] Read unrelated historical logs, PDFs, or milestone reports unless the active gate needs them.

## Case Boundary
- [Case A] is the protocol correctness baseline.
- [Case A MUST] keep AI, xApp, rApp, and dApp dynamic control disabled.
- [Case A MUST] pass T2-1 through T2-4 before [Case B] is treated as valid.
- [Case B] is KPM-driven O-RAN policy/control.
- [Case B MUST NOT] mutate or overwrite [Case A] final baseline configs.

## Runtime YAML Rules
- [MUST] Treat `docker-compose.yml`, `docker-compose.mmtc.yml`, and directly mounted config/policy files as the runtime source of truth.
- [MUST] Use `docker-compose.mmtc.yml` only to mount/select policy and contract files.
- [MUST NOT] embed `redcap_policy_case_a.yaml` or `redcap_policy_case_b.yaml` content inside compose.
- [SHOULD] Use `REDCAP_POLICY_HOST_FILE=./control/redcap_policy_case_b.yaml` to switch to [Case B].

## O-RAN Control Rules
- [MUST] Treat [KPM] as observation only.
- [MUST NOT] describe KPM as directly controlling RRC/MAC parameters.
- [MUST] Use [E2SM-RC], [custom SM], or [dApp local API] for actual control.
- [MUST] Apply `redcap_control_contract.yaml` before any runtime parameter update.
- [MUST] Record KPM snapshot, policy version, old value, new value, ACK/NACK, and applied parameter snapshot.
- [SHOULD] Assign ownership:
  - [rApp]: long-term policy.
  - [xApp]: near-real-time decision.
  - [dApp/gNB hook]: local safety guard and apply path.

## Implementation Gate
- [MUST] Before C changes, summarize:
  - active gate,
  - target files,
  - required log markers,
  - expected build targets,
  - spec clauses or `[Needs Verification]`.
- [MUST] Patch one gate at a time.
- [MUST] Never skip from T2-1 to T2-3 before T2-2 passes.
- [MUST] Preserve PDCP counter and UE context expectations during INACTIVE/Resume work.

## Build/Test Reporting
- [MUST] After UE-side C changes, build `nr-uesoftmodem`.
- [MUST] After gNB-side C changes, build `nr-softmodem`.
- [MUST] For shared cross-layer changes, build both.
- [MUST] Report:
  - [source build PASS/FAIL]
  - [unit test PASS/FAIL/NA]
  - [container image rebuilt or not]
  - [RFsim UE/gNB/CN runtime PASS/FAIL/NA]
  - [exit 139 present/absent]

## Sub-task Closeout Knowledge Capture
- [MUST] At the end of each gate or sub-task, decide whether the work produced a reusable [trace step] or recurring [problem pattern].
- [MUST] If useful, add a concise candidate to `agent_doc/Project_management/redcap_trace_problem_kb/candidate_inbox.md`.
- [MUST] Candidate entries include:
  - [Case] A / B / NA
  - [Gate] 0..5 / NA
  - [source evidence path]
  - [success marker]
  - [failure marker]
  - [step-by-step draft]
- [MUST] After every 5 completed sub-tasks, run the KB maintenance rule in `agent_doc/Project_management/redcap_trace_problem_kb/maintenance_rule.md`.
- [MUST] Keep all retained fix procedures numbered and step-by-step.
- [MUST NOT] store raw logs, full Docker output, or one-off command mistakes in the KB.
- [SHOULD] Prefer updating existing `trace_steps.md` or `problem_set.md` entries instead of creating new markdown files.

## Documentation Rule
- [MUST] Mark uncertain 3GPP clauses as `[Needs Verification]`.
- [MUST] Use Traditional Chinese project reports unless the user requests otherwise.
- [SHOULD] Promote only final reusable configs/evidence into `redcap_library/`.
