## 1. OpenSpec Scaffold

- [x] 1.1 Create `openspec/changes/redcap-oran-sdk-workflow-v3/`.
- [x] 1.2 Add `proposal.md`.
- [x] 1.3 Add `design.md`.
- [x] 1.4 Add delta specs for workflow and reporting/static CI.
- [x] 1.5 Add this implementation checklist.

## 2. Project Documentation And Static Checks

- [x] 2.1 Add `agent_doc/Project_management/projects/redcap_oran_sdk_workflow_v3/project_plan.md`.
- [x] 2.2 Add `agent_doc/Project_management/projects/redcap_oran_sdk_workflow_v3/agent_rules.md`.
- [x] 2.3 Add first milestone files for workflow scaffold, SDK contract, SDK runtime v1, and reporting/static CI.
- [x] 2.4 Add Daily Report and Gate Report templates.
- [x] 2.5 Add a standard-library static checker for workflow v3 files.
- [x] 2.6 Route the project from root `AGENTS.md`.

## 3. SDK Runtime V1

- [x] 3.1 Inventory existing RedCap O-RAN control code and confirm reusable SDK seed files.
- [x] 3.2 Define the first reusable xApp C/C++ adapter boundary.
- [x] 3.3 Define the first rApp policy packaging boundary.
- [x] 3.4 Define the first dApp/gNB guard apply boundary.
- [x] 3.5 Wire one minimal SDK runtime path through contract validation and logging.

## 4. Validation

- [x] 4.1 Run OpenSpec validation for this change.
- [x] 4.2 Run the workflow v3 static checker.
- [x] 4.3 Run syntax validation on the static checker.
- [x] 4.4 Run the first SDK build check after runtime v1 code exists.
- [x] 4.5 Run the first RFsim Case B marker validation after runtime v1 code exists.

## 5. dev_refer Reference And SDK Channel Layout Update

- [x] 5.1 Add `spec_refs/dev_refer_reference_overview.md`.
- [x] 5.2 Add `spec_refs/oran_spec_usage_map.md`.
- [x] 5.3 Add `sdk_channel_layout.md`.
- [x] 5.4 Update Workflow 3.0 docs and OpenSpec artifacts to use `dev_refer/` and the docs-first rApp decision.
- [x] 5.5 Add `[Needs Verification]` to the Daily Report template and static checker.

## 6. SDK Scaffold Slice

- [x] 6.1 Add an OAI-tracked RedCap xApp SDK wrapper under `openair2/E2AP/REDCAP_SDK/`.
- [x] 6.2 Refactor `ci-scripts/redcap_ul_prb_ctrl_xapp.c` to use the xApp SDK builder.
- [x] 6.3 Add the first dApp guard SDK skeleton under `openair2/E3AP/`.
- [x] 6.4 Add the rApp docs-first policy package schema and Case B example.
- [x] 6.5 Extend the Workflow 3.0 static checker to verify SDK scaffold files.
- [x] 6.6 Extend the RedCap interface validator to check SDK scaffold files.

## 7. Python SDK Pairing

- [x] 7.1 Add Python xApp SDK helpers matching the C RedCap UL PRB control builder.
- [x] 7.2 Add Python dApp guard helpers matching the C guard SDK.
- [x] 7.3 Add C and Python rApp policy package helpers matching the docs-first policy schema.
- [x] 7.4 Extend static checker and interface validator to require C + Python SDK files.
