## 1. Baseline and archived-source qualification

- [ ] 1.1 Retain the recorded eight-error full-validator output as RED
  evidence and confirm the two archived OpenSpec target files exist.

## 2. Content-only repair

- [ ] 2.1 Retarget the xApp observation/control and pipeline approval
  `source_refs` to their existing archived OpenSpec artifacts.
- [ ] 2.2 Replace unsupported decision metadata with supported existing
  vocabulary and add bounded source-trace labels to the three decision pages.
- [ ] 2.3 Add only the two missing decision entries to the canonical wiki
  index; preserve all append-only log text.

## 3. Regression evidence and review

- [ ] 3.1 Run the existing validator self-test, Python syntax check, and full
  no-argument validator; retain GREEN evidence showing PASS and exit zero.
- [ ] 3.2 Review the scoped content diff for altered claims, archived-reference
  accuracy, unchanged validator rules, and unchanged historical log text.
