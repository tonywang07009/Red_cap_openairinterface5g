# Specs

## Purpose
- Local RedCap and 3GPP reference material used by implementation, validation, and review.
- This is a local convenience reference, not a substitute for checking official 3GPP documents when exact clause wording matters.

## Key Paths
| Path | Role |
|---|---|
| `redcap_3gpp/spec.md` | Primary RedCap behavior notes |
| `redcap_3gpp/redcap5g_spec.md` | RedCap 5G project notes |
| `redcap_3gpp/Redcap/` | RedCap RF/PHY/RRC-related PDFs |
| `redcap_3gpp/DRX/` | DRX references |
| `redcap_3gpp/eDRX/` | eDRX references |
| `redcap_3gpp/PSM/` | PSM references |
| `redcap_3gpp/WUS/` | Wake-up signal references |
| `redcap_3gpp/RRM/` | RRM references |
| `redcap_l1_l2_protocol_guide.md` | RedCap L1/L2 protocol guide for implementation learning |
| `function_reference/` | RedCap L1-L3 function lookup tables |
| `../mineru_markdown/specs/redcap_3gpp/` | MinerU Markdown cache for parsed short spec PDFs |

## Rule
- Mark uncertain clause mappings as `[Needs Verification]`.
- For `@spec-38.331`, search under `redcap_doc/specs/redcap_3gpp/`.
- For RedCap L1/L2 learning, start with `redcap_doc/specs/redcap_l1_l2_protocol_guide.md`.
- For exact code entry points, use `redcap_doc/specs/function_reference/redcap_l1_l3_function_lookup.md`.
- For fast PDF lookup, check `redcap_doc/mineru_markdown/scan_manifest.md` first.
- Specs marked `[PENDING_LARGE_PDF]` in the manifest should be opened from the original PDF until an offline MinerU run is completed.
