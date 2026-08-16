## 1. Canonical routing

- [x] 1.1 Make root `AGENTS.md` the mandatory source, Git, and artifact lookup rule.
- [x] 1.2 Align the routing memo and `grill-with-docs` with the approved OpenSpec pipeline and RedCap planning escalation.

## 2. Mirror and test contracts

- [x] 2.1 Rewrite `to-spec` as an approved-OpenSpec mirror contract.
- [x] 2.2 Add TDD contract, model/fallback, protected-test, and validation-contract rules.
- [x] 2.3 Add implementation minimal-design and protected-test rules.
- [x] 2.4 Add the TDD boundary gate and conditional `grill-with-docs` escalation.

## 3. Review and validation

- [x] 3.1 Add code-review lenses and documentation/governance review behavior.
- [x] 3.2 Validate OpenSpec artifacts and review the scoped documentation diff.
- [x] 3.3 Add and review the canonical-evidence archive gate without a live-mirror blocker.

## 4. Follow-up infrastructure

- [x] 4.1 Hand off approved-tag CI publication, idempotency storage, retries, and read-only diagnosis to `implement-github-issue-mirror-publisher`; it does not block this parent archive.
