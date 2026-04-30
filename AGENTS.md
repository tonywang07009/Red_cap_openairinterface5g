You are Codex, based on GPT-5.4. You are running as a coding agent in the Codex CLI on a user's computer.

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

- All RedCap project spec notes and local 3GPP references are stored under `spec/redcap_3gpp/` relative to the OAI repo root.
- Key docs for this project:
  - `spec/redcap_3gpp/spec.md` (active RedCap behavior notes)
  - `spec/redcap_3gpp/redcap5g_spec.md` (RedCap project summary)
  - `spec/redcap_3gpp/Redcap/` (RedCap-related local reference material)
  - `spec/redcap_3gpp/DRX/`, `spec/redcap_3gpp/eDRX/`, `spec/redcap_3gpp/PSM/`, `spec/redcap_3gpp/WUS/`, `spec/redcap_3gpp/RRM/`
- When answering questions, prefer these local specs first.
- All RedCap, mMTC, PHY, MAC, RRC, and NAS changes must be checked against the relevant local 3GPP notes or reference artifacts before implementation, and any uncertain clause or interpretation must be marked as `Needs Verification`.
- When I write `@spec-38.331`, interpret it as “look under `spec/redcap_3gpp/` for the local TS 38.331 reference or project note and cite the relevant clause if possible”.
- For detailed RedCap RRC behavior, see `spec/redcap_3gpp/spec.md`.

---

## Project Docs & Task Plans

- All high-level project plans, milestones, and task breakdowns for this repo live under:
  - `agent_doc/Project_management/`
- Active execution project path:
  - `agent_doc/Project_management/projects/redcap_mmtc_priority_execution_v1/project_plan.md`
- Baseline milestone definition file:
  - `agent_doc/Project_management/Simluation_v2.md`
- For the RedCap mMTC work:
  - The primary execution plan is `agent_doc/Project_management/projects/redcap_mmtc_priority_execution_v1/project_plan.md`.
  - `Simluation_v2.md` remains the baseline milestone/spec definition.
  - Before making any changes to PHY, MAC, or RRC, you must:
    1) read the relevant sections of `project_plan.md` and `Simluation_v2.md`, and  
    2) summarize in a few bullet points which milestone and sub-tasks you are working on.
- For Gantt charts and progress visualization:
  - Treat `project_plan.md` as the primary source of truth, with `Simluation_v2.md` as the baseline reference.
  - When I ask for a Gantt chart, derive all tasks and milestones from those Markdown files instead of inventing new items.
- When planning or modifying PHY code for RedCap:
  - explicitly reference the corresponding milestones/sub-tasks in `project_plan.md` and `Simluation_v2.md`, and  
  - cross-check against `spec/redcap_3gpp/spec.md` and TS 38.306 / 38.101-1 before proposing code changes.

---

## O-RAN Scope Definition

- Current priority is RedCap and mMTC behavior inside OAI: UE/gNB flow, 3GPP alignment, RFsim runtime validation, and repeatable logs.
- Do not implement xApp/rApp/dApp SDKs until the RedCap UE/gNB behavior has passed the planned 3GPP-aligned validation flow.
- Near-RT RIC / xApp scope before that point is limited to existing FlexRIC runtime checks:
  - verify whether FlexRIC containers start,
  - verify E2 disabled/enabled mode behavior,
  - inspect existing KPM/RC monitor logs when the scenario already uses them.
- Non-RT RIC / rApp work is design/documentation only until explicitly promoted by the user.
- dApp work is out of implementation scope unless the user defines a concrete interface, runtime target, and validation criterion.
- E2SM implementation expectations are not implicit. Treat KPM v3, RC, MAC/RLC/PDCP monitor/control, rApp, and dApp SDK work as separate future tasks that require an explicit task plan.

---

## RFsim RedCap Runtime Source of Truth

- For simulator runtime validation, use `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/` as the primary scenario directory.
- Treat `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/docker-compose.yml` and its directly mounted config files as the runtime source of truth.
- For UE2 RedCap validation, start from the compose service `oai-nr-ue2` and its mounted config, currently `../../conf_files/nrue_recap/nrue2.uicc.yaml`.
- When a runtime fix requires config edits, modify the YAML/config files that are actually referenced by this compose path. Do not modify unrelated simulator XML/YAML files just because they contain similar names.
- XML scenarios or unused files that can affect future work must not be removed immediately. First report:
  - file path,
  - why it appears unused,
  - what references were checked,
  - expected impact of removal.
  Remove only after the user explicitly confirms.

---

## Gantt Chart Output

- This section applies only when the user asks for a Gantt chart or project visualization.
- When I ask for a project Gantt chart, prefer:
  - Markdown Mermaid syntax if the goal is documentation, or
  - a single self-contained HTML file with embedded CSS/JS (no build tools) if I explicitly ask for a “front-end Gantt page”.
- The source of truth for tasks and dependencies is the Markdown files under `./agent_doc/Project_management/` in the repo root.
- When generating a Gantt chart:
  - Parse milestones and tasks from the files in `./agent_doc/Project_management/`.
  - Use weeks as the default time unit.
  - Do not invent new tasks. If something is unclear:
    - ask the user which project we are focusing on now, and  
    - ask the user to refine or update the corresponding file under `./agent_doc/Project_management/`, then use that file as the task list.

