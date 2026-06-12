# D1 Document Architecture

## Goal
- Build a lightweight bilingual documentation structure for RedCap operator-facing folders.

## Scope
- Add `Doc/README.en.md` and `Doc/README.zh-TW.md` to folders that need navigation help.
- Keep stable docs in `redcap_doc/`.
- Keep reusable evidence and configs in `redcap_library/`.
- Keep execution plans and validation inventories in `agent_doc/Project_management/`.

## Acceptance Criteria
- [x] Each target `Doc/` folder has English and Traditional Chinese pages.
- [x] Pages identify the folder purpose and the next file to read.
- [x] API, Bash, and step-by-step sections are called out where useful.
- [x] No raw runtime logs are copied into stable docs.

## Discussion Point
- Historical report paths remain unchanged unless the report itself is being revised.
