## ADDED Requirements

### Requirement: Named workspace initialization
The system SHALL create a named DRL xApp workspace from one Bash command using
an explicitly supplied workspace root, compose path, runtime variant, and
profile. It MUST refuse an existing name without modifying that workspace and
MUST leave no partial workspace when preflight fails.

#### Scenario: Initialize a new live-control workspace
- **WHEN** the operator initializes `tag_scheduler_dqn` with a unique name,
  `ul-prb-cap-v1`, a valid compose path, and an available runtime release
- **THEN** the system creates its workspace lock, editable source mount,
  generated overlay metadata, and artifact directories without changing the
  base compose files or services

#### Scenario: Existing workspace name
- **WHEN** initialization receives a name that already exists below the
  selected workspace root
- **THEN** the command fails before creating, overwriting, or deleting any
  workspace file

### Requirement: Immutable shared DRL releases
The system SHALL use one shared local CPU or GPU DRL image release and one
separate bridge release across workspaces. A workspace lock MUST record both
the requested tag and resolved local image digest or ID. The system MUST NOT
rebuild, retag, or mutate a shared release during workspace initialization.

#### Scenario: Reuse an existing CPU release
- **WHEN** two workspaces select the same available CPU release
- **THEN** both locks resolve to that release identity and neither command
  builds a duplicate Python, PyTorch, Gymnasium, or Stable-Baselines3 image

#### Scenario: Upgrade dependencies
- **WHEN** an operator needs a changed DRL or native dependency
- **THEN** the system requires a newly built and smoke-tested immutable
  release and an explicit workspace upgrade, preserving the old lock if that
  upgrade fails

### Requirement: Resolved compose overlay isolation
The system SHALL derive the required external Docker network and service
descriptors from the supplied compose configuration. It MUST stop on missing
or ambiguous required values and MUST NOT hard-code a RIC, gNB, network, or
port name. It SHALL generate an overlay that adds only the runtime and bridge
services to the resolved network.

#### Scenario: Valid resolved network
- **WHEN** compose resolution finds exactly one required external network and
  required service descriptors
- **THEN** the workspace overlay joins that network while the base compose
  file remains unchanged

#### Scenario: Ambiguous RIC or network resolution
- **WHEN** compose resolution cannot determine exactly one required RIC or
  network descriptor
- **THEN** initialization fails with a diagnostic and starts no xApp
  container

### Requirement: Workspace lifecycle containment
The system SHALL provide `up`, `verify`, `down`, and `remove` operations that
affect only named workspace runtime and bridge containers. `down` and
`remove` MUST NOT stop, restart, remove, or alter gNB, UE, CN, RIC, base
compose, control contract, or another workspace's container. External
configuration exposed to xApp containers MUST be mounted read-only.

#### Scenario: Stop a workspace
- **WHEN** the operator runs `down` for one workspace
- **THEN** only that workspace's generated overlay services stop and its run
  artifacts remain available

#### Scenario: Remove a workspace
- **WHEN** the operator runs `remove` for one workspace
- **THEN** only that workspace's generated services and workspace state are
  removed and existing simulator containers and retained evidence are intact

### Requirement: Runtime smoke verification
The system SHALL provide a smoke verification that imports Python, PyTorch,
Gymnasium, Stable-Baselines3, and the shared xApp function library; executes a
minimal Gymnasium environment; loads the SWIG native extension; and checks
bridge health. For a running selected compose scenario it SHALL also report
RIC name-resolution or network reachability as a separate result, not E2
success proof.

#### Scenario: Offline runtime smoke passes
- **WHEN** the selected runtime and bridge release are correctly installed
- **THEN** the verification reports successful library imports, minimal Gym
  execution, native-extension loading, and bridge health without E2 control

#### Scenario: RIC reachability is absent
- **WHEN** runtime library smoke passes but the resolved RIC cannot be reached
- **THEN** verification reports the reachability gate failure and does not
  claim E2 setup, KPM availability, or control readiness

### Requirement: Chinese CLI help and explicit release operations
The CLI SHALL provide read-only Traditional-Chinese top-level and per-command
help that states each parameter name, requiredness, allowed values, default,
side effect, emitted evidence, and safe next command. `build-release` and
`upgrade` help MUST additionally state the dependency-upgrade order and that
upgrade does not issue E2 control.

#### Scenario: Inspect help without Docker access
- **WHEN** an operator executes a help command
- **THEN** the command prints the applicable Traditional-Chinese explanation
  without creating a workspace, starting a container, resolving compose, or
  contacting Docker
