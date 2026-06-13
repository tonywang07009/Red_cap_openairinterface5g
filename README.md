# OpenAirInterface5G RedCap Research Fork

<p align="center">
  <a href="https://openairinterface.org/">
    <img src="https://openairinterface.org/wp-content/uploads/2015/06/cropped-oai_final_logo.png" alt="OAI" width="420">
  </a>
</p>

<p align="center">
  <a href="https://gitlab.eurecom.fr/oai/openairinterface5g/-/blob/master/LICENSE"><img src="https://img.shields.io/badge/license-OAI--Public--V1.1-blue" alt="License"></a>
  <a href="https://releases.ubuntu.com/22.04/"><img src="https://img.shields.io/badge/OS-Ubuntu22-green" alt="Ubuntu 22"></a>
  <a href="https://releases.ubuntu.com/24.04/"><img src="https://img.shields.io/badge/OS-Ubuntu24-green" alt="Ubuntu 24"></a>
  <a href="https://gitlab.eurecom.fr/oai/openairinterface5g/-/releases"><img alt="OAI releases" src="https://img.shields.io/gitlab/v/release/oai/openairinterface5g?gitlab_url=https%3A%2F%2Fgitlab.eurecom.fr&include_prereleases&sort=semver"></a>
</p>

This repository is an OpenAirInterface5G-based research workspace for [RedCap], [mMTC], [RRC_INACTIVE], [SDT], and [O-RAN/FlexRIC] experiments. It keeps the upstream OAI RAN codebase intact while adding local RedCap operator scripts, documentation routes, reusable runtime evidence, and project management records.

