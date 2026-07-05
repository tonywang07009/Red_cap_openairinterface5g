# RedCap Docs README and Protocol Routing Update

## Conclusion
- Root `README.md` was rewritten as a template-style RedCap/OAI route page.
- `redcap_docs_interface_reorg_v1` now owns D4: root README and protocol routing.
- A dedicated RedCap L1/L2 protocol guide now lives under `redcap_doc/specs/`.

## Required Project Fields
- Project Path: `agent_doc/Project_management/projects/redcap_docs_interface_reorg_v1/project_plan.md`
- [Case]: Documentation
- [Gate]: D4
- [source build PASS/FAIL/NA]: NA, docs only.
- [unit test PASS/FAIL/NA]: NA, docs only.
- [RFsim runtime PASS/FAIL/NA]: NA, docs only.
- [exit 139]: NA.

## Changed Routes
| Route | Purpose |
|---|---|
| `README.md` | RedCap/OAI root route page |
| `redcap_doc/specs/redcap_l1_l2_protocol_guide.md` | RedCap L1/L2 protocol overview |
| `redcap_doc/specs/function_reference/redcap_l1_l3_function_lookup.md` | Exact function lookup |
| `agent_doc/Project_management/projects/redcap_docs_interface_reorg_v1/milestones/D4_root_readme_protocol_routing.md` | D4 acceptance criteria |

## Validation
- Documentation diff check: `git diff --check` on touched docs.
- Stale template scan: check for `Best_README_template`, `shaojintian`, `MIT License`, and `LinkedIn` in routed docs.
- Stale function-reference route scan: check for incorrect `redcap_doc/function_reference/README.md` references.
