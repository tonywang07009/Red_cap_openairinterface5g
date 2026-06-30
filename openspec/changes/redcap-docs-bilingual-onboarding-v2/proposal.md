## Why

The RedCap/OAI workspace has useful local documentation, but a third-party beginner still needs a clearer path from zero setup to a validated RedCap RFsim run. Public documentation also needs consistent English/Traditional Chinese routing, separated install and rebuild procedures, paper reproduction tutorials, and no Codex-only command wrappers in user-facing manuals.

## What Changes

- Add root README language routing with English and Traditional Chinese entry pages.
- Add install manuals under `redcap_doc/manuals/install/`.
- Split zero-to-build-and-run setup from rebuild-after-change workflows.
- Align stable RedCap API, interface, and tutorial docs with the local examples in `doc_example/`.
- Rewrite paper recovery tutorials as bilingual procedural manuals while preserving historical reports as linked evidence.
- Add a newcomer runtime gate that another Codex session can execute from zero setup to 29 UE RFsim validation.
- Keep `agent_doc/`, MinerU-generated Markdown, and historical raw evidence outside the first public-document rewrite batch.

## Capabilities

### New Capabilities

- `redcap-doc-language-routing`: English and Traditional Chinese README routes without unsupported language links.
- `redcap-begin-install-manual`: Beginner path from repository entry to build, image rebuild, and 29 UE validation.
- `redcap-rebuild-manual`: Rebuild path after C, xApp, rApp, dApp, script, or library changes.
- `redcap-paper-recovery-tutorials`: Bilingual paper reproduction manuals for Paper-07, Paper-10, and Paper-11 recovery workflows.
- `redcap-newcomer-runtime-gate`: Reproducible gate for a fresh Codex window to validate documentation clarity and runtime readiness.

### Modified Capabilities

- Existing root README routing.
- Existing `redcap_doc/`, `redcap_interface/`, and `redcap_library/` public documentation routes.
- Existing RedCap doc writer guidance for future public-document updates.

## Impact

- Affected docs: `README.md`, `README.en.md`, `README.zh-TW.md`, `redcap_doc/`, `redcap_interface/`, `redcap_library/`.
- Affected examples: `doc_example/install_example.md`, `doc_example/api_introfuction_example.md`, `doc_example/tutro_example.md`.
- Affected validation: Markdown link checks, bilingual file pairing, public-doc `rtk` scan, encoding scan, and 29 UE RFsim marker checks.
- Runtime source of truth remains the existing RedCap RFsim scripts and YAML under `redcap_interface/` and `ci-scripts/`.
