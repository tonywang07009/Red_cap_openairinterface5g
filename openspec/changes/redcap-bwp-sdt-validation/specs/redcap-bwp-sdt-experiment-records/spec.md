## ADDED Requirements

### Requirement: Project planning document captures paper settings
The system SHALL store a project planning document with project name, 3GPP mappings, experiment goals, scenario descriptions, extracted parameters, and expected outputs.

#### Scenario: Planning document is present
- **WHEN** the validation project scaffold is created
- **THEN** `project_BWP_SDT.md` exists under `agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/`

### Requirement: Experiment steps are recorded per technology
The system SHALL provide separate Markdown step records for BWP switching and SDT small-data experiments.

#### Scenario: Step records include runtime provenance
- **WHEN** experiment step files are inspected
- **THEN** they include git commit, branch, runtime config, commands, log paths, and adjusted 3GPP parameters

### Requirement: Results use a stable CSV schema
The system SHALL store BWP and SDT result CSVs with the schema `scenario,metric,paper_value,local_value,diff_absolute,diff_percent`.

#### Scenario: Result files match schema
- **WHEN** result CSVs are parsed
- **THEN** each file exposes the required six columns in the required order

### Requirement: Plots compare paper and local values
The system SHALL generate PNG figures from result CSVs comparing paper values against local values.

#### Scenario: Figure output exists
- **WHEN** the matplotlib plotting script runs
- **THEN** `BWP_paper_vs_local.png` and `SDT_paper_vs_local.png` are written under `exp_pictture/`
