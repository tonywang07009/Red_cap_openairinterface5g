# RedCap Trace Steps

## Usage
- Add only reusable RedCap/OAI trace procedures.
- Use numbered step-by-step instructions.
- Prefer stable paths, log markers, and commands over narrative notes.
- Mark uncertain spec references as `[Needs Verification]`.

## Template

### [Trace ID] TRACE-YYYYMMDD-NN
- [Title]:
- [Applies To]:
- [Trigger]:
- [Source]:
- [Status]: active

#### [Step-by-step]
1. Identify the active project, milestone, and gate.
2. Read only the project plan, agent rules, target milestone, and relevant validation file.
3. Locate the runtime source of truth, usually `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/`.
4. Run the smallest command or log query that proves the suspected boundary.
5. Record expected success markers.
6. Record expected failure markers.
7. Compare the result with the target validation checklist.
8. Classify the result as `[PASS]`, `[PARTIAL]`, `[BLOCKED]`, or `[Needs Verification]`.

#### [Success Markers]
- [TBD]

#### [Failure Markers]
- [TBD]

#### [Common Misread]
- [TBD]

#### [Final Verification]
1. Re-run the exact query or validation command.
2. Confirm the marker count or specific log line.
3. Link the evidence path in the active project note or work_daily entry.

## Curated Entries
- No curated trace entries yet.
