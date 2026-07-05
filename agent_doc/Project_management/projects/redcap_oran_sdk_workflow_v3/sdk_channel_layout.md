# SDK Channel Layout

## Purpose

- [Goal]: define how future RedCap xApp, dApp, and rApp SDK work should be placed relative to OAI source directories.
- [Rule]: match OAI channel organization before adding SDK code.
- [Current Phase]: documentation and planning only; no new runtime channel is created by this file.

## Channel Decisions

| SDK Family | Channel Decision | Reason | Current Action |
|---|---|---|---|
| [xApp] | Use `openair2/E2AP/REDCAP_SDK/` as the OAI-tracked wrapper and `openair2/E2AP/flexric/` as the FlexRIC dependency | OAI already places E2AP/FlexRIC integration under the E2AP channel, but `flexric` is a dirty submodule in this checkout | Keep RedCap SDK code in the tracked wrapper and compile it against FlexRIC |
| [dApp] | Use `openair2/E3AP/` | dApp references use E3/E3AP and E3 Service Models as the RAN-local application interface | Start with a guard SDK skeleton before adding transport or service-model code |
| [rApp] | Keep docs-first only | rApp spans Non-RT RIC, A1, O1, and generated API packages rather than one confirmed OAI runtime channel | Do not create `openair2/RAPP`, `openair2/A1AP`, or `openair2/O1` in this phase |

## Future xApp Placement

- [Target Root]: `openair2/E2AP/REDCAP_SDK/`.
- [FlexRIC Dependency]: `openair2/E2AP/flexric/`.
- [Allowed Content]:
  - thin RedCap-specific C/C++ xApp SDK adapters,
  - examples that reuse existing FlexRIC E2SM-KPM/E2SM-RC support,
  - build glue only when it is required by a pulled SDK task.
- [Not Allowed]:
  - broad Python xDevSM import,
  - full external example repository copy,
  - KPM-as-control wording.

## Future dApp Placement

- [Target Root]: `openair2/E3AP/`.
- [Expected Shape]:
  - `service_models/` for agent-side E3 Service Model code,
  - `sdk/` for thin OAI-facing dApp helpers,
  - `docs/` for channel-local integration notes,
  - `tests/` only after buildable code exists.
- [First Pull Requirement]:
  - define one service model,
  - define one RAN-side marker,
  - define build command and validation command,
  - document rollback or reject behavior.

## rApp Docs-First Rule

- [Current Home]: `agent_doc/Project_management/projects/redcap_oran_sdk_workflow_v3/spec_refs/`.
- [Allowed Content]:
  - Non-RT RIC role notes,
  - A1/O1 usage notes,
  - OpenAPI generation notes,
  - policy-package shape proposals.
- [Promotion Rule]: create an `openair2` rApp-facing channel only after a concrete OAI runtime boundary is selected and reviewed.

## Pull-Based Guard

- Start with one SDK family and one runtime or documentation objective.
- Require a source reference, channel target, validation marker, and report target before writing SDK code.
- Keep SLM evaluation out of this workflow until the local SLM tool exists.
