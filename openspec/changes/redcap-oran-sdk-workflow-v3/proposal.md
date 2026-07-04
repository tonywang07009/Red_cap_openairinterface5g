## Why

RedCap O-RAN SDK work now needs a concrete workflow that connects OpenSpec planning, existing OAI/FlexRIC code navigation, Ponytail review, standardized reporting, and low-cost CI checks. This change creates the workflow and project scaffold before implementing new xApp/dApp/rApp runtime behavior.

## What Changes

- Add a RedCap Workflow 3.0 project for O-RAN SDK planning and execution.
- Define a minimal SDK v1 contract split across [rApp policy], [xApp C/C++ KPM/RC adapter], and [dApp/gNB guard].
- Add Daily Report and Gate Report templates for progress and validation evidence.
- Add a static CI/checker path for OpenSpec artifacts, YAML control contracts, report templates, and overclaim prevention.
- Keep [SLM evaluation tooling] out of scope until the local SLM environment is available.

## Capabilities

### New Capabilities

- `redcap-oran-sdk-workflow`: Project workflow, pull rules, and SDK v1 ownership boundaries for RedCap xApp/dApp/rApp work.
- `redcap-workflow-reporting-ci`: Daily/Gate reporting requirements and static CI checks for contract/report quality.

### Modified Capabilities

- None.

## Impact

- Affected planning artifacts: `openspec/changes/redcap-oran-sdk-workflow-v3/`.
- Affected project docs: `agent_doc/Project_management/projects/redcap_oran_sdk_workflow_v3/`.
- Affected root routing: `AGENTS.md` active project entries.
- Affected validation: a new static checker under the workflow v3 project scripts.
- Runtime OAI/FlexRIC behavior is not changed by this scaffold.
