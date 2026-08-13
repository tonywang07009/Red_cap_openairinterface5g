## 1. Approval and frozen TDD contract

- [ ] 1.1 Obtain human scope confirmation and create the approved annotated tag for this revision.
- [ ] 1.2 Add a registered local fake-GitHub validator in `redcap_library/` for tag validation, key generation, recovery, mismatch, retry, diagnosis immutability, and token redaction cases.
- [ ] 1.3 Record the TDD model/effort, test paths, SHA-256 values, and frozen test-diff baseline in `design.md`; make the tests read-only.

## 2. Publisher and local evidence

- [ ] 2.1 Implement the standard-library publisher that validates the approved tag, builds a redacted payload, and derives the deterministic key.
- [ ] 2.2 Implement GitHub Issue marker query, create/recovery, mismatch refusal, and generated state under `openspec/.to-spec/`.
- [ ] 2.3 Implement `to-spec status`, `to-spec diff`, and guarded single-shot `to-spec retry` using the same payload and key.

## 3. GitHub Actions integration

- [ ] 3.1 Add the tag-push workflow with least-privilege `issues: write` permission and no repository credential.
- [ ] 3.2 Add bounded automatic retry and read-only diagnosis, plus the manual workflow-dispatch guard for a human-remedied retry.
- [ ] 3.3 Ignore generated local staging without excluding OpenSpec source artifacts.

## 4. Verification and review

- [ ] 4.1 Run frozen fixture tests and workflow/static checks; compare TDD SHA-256 and frozen test-diff baseline.
- [ ] 4.2 Run `$code-review` for the code change, including boundary, business-logic, and readability findings.
- [ ] 4.3 Record bootstrap completion without a self-mirror; a live GitHub Issue publication remains unverified until a later approved tag is authorized.