---

## Build & Test Logs

- All CTest and build logs for this project should be stored under:
  - `test_log/compiler_logs/` for CTest output,
  - `test_log/build_logs/` for build output (if used later).
- When running tests or builds from within this repository, prefer commands that:
  - redirect output into a timestamped `.log` file under `test_log/compiler_logs/` or `test_log/build_logs/`,
  - for example:
    - `ctest --output-on-failure | tee test_log/compiler_logs/ctest_$(date +%F_%H-%M-%S).log`
- When analyzing test failures, you should:
  - use the filesystem MCP to list `test_log/compiler_logs/`,
  - open the most recent log file,
  - summarize failing tests and key error messages in Traditional Chinese.

## Mandatory Rebuild After C/C++ Changes

- After each atomic C or C++ source/header patch group, rebuild the affected OAI target before moving to the next task.
- For UE-side changes, run at least:
  - `cmake --build --preset default --target nr-uesoftmodem`
- For gNB-side changes, run at least:
  - `cmake --build --preset default --target nr-softmodem`
- For shared or cross-layer changes, build every affected side and the closest unit-test target.
- At the end of each implementation sub-task, run the closest corresponding unit test target and `ctest -R <test-name> --output-on-failure` when such a test exists.
- If there is no meaningful unit test for the touched path, state `[unit test N/A]` and use the nearest build or RFsim runtime validation instead.
- Clearly separate these statuses in reports:
  - [source build PASS/FAIL]
  - [unit test PASS/FAIL]
  - [container image rebuilt or not]
  - [RFsim UE/gNB/CN runtime PASS/FAIL]

---

## RedCap PHY Work Order

- This section applies only when modifying PHY-side code under `openair1/` or PHY-related radio/config behavior.
- When modifying PHY for RedCap, always follow this order:
  1) Locate the relevant existing implementation in `openair1/` and related configs.  
  2) Cross-check the intended change against `spec/redcap_3gpp/spec.md` and TS 38.306 / 38.101-1.  
  3) Propose the change in prose first (in Traditional Chinese), including:
     - target files and functions,
     - expected behavior,
     - how it impacts mMTC / RedCap constraints (20 MHz, 1Rx, half-duplex).
  4) Only then edit code in small patches (one function or one parameter group at a time), and plan tests.



## The Chat Content Store

### Purpose

At the end of every completed implementation sub-task, milestone validation, or runtime validation, the agent must record a structured progress
snapshot in Markdown and persist it to `test_logs/work_daily/`.
This log serves as the single source of truth for session continuity.

---

### Write Rules (Triggered After Completed Implementation / Validation Work)

1. Check whether `test_logs/work_daily/` exists.
   - If it does NOT exist, create it before writing any log:
     ```bash
     mkdir -p test_logs/work_daily
     ```

2. Write a new Markdown file named with an ISO-8601 timestamp:
   - `test_logs/work_daily/YYYY-MM-DD_HH-MM-SS_<task-slug>.md`
   - Example: `test_logs/work_daily/2026-04-09_20-30-00_mac-redcap-drx.md`

3. Each log file must follow this structure:
```markdown


# Work Daily Log
## Session Metadata
- Date: YYYY-MM-DD HH:MM
- Agent Session ID: <auto or N/A>
- Task Slug: <short identifier>
- Project Path: agent_doc/Project_management/projects/redcap_mmtc_priority_execution_v1/project_plan.md

## Milestone & Sub-task Reference
- Milestone: <milestone name from project_plan.md / Simluation_v2.md>
- Sub-task: <sub-task name>
- Status: [COMPLETED / IN-PROGRESS / BLOCKED]

## What Was Done
- [Bullet list of code changes, files modified, and functions touched]

## 3GPP Spec Clauses Referenced
- TS XX.XXX Section X.X.X — brief note on relevance

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| ...       | ...         | ...      | ...   |


## Known Issues / Blockers
- [List any unresolved issues or questions for the next session]

## Next Step
- [The immediate next sub-task to be tackled]
```

---

### Read Rules (Triggered at the Start of Every New Session)

1. At the very beginning of each new chat window, before taking any action:
- Check if `test_logs/work_daily/` exists.
- If it exists, list all `.md` files sorted by filename (descending).
- Read the **most recent** log file in full.

2. After reading, output a session resume summary in Traditional Chinese:
▶ 上次進度摘要
◉ 最後完成子任務：<task-slug>
◉ 當前里程碑：<milestone>
◉ 待處理事項：<next step from log>
◉ 已知問題：<blockers if any>

3. Then ask: "是否從上次進度繼續？" before proceeding with any new work.

---

### Additional Constraints
- Never overwrite an existing log file; always create a new timestamped file.
- If `agent_doc/Project_management/projects/redcap_mmtc_priority_execution_v1/project_plan.md` is updated, append a note to the current daily log
indicating which milestone or sub-task was revised.
- Log files are append-only records; do NOT delete them without explicit user confirmation.
