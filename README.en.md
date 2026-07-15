# OpenAirInterface5G RedCap Research Fork

[English](./README.en.md) | [繁體中文](./README.zh-TW.md)

## Overview

This repository is an OpenAirInterface5G-based research workspace for RedCap, mMTC, RRC_INACTIVE, SDT, and O-RAN/FlexRIC experiments. It keeps the upstream OAI RAN codebase intact while adding local RedCap operator scripts, documentation routes, reusable runtime evidence, and project management records.

## Start Here

| Goal | First File |
|---|---|
| Build and reproduce the 29 UE beginner flow | [Beginner build and 29 UE reproduction](./redcap_doc/manuals/install/redcap_begin_from_zero.en.md) |
| Configure the 56 UE profile and dApp/xApp experiment | [56 UE experiment tutorial](./agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/Doc/gate_e_core56_manual_reproduction.en.md) |
| Develop or trace the dApp/xApp SDK | [SDK development guide](./agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/Doc/sdk_development_guide.en.md) |
| Look up the active RedCap L1-L3 control path | [L1-L3 function lookup](./redcap_doc/specs/function_reference/redcap_l1_l3_function_lookup.md) |
| Rebuild after C, xApp, rApp, dApp, or library changes | [Rebuild after changes](./redcap_doc/manuals/install/redcap_rebuild_after_changes.en.md) |
| Find all install manuals | [Install manual index](./redcap_doc/manuals/install/README.en.md) |
| Run daily RedCap/mMTC operations | [RedCap interface docs](./redcap_interface/Doc/README.en.md) |
| Read stable RedCap documentation | [RedCap stable docs](./redcap_doc/Doc/README.en.md) |
| Find curated evidence and reusable assets | [RedCap library docs](./redcap_library/Doc/README.en.md) |

## Quick Commands

Run from the repository root unless a step changes directory.

```bash
# Validate the RedCap public operator interface without starting RFsim.
bash redcap_interface/validate_redcap_interface.sh

# Open the unified RedCap entry for introduction, evidence, experiment setup, and advanced RFsim.
./mmtc.menu.bash

# Show accepted paper/performance evidence without starting Docker.
./mmtc.menu.bash performance
```

## Verified Experiment Profile

| Field | Current contract | Source |
|---|---|---|
| Service ceiling | `MMTC_TOTAL_UES=56` | `redcap_interface/bash_library/fc_mmtc_smoke_validation.sh` |
| Active UE selection | `MMTC_ACTIVE_UES`, unique indices in `1..56` | `redcap_interface/bash_library/fc_mmtc_smoke_validation.sh` |
| Topology | One gNB with RFsim | `redcap_interface/Doc/README.en.md` |
| Multiple gNBs or CU/DU split | Unsupported by experiment profile v1 | `redcap_interface/Doc/README.en.md` |

The older proposed name `MMTC_ACTIVATE_UE` is not the current script contract.

## Documentation Routes

| Route | Purpose | First File |
|---|---|---|
| Install manuals | Beginner setup, rebuild, and newcomer gate | [redcap_doc/manuals/install/README.en.md](./redcap_doc/manuals/install/README.en.md) |
| Operator scripts | RFsim, Docker, Gate, DRX/eDRX/PSM, and paper demo menus | [redcap_interface/Doc/README.en.md](./redcap_interface/Doc/README.en.md) |
| Stable RedCap docs | Specs, papers, manuals, checklists, and function references | [redcap_doc/Doc/README.en.md](./redcap_doc/Doc/README.en.md) |
| Curated reusable evidence | Final configs, CN5G overlays, runtime probes, and accepted reports | [redcap_library/Doc/README.en.md](./redcap_library/Doc/README.en.md) |
| Active project management | Milestones, validation plans, and analysis records | [agent_doc/Project_management/](./agent_doc/Project_management/) |
| dApp/xApp SDK | SDK scenario, API behavior, developer guide, and 56 UE Gate E-Core manual reproduction | [agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/Doc/README.en.md](./agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/Doc/README.en.md) |

## Documentation and Evidence Layers

| Layer | Use it for | Route |
|---|---|---|
| Reference | Signatures, callers, guards, apply points, and runtime markers | [L1-L3 lookup](./redcap_doc/specs/function_reference/redcap_l1_l3_function_lookup.md) |
| Guide | How to extend and validate the dApp/xApp SDK | [SDK development guide](./agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/Doc/sdk_development_guide.en.md) |
| Example | Reproducible beginner and 56 UE experiments | [29 UE](./redcap_doc/manuals/install/redcap_begin_from_zero.en.md) / [56 UE](./agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/Doc/gate_e_core56_manual_reproduction.en.md) |

Evidence labels are independent: `Public` means declared, `Integrated` requires a production caller and apply path, `Runtime-evidenced` requires a matching retained marker, and `Dormant/blocked` means the public or implemented path lacks active integration or proof. Missing evidence or standards mappings are marked `[Needs Verification]`.

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
| Daily RFsim and mMTC operation | `./mmtc.menu.bash` |
| Paper/performance evidence and explicit reproduction entry | `./mmtc.menu.bash performance` |
| Functional script implementation | `redcap_interface/bash_library/` |
| Interface validation | `bash redcap_interface/validate_redcap_interface.sh` |
| Current RFsim YAML source of truth | `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/` |

## Protocol Learning Path

| Topic | First File |
|---|---|
| RedCap stable docs | [redcap_doc/Doc/README.en.md](./redcap_doc/Doc/README.en.md) |
| Spec notes | [redcap_doc/specs/Doc/README.en.md](./redcap_doc/specs/Doc/README.en.md) |
| RedCap L1-L3 function lookup | [redcap_doc/specs/function_reference/redcap_l1_l3_function_lookup.md](./redcap_doc/specs/function_reference/redcap_l1_l3_function_lookup.md) |

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
