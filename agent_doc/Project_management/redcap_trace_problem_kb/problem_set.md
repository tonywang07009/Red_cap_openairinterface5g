# RedCap Problem Set

## Usage
- Add recurring RedCap/OAI problems that improve future diagnosis quality.
- Each fix must be step-by-step.
- Keep root cause claims conservative when runtime evidence is incomplete.
- Mark uncertain 3GPP clause interpretation as `[Needs Verification]`.

## Template

### [Problem ID] PROB-YYYYMMDD-NN
- [Title]:
- [Symptom]:
- [Likely Cause]:
- [Applies To]:
- [Source]:
- [Status]: active

#### [Step-by-step Fix]
1. Confirm the symptom with the smallest log query or validation command.
2. Check whether the failure belongs to [UE], [gNB], [CN], [RFsim], [Docker], or [test harness].
3. Compare the observed markers with the relevant validation checklist.
4. Inspect only the smallest code/config boundary needed to explain the failure.
5. Apply or propose the minimal fix.
6. Rebuild the affected target when C/C++ code changes.
7. Re-run the closest unit, build, or RFsim validation.
8. Record the final status and evidence path.

#### [Confirming Commands]
- [TBD]

#### [Avoidance Rule]
- [TBD]

#### [Final Verification]
1. Confirm the original failure marker is absent or reduced as expected.
2. Confirm the success marker is present.
3. Update the active project validation or work_daily note only if the result is reusable.

## Curated Entries
- No curated problem entries yet.
