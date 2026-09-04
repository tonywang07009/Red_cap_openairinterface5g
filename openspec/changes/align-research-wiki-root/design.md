## Context

`redcap_research_wiki/` is the checked-in wiki root. The registered validator
and the reusable `redcap-research-wiki` skill still name the retired
`agent_doc/Project_management/redcap_research_wiki/` location. The validator's
default CLI path consequently fails before page validation. Twenty-seven
maintained wiki pages/templates and current project/course navigation also
retain that retired prefix; `log.md` contains historical references that must
remain append-only.

## Goals / Non-Goals

**Goals:**

- Make `redcap_research_wiki/` the only root used by current validation and
  current skill instructions.
- Make all maintained local metadata/template links and current project/course
  navigation resolve from that root.
- Prove the validator self-test passes and its default invocation resolves the
  canonical root without a retired-root failure.
- Preserve historical log text and raw evidence references.

**Non-Goals:**

- Add the two-role skill-evolution loop, a raw-trace store, candidate skills,
  or a new wiki category.
- Rewrite historical log entries, move raw evidence, promote wiki content, or
  change L0-L4 governance.
- Change runtime, protocol, xApp, or gNB behavior.

## Decisions

### Canonical root is repository-relative

The canonical root is `redcap_research_wiki/`, resolved from the repository
root. The validator, its self-test fixtures, current skill Load Contracts,
maintained internal metadata/template links, and current project/course
navigation SHALL use this path.

This is preferred over a compatibility symlink or dual-root lookup. A second
accepted root would mask drift and make every future agent decide which copy is
authoritative.

### Historical records remain historical

`log.md` remains append-only even where it names the retired path. It records
what was proposed or changed at the time, rather than serving as current
navigation. Current metadata and templates are maintained navigation and SHALL
be repaired.

### Validate through the existing public seam

Use the existing validator's `--self-test` and no-argument CLI invocation as
the regression seam. The no-argument invocation proves the configured default
root even when it exposes separate pre-existing contract debt; the self-test
proves the checker still accepts and rejects its fixtures. No new framework,
compatibility wrapper, or path configuration is required.

## TDD contract

- Model / effort: [Needs Verification]
- Test boundary: `python3 redcap_library/bash_tool/scripts/validate_redcap_research_wiki.py`
  and its `--self-test` public CLI modes.
- Acceptance links: `research-wiki-root-contract` requirements in this change.
- Irreversible side effects: none; validation is read-only except for its
  temporary self-test directory.
- Boundary gate: clear; canonical root and historical-log boundary are
  confirmed in the `grill-with-docs` discussion.
- Test files: existing `validate_redcap_research_wiki.py` self-test fixture;
  no new framework or parallel test file.
- Test evidence: timestamped compiler log for RED and GREEN CLI invocations.

## Risks / Trade-offs

- [A maintained metadata link is missed] -> Run the full validator after the
  root switch; do not accept a self-test-only pass.
- [A historical record is rewritten as current state] -> Exclude `log.md` from
  the path migration and review its diff explicitly.
- [A second root reappears later] -> Keep one hard-coded repository-relative
  root in the validator and one canonical path in current skill instructions.

## Migration Plan

1. Record the current default-validator failure as RED evidence.
2. Change the validator default and fixture paths to the canonical root.
3. Update current skill instructions, maintained metadata/template links, and
   current project/course navigation; leave `log.md` untouched.
4. Run the validator self-test, Python syntax check, and default full check.
   Treat only retired-root or canonical-navigation failures as this change's
   regression verdict; record other mechanical debt for a separate change.
5. Review the diff to verify the edit set excludes historical log rewrites.

Rollback restores the prior small source/doc edits. No data migration, service
deployment, or external state exists.

## Open Questions

None for this repair. The two-role skill-evolution MVP remains a separate,
later OpenSpec scope after this root contract is green.
