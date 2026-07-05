# P6 Repo Audit Inventory

## 2026-05-25 Evidence Cleanup Note
- The approved cleanup batch promoted reusable evidence into `redcap_library/` and cleaned the selected heavy `test_log` folders.
- Use `redcap_library/README.md` as the current evidence index.

## Milestone Metadata
- Milestone: P6
- Task IDs: P6-T1
- Status: [COMPLETED]

## Purpose
- Inventory folders, stale logs, unused manuals, and cleanup candidates.

## Audit Rule
- This milestone is [inventory-only].
- Do not delete, move, or rewrite files unless the user explicitly approves a specific cleanup batch.

## Required Checks
- tree-level folder inventory
- large file inventory
- old work log inventory
- duplicate manual/document candidates
- unreferenced scenario/config candidates

## Candidate Classification
- [Keep]
- [Archive Candidate]
- [Delete Candidate]
- [Needs Owner Review]
- [Generated Artifact]

## Acceptance Criteria
- [x] Every cleanup candidate has path, reason, references checked, and expected impact.
- [x] No deletion is performed during inventory.

## Evidence Output
- Audit inventory: `agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/validation/repo_audit_inventory.md`
- Cleanup batch 1 log: `test_log/work_daily/2026-05-21_13-18-58_p6-cleanup-batch1.md`

## Findings Summary
- Largest generated artifact areas:
  - `test_log/` at `5.3G`
  - `cmake_targets/` at `3.7G`
- Highest-confidence cleanup candidates after approval:
  - Python `__pycache__/` directories.
  - Source-tree CMake artifacts under `openair1/`.
  - Tiny `.env.bak.*` files under `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/`.
  - Empty `paper_test/` folder after updating the paper index note.
- High-risk evidence stores that should not be deleted blindly:
  - `test_log/compiler_logs/`
  - `test_log/runtime_artifacts/`
  - `cmake_targets/log/container_5g_flexric_rfsim_redcap.xml.d/`

## Cleanup Batch 1
- Status: [COMPLETED]
- Scope: low-risk generated artifacts and empty legacy folder only.
- Preserved evidence stores and historical manuals.
