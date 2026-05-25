# M7 Repository Hygiene

## Scope
- Identify unused Bash scripts, Markdown files, generated runtime artifacts, and stale references.
- Propose safe removals to keep `Red_cap_openairinterface5g` clean and maintainable.
- Preserve files needed for RedCap/mMTC reproducibility, runtime validation, evidence, or learning reports.

## Out of Scope
- Removing source files used by OAI build targets.
- Removing XML/YAML scenarios without explicit pre-removal report and user approval.
- Refactoring protocol behavior.
- Deleting daily logs or runtime evidence without explicit user approval.

## 3GPP Spec Mapping
- N/A — repository hygiene task.
- Any file tied to a spec validation flow must be preserved until its replacement is documented.

## Target Files
- Bash scripts under:
  - `ci-scripts/`
  - `scripts/`
  - scenario-local `scripts/` directories.
- Markdown files under:
  - `agent_doc/`
  - `doc/`
  - project reports and local planning folders.
- Generated or historical artifacts under:
  - `test_log/`
  - legacy `test_logs/` references, if any remain in historical docs.
- Cross-reference sources:
  - `AGENTS.md`
  - `project_plan.md`
  - milestone files under `milestones/`
  - validation files under `validation/`

## Implementation Tasks
- `M7-T1`: Inventory unused Bash and Markdown files.
- `M7-T2`: Report removal candidates with path, reason, references checked, and expected impact.
- `M7-T3`: Remove only user-approved candidates and update stale references.

## Flow Validation
- For every candidate file, check:
  - `rg` references across the repo.
  - compose, CI, and helper script references.
  - project docs and daily logs references.
  - whether the file is generated output, source-of-truth input, or preserved evidence.

## System Unit Tests
- `UT-M7-001`: `git diff --check` after approved cleanup.
- `UT-M7-002`: Shell syntax check for modified `.sh` files.
- `UT-M7-003`: Documentation link/reference scan after approved removals.

## RFsim Runtime Tests
- Runtime is not required for documentation-only cleanup.
- If cleanup touches RFsim scripts or compose-related files, run the closest prepare-only or smoke validation before marking complete.

## Current Evidence
- 2026-05-25 approved cleanup batch:
  - User approved removal of low-value `test_log` work logs and promotion of reusable artifacts into `redcap_library/`.
  - Curated library root: `redcap_library/`.
  - Runtime/build/compiler scripts continue to write new generated logs under `test_log/`.
  - Reusable final configs, reports, CN5G overlays, runtime probe logs, and retained FlexRIC service-model libs are now indexed by `redcap_library/README.md`.
- 2026-05-08 inventory-only report:
  - Report: `redcap_library/library_reports_summary/m7_repo_hygiene_inventory_legacy.md`.
  - Markdown inventory count: `460`.
  - Shell script inventory count: `90`.
  - Report inventory count: `90`.
  - Work daily inventory count: `175`.
- Legacy reference scan highlights:
  - `agent_doc/Project_management/Simluation_v2.md` is referenced as baseline archive and must be preserved.
  - `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/docker-compose.mmtc.yml` is runtime source-of-truth/generated overlay and must be preserved.
  - `test_log/work_daily/` remains the only temporary work-log store.
  - Heavy generated `test_log/` artifacts are no longer treated as permanent evidence once promoted into `redcap_library/`.
- The 2026-05-08 closure was inventory-only; the 2026-05-25 cleanup supersedes that retention decision for the approved target folders.

## Removal Approval Contract
- Do not remove files immediately after detection.
- First report:
  - file path,
  - why it appears unused,
  - references checked,
  - expected impact of removal,
  - rollback note.
- Remove only after explicit user confirmation.

## Completion Criteria
- [inventory report completed]
- [user approval obtained before deletion] [x for 2026-05-25 target batch]
- [approved removals applied] [x for 2026-05-25 target batch]
- [stale references updated] [x for promoted final paths]
- [syntax and documentation checks PASS]
- [daily work log written]

## Closure Decision
- Status: [COMPLETED as inventory-only]
- Closure date: 2026-05-08.
- Closure basis:
  - Inventory report completed.
  - Reference scan completed for likely cleanup-looking project files and evidence stores.
  - No deletion was performed because deletion requires explicit user approval.
