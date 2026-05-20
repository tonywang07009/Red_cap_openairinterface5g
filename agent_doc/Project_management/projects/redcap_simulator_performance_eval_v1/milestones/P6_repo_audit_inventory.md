# P6 Repo Audit Inventory

## Milestone Metadata
- Milestone: P6
- Task IDs: P6-T1
- Status: [NOT STARTED]

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
- [ ] Every cleanup candidate has path, reason, references checked, and expected impact.
- [ ] No deletion is performed during inventory.
