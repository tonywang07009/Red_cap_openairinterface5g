# RedCap Research Wiki

This directory is the human-reviewed layer for derived RedCap knowledge and
decisions.

## Start Here

1. Read [governance.md](governance.md).
2. Use [index.md](index.md) to find sources, concepts, systems, decisions, and cases.
3. Use [agent_goals.md](agent_goals.md) to assign a bounded agent task.
4. Record ingest, query, lint, review, supersession, and capture events in [log.md](log.md).

## Boundaries

- Raw PDFs, specifications, papers, source code, configurations, and runtime evidence remain in their owning directories.
- Wiki pages summarize and link sources; they do not replace the raw source.
- Content conclusions remain `review-required` until human approval.
- Runtime evidence can establish an observation, not standards conformance or a complete end-to-end protocol path by itself.

## Operations

| Operation | Input | Output |
|---|---|---|
| Ingest | One bounded source pack | Source record and page-update proposal |
| Query | Research question and related index entries | Source-backed answer and optional page proposal |
| Decide | Sources, hypothesis, observable markers | Decision/experiment contract |
| Sync docs | Confirmed wiki conclusion | Existing README or stable-document proposal |
| Lint | Wiki root | Structural validation report |
| Capture triage | One completed bounded operation | `none`, `log`, `update-page`, `case-draft`, or `decision-contract` |

Run the registered read-only validator:

```bash
python3 redcap_library/bash_tool/scripts/validate_redcap_research_wiki.py
```
