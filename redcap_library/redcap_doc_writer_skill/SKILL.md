---
name: redcap-doc-writer
description: Use when updating RedCap/OAI documentation for this repo, especially API/config behavior, Bash operator usage, step-by-step recap commands, bilingual Doc pages, Project_management plans, README routing, OpenSpec-backed documentation changes, or active-path migrations that must preserve historical evidence.
metadata:
  input: Target documentation scope, audience, language requirement, and approved behavior or path contract.
  output: Updated documentation paths, validation status, retained historical evidence, and next action.
  tool_dependencies:
    - validate_redcap_public_docs
    - validate_dapp_xapp_sdk_docs
    - selftest_dapp_xapp_sdk_contract
    - validate_redcap_oran_sdk_workflow_v3
---

# RedCap Doc Writer

## Workflow

1. Load the smallest context pack:
   - target project `project_plan.md` and `agent_rules.md` when project-scoped,
   - target folder `Doc/README.en.md`,
   - target folder `Doc/README.zh-TW.md`,
   - target script or config only when needed.
2. Classify the update:
   - API/config behavior,
   - Bash usage,
   - step-by-step recap,
   - beginner build/run guide,
   - validation/report summary.
3. Update English and Traditional Chinese pages together.
4. Keep the writing KISS:
   - short bullets,
   - runnable commands,
   - expected markers,
   - links to source files instead of copied logs.
5. Use current entrypoints:
   - installation and 1 UE acceptance: root `mmtc.menu.bash install`,
   - daily RFsim: root `mmtc.menu.bash`,
   - paper/demo: `redcap_interface/mmtc.display.bash`,
   - implementation helpers: `redcap_interface/bash_library/fc_*`.
6. Preserve historical evidence:
   - do not rewrite old report commands unless the report is being actively corrected,
   - explain legacy root scripts as compatibility shims.
7. Handle standards carefully:
   - cite exact local notes or exact 3GPP clause numbers only after verification,
   - write `[Needs Verification]` when the clause mapping is uncertain.

## OpenSpec Documentation And Path Migration

Use this sequence for documentation structure changes, README routing, and canonical-path migrations. Reference implementation: `openspec/changes/migrate-redcap-sdk-reference-root-to-apps-dev/`.

1. Challenge the scope before editing:
   - reuse an existing README, guide, checker, or skill,
   - create a separate small OpenSpec change when the work is repository hygiene rather than part of a larger feature change,
   - do not create a compatibility symlink, duplicate reference tree, generator, or parallel document hierarchy without a demonstrated need.
2. Inventory before writing:
   - locate the real files and all active consumers,
   - classify each match as active documentation, active validator, historical report, runtime evidence, or completed change artifact,
   - inspect tracking and ignore state before renaming a tracked file; edit in place when a replacement path would be ignored.
3. Define the contract in English OpenSpec artifacts:
   - proposal: state the path or documentation drift and explicit non-goals,
   - spec: use a real `## ADDED Requirements` delta with `#### Scenario:` blocks,
   - design: record active-versus-historical boundaries and rejected symlink/copy alternatives,
   - tasks: include inventory, implementation, stale-reference scan, path existence, checker results, diff hygiene, and strict OpenSpec validation.
4. Write the smallest useful navigation layer:
   - use one concise bilingual README for a small internal reference root,
   - keep public root README selector-only and route to split `.en.md` and `.zh-TW.md` pages,
   - use a table when users must map several needs to several paths,
   - state which paths are reference inputs and which modules own production behavior.
5. Update every active consumer:
   - plans, rules, guides, gate definitions, module READMEs, defaults, messages, and static validators,
   - preserve historical paths when they record the state used by an old report or retained evidence,
   - avoid mechanical full-repository replacement.
6. Falsify completion:
   - scan beyond the first known project for other active consumers,
   - verify every newly documented path exists,
   - rerun the registered checker that owns each changed contract,
   - report unrelated checker failures separately instead of folding them into the documentation change.
7. Finish only when:
   - active scope has no stale canonical path,
   - historical evidence is unchanged,
   - relevant registered checks and diff hygiene have run,
   - OpenSpec strict validation passes and all tasks record honest status.

