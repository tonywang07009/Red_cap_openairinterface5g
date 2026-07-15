# RedCap Library Agent Rules

## Scope
- Treat `redcap_library/` as curated reusable evidence, not as a live log sink.
- Generated runtime/build/compiler logs still belong in `test_log/`.
- Promote a generated artifact here only when it is final, reusable, or directly cited by a project report.

## Reading Order
1. `redcap_library/README.md`
2. One target subfolder `README.md`
3. Only the specific config, report, or log needed for the task

## Cleanup Rule
- Do not delete files from this library unless the user explicitly approves a new cleanup batch.
- If a file is replaced by a newer final artifact, update the relevant `README.md` and standardize the filename without timestamps.

## CN5G Rule
- The active CN5G runtime lives at repository root `oai-cn5g/`.
- Generate run-specific SQL and Compose overlays under `test_log/runtime_configs/`.
- Do not create a parallel CN5G asset library; Git history and the migration report retain removed legacy evidence.

## Naming Rule
- Use lowercase snake case.
- Remove timestamps from promoted final artifacts.
- Add a role suffix such as `_final`, `_report`, `_summary`, `_override`, or `_backup`.
