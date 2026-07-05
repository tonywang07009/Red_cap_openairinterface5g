# OpenAirInterface5G RedCap Research Fork

[English](./README.en.md) | [繁體中文](./README.zh-TW.md)

## Overview

This repository is an OpenAirInterface5G-based research workspace for RedCap, mMTC, RRC_INACTIVE, SDT, and O-RAN/FlexRIC experiments. It keeps the upstream OAI RAN codebase intact while adding local RedCap operator scripts, documentation routes, reusable runtime evidence, and project management records.

## Start Here

| Goal | First File |
|---|---|
| Install and build from zero | [Begin from zero](./redcap_doc/manuals/install/redcap_begin_from_zero.en.md) |
| Rebuild after C, xApp, rApp, dApp, or library changes | [Rebuild after changes](./redcap_doc/manuals/install/redcap_rebuild_after_changes.en.md) |
| Run the newcomer validation gate | [Newcomer runtime gate](./redcap_doc/manuals/install/redcap_newcomer_runtime_gate.en.md) |
| Find all install manuals | [Install manual index](./redcap_doc/manuals/install/README.en.md) |
| Run daily RedCap/mMTC operations | [RedCap interface docs](./redcap_interface/Doc/README.en.md) |
| Read stable RedCap documentation | [RedCap stable docs](./redcap_doc/Doc/README.en.md) |
| Find curated evidence and reusable assets | [RedCap library docs](./redcap_library/Doc/README.en.md) |

## Quick Commands

Run from the repository root unless a step changes directory.

```bash
# Validate the RedCap public operator interface without starting RFsim.
bash redcap_interface/validate_redcap_interface.sh

# Open the daily RedCap/mMTC operator menu.
bash redcap_interface/mmtc.menu.bash

# Open paper/demo display tools.
bash redcap_interface/mmtc.display.bash
```

## Documentation Routes

| Route | Purpose | First File |
|---|---|---|
| Install manuals | Beginner setup, rebuild, and newcomer gate | [redcap_doc/manuals/install/README.en.md](./redcap_doc/manuals/install/README.en.md) |
| Operator scripts | RFsim, Docker, Gate, DRX/eDRX/PSM, and paper demo menus | [redcap_interface/Doc/README.en.md](./redcap_interface/Doc/README.en.md) |
| Stable RedCap docs | Specs, papers, manuals, checklists, and function references | [redcap_doc/Doc/README.en.md](./redcap_doc/Doc/README.en.md) |
| Curated reusable evidence | Final configs, CN5G overlays, runtime probes, and accepted reports | [redcap_library/Doc/README.en.md](./redcap_library/Doc/README.en.md) |
| Active project management | Milestones, validation plans, and analysis records | [agent_doc/Project_management/](./agent_doc/Project_management/) |

## Build and Test

For first-time RedCap use, follow:

- [Begin from zero](./redcap_doc/manuals/install/redcap_begin_from_zero.en.md)

For a normal local OAI build:

```bash
cmake --preset default
cmake --build --preset default --target nr-softmodem
cmake --build --preset default --target nr-uesoftmodem
```

For dependency installation or upstream wrapper flow:

```bash
cd cmake_targets
./build_oai -I --install-optional-packages -w USRP
./build_oai --ninja --gNB --nrUE
cd ..
```

For local RedCap RFsim image refresh:

```bash
bash redcap_interface/redcap_rebuild_local_oai_images.sh
bash redcap_interface/redcap_inspect_gnb_image.sh
```

## RedCap Operator Routes

| Task | Command or File |
|---|---|
| Daily RFsim and mMTC operation | `bash redcap_interface/mmtc.menu.bash` |
| Paper reproduction and display panels | `bash redcap_interface/mmtc.display.bash` |
| Functional script implementation | `redcap_interface/bash_library/` |
| Interface validation | `bash redcap_interface/validate_redcap_interface.sh` |
| Current RFsim YAML source of truth | `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/` |

## Protocol Learning Path

| Topic | First File |
|---|---|
| RedCap stable docs | [redcap_doc/Doc/README.en.md](./redcap_doc/Doc/README.en.md) |
| Spec notes | [redcap_doc/specs/Doc/README.en.md](./redcap_doc/specs/Doc/README.en.md) |
| Function reference route | [redcap_doc/function_reference/Doc/README.en.md](./redcap_doc/function_reference/Doc/README.en.md) |

## Repository Map

```text
openairinterface5g
├── openair1/         L1 PHY and frame-parameter code
├── openair2/         L2 MAC/RLC/PDCP/RRC, F1/E1/X2, and E2AP
├── openair3/         NGAP, GTP, NAS, UICC, and related control-plane code
├── executables/      gNB, eNB, UE, and softmodem entry points
├── radio/            RF back ends, including RFsim
├── ci-scripts/       CI helpers, runtime YAML, RFsim scenarios, and xApp assets
├── doc/              Upstream OAI documentation
├── redcap_interface/ RedCap operator menus and functional script library
├── redcap_doc/       Stable RedCap docs, specs, manuals, and checklists
├── redcap_library/   Curated reusable RedCap evidence and configs
└── agent_doc/        Project management, milestones, validation, and rules
```

## License and Support

This repository keeps the upstream [OAI Public License V1.1](./LICENSE). Third-party notices are listed in [NOTICE.md](./NOTICE.md).

For upstream OAI support, use the OAI community channels. For local RedCap research work, include the active project path, command, expected marker, and log path.
