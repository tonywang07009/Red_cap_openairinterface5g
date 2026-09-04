---
status: review-required
source_refs:
  - https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
evidence_tier: source-record
last_reviewed: 2026-07-30
related_pages:
  - redcap_research_wiki/governance.md
  - redcap_research_wiki/concepts/evidence-first-research-method.md
---

# Karpathy LLM Wiki Pattern

## Source

- Title: `LLM Wiki`
- Author: Andrej Karpathy
- URL: <https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f>

## Pattern Used by This Project

[Inference] The RedCap wiki adopts the source's three-layer separation:

1. immutable raw sources;
2. LLM-maintained derived Markdown knowledge;
3. a schema or agent contract that governs structure and workflows.

[Inference] It also adopts `ingest`, `query`, and `lint` operations, a
content-oriented `index.md`, and a chronological `log.md`.

[Needs Verification] An optional search engine, embeddings, Obsidian
integrations, and other tools remain out of scope until repository-scale
measurement demonstrates a need.
