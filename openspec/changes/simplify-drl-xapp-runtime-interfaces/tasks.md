## 1. P1-A Model developer guide

- [x] 1.1 Add a focused regression assertion for the supported model entrypoint
  and the absence of `redcap_drl.Client` in the developer guide.
- [x] 1.2 Update the guide to route model code through
  `module:callable(observation)` and retain CLI/Bridge ownership of candidate
  validation and UDS control.

## 2. P1-B Single Control Run lifecycle

- [x] 2.1 Move collector-refusal coverage from the legacy helper to the public
  enabled Control Run orchestration and prove that no UDS request is sent.
- [x] 2.2 Remove the test-only `control_once()` helper and its obsolete direct
  caller.

## 3. P1-C Direct observation interface

- [x] 3.1 Add focused Bridge tests for direct no-control `observe` and rejected
  `open(mode=observation-only)`.
- [x] 3.2 Remove `observation-only` from the Bridge `open` implementation while
  preserving `control-once` session, direct observation, and fail-closed errors.

## 4. Validation

- [x] 4.1 Run the focused P1 tests and the full DRL xApp Python test file.
- [x] 4.2 Run Python syntax validation, `git diff --check`, and strict OpenSpec
  validation; record the evidence paths and review the final diff.
