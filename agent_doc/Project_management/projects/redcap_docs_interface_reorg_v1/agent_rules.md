# RedCap Docs and Interface Reorganization Agent Rules

## Project Entry
- Project plan: `agent_doc/Project_management/projects/redcap_docs_interface_reorg_v1/project_plan.md`
- Milestones: `agent_doc/Project_management/projects/redcap_docs_interface_reorg_v1/milestones/`
- Validation: `agent_doc/Project_management/projects/redcap_docs_interface_reorg_v1/validation/`

## Context Pack
- Read only:
  1. `project_plan.md`
  2. target milestone file
  3. relevant validation file
  4. target folder `Doc/README.en.md` and `Doc/README.zh-TW.md`

## Documentation Rules
- Keep every page short and task-oriented.
- Maintain English and Traditional Chinese together.
- Use these sections when relevant:
  - API / config behavior
  - Bash usage
  - Step-by-step recap commands
- Do not paste raw logs into stable docs.
- Reference log paths, markers, and commands instead.
- Mark uncertain standard mappings as `[Needs Verification]`.

## Script Rules
- Public operator scripts:
  - `redcap_interface/mmtc.menu.bash`
  - `redcap_interface/mmtc.display.bash`
- Functional scripts:
  - `redcap_interface/bash_library/fc_*`
- Legacy root scripts are shims only.
- Do not delete shims until references are migrated and the owner approves removal.

## Validation Rules
- Shell scripts: `bash -n`.
- Python scripts: AST syntax parse through `redcap_interface/validate_redcap_interface.sh`.
- Interface package: `bash redcap_interface/validate_redcap_interface.sh`.
- Documentation hygiene: targeted `rg` stale-path scan plus `git diff --check`.
