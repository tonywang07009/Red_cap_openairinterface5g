# RedCap Docs and Interface Reorganization Project (v1)

## Project Metadata
- Project Path: `agent_doc/Project_management/projects/redcap_docs_interface_reorg_v1/project_plan.md`
- Created Date: 2026-06-12
- Updated Date: 2026-06-12
- Milestone Directory: `agent_doc/Project_management/projects/redcap_docs_interface_reorg_v1/milestones/`
- Validation Directory: `agent_doc/Project_management/projects/redcap_docs_interface_reorg_v1/validation/`
- Interface Root: `redcap_interface/`
- Stable Docs Root: `redcap_doc/`
- Curated Library Root: `redcap_library/`
- Objective: Keep RedCap documentation and Bash operator interfaces small, bilingual, traceable, and easy to maintain.

## QFD Summary
| Voice of User | Quality Characteristic | Implementation | Validation |
|---|---|---|---|
| Keep docs simple | KISS, short sections, no raw log dumps | Use `Doc/README.en.md` and `Doc/README.zh-TW.md` per target folder | `validation/doc_style_checklist.md` |
| Split docs by use case | API, Bash, step-by-step recap sections | Each doc page states scope and next file to read | `Doc/` page review |
| Keep English and Traditional Chinese | American English page plus zh-TW page | Pair `README.en.md` with `README.zh-TW.md` | Bilingual page existence check |
| Make Bash menu usable | Only two public menus | `mmtc.menu.bash` and `mmtc.display.bash` | `validation/script_interface_checklist.md` |
| Keep functional scripts organized | Function scripts named `fc_*` | Move implementations into `redcap_interface/bash_library/` | `redcap_interface/validate_redcap_interface.sh` |
| Avoid unsafe cleanup | Inventory first, delete only after approval | Keep shims and list cleanup candidates | `validation/cleanup_inventory.md` |
| Preserve future doc consistency | Reusable doc writer skill | `redcap_library/redcap_doc_writer_skill/SKILL.md` | Skill file existence and content review |

## Seven-Question Definition
| Question | Answer |
|---|---|
| What | Reorganize RedCap docs and shell interface entrypoints. |
| Why | Current operator scripts and docs are hard to scan, and old paths mix daily tests with paper demos. |
| Who | Caramel Bird uses the menus and docs; Codex maintains the structure during future feature work. |
| Where | `redcap_interface/`, `redcap_doc/`, `redcap_library/`, and active `agent_doc/Project_management/projects/*/Doc/`. |
| When | Apply now as a documentation and script hygiene batch before the next runtime-heavy RFsim pass. |
| How | Keep two public menus, move functional helpers to `bash_library/fc_*`, and add bilingual `Doc/` pages. |
| How Verified | Shell syntax, Python syntax, interface validator, doc diff check, and stale-path inventory. |

## Milestone Index
| Milestone | File | Purpose | Status |
|---|---|---|---|
| D1 | `milestones/D1_document_architecture.md` | Define bilingual KISS doc layout and folder routing | [x] |
| D2 | `milestones/D2_script_interface_reorg.md` | Define two-menu Bash interface and `fc_*` library rules | [x] |
| D3 | `milestones/D3_doc_writer_skill.md` | Define reusable documentation Skill workflow | [x] |

## Validation Index
| File | Purpose |
|---|---|
| `validation/cleanup_inventory.md` | Inventory of retained, shimmed, or future cleanup candidates |
| `validation/doc_style_checklist.md` | KISS, bilingual, API/Bash/step-by-step checklist |
| `validation/script_interface_checklist.md` | Shell/Python/interface validation checklist |

## Current Boundary
- This project is a repository organization and documentation implementation batch.
- It does not claim new 3GPP behavior.
- DRX/eDRX/PSM knobs exposed through the menu and control contract are a configuration surface. Exact Release 17/18 timer encoding remains `[Needs Verification]` until checked against the local spec notes.
- Legacy root scripts remain as compatibility shims because existing reports and manuals still reference them.

## Next Action
- Use `redcap_library/redcap_doc_writer_skill/SKILL.md` whenever a future feature adds API behavior, Bash behavior, or recap instructions.
- Promote old root-script references to the new two-menu model only when editing the target manual for a real update.
