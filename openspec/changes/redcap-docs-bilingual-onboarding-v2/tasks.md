## 1. OpenSpec Scaffold

- [x] 1.1 Create `openspec/changes/redcap-docs-bilingual-onboarding-v2/`.
- [x] 1.2 Add `proposal.md`.
- [x] 1.3 Add `design.md`.
- [x] 1.4 Add `tasks.md`.
- [x] 1.5 Add OpenSpec delta requirements for public RedCap documentation.

## 2. README Language Routing

- [x] 2.1 Convert root `README.md` into a short language selector.
- [x] 2.2 Add `README.en.md`.
- [x] 2.3 Add `README.zh-TW.md`.
- [x] 2.4 Add `English | 繁體中文` links only.
- [x] 2.5 Route English pages to English docs and Traditional Chinese pages to Traditional Chinese docs.

## 3. Install Manuals

- [x] 3.1 Add `redcap_doc/manuals/install/README.en.md`.
- [x] 3.2 Add `redcap_doc/manuals/install/README.zh-TW.md`.
- [x] 3.3 Add `redcap_doc/manuals/install/redcap_begin_from_zero.en.md`.
- [x] 3.4 Add `redcap_doc/manuals/install/redcap_begin_from_zero.zh-TW.md`.
- [x] 3.5 Add `redcap_doc/manuals/install/redcap_rebuild_after_changes.en.md`.
- [x] 3.6 Add `redcap_doc/manuals/install/redcap_rebuild_after_changes.zh-TW.md`.
- [x] 3.7 Update existing manual indexes to point to the install folder.

## 4. Public Doc Style Alignment

- [x] 4.1 Inventory stable public RedCap docs under `redcap_doc/`, `redcap_interface/`, and `redcap_library/`.
- [x] 4.2 Align API/config/tutorial docs with `doc_example/api_introfuction_example.md`.
- [x] 4.3 Keep historical reports as linked evidence instead of rewriting them as tutorials.
- [x] 4.4 Fix visible Traditional Chinese encoding issues in touched public docs.

## 5. Paper Recovery Tutorials

- [x] 5.1 Rewrite Paper-07 recovery tutorial in English and Traditional Chinese.
- [x] 5.2 Rewrite Paper-10 recovery tutorial in English and Traditional Chinese.
- [x] 5.3 Rewrite Paper-11 recovery tutorial in English and Traditional Chinese.
- [x] 5.4 Use `doc_example/tutro_example.md` as the tutorial structure.
- [x] 5.5 Mark proxy reproduction and RF-equivalence limits explicitly.

## 6. Newcomer Runtime Gate

- [x] 6.1 Add `redcap_doc/manuals/install/redcap_newcomer_runtime_gate.en.md`.
- [x] 6.2 Add `redcap_doc/manuals/install/redcap_newcomer_runtime_gate.zh-TW.md`.
- [x] 6.3 Include dependency checks, build, image rebuild, 29 UE RFsim run, and marker validation.
- [x] 6.4 Define the feedback format for a new Codex session.
- [x] 6.5 Add a public-doc static validation script for links, language pairing, forbidden `rtk`, encoding artifacts, and required markers.

## 7. Validation

- [x] 7.1 Run `bash redcap_interface/validate_redcap_interface.sh`.
- [x] 7.2 Run the new documentation gate script.
- [x] 7.3 Run `git diff --check` on touched documentation paths.
- [x] 7.4 Execute the newcomer runtime gate in a fresh Codex session or record why host-state validation is deferred.
- [x] 7.5 Record unclear steps, failures, and next-version documentation fixes.
