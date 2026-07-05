# Public Documentation Inventory

## Included In This Change

| Area | Status | Notes |
|---|---|---|
| Root README | Updated | `README.md` is a language selector; `README.en.md` and `README.zh-TW.md` are public entry pages. |
| Install manuals | Added | `redcap_doc/manuals/install/` now contains begin, rebuild, and newcomer gate pages in English and Traditional Chinese. |
| Paper recovery tutorials | Added | Paper-07, Paper-10, Paper-11 service gate, and Paper-11 Table 3 tutorials now have English and Traditional Chinese pages. |
| RedCap doc router | Updated | `redcap_doc/README.md` and `redcap_doc/Doc/` point to install and paper recovery routes. |
| Interface router | Updated | `redcap_interface/README.md` and `redcap_interface/Doc/` point to language-specific public manuals. |
| Library router | Updated | `redcap_library/README.md` and `redcap_library/Doc/` point to language-specific public manuals. |
| Static doc gate | Added | `redcap_interface/bash_library/fc_doc_newcomer_gate_check.sh` checks language pairs, forbidden wrappers, encoding artifacts, and 29 UE markers. |

## Preserved As Historical Evidence

| Area | Reason |
|---|---|
| `redcap_doc/evluation_recover/*_report.md` | Historical result evidence; new tutorials link to these instead of rewriting them. |
| `redcap_library/library_reports_summary/*.md` | Accepted report summaries; not rewritten as tutorials in this batch. |
| `test_log/` | Temporary runtime/build logs; not public documentation. |
| `redcap_doc/mineru_markdown/` | Generated Markdown cache; do not manually rewrite as bilingual docs. |
| `agent_doc/Project_management/` | Internal project-management records; outside this public-doc rewrite scope. |

## Follow-Up Candidates

| Candidate | Reason |
|---|---|
| `redcap_doc/specs/redcap_l1_l2_protocol_guide.md` | Candidate for a future dedicated bilingual protocol tutorial pass. |
| `redcap_doc/specs/function_reference/redcap_l1_l3_function_lookup.md` | Candidate for a future API/function-reference bilingual pass. |
| `redcap_doc/manuals/redcap_project_onboarding_step_by_step.md` | Candidate for migration into the new install/manual structure. |
| `redcap_doc/manuals/redcap_mmtc_systematic_usage_steps.md` | Candidate for a future runtime-operations tutorial pass. |
