## 1. Approval and frozen TDD contract

- [x] 1.1 Obtain human scope confirmation for this revision.
- [ ] 1.1b Record the one-time self-hosting parent and child tags after the approved pipeline-contract baseline commit; prohibit raw-Git tagging for later changes.
- [ ] 1.1a Define and test `to-spec add --confirm-scope` through an isolated `redcap_library/.test_tmp/` local worktree/bare-remote fixture: success output, scoped-revision alignment, `origin` preflight, refusal and uncertain-push exit behavior, remote idempotency, and fixed immutable annotated-tag confirmation record.
- [ ] 1.2 Add a registered local fake-GitHub validator in `redcap_library/` for tag validation, key generation, recovery, mismatch, retry, diagnosis immutability, and token redaction cases.
- [ ] 1.2a Add the read-only local fixture validator for `to-spec status` state and redaction behavior.
- [ ] 1.3 Record the TDD model/effort, test paths, SHA-256 values, and frozen test-diff baseline in `design.md`; make the tests read-only.

## 2. Publisher and local evidence

- [ ] 2.1 Implement the standard-library publisher that validates the approved tag, builds a redacted payload, and derives the deterministic key.
- [ ] 2.2 Implement GitHub Issue marker query, create/recovery, mismatch refusal, stable title/body/labels, and generated state plus field memo under `openspec/.to-spec/`.
- [ ] 2.3a Implement read-only `to-spec status` using local state and approved-tag metadata.
- [ ] 2.3b Implement read-only `to-spec diff` using the prepared payload.
- [ ] 2.3c Implement guarded single-shot `to-spec retry` using the same payload and key.
- [ ] 2.3d Implement approval-gated `to-spec add --confirm-scope` that creates and pushes the annotated tag only after explicit confirmation.

## 3. GitHub Actions integration

- [ ] 3.1 Add the tag-push workflow with `issues: write` on the publisher job only, no repository credential, and administrator-prerequisite documentation.
- [ ] 3.2 Add bounded automatic retry and read-only diagnosis, plus the manual workflow-dispatch guard for a human-remedied retry.
- [ ] 3.3 Ignore generated local staging without excluding OpenSpec source artifacts.
- [ ] 3.4 Implement daily GitHub Actions cleanup on the persistent self-hosted staging runner for confirmed 30-day terminal regenerable staging; reject stateless GitHub-hosted configuration, do not delete state records or canonical evidence, and do not call the GitHub API.

## 4. Verification and review

- [ ] 4.1 Run frozen fixture tests and workflow/static checks; compare TDD SHA-256 and frozen test-diff baseline.
- [ ] 4.2 Run `$code-review` for the code change, including boundary, business-logic, and readability findings.
- [ ] 4.3 Record bootstrap completion without a self-mirror; a live GitHub Issue publication remains unverified until a later valid approved tag is pushed after the one-time administrator prerequisite.
