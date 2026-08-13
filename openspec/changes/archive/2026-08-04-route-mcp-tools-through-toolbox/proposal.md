## Why

`ask-matt` selects a workflow but does not state the tool route that follows it.
The existing toolbox already owns the tool knowledge, so a second memo or skill
would duplicate rules and drift.

## What Changes

- Make `redcap_toolbox.md` the authoritative tool-routing reference.
- Require `ask-matt` to return a minimal, checkable tool-routing packet after
  selecting the primary skill.
- Preserve a directly selected primary skill's explicit tool instructions; use
  the toolbox only to fill an omitted necessary tool step.
- Link research-wiki work to the existing context gate and routing memo without
  copying either rule.
- Define direct maintenance versus OpenSpec escalation for toolbox changes.

## Capabilities

### New Capabilities

- `oai-tool-routing`: Routes OAI work to the smallest appropriate tool sequence
  with stop conditions and fallbacks.

### Modified Capabilities

- `oai-workflow-routing`: Extends the fallback workflow packet with the
  authoritative tool-routing result.

## Impact

- `agent_doc/Project_management/redcap_toolbox.md`
- `.agents/skills/ask-matt/SKILL.md`
- `openspec/specs/oai-workflow-routing/spec.md`
