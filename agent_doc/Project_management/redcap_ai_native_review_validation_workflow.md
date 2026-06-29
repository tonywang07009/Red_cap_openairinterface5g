# RedCap AI-Native Review And Validation Workflow

## Purpose

- [Goal]: make RedCap/OAI code review and functional validation repeatable, evidence-based, and token-efficient.
- [Audience]: Caramel Bird and future AI coding agents working on RedCap/mMTC protocol behavior.
- [Toolbox]: use `agent_doc/Project_management/redcap_toolbox.md` for MCP status, routing, and reusable commands.
- [Rule]: this workflow guides review and validation; milestone-specific truth stays in the active project plan, milestone file, and validation file.

## Minimal Context Pack

- [Root router]: `AGENTS.md`.
- [Active plan]: the target project `project_plan.md`.
- [Active rules]: the target project `agent_rules.md`.
- [Task contract]: only the target milestone or validation file.
- [Continuity]: latest relevant `test_log/work_daily/*.md` only when resuming from prior runtime work.
- [Evidence library]: read `redcap_library/README.md` before scanning old generated logs.
- [Do not load first]: old PDFs, all runtime logs, historical reports, unrelated milestones, or generated artifacts unless the active task requires them.

## Preflight

- [Tool preflight]:
  - confirm `symdex` index exists with `repos` when code navigation is needed.
  - use `filesystem MCP` or targeted reads for docs/logs.
  - use `rtk` for normal shell commands.
  - use raw shell only for shell builtins, complex `find`, or syntax unsupported by `rtk`.
- [Spec preflight]:
  - check local RedCap notes or MinerU cached Markdown before claiming a clause.
  - mark uncertain exact clause mappings as `[Needs Verification]`.
- [Scope preflight]:
  - identify affected layer: [PHY], [MAC], [RLC], [PDCP], [RRC], [NAS], [E2/O-RAN], [runtime config], or [docs].
  - define what [PASS], [PARTIAL], and [BLOCKED] mean before running runtime validation.

## Step-By-Step Implementation Flow

Use this sequence when starting a RedCap protocol task or code review.

1. [Enter Task]
   - Read `AGENTS.md`, active `project_plan.md`, active `agent_rules.md`, and only the target milestone or validation file.
   - State the [Task ID], [target behavior], [affected layer], and [expected validation gate].

2. [Inventory]
   - Use `symdex search/text/outline` to locate C code paths and existing log markers.
   - Use local spec notes or MinerU cached Markdown for clause checks.
   - Stop inventory once the target code path, expected marker, and validation command are known.

3. [Design]
   - Fill the [Code Review Packet] before editing.
   - List each change as `[Modification Point] -> [Reason] -> [Before vs. After] -> [Discussion Point]`.
   - Mark unresolved spec details as `[Needs Verification]`.

4. [Build]
   - Patch one function or one parameter group at a time.
   - Keep RedCap-specific behavior gated so normal UE behavior remains explainable.
   - Add or preserve log markers that will be used in validation.

5. [Test]
   - Run the closest build and unit/module test first.
   - Run RFsim only after source-level checks are meaningful.
   - Fill the [Functional Validation Packet] with evidence paths and markers.

6. [Review]
   - Re-check protocol correctness, OAI integration risk, runtime evidence strength, and normal UE regression risk.
   - Do not mark [PASS] if the evidence only proves attach, PDU session, tunnel, or ping.

7. [Document]
   - Write a learning report when the validation slice teaches a reusable concept.
   - Add a work-daily note only when a completed result improves future handoff.
   - Add trace/problem KB candidates only for reusable trace steps or recurring problem patterns.

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
