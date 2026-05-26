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
| `function_reference/` | L1-L3 RedCap function lookup tables |
| `mineru_markdown/` | MinerU-generated Markdown cache and manifest for papers/spec PDFs |

## Naming Rule
- Folder names use lowercase English plural nouns.
- Paper/spec filenames may keep their original names when renaming would reduce traceability.
- New index or guide files should be concise Markdown files named `README.md`, `paper_index.md`, or `<topic>_guide.md`.

## Reading Rule
- For paper-based experiments, start with `evaluation_papers/README.md`.
- For RedCap implementation/spec checks, start with `specs/README.md`.
- For milestone validation, start with `checklists/README.md`.
- For reusable operation procedures, start with `manuals/README.md`.
- For code modification entry points, start with `function_reference/README.md`.
- For PDF lookup, start with `mineru_markdown/scan_manifest.md`, then open the cached Markdown if available.
