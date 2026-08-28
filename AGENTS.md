You are Codex, based on GPT-5.6. You are running as a coding agent in
the Codex CLI on a user's computer.

# Repository Guidelines

## Project Structure & Module Organization

Core RAN code is split by layer: `openair1/` for PHY, `openair2/` for
MAC/RLC/PDCP/RRC and E2AP, and `openair3/` for NGAP/GTP/NAS and related
control-plane code. Shared utilities live in `common/`, top-level
softmodem entry points are in `executables/`, and radio back ends are
in `radio/` (`USRP/`, `rfsimulator/`, `fhi_72/`, etc.). Build helpers
and generated build trees live under `cmake_targets/`. Project
documentation is in `doc/`; CI orchestration and test assets are in
`ci-scripts/`.

## OpenSpec Planning Trigger

Use the repository-local OpenSpec skill matching the request phase when the
request:
- Mentions planning, proposals, spec, change, or plan.
- Introduces new capabilities, breaking changes, architecture shifts,
  or large performance/scheduling work (e.g. DRX, multi-Tag scheduling).
- Is ambiguous and needs an authoritative spec before coding.

If `openspec/AGENTS.md` exists, read it before the selected skill. Otherwise
the selected repository-local OpenSpec skill is authoritative. Do not invent
instructions for a missing OpenSpec guidance file.

## No-New-File Policy (RedCap modifications)

Before creating any file:
1. Search `openair1/`, `openair2/`, `openair3/` for the module that
   already owns this behavior. Use `symdex` first.
2. If an owning module exists, edit it in place. Do not create a
   parallel implementation elsewhere.
3. New files are permitted only when no existing module owns the
   behavior, and only inside the correct `openair{1,2,3}` subdirectory
   matching its layer (PHY / MAC-RLC-PDCP-RRC / NGAP-GTP-NAS).
4. `redcap_interface/` and `redcap_library/` are staging and reference
   only. Once a change is verified and merged, it must live in
   `openair1/2/3`, not in these directories.
5. This policy is effective immediately for all modules, starting
   with DRX-related changes.

## File Query Workflow

This section is the single source of truth for tool selection. Skills link to
it and do not restate a competing route.

| Need | Required first tool | Allowed fallback |
| --- | --- | --- |
| Source symbols, definitions, callers, callees, or ownership | Symdex MCP | Local `.symdex` CLI only when MCP is not indexed or cannot perform the lookup |
| Git status, diff, log, blame, branch, commit lookup | rtk | Git CLI only when rtk cannot perform the operation |
| Ordinary source reads, Markdown, PDF, config, logs, generated artifacts | Direct file read | Use a narrower read when the file is large |

- State a fallback reason only for a symbol/caller or Git lookup.
- Do not use `rg` as a substitute for a required Symdex symbol/caller lookup.
- Do not infer source ownership from filenames when a symbol or call relationship is required.

## Model Switch Gate

- The user selects the model and effort. Require a switch only when the user
  explicitly requests a cost or quality boundary.
- Do not infer a model switch or start a fallback subagent automatically.
- Record the active model/effort when it is material to a TDD or implementation
  decision; mark unavailable metadata **[Needs Verification]**.

## Build, Test, and Development Commands

Prefer the preset-based CMake flow (native JSON via `CMakePresets.json`,
do not re-wrap):

```bash
cmake --preset default
cmake --build --preset default
cmake --preset tests
cmake --build --preset tests
cd cmake_targets/ran_build/build_test && ctest --output-on-failure
```

For reusable, externally invoked, or side-effecting `build_oai` wrappers, look
up the semantic target in `redcap_library/bash_tool/registry.json` before
running manually. One-off diagnostics and narrow unit-test commands may run
directly.

Artifacts are written below `cmake_targets/ran_build/build*`.

## Bash Tool Registry (repetitive test/build workflows)

- Location: `redcap_library/bash_tool/registry.json`
- Scripts: `redcap_library/bash_tool/scripts/`
- Required registry entries declare:
  - `description`
  - `script_path`
  - `input` (parameters the script expects)
  - `output` (log_path, exit_code, status_field written to
    `task_log/tasks.json`)
  - `side_effects` (whether it writes source, only logs, or is
    read-only — required for safe parallel scheduling)
- Register only reusable, externally invoked, or side-effecting scripts.
  One-off diagnostics and narrow verification commands need only retain their
  output log.

## Skill Composition Layer

- Location: `redcap_library/skills/`
- Reusable skills compose Bash Tool Registry entries. A skill may directly run
  a narrow read-only diagnostic or unit verification when no reusable command
  is needed.
- Every skill declares in frontmatter:
  - `input`: what the caller must provide
  - `output`: what the skill returns (report path, pass/fail,
    next_action)
  - `tool_dependencies`: which `registry.json` entries it calls
- Skills reference the OpenSpec change they were created to serve, if
  applicable.

## Long-Running Command Protocol (Bash + Task Manifest)

Track Docker operations, live E2/control transactions, and very long builds or
batches through a task manifest. Ordinary CMake/CTest unit runs keep their
timestamped log without a manifest entry.

For a tracked operation, before running, write or update `task_log/tasks.json`:
   ```json
   {
     "task_id": "drx-onduration-boundary-fix",
     "status": "pending",
     "command": "cmake --build --preset tests",
     "log_path": "test_log/build_logs/<timestamp>.log",
     "started_at": null,
     "completed_at": null,
     "next_action": "update_doc"
   }
   ```
