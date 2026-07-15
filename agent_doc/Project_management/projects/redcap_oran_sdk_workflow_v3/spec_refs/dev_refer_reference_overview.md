# Apps_dev Reference Overview

## Purpose

- [Goal]: explain how the `Apps_dev/` library supports future RedCap xApp, dApp, and rApp SDK work.
- [Scope]: planning and SDK layout only; this file does not claim runtime behavior or O-RAN clause compliance.
- [Verification Rule]: exact O-RAN clause mappings remain `[Needs Verification]` until the local PDF/DOCX text is extracted and reviewed.

## Source Families

| Family | Path | What It Is For | Workflow Use |
|---|---|---|---|
| [Formal xApp references] | `Apps_dev/develop_refer_doc/xapp/` | O-RAN WG3 documents for Near-RT RIC, E2, E2SM-KPM, E2SM-RC, E2SM-CCC, and ETSI PAS E2 service-model material | Use before defining xApp SDK behavior, KPM observation, or RC/custom-SM control |
| [Formal dApp references] | `Apps_dev/develop_refer_doc/dapp/` | nGRG dApps architecture and interfaces reference | Use before defining dApp/E3 runtime boundaries |
| [Formal rApp references] | `Apps_dev/develop_refer_doc/rapp/` | O-RAN WG2 Non-RT RIC, A1, O1, and use-case requirement references | Use for rApp policy and management-interface planning only |
| [xApp SDK references] | `Apps_dev/xapp_dev_need/` | xDevSM framework and example xApps | Use as external SDK design input, not as code to copy into OAI |
| [dApp SDK references] | `Apps_dev/dapp_dev_need/` | FlexRIC, E3Controller, libe3, dApp library, and dApp-oriented OAI fork references | Use to extend the `openair2/E3AP/` scaffold |
| [rApp SDK references] | `Apps_dev/rapp_dev_need/` | OpenAPI Generator reference for API client/server/document generation | Use only for rApp-facing API packaging after the runtime boundary is defined |

## Practical Interpretation

- [xApp]: the strongest current OAI-compatible path is a small RedCap wrapper under `openair2/E2AP/REDCAP_SDK/`, compiled against FlexRIC under `openair2/E2AP/flexric/`.
- [dApp]: the reference material points to an E3AP/E3 Service Model pattern; OAI-facing work starts under `openair2/E3AP/`.
- [rApp]: keep docs-first for now. rApp references explain policy, A1/O1, and Non-RT RIC roles, but they do not yet justify creating an OAI runtime channel.
- [No Vendor Dump]: do not copy full external SDK repositories into `openair2`; create thin OAI-facing SDK boundaries only when a pulled work item needs them.

## Pull Rule

- Before pulling a new SDK implementation task, add or update a short spec note in this folder that states:
  - source file or directory,
  - target OAI channel,
  - expected SDK responsibility,
  - validation marker or static check,
  - `[Needs Verification]` items.
