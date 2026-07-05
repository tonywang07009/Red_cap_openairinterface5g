# D5 Zero-to-Build Beginner Guide

## Goal
- Add a beginner-facing build and run guide.
- Keep English and Traditional Chinese pages paired.
- End the guide with one concrete RFsim validation target: 29 UE RedCap/mMTC.
- Update the reusable doc writer Skill so future beginner guides follow the same structure.

## Scope
- Add:
  - `redcap_doc/manuals/redcap_zero_to_build_and_run_guide.en.md`
  - `redcap_doc/manuals/redcap_zero_to_build_and_run_guide.zh-TW.md`
- Update routes:
  - root `README.md`
  - `redcap_doc/README.md`
  - `redcap_doc/manuals/README.md`
  - `redcap_doc/manuals/Doc/README.en.md`
  - `redcap_doc/manuals/Doc/README.zh-TW.md`
- Update Skill:
  - `redcap_library/redcap_doc_writer_skill/SKILL.md`

## Acceptance Criteria
- [x] A first-time user can follow one linear path from repository root to build commands.
- [x] The guide includes Docker image rebuild for `oai-gnb:latest` and `oai-nr-ue:latest`.
- [x] The guide includes a 29 UE RFsim validation command.
- [x] The guide defines pass markers:
  - `sample=29`
  - `running=29`
  - `attach=29`
  - `pdu=29`
  - `tun=29`
  - `forward_ping_ok=29`
  - `gnb_restart=0`
  - `failures=0`
- [x] English and Traditional Chinese pages are updated together.
- [x] Stable user manuals do not include Codex-only `rtk` command wrappers.

## Discussion Point
- The beginner guide is documentation only. It does not claim a new RFsim result.
- Actual RFsim execution remains a separate runtime validation task.
