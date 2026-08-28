---
name: redcap-drl-xapp-gates
description: Gate RedCap DRL xApp work. Use when creating or operating a DQN, PPO, DDPG, or other DRL workspace; changing a Python model entrypoint; inspecting KPM evidence; running bounded E2 control; recovering an interrupted control; upgrading the shared runtime; or proposing a new KPM/RC profile.
metadata:
  input: Workspace path or init parameters, requested operation, and whether live control is intended.
  output: Gate status, evidence manifest path, and safe next command.
  tool_dependencies: redcap_drl_xapp
---

# RedCap DRL xApp gates

Gate scope before acting:

- Treat Python model work and native profile work as different routes.
- Use `redcap_library/bash_tool/scripts/redcap_drl_xapp.sh`; resolve it through
  `redcap_library/bash_tool/registry.json` before execution.
- Never edit or restart the existing gNB, UE, CN, or RIC compose services for
  a workspace operation.
- Never claim that Docker reachability, E2 ACK, or static configuration proves
  gNB apply or closed-loop learning.

Gate model-developer work:

1. Read [references/control-gates.md](references/control-gates.md).
2. Run `verify`, then `qualify-kpm` for live work. `qualify-kpm` performs
   discovery and records the combined result; use `discover-kpm` alone only
   for capability diagnostics.
3. Edit only the bind-mounted workspace `src/` and expose a
   `module:callable` entrypoint.
4. Use the `redcap_drl.Client` interface; do not import SWIG, ASN.1, or C
   objects in model code.
5. Stop when any gate fails and report its manifest and safe next command.

Gate profile-maintainer work:

1. Read [references/profile-contract.md](references/profile-contract.md).
2. Start a new OpenSpec change before changing C, SWIG, E2SM-KPM, E2SM-RC,
   action semantics, freshness thresholds, binding rules, reward, or reset.
3. Preserve the existing control contract and native FlexRIC owner seams.
4. Require contract validation, xApp ACK, gNB apply marker, and a later KPM
   observation before reporting a successful candidate action.

Gate evidence handling:

1. Read [references/evidence.md](references/evidence.md).
2. Keep evidence after `down` and `remove`.
3. Label absent live KPM style or UE-to-RC identity facts
   `[Needs Verification]`; never fill them with service names or log guesses.
4. Treat `ROLLBACK_UNCONFIRMED` as a control lock requiring explicit
   `recover`.
