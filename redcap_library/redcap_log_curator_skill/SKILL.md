---
name: redcap-log-curator
description: Use when cleaning RedCap OAI test_log artifacts into redcap_library, preserving reusable configs/evidence and deleting low-value timestamped logs after explicit user approval.
---

# RedCap Log Curator

## Workflow
1. Confirm the user has approved deletion or cleanup for the target artifact batch.
2. Inventory target folders with counts by extension and size before moving or deleting.
3. Promote only high-value artifacts into `redcap_library/`:
   - reproducible CN5G SQL/YAML overlays,
   - final gNB configs,
   - current runtime probe raw evidence,
   - final build evidence tied to a retained result,
   - curated Markdown reports or summaries.
4. Standardize promoted filenames:
   - lowercase snake case,
   - no timestamps,
   - include role suffixes such as `_final`, `_report`, `_summary`, `_override`, `_backup`.
5. Delete low-value artifacts after promotion:
   - duplicate timestamped logs,
   - generated runtime artifact folders,
   - generated binaries that can be rebuilt,
   - obsolete one-off reports already summarized.
6. Update references:
   - `redcap_library/README.md`,
   - target subfolder `README.md`,
   - root `AGENTS.md` router if a new reusable path is introduced,
   - bash defaults that pointed at moved final artifacts.
7. Verify with `rg` for stale final-path references and `git diff --check`.

## Guardrails
- Treat repository root `oai-cn5g/` as the active runtime; do not create a parallel CN5G asset library.
- Keep new runtime logs in `test_log/`; promote only final evidence.
- If an old report keeps historical `test_log/...` citations, explain that they are original evidence references.
