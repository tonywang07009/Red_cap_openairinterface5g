## Why

The maintained research wiki resides at `redcap_research_wiki/`, while its
validator and reusable workflow skill still resolve the retired
`agent_doc/Project_management/redcap_research_wiki/` path. The validator
therefore fails before it can assess any wiki page, and its Load Contracts
cannot be followed as written.

## What Changes

- Declare `redcap_research_wiki/` the sole canonical root for maintained wiki
  content and mechanical validation.
- Align the validator default root and its self-test fixture with that root.
- Align the research-wiki skill Load Contracts, maintained wiki
  metadata/template links, and current project/course navigation with the
  canonical root.
- Preserve append-only historical log entries and raw evidence paths; do not
  rewrite history merely to make a past path look current.
- Add a regression check proving that the default invocation resolves the
  canonical root and does not report a retired-root failure.

## Capabilities

### New Capabilities

- `research-wiki-root-contract`: Define the canonical research-wiki root and
  the required behavior for validation, maintained links, and historical
  records.

### Modified Capabilities

- None.

## Impact

- `redcap_library/bash_tool/scripts/validate_redcap_research_wiki.py`
- `redcap_library/skills/redcap_research_wiki/SKILL.md`
- Maintained metadata and template links below `redcap_research_wiki/`
- Current canonical-root navigation in `AGENTS.md` and
  `redcap_library/luna_cli_trace_course/`
- Wiki validation evidence only; no runtime, protocol, external API, or active
  skill-evolution behavior changes are included.