繁體中文使用者：此 README 是專案入口。若你只想跑 RedCap/mMTC 測試，先看 [RedCap Operator Routes](#redcap-operator-routes)。若你想理解 L1/L2 協定與程式路徑，先看 [RedCap Protocol Learning Path](#redcap-protocol-learning-path)。

## Contents

- [Quick Start](#quick-start)
- [Documentation Routes](#documentation-routes)
- [RedCap Operator Routes](#redcap-operator-routes)
- [RedCap Protocol Learning Path](#redcap-protocol-learning-path)
- [Repository Map](#repository-map)
- [Build and Test](#build-and-test)
- [License and Support](#license-and-support)

## Quick Start

Use these commands from the repository root.

```bash
# First-time build and 29 UE run guide.
sed -n '1,220p' redcap_doc/manuals/redcap_zero_to_build_and_run_guide.en.md
sed -n '1,220p' redcap_doc/manuals/redcap_zero_to_build_and_run_guide.zh-TW.md

# Validate the RedCap operator interface without starting RFsim.
bash redcap_interface/validate_redcap_interface.sh

# Open the daily RedCap/mMTC operator menu.
bash redcap_interface/mmtc.menu.bash

# Open paper/demo display tools.
bash redcap_interface/mmtc.display.bash

# Read the RedCap documentation router.
sed -n '1,160p' redcap_doc/README.md
```

For upstream OAI build and modem usage, start with the official local docs:

| Need | Start Here |
|---|---|
| General OAI documentation | [`doc/README.md`](./doc/README.md) |
| Implemented OAI features | [`doc/FEATURE_SET.md`](./doc/FEATURE_SET.md) |
| System requirements | [`doc/system_requirements.md`](./doc/system_requirements.md) |
| Build OAI | [`doc/BUILD.md`](./doc/BUILD.md) |
| Run OAI modems | [`doc/RUNMODEM.md`](./doc/RUNMODEM.md) |

## Documentation Routes

| Route | Purpose | First File |
|---|---|---|
| Beginner build and 29 UE run | Compile gNB/NR UE, rebuild local images, and run a 29 UE RFsim validation | [`redcap_zero_to_build_and_run_guide.en.md`](./redcap_doc/manuals/redcap_zero_to_build_and_run_guide.en.md) / [`zh-TW`](./redcap_doc/manuals/redcap_zero_to_build_and_run_guide.zh-TW.md) |
| RedCap operator scripts | Daily RFsim, Docker, Gate, DRX/eDRX/PSM, and display menus | [`redcap_interface/README.md`](./redcap_interface/README.md) |
| Stable RedCap docs | Specs, papers, manuals, checklists, function references | [`redcap_doc/README.md`](./redcap_doc/README.md) |
| Curated reusable evidence | Final configs, CN5G overlays, reports, runtime probes, build evidence | [`redcap_library/README.md`](./redcap_library/README.md) |
| Active project management | Milestones, validation plans, cleanup inventories, implementation boundaries | [`agent_doc/Project_management/`](./agent_doc/Project_management/) |
| Docs/interface reorg project | Rules for this README and RedCap documentation routing | [`redcap_docs_interface_reorg_v1`](./agent_doc/Project_management/projects/redcap_docs_interface_reorg_v1/project_plan.md) |

Documentation style follows the local RedCap reorganization project:

- Keep stable docs short and task-oriented.
- Keep English and Traditional Chinese pages paired when a folder has `Doc/`.
- Split [API/config behavior], [Bash usage], and [step-by-step recap] instead of mixing them.
- Do not paste raw runtime logs into stable docs; link to log paths and marker names.
- Mark uncertain 3GPP clause mappings as `[Needs Verification]`.

## RedCap Operator Routes

| Task | Command or File |
|---|---|
| Daily RFsim and mMTC operation | `bash redcap_interface/mmtc.menu.bash` |
| Paper reproduction and display panels | `bash redcap_interface/mmtc.display.bash` |
| Functional script implementation | [`redcap_interface/bash_library/`](./redcap_interface/bash_library/) |
| Validate shell/Python layout | `bash redcap_interface/validate_redcap_interface.sh` |
| Current runtime YAML source of truth | [`ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/`](./ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/) |

Common RedCap gate commands:

```bash
# Gate 3 CG-SDT smoke path.
MMTC_RRC_INACTIVE_GATE3_CG_CONFIG=1 bash redcap_interface/mmtc.menu.bash gate3

# Gate 4 TA/RSRP fallback smoke path.
MMTC_RRC_INACTIVE_GATE4_FORCE_FALLBACK=1 bash redcap_interface/mmtc.menu.bash gate4
```

Legacy root scripts under `redcap_interface/` are compatibility shims unless a current manual explicitly says otherwise. New operator work should route through `mmtc.menu.bash`, `mmtc.display.bash`, or `bash_library/fc_*`.

## RedCap Protocol Learning Path

Start here when the goal is to understand or modify RedCap behavior in OAI.

| Topic | First File |
|---|---|
| L1/L2 RedCap protocol overview | [`redcap_doc/specs/redcap_l1_l2_protocol_guide.md`](./redcap_doc/specs/redcap_l1_l2_protocol_guide.md) |
| L1-L3 function lookup | [`redcap_doc/specs/function_reference/redcap_l1_l3_function_lookup.md`](./redcap_doc/specs/function_reference/redcap_l1_l3_function_lookup.md) |
| Local RedCap spec notes | [`redcap_doc/specs/README.md`](./redcap_doc/specs/README.md) |
| RRC_INACTIVE + SDT project gates | [`redcap_rrc_inactive_sdt_oran_control_v1`](./agent_doc/Project_management/projects/redcap_rrc_inactive_sdt_oran_control_v1/project_plan.md) |

Layer entry points:

| Layer | OAI Area | RedCap Focus |
|---|---|---|
| L1 PHY | `openair1/PHY/` | FR1 PRB limits, frame parameter validation, RedCap UE/gNB capability checks |
| L2 MAC/RLC/PDCP | `openair2/LAYER2/` | RedCap BWP, RACH, Msg2/Msg3, configured grant, CG-SDT, scheduler gates |
| L3 RRC/UICC | `openair2/RRC/`, `openair3/UICC/` | UE capability, SIB1 RedCap parsing, RRC_INACTIVE, RRCResume |
| O-RAN control | `openair2/E2AP/`, `ci-scripts/redcap_ul_prb_ctrl_xapp.c` | RedCap UL PRB control and policy experiments |

## Repository Map

```text
openairinterface5g
├── openair1/         L1 PHY and frame-parameter code
├── openair2/         L2 MAC/RLC/PDCP/RRC, F1/E1/X2, and E2AP
├── openair3/         NGAP, GTP, NAS, UICC, and related control-plane code
├── executables/      gNB, eNB, UE, and softmodem entry points
├── radio/            RF back ends, including RFsim
├── ci-scripts/       CI helpers, runtime YAML, RFsim scenarios, xApp assets
├── docker/           OAI runtime/build Dockerfiles
├── doc/              Upstream OAI documentation
├── redcap_interface/ RedCap operator menus and functional script library
├── redcap_doc/       Stable RedCap docs, specs, manuals, and checklists
├── redcap_library/   Curated reusable RedCap evidence and configs
└── agent_doc/        Project management, milestones, validation, and rules
```

## Build and Test

For a first-time RedCap workflow, use the bilingual step-by-step guide:

- English: [`redcap_doc/manuals/redcap_zero_to_build_and_run_guide.en.md`](./redcap_doc/manuals/redcap_zero_to_build_and_run_guide.en.md)
- 繁體中文：[`redcap_doc/manuals/redcap_zero_to_build_and_run_guide.zh-TW.md`](./redcap_doc/manuals/redcap_zero_to_build_and_run_guide.zh-TW.md)

Prefer preset-based CMake for local builds:

```bash
cmake --preset default
cmake --build --preset default
cmake --preset tests
cmake --build --preset tests
cd cmake_targets/ran_build/build_test && ctest --output-on-failure
```

Use the standard OAI wrapper when dependency installation or target selection is needed:

```bash
cd cmake_targets
./build_oai -I --install-optional-packages -w USRP
./build_oai --ninja --gNB --nrUE
./build_oai --phy_simulators
```

RedCap documentation/interface-only changes should at minimum run:

```bash
bash redcap_interface/validate_redcap_interface.sh
git diff --check -- README.md redcap_doc redcap_interface agent_doc/Project_management
```

## License and Support

This repository keeps the upstream [OAI Public License V1.1](./LICENSE). Third-party notices are listed in [`NOTICE.md`](./NOTICE.md).

For upstream OAI community support, use the [OAI mailing lists](https://gitlab.eurecom.fr/oai/openairinterface5g/-/wikis/MailingList) and include:

- A clear subject with `[Query]` or `[Problem]`.
- Configuration files in `.conf` or `.yaml` format.
- Logs in `.log` or `.txt` format.
- System details and topology when the question is performance-related.

For local RedCap research work, first include the active project path, command, expected marker, and log path.
