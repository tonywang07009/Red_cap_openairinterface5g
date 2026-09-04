## Why

The canonical-root repair exposes eight pre-existing research-wiki contract
failures. The full validator cannot report PASS until archived source paths,
decision metadata, evidence labels, and index membership are repaired without
weakening its checks.

## What Changes

- Repair the archived OpenSpec `source_refs` for the xApp observation/control
  page and the pipeline approval decision.
- Bring the three decision pages into the validator's supported metadata,
  evidence-label, and index contracts.
- Retain the validator rules, its canonical root, append-only log entries, and
  all runtime claims unchanged.
- Add full-validator PASS evidence after the content-only repair.

## Capabilities

### New Capabilities

- `research-wiki-validation-conformance`: Define the maintained-content
  contract required for the existing full research-wiki validator to pass.

### Modified Capabilities

- None.

## Impact

- `redcap_research_wiki/systems/xapp-dapp/xapp-observation-control.md`
- `redcap_research_wiki/decisions/github-issue-mirror-format-context-2026-08-15.md`
- `redcap_research_wiki/decisions/pipeline-unified-approval-context-2026-08-13.md`
- `redcap_research_wiki/decisions/tdd-observable-behavior-context-2026-08-13.md`
- `redcap_research_wiki/index.md`
- Validation evidence only; no validator code, protocol behavior, runtime
  operation, or skill-evolution workflow changes.
