# MinerU Markdown Cache

## Purpose
- Store Markdown cache generated from RedCap specs and evaluation paper PDFs.
- Use this folder for quick lookup before opening original PDFs.
- Treat cached Markdown as extraction aid only; verify exact 3GPP clauses against the source PDF or official spec.

## Entry Points
| Path | Role |
|---|---|
| `scan_manifest.md` | Inventory of every source PDF, generated Markdown path, page count, and status |
| `evaluation_papers/` | MinerU Markdown cache for RedCap evaluation papers |
| `specs/redcap_3gpp/` | MinerU Markdown cache for short RedCap/3GPP specs currently parsed |
| `../../mcp/magic-pdf/redcap_doc_mineru_scan.py` | Batch scanner used to refresh this cache |

## Current Coverage
| Source Type | Status |
|---|---|
| Evaluation papers | 10/10 cached |
| RedCap/3GPP specs | 4/30 cached |
| Large specs | Listed as `[PENDING_LARGE_PDF]` in `scan_manifest.md` |

## Reading Rule
- Start with `scan_manifest.md`.
- If a PDF has a Markdown cache, search the cached `.md` first.
- If a PDF is marked `[PENDING_LARGE_PDF]`, use the original PDF or schedule an offline MinerU run with a higher page threshold.
- Refresh command: `/home/tonywang/miniforge3/envs/mcp/bin/python mcp/magic-pdf/redcap_doc_mineru_scan.py --language ch --max-spec-pages 150`.
