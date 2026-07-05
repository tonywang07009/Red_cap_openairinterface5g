# RedCap Trace / Problem KB Maintenance Rule

## Cadence
- Run this review after every 5 completed RedCap sub-tasks.
- A [completed sub-task] means the project note can report build/test/runtime status or a completed investigation result.
- Do not count ordinary chat turns as sub-tasks.

## Step-by-step Review
1. Open `candidate_inbox.md`.
2. Group candidates by [trace] and [problem].
3. Remove candidates that are one-off, unverifiable, or missing a source path.
4. Merge candidates that share the same symptom, log marker, or fix path.
5. Promote reusable trace procedures into `trace_steps.md`.
6. Promote recurring issues into `problem_set.md`.
7. Mark replaced entries as `[superseded]` only when the replacement is clearer.
8. Delete unsuitable entries only inside this KB.
9. Count `.md` files in this directory and keep the total `<=30`.
10. Run a targeted stale-reference check before reporting completion.

## Promotion Criteria
- Promote a [trace] only if it includes:
  1. Trigger condition.
  2. Step-by-step diagnosis.
  3. Success markers.
  4. Failure markers.
  5. Source evidence.
- Promote a [problem] only if it includes:
  1. Symptom.
  2. Likely root cause or `[Needs Verification]`.
  3. Step-by-step fix.
  4. Confirming command or marker.
  5. Final verification.

## Replacement Criteria
- Replace or remove an entry when:
  1. A newer procedure is more accurate.
  2. The entry points to stale paths.
  3. The problem is no longer reproducible.
  4. The entry is too broad to guide action.
  5. The entry duplicates another retained item.

## Validation Commands
```bash
rtk find agent_doc/Project_management/redcap_trace_problem_kb -name '*.md' -type f
rtk rg -n "TODO|FIXME|Needs Verification|remove-candidate|superseded" agent_doc/Project_management/redcap_trace_problem_kb
rtk git diff --check -- agent_doc/Project_management/redcap_trace_problem_kb
```
