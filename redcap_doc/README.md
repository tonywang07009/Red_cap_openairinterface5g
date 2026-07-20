# RedCap Doc

[English](./Doc/README.en.md) | [繁體中文](./Doc/README.zh-TW.md)

## Purpose
- This folder is the unified document root for RedCap papers, local specs, validation checklists, and reusable manuals.
- Keep generated runtime/build logs out of this folder; temporary logs belong under `test_log/`.
- Keep curated reusable runtime evidence under `redcap_library/`.

## Folder Map
| Folder | Role |
|---|---|
| `evaluation_papers/` | RedCap performance and technology papers used by the simulator evaluation project |
| `evluation_recover/` | Bilingual paper reproduction tutorials and historical recovery evidence |
| `specs/` | Local 3GPP/RedCap reference notes and PDFs |
| `checklists/` | Human-checkable milestone and validation checklists |
| `manuals/` | Stable operator and reproduction manuals |
| `manuals/aiot_tag_aiotf_architecture.zh-TW.md` | 繁體中文 A-IoT Tag/AIOTF 架構、profile 與 evidence boundary |
| `manuals/aiot_tag_aiotf_architecture.en.md` | English A-IoT Tag/AIOTF architecture, profiles, and evidence boundaries |
| `manuals/aiot_tag_aiotf_operator.zh-TW.md` | 繁體中文 A-IoT registered operator、展示與 cleanup 流程 |
| `manuals/aiot_tag_aiotf_operator.en.md` | English A-IoT registered operator, demonstration, and cleanup workflow |
| `manuals/install/` | Public install, rebuild, and newcomer gate manuals |
| `manuals/install/redcap_begin_from_zero.en.md` | English beginner path from zero setup to 29 UE RFsim validation |
| `manuals/install/redcap_begin_from_zero.zh-TW.md` | 繁體中文新手路徑：從 0 安裝到 29 UE RFsim 驗證 |
| `manuals/install/redcap_rebuild_after_changes.en.md` | English rebuild path after C, xApp, rApp, dApp, config, or library changes |
| `manuals/install/redcap_rebuild_after_changes.zh-TW.md` | 繁體中文修改後重建流程 |
| `specs/redcap_l1_l2_protocol_guide.md` | RedCap L1/L2 protocol guide for implementation learning |
| `specs/function_reference/` | L1-L3 RedCap function lookup tables |
| `function_reference/` | Compatibility Doc folder for function-reference writing rules |
| `mineru_markdown/` | MinerU-generated Markdown cache and manifest for papers/spec PDFs |

## Naming Rule
- Folder names use lowercase English plural nouns.
- Paper/spec filenames may keep their original names when renaming would reduce traceability.
- New index or guide files should be concise Markdown files named `README.md`, `paper_index.md`, or `<topic>_guide.md`.

## Reading Rule
- For paper-based experiments, start with `evluation_recover/README.en.md` or `evluation_recover/README.zh-TW.md`, then use `evaluation_papers/README.md` for PDF source lookup.
- For RedCap implementation/spec checks, start with `specs/README.md`.
- For milestone validation, start with `checklists/README.md`.
- For first-time build and 29 UE RFsim use, start with `manuals/install/redcap_begin_from_zero.zh-TW.md` or `manuals/install/redcap_begin_from_zero.en.md`.
- For rebuild after source, xApp, config, or library changes, start with `manuals/install/redcap_rebuild_after_changes.zh-TW.md` or `manuals/install/redcap_rebuild_after_changes.en.md`.
- For newcomer reproducibility checks, start with `manuals/install/redcap_newcomer_runtime_gate.zh-TW.md` or `manuals/install/redcap_newcomer_runtime_gate.en.md`.
- For reusable operation procedures, start with `manuals/README.md`.
- For L1/L2 protocol learning, start with `specs/redcap_l1_l2_protocol_guide.md`.
- For code modification entry points, start with `specs/function_reference/README.md`.
- For PDF lookup, start with `mineru_markdown/scan_manifest.md`, then open the cached Markdown if available.
