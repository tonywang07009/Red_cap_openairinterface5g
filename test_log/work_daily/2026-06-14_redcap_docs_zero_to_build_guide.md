# 2026-06-14 RedCap Docs Zero-to-Build Guide

## Scope
- Project: `agent_doc/Project_management/projects/redcap_docs_interface_reorg_v1`
- Task: add a beginner build/run guide and update the doc writer Skill.

## Completed
- Added bilingual zero-to-build guide:
  - `redcap_doc/manuals/redcap_zero_to_build_and_run_guide.en.md`
  - `redcap_doc/manuals/redcap_zero_to_build_and_run_guide.zh-TW.md`
- Routed the guide from:
  - root `README.md`
  - `redcap_doc/README.md`
  - `redcap_doc/manuals/README.md`
  - manual `Doc/` pages
- Updated `redcap_library/redcap_doc_writer_skill/SKILL.md` with Beginner Build/Run Guide Rules.
- Added project milestone `D5_zero_to_build_guide.md`.

## Validation Target
- Documentation target: route and style validation.
- Runtime target documented for future execution:
  - 29 UE stage scan.
  - PASS markers: `sample=29`, `running=29`, `attach=29`, `pdu=29`, `tun=29`, `forward_ping_ok=29`, `gnb_restart=0`, `failures=0`.

## Boundary
- No C code, Bash behavior, Docker image, or RFsim runtime state changed in this documentation batch.
