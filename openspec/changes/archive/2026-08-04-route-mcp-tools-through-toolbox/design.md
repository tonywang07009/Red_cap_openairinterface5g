## Context

The fallback router already selects an active workflow, while the project
toolbox already records tool choice, limitations, and fallbacks. The missing
seam is a checkable tool route for the selected workflow.

## Goals / Non-Goals

**Goals:**

- Keep `redcap_toolbox.md` as the only source for MCP and command routing.
- Have `ask-matt` return a minimal tool route without executing it.
- Keep direct primary-skill instructions authoritative and use the toolbox only
  for an omitted necessary step.

**Non-Goals:**

- Add an MCP router skill, a second routing memo, or tool execution logic.
- Copy research-wiki context or governance rules into the toolbox.
- Rework tool-health history or unrelated command guidance.

## Decisions

### Toolbox is the route-table authority

Add a compact route contract to the existing toolbox: trigger, primary skill,
ordered tool steps, stop condition, and fallback. This reuses its existing
tool rows and avoids a second source of truth.

### `ask-matt` owns packet assembly, not execution

After selecting a primary skill, `ask-matt` reads the toolbox and returns the
five-field tool packet. A directly selected skill's explicit tool instruction
is retained. Only a missing necessary step is selected from the toolbox.

### Keep research-wiki rules external

The toolbox points to `CONTEXT.md` and `ASK_MATT_ROUTING_MEMO.md` for
research-wiki work. Those files remain the authoritative context-gate and
governance rules.

### Escalate rule changes, not maintenance

Tool availability, examples, and fallback corrections are toolbox maintenance.
Changes to default routes, stop conditions, or evidence thresholds are
OpenSpec candidates.

## Risks / Trade-offs

- [A packet can be verbose for a trivial request] → Return only the five
  fields and use `none` where a primary skill or fallback is unnecessary.
- [A stale toolbox route can misdirect work] → Preserve the existing health
  snapshot and require an OpenSpec candidate for rule changes.
