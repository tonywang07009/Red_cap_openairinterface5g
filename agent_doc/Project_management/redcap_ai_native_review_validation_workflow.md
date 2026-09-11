# RedCap AI-Native Development, Review And Validation Workflow

## Purpose

- [Goal]: connect design clarification, architecture, OpenSpec tracking, TDD, review, and runtime validation with traceable evidence and bounded context.
- [Audience]: Caramel Bird and future AI coding agents working on RedCap/mMTC protocol behavior.
- [Toolbox]: use `agent_doc/Project_management/redcap_toolbox.md` for MCP status, routing, and reusable commands.
- [Rule]: use this document as the end-to-end guide. Approved OpenSpec artifacts own requirements and acceptance; project plans own milestones; logs and review records own observed results. Task checkboxes alone do not prove runtime behavior.

## Workflow Authorities

Use [`$workflow`](../../.agents/skills/workflow/SKILL.md) for development start
and resume. Confirm one change's scope and acceptance, continue through its
normal stage handoffs, and stop after successful archive. A single active
workflow resumes directly; multiple plausible workflows require selection.
An explicit status-only or stage-only request does not authorize later stages.

Adopt new changes immediately and existing changes only when resumed. Preserve
their decisions, evidence, and paths; do not bulk-migrate or rewrite archives.
Keep existing project plans and Toolbox here. Subsequent change requirements,
design, tasks, and acceptance live in OpenSpec, with links from project plans
instead of a second progress ledger.

Synchronize [code trace and read-only Archify views](../../.agents/skills/workflow/references/code-trace.md)
after specification confirmation, implementation updates, and validation/review
results. Update canonical records first. A failed refresh marks the view stale
and permits independent work; a stale or missing required trace blocks archive.
Preserve the final trace with the archived change and verify relocated links.

For this workflow-integration maintenance edit, the user explicitly waived an
OpenSpec proposal on 2026-09-11. Validate against the confirmed conversation;
do not create a change or claim an archive for this edit. Future work retains
the normal OpenSpec routing unless the user supplies a scoped exception.

Integration validation (2026-09-11): 9 installed/updated files, 32 local Markdown
links, and staged skill hashes checked. The new workflow skill passed metadata
validation; the three existing OpenSpec skills retain their pre-existing
`compatibility` frontmatter warning. Archify smoke validate/deliver passed 9/9;
receipt hashes matched, invalid input was rejected without replacing last-good
HTML, and four desktop viewport checks passed. Light/dark smoke screenshots were
inspected for readable nodes and routes; this is not a full-change runtime test.
Standards/accepted-decisions inspection covered single/multiple/no workflow,
status-only, explicit stage stops, progressive adoption, stale/missing traces,
concurrent input changes, and final archive path repair. These are instruction
checks, not an automated agent lifecycle test.
Backup and runnable smoke evidence: `/tmp/redcap-workflow-align.Tqj2tQ/`
(`before.tar`, `check.cjs`, `validation-20260911.log`, diagram receipts/screenshots).
This directory and the discovered Archify CLI are temporary. The `.agents`
skill files remain local under the existing Git ignore policy; no commit/push
or protocol source change was made.

