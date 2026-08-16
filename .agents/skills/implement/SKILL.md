---
name: implement
description: "Implement a piece of work based on a spec or set of tickets."
disable-model-invocation: true
---

Implement only the work covered by an approved OpenSpec revision and its TDD
or Validation contract. Use GPT-5.6 Luna / max for production implementation
only when explicitly available and authorized; record the actual model and
effort in the change evidence.

Follow [the root Model Switch Gate](../../../AGENTS.md#model-switch-gate).
If production requires a different model or effort, stop before editing and
wait for the user to switch or explicitly authorize the active model. Do not
open a subagent or automatically delegate to a fallback model to satisfy that
requirement.

Follow the mandatory lookup route in [root AGENTS.md](../../../AGENTS.md#file-query-workflow).

Before changing production code, add this minimal design check to `design.md`:

```md
## Implementation design check

- Owner module:
- Existing path reused:
- Seam and interface:
- Locality:
- Ponytail decision:
- Escalation: none | architecture review required
```

Find the existing owner and callers first. Prefer the smallest owner-level fix,
existing test, standard facility, and existing registered tool. Escalate to a
full architecture review only when ownership is unclear, the work crosses major
seams, a new adapter is required, or the existing interface cannot test the
agreed behavior.

Never modify protected TDD tests, their hash record, frozen test-diff baseline,
or their read-only mode. Run the agreed tests regularly. At completion, execute
the frozen tests and verify SHA-256 plus the frozen test-diff baseline before
review.

Run typechecking regularly, single test files regularly, and the relevant full
suite once at the end.

Once done, use /code-review. Commit only when the user explicitly authorizes a
commit.
