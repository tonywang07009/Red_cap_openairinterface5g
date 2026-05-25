# RedCap Milestone Checklist Rules

## Purpose
- Keep a human-checkable validation record for every major RedCap/mMTC milestone.
- Use the format requested by the engineer: `流程 -> 要驗證的對應規範的 clause`.
- Keep uncertain 3GPP references explicitly marked as `[Needs Verification]`.

## Files
- `redcap_milestone_validation_checklist.md`
  - Master schedule and reusable validation checklist.
- `completed/YYYY-MM-DD_<milestone>_<slug>.md`
  - One completion record per major milestone after validation is finished.

## Completion Record Template
```markdown
# <Milestone> Completion Checklist

## Metadata
- Date:
- Milestone:
- Task ID:
- Validation Log:
- Result: [PASS / FAIL / BLOCKED]

## Checklist
| 流程 | 要驗證的對應規範的 clause | Evidence | Result |
|---|---|---|---|
| ... | ... | ... | ... |

## Notes
- [Known issue / blocker / follow-up]
```

## Rule
- After each large milestone is completed, add a new file under `redcap_doc/checklists/completed/`.
- Do not mark an uncertain clause as verified unless the local spec source or user-provided source confirms it.
