# RedCap Doc

## Purpose
- This folder is the unified document root for RedCap papers, local specs, validation checklists, and reusable manuals.
- Keep generated runtime/build logs out of this folder; temporary logs belong under `test_log/`.
- Keep curated reusable runtime evidence under `redcap_library/`.

## Folder Map
| Folder | Role |
|---|---|
| `evaluation_papers/` | RedCap performance and technology papers used by the simulator evaluation project |
| `specs/` | Local 3GPP/RedCap reference notes and PDFs |
| `checklists/` | Human-checkable milestone and validation checklists |
| `manuals/` | Stable operator and reproduction manuals |
| `manuals/redcap_zero_to_build_and_run_guide.en.md` | Beginner build and 29 UE RFsim run guide |
| `manuals/redcap_zero_to_build_and_run_guide.zh-TW.md` | 新手從零編譯到 29 UE RFsim 執行指南 |
| `specs/redcap_l1_l2_protocol_guide.md` | RedCap L1/L2 protocol guide for implementation learning |
| `specs/function_reference/` | L1-L3 RedCap function lookup tables |
| `function_reference/` | Compatibility Doc folder for function-reference writing rules |
| `mineru_markdown/` | MinerU-generated Markdown cache and manifest for papers/spec PDFs |

## Naming Rule
- Folder names use lowercase English plural nouns.
- Paper/spec filenames may keep their original names when renaming would reduce traceability.
- New index or guide files should be concise Markdown files named `README.md`, `paper_index.md`, or `<topic>_guide.md`.

## Reading Rule
- For paper-based experiments, start with `evaluation_papers/README.md`.
- For RedCap implementation/spec checks, start with `specs/README.md`.
- For milestone validation, start with `checklists/README.md`.
- For first-time build and 29 UE RFsim use, start with `manuals/redcap_zero_to_build_and_run_guide.zh-TW.md` or `manuals/redcap_zero_to_build_and_run_guide.en.md`.
- For reusable operation procedures, start with `manuals/README.md`.
- For L1/L2 protocol learning, start with `specs/redcap_l1_l2_protocol_guide.md`.
- For code modification entry points, start with `specs/function_reference/README.md`.
- For PDF lookup, start with `mineru_markdown/scan_manifest.md`, then open the cached Markdown if available.
