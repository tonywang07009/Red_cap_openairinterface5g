# RedCap mMTC Priority Execution Agent Rules

## Project Entry
- Project plan: `agent_doc/Project_management/projects/redcap_mmtc_priority_execution_v1/project_plan.md`
- Milestones: `agent_doc/Project_management/projects/redcap_mmtc_priority_execution_v1/milestones/`
- Validation: `agent_doc/Project_management/projects/redcap_mmtc_priority_execution_v1/validation/`
- Baseline archive: `agent_doc/Project_management/Simluation_v2.md`

## Token-Efficient Context Pack
- Read only:
  1. `project_plan.md`
  2. target milestone file
  3. relevant validation file
  4. latest `test_logs/work_daily/*.md`

## Document Model
- `project_plan.md` is the active index and status source.
- `Simluation_v2.md` is retained as a baseline archive only.
- One milestone equals one Markdown file under `milestones/`.
- Test definitions are centralized in `validation/test_matrix.md`.
- RFsim log-marker expectations are centralized in `validation/runtime_checklist.md`.
- 3GPP clause traceability is centralized in `validation/spec_traceability_matrix.md`.
- New tasks should update the smallest relevant milestone file.
- Do not mark a milestone complete unless its milestone file and validation matrix agree on required evidence.

## Implementation Gate
- Before changing PHY, MAC, or RRC:
  1. Read the project plan.
  2. Read the target milestone file.
  3. Read the relevant validation file.
  4. Summarize milestone, task ID, and validation IDs.

## O-RAN Scope
- Current priority is RedCap and mMTC behavior inside OAI:
  - UE/gNB flow
  - 3GPP alignment
  - RFsim runtime validation
  - repeatable logs
- Do not implement xApp/rApp/dApp SDKs until RedCap UE/gNB behavior has passed the planned validation flow.
- Near-RT RIC / xApp scope is limited to existing FlexRIC runtime checks unless explicitly promoted.
- Non-RT RIC / rApp work is design/documentation only until explicitly promoted.
- dApp work is out of implementation scope unless the user defines interface, runtime target, and validation criterion.

## RFsim Runtime Source
- Runtime scenario directory:
  - `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/`
- Treat this compose path and its directly mounted config files as source of truth.
- For UE2 RedCap validation, start from compose service `oai-nr-ue2` and mounted config `../../conf_files/nrue_recap/nrue2.uicc.yaml`.
- If runtime fixes require config edits, modify only files referenced by this compose path.
- XML scenarios or unused files that can affect future work must be reported before removal:
  - path
  - why it appears unused
  - references checked
  - expected impact

## PHY Work Order
- Applies to `openair1/` or PHY-related radio/config behavior.
- Required order:
  1. Locate existing implementation in `openair1/` and related configs.
  2. Cross-check against `spec/redcap_3gpp/spec.md` and TS 38.306 / TS 38.101-1.
  3. Propose the change in Traditional Chinese before editing.
  4. Patch one function or one parameter group at a time.
  5. Plan the closest build/test.

## Build/Test Reporting
- After C/C++ patches, rebuild affected targets:
  - UE-side: `cmake --build --preset default --target nr-uesoftmodem`
  - gNB-side: `cmake --build --preset default --target nr-softmodem`
- For shared or cross-layer changes, build every affected side and the closest unit-test target.
- At the end of each implementation sub-task, run the closest corresponding unit test when one exists.
- If no meaningful unit test exists, report `[unit test N/A]` and use nearest build or RFsim runtime validation.
- Reports must separate:
  - `[source build PASS/FAIL]`
  - `[unit test PASS/FAIL]`
  - `[container image rebuilt or not]`
  - `[RFsim UE/gNB/CN runtime PASS/FAIL]`
