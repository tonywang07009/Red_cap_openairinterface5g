## Context

The repo already contains RedCap RFsim/FlexRIC assets and prior [RRC_INACTIVE + SDT] validation work. The requested work creates a new validation project that turns two papers into reproducible artifacts: Markdown sources, metadata, experiment steps, result tables, and figures.

## Goals / Non-Goals

**Goals:**
- Create deterministic paper conversion and metadata refresh.
- Keep paper-derived parameters traceable to Markdown sources.
- Define result files that compare `[paper_value]` and `[local_value]`.
- Keep the first pass C-code neutral; map experiments to existing RFsim and RedCap control paths.
- Preserve uncertainty using `[TBD]` and `[Needs Verification]`.

**Non-Goals:**
- Do not fabricate paper curve values that cannot be extracted reliably from the converted Markdown.
- Do not modify OAI MAC/RRC/PHY behavior in the scaffold pass.
- Do not claim TS 38.523-1 clause 7.1.1.12/7.1.1.13 correctness until local spec Markdown is checked.

## Decisions

- Use `markitdown` for PDF-to-Markdown conversion because it is already installed in the MCP conda environment.
- Use `symdex` with repo-local `.symdex` state for source and paper-folder indexing; keep `.symdex/` ignored by Git.
- Store project deliverables under `agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/` to avoid overloading the existing SDT control project.
- Use CSV as the canonical metric exchange format and matplotlib PNGs as generated plot artifacts.
- Use placeholder `[TBD]` rows for unavailable curve values so future RFsim runs can update the same schema without changing report shape.

## Risks / Trade-offs

- [Risk] Markitdown table extraction is noisy for IEEE PDFs. → Mitigation: extract only high-confidence parameters and keep ambiguous values `[TBD]`.
- [Risk] BWP paper uses a proprietary simulator and not OAI. → Mitigation: reproduce comparable metrics and explicitly document simulator gaps.
- [Risk] SDT paper is analytical/simulation-based and not a direct OAI RFsim recipe. → Mitigation: map RA-SDT/CG-SDT concepts to available RedCap RFsim markers and keep exact curve reproduction pending local metric runs.
- [Risk] Local 3GPP files may not include the requested exact clauses. → Mitigation: convert local specs before citation and mark uncertain mappings `[Needs Verification]`.