| Concern | Source | Use |
|---|---|---|
| Tool selection and model choice | [Root rules](../../AGENTS.md#file-query-workflow) | Follow the required-first tool and fallback; the user chooses model and effort. |
| Formal change routing | [Routing memo](../../redcap_research_wiki/ASK_MATT_ROUTING_MEMO.md) | Preserve a directly selected skill and use the formal change route when applicable. |
| Design clarification | [grill-with-docs](../../.agents/skills/grill-with-docs/SKILL.md) | Resolve intent, non-goals, ownership, acceptance, and stop conditions one decision at a time. |
| Architecture review | [improve-codebase-architecture](../../.agents/skills/improve-codebase-architecture/SKILL.md), [codebase-design](../../.agents/skills/codebase-design/SKILL.md) | Review scoped candidates when needed; prefer small interfaces, depth, locality, and tests through the caller's interface. |
| Change execution | [OpenSpec apply](../../.codex/skills/openspec-apply-change/SKILL.md), [TDD](../../.agents/skills/tdd/SKILL.md) | Follow the approved tasks and acceptance contract. |
| Review and closeout | [code-review](../../.agents/skills/code-review/SKILL.md), [sync](../../.codex/skills/openspec-sync-specs/SKILL.md), [archive](../../.codex/skills/openspec-archive-change/SKILL.md) | Review a fixed point, reconcile specifications, and archive completed work. |

Use [wiki governance](../../redcap_research_wiki/governance.md) for retained wiki decisions. Ordinary exploration does not require a context packet. Some skill links still use the former `agent_doc/Project_management/redcap_research_wiki/` location; the canonical wiki links above resolve at the repository root.

## Minimal Context Pack

- [Root router]: `AGENTS.md`.
- [Active plan]: the target project `project_plan.md`.
- [Active rules]: the target project `agent_rules.md`.
- [Task contract]: only the target milestone or validation file.
- [Approved change]: read the context files returned by OpenSpec for the selected change; do not infer approval from artifact existence.
- [Continuity]: latest relevant `test_log/work_daily/*.md` only when resuming from prior runtime work.
- [Evidence library]: read `redcap_library/README.md` before scanning old generated logs.
- [Do not load first]: old PDFs, all runtime logs, historical reports, unrelated milestones, or generated artifacts unless the active task requires them.

## Preflight

- [Tool preflight]:
  - follow root `AGENTS.md`: Symdex MCP first for symbols and call relationships; local Symdex CLI only when MCP is not indexed or cannot answer.
  - use direct filesystem reads for Markdown, configuration, logs, and artifacts; narrow large reads.
  - use `rtk` first for Git; fall back to Git CLI only when RTK cannot perform the operation.
  - check relevant tool availability before a demonstration; historical toolbox health is not current evidence.
- [Spec preflight]:
  - check local RedCap notes or MinerU cached Markdown before claiming a clause.
  - mark uncertain exact clause mappings as `[Needs Verification]`.
- [Scope preflight]:
  - identify affected layer: [PHY], [MAC], [RLC], [PDCP], [RRC], [NAS], [E2/O-RAN], [runtime config], or [docs].
  - define what [PASS], [PARTIAL], and [BLOCKED] mean before running runtime validation.

## Step-By-Step Implementation Flow

Resume at the first unmet condition; an approved implementation task need not repeat settled design discussions. A review-only request does not authorize implementation.

| Stage | Action and artifact | Completion or return condition |
|---|---|---|
| 1. Enter and inventory | Identify task, target behavior, layer, existing owner and callers, governing specification, and current evidence. Load the minimal context pack. | Stop searching when the relevant path and unresolved questions are known. Mark unsupported mappings `[Needs Verification]`. |
| 2. Clarify intent | Use `grill-with-docs` for unresolved behavior, non-goals, acceptance, ownership, or rollback decisions. Show one concrete input/output or refusal example. | Record resolved decisions in the appropriate contract before dependent implementation. |
| 3. Check architecture | Reuse the existing owner and interface. Use the minimal implementation design check; enter `improve-codebase-architecture` when ownership is unclear, major seams are crossed, or the interface cannot test the intended behavior. | Compare scoped before/after candidates using locality, leverage, and the deletion test. Agree on a candidate before refactoring. Skip a full review when the existing design suffices. |
| 4. Establish OpenSpec contract | Use explore/propose as appropriate. Capture scope, scenarios, design, tasks, validation, and explicit approval of the governing revision. | Missing acceptance returns to clarification. Changed acceptance returns to OpenSpec. An issue mirror does not add requirements. |
| 5. TDD: RED | Record the test boundary, independent expected outcome, acceptance links, and side effects. Add one behavior test through the interface used by production callers. Run it before implementation. | Confirm failure is the intended missing behavior, not a broken build, fixture, or environment. For documentation-only work, use a Validation contract instead. |
| 6. TDD: GREEN | Implement the smallest owner-level change for that test. Run the test and the affected build/regression checks. Repeat RED → GREEN for the next behavior. | Preserve normal UE behavior. Failure returns to the governing requirement and root cause. Do not weaken an assertion to obtain GREEN. |
| 7. Review and validate | Review against a recorded fixed point on both Standards and Spec axes. Run the applicable runtime/A/B gates; retain commands, logs, metrics, and limitations. Refactoring belongs to review and must preserve accepted behavior. | Missing coverage returns to TDD; changed behavior returns to OpenSpec; defects return to the affected task. Build or unit success alone cannot prove runtime or RF performance. |
| 8. Track and close | Update tasks with evidence references after their acceptance is met. Reconcile delta specs, run strict validation, then use the archive skill for completed work. Retain unresolved limitations and useful handoff records. | Do not declare complete with required failed checks or unresolved review defects. Commit, tag publication, and push require the user's authorization for that scope. |

## OpenSpec Tracking And Evidence Placement

| Artifact | Owns | Update when |
|---|---|---|
| `proposal.md` | Why, scope, non-goals | The approved scope changes. |
| `specs/<capability>/spec.md` | Observable requirements and acceptance scenarios | The expected behavior changes. |
| `design.md` | Architecture decisions, TDD/Validation contract, implementation design check | A design or contract decision changes; link evidence rather than appending run histories. |
| `tasks.md` | Executable steps and completion state | A step meets its acceptance; link its supporting evidence. |
| Change-local `review/` records | Review findings, continuation review evidence, fixed point, remaining limitations | A review or evidence update occurs; reuse existing records such as `continuation_review_evidence.md`. |
| `test_log/` | Raw timestamped build, test, and runtime logs | A check runs; retain command, exit status, and relevant output. |

Use the selected change's existing paths and CLI-resolved context. These are responsibilities, not a requirement to create every listed file. Keep continuation review evidence out of `design.md`.

```bash
openspec status --change "<change-name>" --json
openspec instructions apply --change "<change-name>" --json
openspec validate "<change-name>" --strict
```

Run strict validation at a milestone or completion, not after every test cycle. It checks specification structure and consistency, not software behavior. During closeout, validate the resulting main specifications; do not pass an archived directory as an active change. Approved-tag/`to-spec` publication follows the routing memo when that workflow applies.

## Agent Effort And Test Design

The user selects the model and effort under the root Model Switch Gate. The following are task-sizing recommendations, not a model ranking or automatic switch policy. Record actual model/effort when exposed; otherwise use `[Needs Verification]`.

| Task condition | Recommended work allocation | Evidence that still applies |
|---|---|---|
| One owner, explicit acceptance, repeatable local test | Use the selected agent for one bounded RED → GREEN slice. | Independent expected value, intended RED failure, GREEN, and affected regression checks. |
| Ambiguous ownership, cross-layer state, concurrency, or specification interpretation | Resolve the seam and failure cases first; recommend more reasoning effort or a focused review if needed. | Source/caller trace, edge cases, agreed acceptance, and review of shared-state effects. |
| Irreversible control or security-sensitive refusal | Separate acceptance/test authorship from production editing where practical; protect the designated high-risk test evidence. | Refusal reason and absence of forbidden effects; hash/read-only protection only for the designated high-risk cases. |
| Agent repeatedly guesses, broadens scope, or changes tests to pass | Stop the slice, inspect the counterexample, and reduce the task. Request a user-selected model change only if a real capability or cost boundary requires it. | Keep the same acceptance threshold regardless of agent strength. |

Ordinary tests use version control and CI. Apply frozen-test SHA-256 and read-only checks only when the TDD contract designates protected high-risk tests; do not impose them on every unit test. Generic frozen-test wording in implementation/review skills must be read with this TDD applicability limit.

## Test Effectiveness And Performance Evidence

- Verify observable behavior through the production interface with an expected result derived independently from the implementation.
- Identify applicable boundaries: empty/null, zero, negative, min/max and adjacent values, first/last element, overflow, timer edges, and concurrent state changes. Record why a boundary does not apply rather than inventing irrelevant tests.
- Retain the intended RED failure and subsequent GREEN result. A test that already passes cannot establish that the missing behavior was detected; diagnose the baseline or select the missing scenario before claiming a RED tracer.
- For refusal behavior, assert both the reported reason and the absence of the prohibited effect. Code coverage alone does not prove either.
- Use the same acceptance conditions for review and execution. Classify evidence as build, unit/module, simulator runtime, or hardware; state what each cannot establish.

For a performance claim, define this measurement contract before comparing runs. Use existing project acceptance thresholds; unresolved thresholds prevent a performance PASS.

| Field | Required content |
|---|---|
| Claim and metric | A measurable outcome, unit, and desired direction, such as latency, throughput, CPU, memory, or energy. |
| Baseline and candidate | Revision, build flags, configuration, and the intended difference. |
| Controlled setup | Hardware or simulator, workload, duration, warm-up, seed where applicable, and relevant background load. |
| Sampling | Predeclared repeat count and aggregation; retain individual results and spread. A single demonstration run is not a repeatability claim. |
| Acceptance | Target and tolerated regression from the approved requirement; include behavior correctness checks. |
| Evidence and limitations | Commands, raw logs, run IDs, failures, and environmental differences. Report inconclusive comparisons as PARTIAL. |

## Token-Efficient Tool Use

Use the root tool route throughout the stages, not as a final optimization step. Stop a lookup once it answers the current question.

| Question | Tool route | Bounded result |
|---|---|---|
| Who owns this symbol; who calls it? | Symdex MCP; permitted local Symdex fallback | Relevant definition and caller/callee relationships, then the necessary source excerpt. |
| What changed since the review fixed point? | RTK Git; permitted Git CLI fallback | Scoped status/diff/log for the task. |
| What does the contract or log say? | Direct filesystem read | Selected Markdown/config or relevant log section, not all history. |
| Does this behavior pass? | The applicable build/test command | Retain raw evidence; return exit status, decisive output, and evidence path. |

To demonstrate savings, compare the same question, revision, and required answer under a documented baseline and bounded tool route. Record tool calls, returned bytes or lines, elapsed time, and actual token usage when available. Keep tokenizer/model and cache conditions comparable. Report `(baseline - candidate) / baseline` only for a positive baseline and the same metric; byte reduction is not measured token reduction. Tool availability or compressed output alone does not prove savings. Confirm both routes preserve the evidence needed to answer correctly.

Track Docker operations, live E2/control transactions, and very long builds/batches in the task manifest per root rules. Ordinary unit checks retain timestamped logs without an extra manifest. Register only reusable, externally invoked, or side-effecting wrappers.

## Code Review Packet

Use this packet for every RedCap protocol review.

```markdown
# [RedCap Code Review Packet]

## [Change Intent]
- [Goal]:
- [Expected behavior]:
- [Non-goal]:

## [Touched Subsystem]
- [Layer]:
- [Touched files]: list the core 3-5 files only.
- [Functions / Data structures]:
- [Runtime config impact]:

## [3GPP / O-RAN Mapping]
| Behavior | Spec / Clause | Status | Local evidence |
|---|---|---|---|
|  |  | [Verified] / [Needs Verification] |  |

## [Expected Runtime Markers]
- [gNB marker]:
- [UE marker]:
- [CN / user-plane marker]:

## [Protocol Correctness Review]
- [State machine]:
- [Message / IE handling]:
- [Timer / counter / BWP / scheduler interaction]:
- [Normal UE regression risk]:

## [OAI Integration Review]
- [Ownership boundary]:
- [Memory / lifetime]:
- [Assert / DevAssert appropriateness]:
- [Logging marker]:

## [Required Validation]
- [Source build]:
- [Unit / module test]:
- [RFsim runtime]:
- [Validation command]:
- [Pass criteria]:

## [Open Questions]
- [Needs Verification]:
- [Owner decision]:
```

## Review Types

Keep these review modes separate; do not collapse them into one generic review.

| Review Type | Question | Required Output |
|---|---|---|
| [Protocol Correctness Review] | Does the behavior match RedCap/mMTC state-machine and spec intent? | spec mapping, state/event notes, `[Needs Verification]` items |
| [OAI Integration Review] | Could the change break normal UE, gNB scheduler, RRC/MAC/RLC/PDCP ownership, or memory lifetime? | regression risks and affected layer boundaries |
| [Runtime Evidence Review] | Do logs prove the intended RedCap mechanism, not only attach/ping success? | evidence path, key marker, pass/partial/fail decision |
| [Student Learning Review] | Can the result teach the code path and validation intent clearly? | learning report with functions, tests, and exercises |

## Functional Validation Packet

Use this packet after each unit test, build, or RFsim run.

```markdown
# [RedCap Functional Validation Packet]

## [Validation Intent]
- [Test item]:
- [Claim being tested]:
- [Cannot claim PASS if]:

## [Setup]
- [Command]:
- [Config]:
- [UE / gNB / CN scope]:
- [Log path]:

## [Result Summary]
| Test Item | Pass-Fail Status | Evidence Path | Key Log Marker | Coverage / Limitation |
|---|---|---|---|---|
|  |  |  |  |  |

## [Runtime Evidence]
- [gNB marker]:
- [UE marker]:
- [CN / user-plane marker]:
- [Counter or metric]:

## [Decision]
- [Status]: PASS / PARTIAL / FAIL / BLOCKED
- [Reason]:
- [Next action]:
```

## Fixed Validation Output

Every validation response must include these fields, even when a field is `[N/A]`.

- [Test Item]
- [Pass/Fail]
- [Evidence Path]
- [Key Log Marker]
- [Coverage / Limitation]
- [Next Action]

## Educational Learning Report

Use this after each meaningful unit test or RFsim validation slice.

```markdown
# [RedCap Learning Report]

## 1. [Technical Background]
- Keep under 300 words.
- Explain only the tested behavior.

## 2. [Key C Functions / Data Structures]
| Item | Path | Role |
|---|---|---|
|  |  |  |

## 3. [Test Results Summary Table]
| Test Item | Pass-Fail Status | Code Coverage / Scope | Modification Logs |
|---|---|---|---|
|  |  |  |  |

## 4. [3GPP Specification Mapping]
| Clause | Local Interpretation | Status |
|---|---|---|
|  |  | [Verified] / [Needs Verification] |

## 5. [Practice Exercises]
- [Basic]:
- [Applied]:
- [Advanced]:
```

## Validation Gates

| Gate | Purpose | Required Evidence |
|---|---|---|
| [Gate A: Source Build] | prove the touched side still builds | `nr-softmodem`, `nr-uesoftmodem`, or closest target build log |
| [Gate B: Unit / Module Test] | prove local behavior when a test exists | CTest output or `[unit test N/A]` with reason |
| [Gate C: Single RedCap Runtime] | prove one RedCap UE path | gNB/UE RedCap-specific marker plus attach/session evidence |
| [Gate D: RedCap vs Normal A/B] | prove behavior differs only where intended | paired normal/RedCap logs and regression notes |
| [Gate E: mMTC / Low-Power Runtime] | prove scaled or low-power behavior | counters, runtime markers, and limitation statement |

## Review Decision Rules

- [Do not overclaim]: attach, PDU session, tunnel, or ping success is not enough for RedCap protocol PASS.
- [Marker required]: use gNB/UE markers for BWP, RA, SDT, DRX/eDRX/PSM, or O-RAN control claims.
- [Fallback honest status]: if evidence proves runtime flow but not the intended RedCap mechanism, mark [PARTIAL].
- [Spec honesty]: exact clause mappings remain `[Needs Verification]` until confirmed from local spec notes or cached spec Markdown.
- [Regression check]: every RedCap-specific change must state expected impact on normal UE behavior.

## Closeout

- [Report]:
  - summarize changed files and validation results in Traditional Chinese.
  - separate `[source build]`, `[unit test]`, `[container image]`, and `[RFsim runtime]`.
- [Knowledge capture]:
  - add a candidate to `agent_doc/Project_management/redcap_trace_problem_kb/candidate_inbox.md` only when the result creates a reusable trace step or recurring problem pattern.
- [Process log]:
  - write `test_log/work_daily/YYYY-MM-DD_HH-MM-SS_<task-slug>.md` only for completed work that improves handoff value.
