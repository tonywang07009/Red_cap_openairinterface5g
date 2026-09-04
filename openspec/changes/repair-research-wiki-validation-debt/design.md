## Context

The canonical-root repair intentionally preserved the existing validator rules.
Its full CLI now reaches the wiki and reports eight content failures: two
archived OpenSpec references, one unsupported evidence tier, three missing
approved evidence labels, and two missing decision-index entries.

## Goals / Non-Goals

**Goals:**

- Repair only the four affected content pages and the decision index.
- Make the existing full validator return PASS without suppressing any rule.
- Preserve claim boundaries, current statuses, raw evidence, and append-only
  log history.

**Non-Goals:**

- Change `validate_redcap_research_wiki.py`, its accepted metadata values, or
  its test fixtures.
- Restore retired active OpenSpec directories, invent source evidence, or
  claim a live xApp/control outcome.
- Start the two-role skill-evolution workflow.

## Decisions

### Repair references to their archived owners

The xApp page and pipeline decision SHALL point to the existing archived
OpenSpec artifacts, rather than recreating retired active change paths. This
keeps source references truthful and makes the validator's existence check
meaningful.

### Use existing evidence vocabulary

The GitHub Issue mirror decision SHALL use the supported `mixed` tier because
it combines OpenSpec artifacts, a skill contract, and the retained human
decision. The three decision pages SHALL add a source-trace evidence label
adjacent to their contract claims. Adding a `human-decision` validator enum is
rejected because no new validator behavior is needed.

### Repair canonical decision navigation

The index SHALL list the pipeline approval and TDD boundary decisions with
their existing titles and boundaries. No content is moved and no case or log
history is rewritten.

### Validate only through the existing public seam

The recorded eight-error full-validator output is the RED baseline. GREEN is
the existing no-argument validator returning `REDCAP_RESEARCH_WIKI_CHECK PASS`;
the self-test and Python syntax check remain regression checks.

## Risks / Trade-offs

- [Archived reference points to the wrong revision] -> Verify each target is
  an existing archive artifact before editing frontmatter.
- [A label upgrades an unsupported claim] -> Use `[Source Trace]` only for the
  cited repository contract and retain each page's stated claim boundary.
- [Index repair changes navigation scope] -> Add only the two missing decision
  links required by the validator.

## Migration Plan

1. Retain the current full-validator error log as RED evidence.
2. Correct archived references, metadata, labels, and index links in place.
3. Run the existing self-test, syntax check, and full validator.
4. Review the scoped diff; rollback restores the five content files only.
