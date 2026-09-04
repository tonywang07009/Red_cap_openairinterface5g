## Context

The Bridge currently gives `open` two modes. `control-once` uses a session to
hold a target lease and to enforce one action. `observation-only` only stores a
session identifier: `observe` neither requires nor consults it, and `close`
cannot change observation ownership. The operator's `probe-kpm` path already
uses direct `observe`.

The CLI also retains a test-only `control_once()` helper that creates an
evidence package without using the Control Run finalization path. The actual
CLI entrypoint uses `execute_control_run()`.

The model-developer guide names `redcap_drl.Client`, but the runtime image
deliberately exposes only `redcap-drl-run-entrypoint` and the model
`module:callable(observation)` contract.

## Goals / Non-Goals

**Goals:**

- Make direct observation and leased control-once the two truthful Bridge
  interaction modes.
- Keep one Control Run lifecycle implementation and one terminal evidence
  finalization path.
- Make the model-developer guide name the runtime interface that exists.
- Preserve no-control KPM diagnostics and all current control proof gates.

**Non-Goals:**

- Change Docker image contents, KPM subscriptions, E2SM-RC encoding, model
  candidate limits, or live-control evidence claims.
- Add an observation session, subscription ownership, reference counting, or
  a generic UDS client.

## Decisions

### Remove observation-only session mode

`open` will accept only `control-once`. Direct `observe` remains a no-control
diagnostic operation and does not acquire a session or a lease.

The alternative was to make observation sessions own subscriptions and close
semantics. No caller requires that ownership, while the existing NativeFlexric
subscription state is shared with control proof. Adding ownership would create
new lifecycle rules without leverage.

### Delete the legacy Control Run wrapper

Remove `control_once()` and migrate its collector-refusal coverage to the
public `run --enable-control` orchestration path. This leaves
`execute_control_run()` as the only module that creates, finalizes, and emits a
Control Run evidence package.

The alternative was to retrofit finalization into the wrapper. That would
retain a second lifecycle interface with no production caller.

### Correct the model guide without expanding runtime privileges

The guide will instruct model developers to provide
`module:callable(observation)` returning one JSON decision. It will state that
candidate validation and UDS control remain CLI/Bridge-owned. The runtime keeps
no generic UDS client and no Bridge socket mount.

## TDD contract

- Model / effort: active metadata unavailable **[Needs Verification]**.
- Test boundary: public `run_model(..., enable_control=True)` for the
  collector-refusal path, and public `Bridge.handle()` for direct observation
  and rejected `open(mode=observation-only)`.
- Acceptance links: `drl-xapp-bridge-gates` stable interface scenarios and the
  approved P1-A/P1-B/P1-C task sequence.
- Irreversible side effects: test-owned temporary workspaces and in-memory
  fakes only; no Docker, KPM subscription, or E2SM-RC control.
- Boundary gate: clear. Direct observation remains no-control; only
  `control-once` acquires a session or lease.
- Test files: `redcap_library/bash_tool/scripts/test_redcap_drl_xapp.py`.
- Test evidence: P1-A RED/GREEN:
  `test_log/compiler_logs/p1a_model_guide_red_2026-09-04_11-41-42.log`,
  `test_log/compiler_logs/p1a_model_guide_green_2026-09-04_11-42-00.log`;
  P1-B GREEN:
  `test_log/compiler_logs/p1b_public_collector_refusal_green_2026-09-04_11-43-17.log`,
  `test_log/compiler_logs/p1b_legacy_removal_green_2026-09-04_11-43-59.log`;
  P1-C RED/GREEN:
  `test_log/compiler_logs/p1c_observation_mode_red_2026-09-04_11-46-12.log`,
  `test_log/compiler_logs/p1c_observation_mode_green_2026-09-04_11-46-49.log`;
  focused and full regression GREEN:
  `test_log/compiler_logs/simplify_drl_xapp_p1_focused_green_2026-09-04_11-47-12.log`,
  `test_log/compiler_logs/simplify_drl_xapp_full_green_2026-09-04_11-47-19.log`.

## Risks / Trade-offs

- [A private caller still uses `open(observation-only)`] → The Bridge rejects
  the mode before native activity; the delta spec and regression test make the
  removal explicit.
- [Collector-refusal test loses coverage during wrapper removal] → Move it to
  the public control-run path and assert no UDS request occurs.
- [Guide drifts again] → Add a small source-level regression test that forbids
  `redcap_drl.Client` and requires the supported entrypoint form.

## Migration Plan

1. Update the guide and its regression test.
2. Remove the legacy helper and move its test to the public orchestration path.
3. Remove observation-only mode, update the delta spec, and add direct-observe
   and rejected-mode tests.
4. Run focused tests, the full DRL xApp test file, strict OpenSpec validation,
   and `git diff --check`.

Rollback is a normal Git revert. No workspace state, image, E2 subscription,
or control transaction is created by the change itself.
