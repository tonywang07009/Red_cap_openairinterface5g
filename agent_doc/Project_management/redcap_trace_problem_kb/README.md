# RedCap Trace / Problem Knowledge Base

## Purpose
- [Goal]: Preserve reusable RedCap/OAI trace steps and common problem fixes.
- [Audience]: Future Codex sessions and Caramel Bird during RedCap/mMTC debugging.
- [Scope]: Store concise, reusable procedure knowledge only.
- [Non-scope]: Do not store raw Docker logs, full compiler logs, packet dumps, or one-off failed command transcripts.

## File Model
- `trace_steps.md`: curated step-by-step trace procedures.
- `problem_set.md`: curated common symptoms, causes, and fixes.
- `candidate_inbox.md`: temporary candidates collected at sub-task closeout.
- `maintenance_rule.md`: every-5-sub-task review and replacement rule.

## Hard Limits
- [Markdown File Limit]: Keep this directory at `<=30` `.md` files.
- [Default Strategy]: Prefer editing the existing core files instead of adding one file per issue.
- [Raw Evidence]: Keep raw or heavy evidence in `test_log/`, `test_log/build_logs/`, `test_log/compiler_logs/`, or promoted `redcap_library/` summaries.

## Sub-task Closeout
- At the end of every implementation, validation, or investigation sub-task:
  1. Check whether the work produced a reusable [trace step].
  2. Check whether the work exposed a recurring [problem pattern].
  3. If yes, add a short candidate entry to `candidate_inbox.md`.
  4. Include source paths, log markers, and validation commands when available.
  5. Keep speculative 3GPP clause links as `[Needs Verification]`.

## Review Cadence
- After every 5 completed sub-tasks:
  1. Review `candidate_inbox.md`.
  2. Promote useful entries into `trace_steps.md` or `problem_set.md`.
  3. Merge duplicates.
  4. Mark obsolete or weak entries as `[remove-candidate]`.
  5. Delete only entries inside this KB that are clearly unsuitable.
  6. Keep unrelated project documents untouched unless the user approves a cleanup batch.

## Entry Quality Bar
- A retained entry must have:
  1. A clear trigger condition.
  2. Step-by-step reproduction or diagnosis.
  3. Expected success or failure markers.
  4. A source path or evidence pointer.
  5. A final verification step.
