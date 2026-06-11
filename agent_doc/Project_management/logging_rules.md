# Project Logging Rules

## Policy
- `test_log/` is the only temporary log root.
- `test_log/work_daily/` is a short-lived process-log area, not a permanent evidence library.
- Permanent reusable evidence belongs in `redcap_library/`.
- Papers, specs, and checklists belong in `redcap_doc/`.
- Reusable RedCap trace steps and common problem fixes belong in `agent_doc/Project_management/redcap_trace_problem_kb/`.

## Read Rules
- At the beginning of a new chat window, read `test_log/work_daily/` only if the user asks to resume from a process log.
- Prefer active project files and `redcap_library/` summaries over old process logs.
- Do not scan historical generated logs unless the active task needs raw evidence.

## Write Rules
- Write a process log only when a completed improvement produced a useful result.
- Do not write a log for pure exploration, repeated failed attempts, path mistakes, or commands that did not change the project state.
- If a failed experiment reveals a new simulator bug or design limitation, record it as a short debug item in the relevant project validation file instead of writing a full process log.
- Keep each process log under 100 lines.
- Use path:
  - `test_log/work_daily/YYYY-MM-DD_HH-MM-SS_<task-slug>.md`

## Trace / Problem KB Rules
- At the end of each RedCap sub-task, check whether the result produced:
  1. a reusable [trace step],
  2. a recurring [problem pattern],
  3. or a step-by-step fix that should improve future diagnosis quality.
- If yes, add a short candidate to:
  - `agent_doc/Project_management/redcap_trace_problem_kb/candidate_inbox.md`
- After every 5 completed RedCap sub-tasks:
  1. review the candidate inbox,
  2. promote useful trace procedures to `trace_steps.md`,
  3. promote recurring issues to `problem_set.md`,
  4. merge duplicates,
  5. remove only clearly unsuitable entries inside the KB,
  6. keep the KB directory at `<=30` `.md` files.
- Do not put raw logs, long transcripts, or one-off command mistakes into the KB.
- All retained fix procedures must use numbered step-by-step instructions.

## Required Log Structure
```markdown
# <Outcome Name>

## Conclusion
- Result:
- Status: PASS / PARTIAL / BLOCKED
- Scope:

## Improvement Target
- Original issue:
- Improvement direction:

## Changes
| Type | File / Parameter / Function | Note |
|---|---|---|
| Code | `path` / `function()` | ... |
| Config | `parameter` | ... |
| Script | `path` | ... |

## Validation
1. ...
2. ...
3. ...

## Key Evidence
| Metric / Gate | Result | Evidence |
|---|---:|---|
| ... | ... | `path` |

## Follow-up
- ...
```
