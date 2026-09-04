## Why

The DRL xApp interface retains two paths that do not represent executable
behavior: an observation-only UDS session whose identifier is never consumed,
and a legacy control helper that bypasses terminal evidence finalization.
The model-developer guide also names a generic UDS client that the runtime
image intentionally does not provide.

## What Changes

- Correct the model-developer guide to describe the existing
  `module:callable(observation)` runtime entrypoint and its strict one-decision
  contract.
- Remove the test-only legacy `control_once()` helper so the existing
  `execute_control_run()` remains the only Control Run lifecycle path.
- **BREAKING** Remove `observation-only` from the Bridge `open` mode. Keep
  direct `observe` for no-control KPM diagnostics and keep `control-once` for
  the leased control transaction.
- Add regression coverage proving the removed paths cannot be used and the
  retained interfaces preserve their current no-control and fail-closed rules.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `drl-xapp-bridge-gates`: remove the unused observation-only session contract
  while retaining direct observation diagnostics and the control-once session.

## Impact

- `redcap_library/skills/redcap-drl-xapp-gates/SKILL.md`
- `redcap_library/bash_tool/scripts/redcap_drl_xapp.py`
- `redcap_library/drl_xapp/bridge_daemon.py`
- `redcap_library/bash_tool/scripts/test_redcap_drl_xapp.py`
- `openspec/specs/drl-xapp-bridge-gates/spec.md`

No Docker image, E2SM-RC encoding, KPM subscription behavior, or live control
claim changes.
