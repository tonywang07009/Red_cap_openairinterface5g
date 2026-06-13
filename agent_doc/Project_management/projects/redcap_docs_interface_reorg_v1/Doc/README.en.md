# RedCap Docs and Interface Reorganization

## Purpose
- This project explains the current documentation and Bash interface layout.
- Use it before changing `redcap_interface/`, `redcap_doc/`, or `redcap_library/`.
- Use it before changing the root `README.md` or RedCap documentation routes.

## Read Order
1. `project_plan.md`
2. `agent_rules.md`
3. Target milestone file
4. Target validation file

## Outputs
- Two public menus: `mmtc.menu.bash` and `mmtc.display.bash`.
- Functional script library: `redcap_interface/bash_library/fc_*`.
- Bilingual `Doc/` pages for key RedCap folders.
- Reusable doc writer Skill: `redcap_library/redcap_doc_writer_skill/SKILL.md`.
- Root `README.md` RedCap routing entry.
- RedCap L1/L2 protocol guide: `redcap_doc/specs/redcap_l1_l2_protocol_guide.md`.
- Beginner build/run guide: `redcap_doc/manuals/redcap_zero_to_build_and_run_guide.en.md`.

## README Template Rule
- Use `doc_example/Best_README_template/README.md` only as a section-structure reference.
- Do not copy the sample project's MIT license, badges, author fields, or Simplified Chinese branding.
- The root README must keep OAI license, NOTICE, upstream docs, and support routes.

## Beginner Guide Rule
- For first-time build/run documentation, keep one linear path from repository root to one pass/fail target.
- Current target: 29 UE RFsim validation markers.
