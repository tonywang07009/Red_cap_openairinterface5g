You are Codex, based on GPT-5.5. You are running as a coding agent in the Codex CLI on a user's computer.

# Repository Guidelines

## Project Structure & Module Organization

Core RAN code is split by layer: `openair1/` for PHY, `openair2/` for MAC/RLC/PDCP/RRC and E2AP, and `openair3/` for NGAP/GTP/NAS and related control-plane code. Shared utilities live in `common/`, top-level softmodem entry points are in `executables/`, and radio back ends are in `radio/` (`USRP/`, `rfsimulator/`, `fhi_72/`, etc.). Build helpers and generated build trees live under `cmake_targets/`. Project documentation is in `doc/`; CI orchestration and test assets are in `ci-scripts/`.

## File Query Workflow

- When querying files, symbols, call relationships, or repository structure in this repo, use the `symdex` MCP tools first. Only fall back to raw filesystem or shell-based search if `symdex` does not cover the needed lookup.

- For file contents, project documents, generated headers, logs, and local spec artifacts, use the filesystem MCP tools whenever possible before falling back to shell commands.

## Build, Test, and Development Commands

Prefer the preset-based CMake flow for local work:

```bash

cmake --preset default
cmake --build --preset default
cmake --preset tests
cmake --build --preset tests
cd cmake_targets/ran_build/build_test && ctest --output-on-failure

```

Use `cmake_targets/build_oai` when you need the repository’s standard wrapper or dependency install flow:

```bash

cd cmake_targets
./build_oai -I --install-optional-packages -w USRP
./build_oai --ninja --gNB --nrUE
./build_oai --phy_simulators

```

Artifacts are written below `cmake_targets/ran_build/build*`.

## Coding Style & Naming Conventions

Follow the root `.clang-format` and `doc/code-style-contrib.md`. Use 2-space indentation, no tabs, and keep C/C++ lines within 132 columns. Function opening braces go on the next line; control-flow braces stay on the same line. Prefer strong OAI types, named constants over magic numbers, `const` for input pointers, and `AssertFatal()` / `DevAssert()` for invariants. Test binaries and many helpers use descriptive snake_case names such as `test_nr_common` or `nr-softmodem`.

## Testing Guidelines

Enable tests with `cmake --preset tests` or `-DENABLE_TESTS=ON`. Most unit tests are declared in nearby `tests/` directories and registered with CTest; common names start with `test_` or `<module>_test`. Add or update the closest module test when changing shared logic, protocol encoding, or PHY utilities. For simulator changes, validate the affected `physim` or RF simulator target before sending for review.

## Commit & Pull Request Guidelines

Reference only unless the user explicitly asks for commit or MR preparation. Target `develop`. Keep branch history linear and rebase instead of merging. Each commit should be a small logical change, compile on its own, and explain why the change is correct. Merge requests go to Eurecom GitLab, require the proper CI label (`~documentation`, `~BUILD-ONLY`, `~4G-LTE`, `~5G-NR`), and should include the scope, validation performed, and any config or test impact.

---

## 3GPP Specs Available Locally

- Local RedCap and 3GPP project references live under `redcap_doc/specs/redcap_3gpp/`.
- Primary RedCap behavior notes:
  - `redcap_doc/specs/redcap_3gpp/spec.md`
  - `redcap_doc/specs/redcap_3gpp/redcap5g_spec.md`
- MinerU Markdown cache and scan manifest:
  - `redcap_doc/mineru_markdown/scan_manifest.md`
- For RedCap, mMTC, PHY, MAC, RRC, or NAS changes, check the relevant local spec notes before implementation.
- Mark uncertain clause interpretation as `[Needs Verification]`.
- `@spec-38.331` means: look under `redcap_doc/specs/redcap_3gpp/` for the local TS 38.331 reference or project note.

---

## Project Router

- Project management root:
  - `agent_doc/Project_management/`
- RedCap operator interface:
  - `redcap_interface/`
- Common logging rules:
  - `agent_doc/Project_management/logging_rules.md`
- Curated RedCap reusable artifacts:
  - `redcap_library/`
- Stable RedCap docs:
  - `redcap_doc/`
- RedCap PDF Markdown cache:
  - `redcap_doc/mineru_markdown/scan_manifest.md`
- RedCap onboarding tutorial:
  - `redcap_doc/manuals/redcap_project_onboarding_step_by_step.md`
- RedCap L1-L3 function lookup:
  - `redcap_doc/function_reference/redcap_l1_l3_function_lookup.md`

## Initial RedCap Project Menu

- At the beginning of a new RedCap project discussion, if the user has not selected a mode, ask which entry they want:
  1. `進入專案`
  2. `開啟教學`
  3. `函式介紹與查詢`
- If the user directly asks for a concrete task, do the task instead of forcing the menu.

## Active Project Entries

| Project | Plan | Project Rules |
|---|---|---|
| RedCap mMTC execution | `agent_doc/Project_management/projects/redcap_mmtc_priority_execution_v1/project_plan.md` | `agent_doc/Project_management/projects/redcap_mmtc_priority_execution_v1/agent_rules.md` |
| RedCap simulator performance evaluation | `agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/project_plan.md` | `agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/agent_rules.md` |

## Context Loading Rule

- For project work, keep the context pack small:
  1. root `AGENTS.md`
  2. active `project_plan.md`
  3. active project `agent_rules.md`
  4. target milestone file
  5. relevant validation file
  6. latest `test_log/work_daily/*.md`
- Do not read unrelated milestones, historical reports, PDFs, logs, or generated artifacts unless the active task needs them.
- Do not add milestone details, validation matrices, paper extraction details, repo audit checklists, or visualization rules back into root `AGENTS.md`.

## Build And Test Logs

- CTest logs go under `test_log/compiler_logs/`.
- Build logs go under `test_log/build_logs/`.
- Prefer timestamped log files when running builds or tests.
- When analyzing test failures, open the most recent relevant log and summarize failures in Traditional Chinese.
- Reusable final configs/reports/evidence promoted from generated logs live under `redcap_library/`; read `redcap_library/README.md` before scanning old `test_log/` artifacts.

## Cleanup Rule

- Do not delete, move, or rewrite files unless the user explicitly asks for that exact cleanup or approves a specific cleanup batch.
- For unused-file audits, produce an inventory first:
  - path
  - reason
  - references checked
  - expected impact
  - recommendation
