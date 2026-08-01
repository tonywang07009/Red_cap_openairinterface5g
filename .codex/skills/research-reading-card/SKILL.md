---
name: research-reading-card
description: Use when solving, diagnosing, designing, reviewing, or teaching a technical or research problem that needs literature or standards reading, source-to-runtime tracing, competing explanations, falsification, evidence grading, or a bounded repair plan. Trigger especially for Research Reading Card requests and RedCap/OAI, A-IoT/AIOTF, xApp/dApp, 3GPP/O-RAN, module ownership, or system-map questions. Do not use for formatting-only or mechanical edits.
---

# Research Reading Card

Build one evidence-first card for the active question. Analyze and propose only
unless the user request and project gates separately authorize mutation or
runtime execution.

## Frame the Question

1. State one exact question.
2. Bound the system or component, expected behavior, observed state, and
   non-goals.
3. Start from the current system map or project owner when one exists.

## Load the Smallest Evidence Pack

Read only the evidence needed for the active claim, in this order:

1. Governing standard clause or research paper.
2. Canonical system map, project plan, or owner document.
3. Source producer-to-consumer and request-to-apply trace.
4. Retained runtime evidence from the owning measurement path.

Preserve raw titles, identifiers, paths, commands, symbols, and markers
verbatim. Mark missing, ambiguous, release-dependent, or stale mappings
`[Needs Verification]`.

## Trace the System Boundary

Record upstream inputs, downstream outputs, owner, caller or transport,
accept/reject point, apply/rollback owner, and observable outcome. Classify each
endpoint as `implemented-called`, `partial`, `dormant`, `definition-only`, or
`missing`.

Use this evidence ladder and stop at the strongest completed step:

1. Definition or reference exists.
2. Source implementation exists.
3. Producer is called or transport is observed.
4. Acknowledgement is observed.
5. Acceptance or rejection is observed.
6. Apply marker, snapshot, or rollback is observed.
7. UE-visible or peer-visible completion is observed.
8. Outcome metric is observed in its owning path.

Never infer a later step from an earlier one. Build, static, attach, ping,
transport, or ACK success is not runtime application or outcome evidence.

## Compare and Falsify

List at least two competing explanations when the evidence does not uniquely
identify a cause. Name the smallest observable check that would falsify the
leading explanation or distinguish the alternatives.

Stop and return `[Needs Verification]` when a governing clause, endpoint owner,
caller/apply path, or required marker is missing or contradictory.

## Return the Card

Use the user's language. Keep technical identifiers and evidence fragments
verbatim.

```markdown
# Research Reading Card

## Question and Boundary
- Question:
- System/component:
- Expected:
- Observed:
- Non-goals:

## System Position
- Upstream inputs/owners:
- Current owner and implementation status:
- Downstream outputs/owners:
- Failure propagation:

## Source Matrix
| Type | Locator | Supports | Contradicts | Status |
|---|---|---|---|---|

## Competing Explanations
1.
2.

## Falsifier
- Leading explanation:
- Falsifying or distinguishing observation:
- Smallest next check:

## Evidence Ladder
- Strongest completed step:
- Missing next step:

## Claim Boundary
- Supported conclusion:
- Not claimed:
- [Needs Verification]:

## Repair or Design Inventory
- Affected existing owners:
- Minimal proposed change:
- Nearest test and boundary cases:
- Stop/rollback condition:

## Course Route
- Prerequisite:
- Current page/function:
- Next page/function:

## Next Action
- Action:
- Approval required:
```

Do not create a new component file when an existing owner can hold the finding.
Do not create an empty page for an unresolved component; record it in the
parent system map as `[Needs Verification]`.
