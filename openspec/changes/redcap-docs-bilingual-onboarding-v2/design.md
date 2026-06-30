## Context

The repository already has a RedCap documentation router, bilingual `Doc/` folders, a zero-to-build guide, RedCap operator scripts, curated evidence folders, and paper recovery notes. The new change turns those pieces into a consistent public documentation system for external users.

## Goals / Non-Goals

**Goals:**
- Make the first README screen understandable to external users.
- Support English and Traditional Chinese as first-class public documentation languages.
- Keep language switching consistent across install, rebuild, API/interface, and tutorial routes.
- Provide separate beginner install and rebuild-after-change workflows.
- Convert Paper-07, Paper-10, and Paper-11 recovery procedures into concise bilingual tutorials.
- Provide a newcomer runtime gate that records unclear steps and verifies the 29 UE RFsim markers.

**Non-Goals:**
- Do not rewrite `agent_doc/` project-management files in this batch.
- Do not rewrite MinerU-generated Markdown or raw historical runtime logs.
- Do not delete historical paper reports.
- Do not claim new 3GPP behavior or runtime success without gate evidence.
- Do not add Japanese or Korean language links until those pages exist.

## Decisions

- Use split language files: `.en.md` and `.zh-TW.md`.
- Keep root `README.md` as a short language selector and project entry.
- Use `redcap_doc/manuals/install/` as the install documentation root.
- Public user-facing docs must not include `rtk`.
- Internal Codex/operator rules may still mention `rtk` when local workflow requires it.
- Preserve the existing `redcap_doc/evluation_recover/` spelling to avoid breaking links.
- Use the existing 29 UE RFsim summary markers as the acceptance target for the newcomer gate.

## Risks / Trade-offs

- [Risk] Paper recovery rewrite may obscure historical evidence. Mitigation: keep reports unchanged and link them from the new tutorials.
- [Risk] Runtime gate depends on Docker, CN5G, local images, and host performance. Mitigation: separate static doc checks from full runtime execution.
- [Risk] Language links may drift. Mitigation: add a static documentation gate that checks bilingual pairs and cross-language links.
- [Risk] Existing Traditional Chinese files may contain encoding artifacts. Mitigation: scan for replacement characters and fix public docs touched by this change.
- [Risk] Some 3GPP clause mappings are not re-verified in this documentation batch. Mitigation: keep `[Needs Verification]` where exact clause proof is absent.