2. Run the command, redirecting output to the declared `log_path`.
3. Set `status` to `running`, then `passed` or `failed` on exit code.
4. While `status` is `running`, proceed with documentation for an
   already-completed sub-task instead of waiting idle.
5. Never mark `status: passed` without reading the log file content.

## Coding Style & Naming Conventions

Follow the root `.clang-format` and `doc/code-style-contrib.md`. Use
2-space indentation, no tabs, keep C/C++ lines within 132 columns.
Function opening braces go on the next line; control-flow braces stay
on the same line. Prefer strong OAI types, named constants over magic
numbers, `const` for input pointers, and `AssertFatal()` / `DevAssert()`
for invariants. Test binaries and helpers use descriptive snake_case
names such as `test_nr_common` or `nr-softmodem`.

## RedCap Spec-Driven Change Loop

Any modification to DRX, RRC, MAC scheduling, or PHY resource
allocation follows this loop before code is written:

1. Query — locate the governing clause under
   `redcap_doc/specs/redcap_3gpp/` (e.g. TS 38.331, TS 38.321). Mark
   `[Needs Verification]` if the clause is ambiguous or absent.
2. Design — state the intended behavior change, citing the clause.
   If this is a new capability or architecture shift, route through
   the OpenSpec Planning Trigger above first.
3. Build — implement inside the existing `openair1/2/3` module per
   the No-New-File Policy above.
4. Test — extend the nearest existing `tests/` unit test.
5. Verify — confirm output against the clause's stated behavior, not
   just against compilation success.
6. Fix — on failure, return to step 1, not step 3.

## Testing Guidelines

Enable tests with `cmake --preset tests` or `-DENABLE_TESTS=ON`. Unit
tests are declared in nearby `tests/` directories and registered with
CTest; common names start with `test_` or `<module>_test`. Add or
update the closest module test when changing shared logic, protocol
encoding, or PHY utilities. Validate the affected `physim` or RF
simulator target before review.

### RedCap-Specific Boundary Cases

When modifying On Duration, DRX timer, or multi-Tag scheduling logic,
explicitly test:
- On Duration window edges: slot N-1, N, N+1.
- DRX timer at min/max configured cycle values (TS 38.331).
- Simultaneous Tag arrival at the same scheduling window boundary.
- Timer expiry coinciding with a paging occasion.

## Documentation Style

Match `doc/BUILD.md` and `doc/code-style-contrib.md` conventions:
- Imperative, terse sentences. No quality adjectives.
- Lead with the command or fact, not with framing sentences.
- Code blocks over prose whenever a command or config is referenced.
- No emoji, no decorative headers.
- Every claim about behavior cites the source file, clause, or module.

## Commit & Pull Request Guidelines

Reference only unless explicitly asked for commit or MR preparation.
Target `develop`. Keep branch history linear; rebase instead of
merging. Each commit is a small logical change, compiles on its own,
and explains why the change is correct. Merge requests go to Eurecom
GitLab, require the proper CI label (`~documentation`, `~BUILD-ONLY`,
`~4G-LTE`, `~5G-NR`), and include scope, validation performed, and any
config or test impact.

---

## 3GPP Specs Available Locally

- Local RedCap and 3GPP references: `redcap_doc/specs/redcap_3gpp/`.
- Primary RedCap behavior notes:
  - `redcap_doc/specs/redcap_3gpp/spec.md`
  - `redcap_doc/specs/redcap_3gpp/redcap5g_spec.md`
- MinerU Markdown cache: `redcap_doc/mineru_markdown/scan_manifest.md`.
- `@spec-38.331` means: look under `redcap_doc/specs/redcap_3gpp/` for
  the local TS 38.331 reference.

## Project Router

- Project management root: `agent_doc/Project_management/`.
- Source-backed research and simulator decision wiki:
  `agent_doc/Project_management/redcap_research_wiki/`.
- Repository-owned CN5G deployment infrastructure: `oai-cn5g/`.
- RedCap operator interface (staging only, see No-New-File Policy):
  `redcap_interface/`.
- Curated reusable artifacts, bash tool registry, and skills (staging
  layer): `redcap_library/`.
- Stable RedCap docs: `redcap_doc/`.
- RedCap L1-L3 function lookup:
  `redcap_doc/specs/function_reference/redcap_l1_l3_function_lookup.md`.
- OpenSpec proposals and specs: `openspec/` (see OpenSpec Planning
  Trigger above).

## Initial RedCap Project Menu

At the start of a new RedCap project discussion, if no mode is
selected, ask which entry the user wants:
1. `進入專案`
2. `開啟教學`
3. `函式介紹與查詢`

If the user directly asks for a concrete task, do the task instead of
forcing the menu.

## Active Project Entries

| Project | Plan | Project Rules |
|---|---|---|
| RedCap mMTC execution | `agent_doc/Project_management/projects/redcap_mmtc_priority_execution_v1/project_plan.md` | `.../agent_rules.md` |
| RedCap simulator performance evaluation | `agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/project_plan.md` | `.../agent_rules.md` |
| RedCap O-RAN SDK workflow 3.0 | `agent_doc/Project_management/projects/redcap_oran_sdk_workflow_v3/project_plan.md` | `.../agent_rules.md` |

## Build And Test Logs

- CTest logs: `test_log/compiler_logs/`.
- Build logs: `test_log/build_logs/`.
- Use timestamped log files.
- Summarize test failures in Traditional Chinese, from the most
  recent relevant log.
- Reusable final configs/reports promoted from logs live under
  `redcap_library/`; read `redcap_library/README.md` first.
