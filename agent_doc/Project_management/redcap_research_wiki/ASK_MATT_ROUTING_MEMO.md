# Ask Matt Routing Memo

Use this memo when you forget how `ask-matt` selects a route for an
unqualified OAI request. A directly invoked skill wins; `ask-matt` is only the
fallback router.

## Active Skill Set

`ask-matt` selects only skills discoverable by the active Codex skill registry.
Skills under `.agents/skills/in-progress/` are incubator skills. They are
unloaded: the router does not name, read, or execute them.

Promote an incubator skill only after a `writing-great-skills` review confirms
its invocation, trigger description, single source of truth, and completion
criteria, and a human approves its move into the active set.

If no active route matches, return no primary skill and ask the human to
clarify the request or approve formal promotion. Do not inspect the incubator
to search for a match.

## Formal OpenSpec Gate

Use `openspec-explore` when the request changes any of the following:

- observable behavior;
- a public contract;
- architectural responsibility; or
- a decision that needs long-term traceability.

The formal path is:

```text
grill-with-docs -> openspec-explore -> human scope confirmation
-> approved tag -> to-spec mirror -> tdd -> implement -> code-review -> archive
```

`openspec-explore` remains the formal route when the work changes observable
behavior, a public contract, architecture, or a traceable decision. The router
does not create an approved tag or apply a change by itself.

## Research-Wiki Escalation

Use the normal research-wiki capture route for a new source-backed reading
card or case that does not change a current conclusion, evidence threshold, or
governance rule.

If a result changes one of those three things, `ask-matt` returns an OpenSpec
candidate and asks for human confirmation before proposal creation. The
context-packet and critical-check requirements remain in
[CONTEXT.md](CONTEXT.md) and [governance.md](governance.md).

## Retained Skill Routes

| Need | Primary skill | Notes |
|---|---|---|
| Formal OAI change | `grill-with-docs` | Then use the formal path above; `openspec-explore` frames the approved proposal. |
| Approved OpenSpec implementation | `openspec-apply-change` | Its workflow requires TDD where applicable and code review. |
| Evidence question | `route-evidence-work` | Selects research, reading-card, or Luna route. |
| Source-to-runtime evidence work | `research-reading-card` | Use for evidence grading and claim boundaries. |
| Learner-guided source trace | `luna-cli-trace-course` | One read-only lookup at a time. |
| Hard bug | `diagnosing-bugs` | Escalate formal changes through OpenSpec. |
| Architecture or skill-pack review | `improve-codebase-architecture` | Discuss selected candidates with `grill-with-docs`. |
| Repository-grounded decision | `grill-with-docs` | Use `domain-modeling` for terminology or ADR decisions. |
| Approved OpenSpec tracker mirror | `to-spec` | Mirrors an approved revision; it does not create requirements or tickets. |

The router output format is defined in
[ask-matt](../../../.agents/skills/ask-matt/SKILL.md). The packet reports a
route; it does not replace human review, raw evidence, or an active project
plan.