## API Documentation Rules

1. Use the existing Markdown destinations:
   - canonical L1-L3 lookup: `redcap_doc/specs/function_reference/redcap_l1_l3_function_lookup.md`,
   - dApp/xApp guide: the active project's paired `sdk_development_guide.*.md` files.
2. Organize content as:
   - Reference: signatures, state, guards, callers, callees, apply points, markers, next trace,
   - Guide: task-oriented development and validation flow,
   - Example: the existing 29 UE and 56 UE tutorials.
3. Put C and Python mirrors in the same API card when both exist. State behavioral differences; do not imply parity from matching names.
4. Record evidence independently:
   - `Public`: declaration or supported Python module,
   - `Integrated`: production caller plus identifiable apply path,
   - `Runtime-evidenced`: matching retained runtime marker,
   - `Dormant/blocked`: missing caller, apply path, or runtime proof.
5. Keep missing caller, callee, apply point, marker, or standards mapping visible as `[Needs Verification]`.
6. Do not add OpenAPI, hosted Stoplight configuration, a generator, or a parallel stable API tree unless a later change proves the need.

## Beginner Build/Run Guide Rules

Use this workflow when writing a guide for a first-time user:

1. Define the audience and the final validation target first.
2. Start from the repository root.
3. Separate the guide into:
   - install-first interactive path and acceptance boundary,
   - prerequisites and manual fallback,
   - dependency install,
   - local CMake build,
   - Docker image rebuild,
   - runtime execution,
   - expected markers,
   - short troubleshooting.
4. Keep user-facing commands as normal shell commands.
   - Do not write Codex-only wrappers such as `rtk` into stable user manuals.
   - Use `rtk` only in Codex conversation-side validation commands when local rules require it.
5. Prefer one concrete acceptance target over many branches.
   - Installer: 1 UE RFsim validation with `sample=1`, `running=1`, `attach=1`, `pdu=1`, `tun=1`, `forward_ping_ok=1`, `gnb_restart=0`, `failures=0`.
   - Newcomer reproduction: keep the separate 29 UE markers and never infer them from installer success.
6. Put logs behind paths and marker names.
   - Do not paste raw runtime logs into the stable guide.
7. When a guide has an English page and a Traditional Chinese page, update both in the same change.
8. Put the installer before tutorials, retain the manual build fallback plus separate 29 UE reproduction, and route 56 UE and dApp/xApp experiments to the existing Gate E-Core manual.

## Public Bilingual Documentation Rules

Use these rules for public RedCap documentation entrypoints:

1. Keep root `README.md` as a short language selector.
2. Keep public English and Traditional Chinese pages split as `.en.md` and `.zh-TW.md`.
3. Do not add language links for languages that do not have real pages.
4. Keep install and rebuild manuals under `redcap_doc/manuals/install/`.
5. Use `redcap_doc/evluation_recover/README.en.md` and `README.zh-TW.md` for paper recovery tutorial routing.
6. Preserve historical reports as evidence and link to them from tutorials instead of rewriting their contents.
7. Public user-facing Markdown must not include Codex-only command wrappers.
8. Keep root `README.md` selector-only; place project routes and evidence definitions in `README.en.md` and `README.zh-TW.md`.

## Validation

Select only the registered checks that own the touched contract:

| Scope | Bash Tool Registry entry |
|---|---|
| Public bilingual routes and newcomer documentation | `validate_redcap_public_docs` |
| dApp/xApp SDK documents, paths, and evidence contracts | `validate_dapp_xapp_sdk_docs` |
| dApp/xApp SDK contract behavior | `selftest_dapp_xapp_sdk_contract` |
| O-RAN SDK Workflow 3.0 reference maps and static contracts | `validate_redcap_oran_sdk_workflow_v3` |

Also perform targeted stale-reference, documented-path existence, syntax, and diff-hygiene checks through the repository file-query workflow. Do not claim the documentation change failed when a registered checker stops on an unrelated pre-existing dependency; record the blocker and prove the changed contract independently.
