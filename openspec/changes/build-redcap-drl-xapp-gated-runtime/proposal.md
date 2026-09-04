## Why

The RedCap/FlexRIC simulator has control-contract and native xApp reference assets, but no reproducible Python DRL development environment that can safely attach to the existing RIC and prove a bounded E2 control path. Researchers need a one-command, reusable workspace for DQN, PPO, and DDPG development without copying ML dependencies into OAI images or allowing experimental Python code to bypass control safety gates.

## What Changes

- Add a shared, version-locked local DRL runtime release with CPU and GPU variants, plus a separate native FlexRIC bridge image.
- Add an atomic named-workspace lifecycle that refuses existing names and resolves the specified existing FlexRIC compose configuration instead of assuming RIC, network, gNB, or port names.
- Add a stable Python-to-Unix-socket-to-SWIG/native C bridge seam for KPM observations and a contract-limited E2SM-RC control transaction.
- Extend only the existing gNB KPM owner and FlexRIC SWIG owner seams as needed to expose separately qualifiable cell and UE KPM streams to that bridge; do not change UE, CN, compose topology, or the control contract.
- Add KPM capability discovery, profile qualification, node-level exclusive control leases, target-binding gates, baseline recovery, and evidence manifests.
- Add a concise operator CLI with Traditional-Chinese help and a model-invoked Gate-oriented developer skill/guide.
- Keep live multi-episode DRL training out of this change until a future research profile defines state, action, reward, reset, and rate semantics.

## Capabilities

### New Capabilities

- `drl-xapp-workspace-lifecycle`: Create, start, verify, upgrade, stop, and remove isolated named DRL xApp workspaces using shared local images and resolved compose data.
- `drl-xapp-bridge-gates`: Provide the stable Python/native bridge interface, KPM discovery and qualification, safe one-action control transactions, target leases, and recovery states.
- `drl-xapp-evidence-guidance`: Preserve evidence for every run and provide the CLI help and Gate-oriented developer guidance needed to operate the environment safely.

### Modified Capabilities

- None.

## Impact

- Adds a new DRL xApp workspace/CLI and shared Docker build assets. The change may modify only the existing gNB KPM owner `openair2/E2AP/RAN_FUNCTION/O-RAN/ran_func_kpm.c`, the existing read-seam declaration `openair2/E2AP/flexric/src/sm/agent_if/read/sm_ag_if_rd.h`, the existing KPM v03.00 agent adapter `openair2/E2AP/flexric/src/sm/kpm_sm/kpm_sm_v03.00/kpm_sm_agent.c`, and the FlexRIC xApp SWIG KPM projection under `openair2/E2AP/flexric/src/xApp/swig/`, subject to the qualification requirements below. The KPM extension reuses the existing event identity and action-definition free lifecycle; it does not add a request-ID registry or a new unsubscribe API.
- Does not modify UE, CN, RIC compose services, compose YAML, Docker socket policy, OAI image topology, or `redcap_interface/control` limits. The gNB and SWIG changes reuse their existing owner seams and must preserve existing KPM/RC behavior until separately validated.
- Requires local Docker, CPU/GPU runtime checks, Python/PyTorch/Gymnasium/Stable-Baselines3, SWIG native-extension loading, and a running user-specified FlexRIC RedCap compose scenario for integration gates.
