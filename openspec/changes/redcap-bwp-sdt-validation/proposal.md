## Why

The RedCap/OAI project needs a reproducible validation track for two evaluation papers: [BWP switching] and [Small Data Transmission]. The current repo has useful RedCap RFsim and SDT hooks, but no project-scoped paper extraction, experiment records, result schema, or plot pipeline for reproducing these papers.

## What Changes

- Add a paper conversion and metadata workflow for the two BWP/SDT PDFs.
- Add a project folder under `agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/`.
- Define structured experiment settings, step records, result CSV schema, summary report, and plot generation for [paper curve vs local curve] comparisons.
- Reuse the existing RedCap RFsim/FlexRIC runtime path without changing OAI C code in this scaffold pass.
- Record 3GPP clause mappings with `[Needs Verification]` until local spec Markdown is converted and checked.

## Capabilities

### New Capabilities
- `redcap-bwp-sdt-paper-sync`: Convert BWP/SDT PDFs to Markdown, refresh metadata, and index the paper folder with SymDex.
- `redcap-bwp-sdt-experiment-records`: Store project planning, experiment steps, result CSVs, summary analysis, and plots for BWP/SDT reproduction.

### Modified Capabilities
- None.

## Impact

- Affected project docs: `agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/`.
- Affected paper docs: `redcap_doc/evaluation_papers/redcap_vaildation_BWP_SDT/`.
- Affected tooling: `markitdown`, `symdex`, `openspec`, Python standard library, matplotlib.
- Runtime source of truth remains `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/`.
