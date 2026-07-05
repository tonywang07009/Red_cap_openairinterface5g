# G3 Reporting And Static CI

## Scope

- Provide standardized Daily Report and Gate Report templates.
- Provide Stage 1 static CI checks.
- Keep static CI separate from runtime validation.

## Acceptance Criteria

- Daily Report template contains `[Today Done]`, `[Evidence Path]`, `[Blocked]`, `[Next Pull Item]`, and `[Status]`.
- Gate Report template contains scope, spec mapping, modification points, validation evidence, limitations, and next action.
- Static checker validates required files, OpenSpec delta specs, YAML control contract fields, and report-template overclaim guard text.
- Static PASS does not imply runtime PASS.

## Status

- [x] Templates added.
- [x] Static checker added.
- [ ] Integration into a wider CI runner remains pending.
