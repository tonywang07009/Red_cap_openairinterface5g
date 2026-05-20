# Project Logging Rules

## Read Rules
- At the beginning of a new chat window, before project work:
  1. Check whether `test_logs/work_daily/` exists.
  2. If it exists, list `.md` files sorted by filename descending.
  3. Read the most recent log file in full.
  4. Output a Traditional Chinese resume summary:
     - `▶ 上次進度摘要`
     - `◉ 最後完成子任務：<task-slug>`
     - `◉ 當前里程碑：<milestone>`
     - `◉ 待處理事項：<next step from log>`
     - `◉ 已知問題：<blockers if any>`
  5. Ask: `是否從上次進度繼續？`

## Write Rules
- After completed implementation, validation, planning, or documentation work, create a new Markdown log.
- Never overwrite an existing log file.
- Use path:
  - `test_logs/work_daily/YYYY-MM-DD_HH-MM-SS_<task-slug>.md`
- If `test_logs/work_daily/` does not exist, create it first.
- If a project plan is updated, append a note to the current daily log indicating which milestone or sub-task was revised.
- Log files are append-only records; do not delete them without explicit user confirmation.

## Required Log Structure
```markdown
# Work Daily Log
## Session Metadata
- Date: YYYY-MM-DD HH:MM
- Agent Session ID: <auto or N/A>
- Task Slug: <short identifier>
- Project Path: <project_plan.md path>

## Milestone & Sub-task Reference
- Milestone: <milestone name>
- Sub-task: <sub-task name>
- Status: [COMPLETED / IN-PROGRESS / BLOCKED]

## What Was Done
- [Bullet list of changes]

## 3GPP Spec Clauses Referenced
- TS XX.XXX Section X.X.X — brief note on relevance

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| ...       | ...         | ...      | ...   |

## Known Issues / Blockers
- [List unresolved issues]

## Next Step
- [Immediate next sub-task]
```
