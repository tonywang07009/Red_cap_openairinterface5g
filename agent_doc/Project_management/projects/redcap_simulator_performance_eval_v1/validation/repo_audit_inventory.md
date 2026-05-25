# Repo Audit Inventory

## Status
- [Superseded By 2026-05-25 RedCap Library Cleanup]
- Audit Date: 2026-05-21
- Scope: top-level repo folders, generated artifacts, stale logs, duplicate manuals, backup/config candidates.

## Superseding Cleanup Note
- On 2026-05-25, the user approved cleanup of `test_log/build_logs`, `test_log/compiler_logs`, `test_log/report`, `test_log/runtime_artifacts`, `test_log/runtime_bins`, `test_log/runtime_configs`, and `test_log/runtime_libs`.
- High-value reusable artifacts were promoted into `redcap_library/`.
- Low-value duplicate/timestamped/generated artifacts in the approved target folders were removed.
- For current lookup, use `redcap_library/README.md` before scanning `test_log/`.
- On 2026-05-25, the user also approved consolidating documentation under `redcap_doc/` and keeping only `test_log/` as the temporary log root.

## Rule
- Inventory only.
- Do not delete, move, or rewrite files without explicit user approval.

## Audit Methods
- Symdex repository index:
  - Repo: `home-tonywang-oai-red_cap_openairinterface5g`
  - Indexed files: `15735`
  - Indexed LOC: `5132035`
  - Index state: `[stale]`; watcher inactive.
- Tree inventory:
  - `tree -a -L 2 .`
  - Displayed summary: `147 directories`, `270 files`.
- Size inventory:
  - `find . -maxdepth 1 -mindepth 1 -type d -exec du -sh {} +`
  - `find test_log -maxdepth 1 -mindepth 1 -exec du -sh {} +`
  - `find cmake_targets -maxdepth 2 -mindepth 1 -type d -exec du -sh {} +`
- Candidate discovery:
  - `find . -type d -name __pycache__`
  - `find . -type f` for `*.pyc`, `*.bak`, `*.bak.*`, `*.backup`, `*.tmp`, `*.orig`, and `*~`.
  - `find . -type f -size +50M`
  - `find . -type d -empty`
- Reference checks:
  - `rg` checks excluding `cmake_targets/`, `test_log/`, and `.git/`.
  - Checked: `paper_test`, `usermaun`, `Simluation_mod`, `Simluation_v2`, `docker-compose.mmtc.yml.backup`, `.env.bak`, `test_log/work_daily`, legacy `test_logs/work_daily`, `function_index.json`, and Gantt/XML display remnants.

## Repo Scale Summary
| Area | Observation | Classification | Notes |
|---|---:|---|---|
| `test_log/` | `5.3G` | [Generated Artifact] | Runtime, compiler, build, and evidence logs. |
| `cmake_targets/` | `3.7G` | [Generated Artifact] | Build trees, binaries, generated CMake files, and runtime scenario logs. |
| `.git/` | `961M` | [Keep] | Git object store; not a cleanup target in this audit. |
| `redcap_doc/specs/` | `256M` | [Keep] | Local specification references. |
| `openair2/` | `79M` | [Keep] | Core OAI source. |
| `openair1/` | `23M` | [Keep + Generated Artifact Candidate] | Source tree also contains local CMake artifacts. |
| `redcap_doc/evaluation_papers/` | `15M` | [Keep] | Formal paper source for this project. |
| `agent_doc/` | `2.9M` | [Keep] | Active project management and experiment notes. |
| `test_log/work_daily/` | temporary | [Generated / Temporary] | Only process logs with successful outcomes should be written here. |

## Top-Level Folder Inventory
| Path | Size | Classification | Recommendation |
|---|---:|---|---|
| `.agents/` | `0` | [Needs Owner Review] | Empty hidden folder; do not delete without owner approval. |
| `.github/` | `12K` | [Keep] | GitHub prompt/config material. |
| `.git/` | `961M` | [Keep] | Git metadata. |
| `agent_doc/` | `2.9M` | [Keep] | Active management docs and experiment skill path. |
| `charts/` | `108K` | [Keep] | Existing project charts. |
| `redcap_doc/checklists/` | `32K` | [Keep] | Milestone checklist material. |
| `ci-scripts/` | `5.2M` | [Keep + Candidate Artifacts] | Active runtime scripts; contains pycache and backup candidates. |
| `cmake_targets/` | `3.7G` | [Generated Artifact] | Build output; clean only after owner approves rebuild cost. |
| `common/` | `5.8M` | [Keep] | Shared OAI utilities. |
| `crashdumps/` | `4.0K` | [Generated Artifact] | Empty runtime crashdump target; keep unless cleanup policy removes empty generated dirs. |
| `doc/` | `16M` | [Keep] | OAI and RedCap docs. |
| `docker/` | `268K` | [Keep] | Docker image definitions. |
| `redcap_doc/evaluation_papers/` | `15M` | [Keep] | Project paper input. |
| `executables/` | `684K` | [Keep] | Softmodem entry points. |
| `nfapi/` | `3.5M` | [Keep] | nFAPI source. |
| `openair1/` | `23M` | [Keep + Candidate Artifacts] | PHY source plus local CMake artifacts. |
| `openair2/` | `79M` | [Keep] | MAC/RLC/PDCP/RRC/E2AP source. |
| `openair3/` | `9.9M` | [Keep] | NGAP/GTP/NAS/control-plane source. |
| `openshift/` | `112K` | [Keep] | Deployment manifests. |
| `paper_test/` | `4.0K` | [Cleaned] | Removed in cleanup batch 1 after owner approval. |
| `radio/` | `2.0M` | [Keep] | RF back ends. |
| `scripts/` | `56K` | [Keep + Candidate Artifacts] | Utility scripts plus generated pycache/output. |
| `redcap_doc/specs/` | `256M` | [Keep] | Local spec references. |
| `targets/` | `6.4M` | [Keep] | OAI target assets. |
| `test_log/` | `5.3G` | [Generated Artifact] | Heavy runtime evidence store. |
| `test_logs/` | `856K` before cleanup | [Cleaned] | Removed after switching to `test_log/` as the single temporary log root. |
| `tests/` | `56K` | [Keep] | Unit/integration test definitions. |
| `tools/` | `164K` | [Keep] | Developer tools. |
| `redcap_doc/manuals/` | `8.0K` | [Keep] | Standardized home for reusable RedCap operator manuals; replaces typo-like `usermaun/`. |

## Heavy Artifact Inventory
| Path | Size / Count | Classification | Recommendation |
|---|---:|---|---|
| `test_log/compiler_logs/` | `4.8G`, `34063` files before cleanup | [Generated Artifact] | Superseded: promote final raw evidence to `redcap_library/library_runtime_probe/`, then clean generated logs after approval. |
| `test_log/runtime_artifacts/` | `471M`, `1629` files before cleanup | [Generated Artifact] | Superseded: preserve summaries in `redcap_library/library_reports_summary/`, then clean raw runtime folders after approval. |
| `test_log/build_logs/` | `44M`, `185` files before cleanup | [Generated Artifact] | Superseded: promote final build evidence to `redcap_library/library_build_evidence/`, then clean old build logs after approval. |
| `test_log/report/` | `2.2M` before cleanup | [Generated Artifact] | Superseded: promote high-value reports to `redcap_library/library_reports_summary/`. |
| `test_log/runtime_configs/` | `1008K` before cleanup | [Generated Artifact] | Superseded: promote final reusable configs to `redcap_library/library_gnb_config/` and `library_cn5g/`. |
| `test_log/runtime_bins/` | `6.7M` before cleanup | [Generated Artifact] | Superseded: generated xApp binaries can be rebuilt and were not retained as source-of-truth. |
| `cmake_targets/ran_build/` | `3.5G` | [Generated Artifact] | Can be regenerated, but cleaning requires rebuild cost acceptance. |
| `cmake_targets/log/` | `60M` | [Generated Artifact] | Active XML scenario evidence; keep unless archived with validation context. |
| `cmake_targets/swig/` | `165M` | [Generated Artifact / External Dependency] | Do not remove unless dependency regeneration is acceptable. |

## Large File Inventory
| Path | Size | Classification | Recommendation |
|---|---:|---|---|
| `cmake_targets/ran_build/build_test/nr-softmodem` | `192203712` bytes | [Generated Artifact] | Keep until rebuild policy is approved. |
| `cmake_targets/ran_build/build/nr-softmodem` | `124432984` bytes | [Generated Artifact] | Keep until rebuild policy is approved. |
| `cmake_targets/ran_build/build_test/openair2/RRC/LTE/MESSAGES/libasn1_lte_rrc.a` | `95093966` bytes | [Generated Artifact] | Keep until rebuild policy is approved. |
| `cmake_targets/ran_build/build_test/build.ninja` | `84649441` bytes | [Generated Artifact] | Build system output; clean with build tree. |
| `cmake_targets/ran_build/build/build.ninja` | `82096434` bytes | [Generated Artifact] | Build system output; clean with build tree. |
| `.git/objects/pack/*.pack` | `320M+` each | [Keep] | Git object storage; not a cleanup target here. |
| `.git/modules/openair2/E2AP/flexric/objects/pack/*.pack` | `96M` | [Keep] | Submodule object storage. |

## Cleanup Candidate Inventory
| Path | Classification | Reason | References Checked | Expected Impact | Recommendation |
|---|---|---|---|---|---|
| `paper_test/` | [Cleaned] | Empty folder; formal project paper path is `redcap_doc/evaluation_papers/`. | `rg paper_test`; only `literature/paper_index.md` recorded it as an empty observed path. | Low; removing it only removes an empty legacy placeholder. | Deleted in cleanup batch 1; `paper_index.md` updated. |
| `test_logs/work_daily/` | [Cleaned] | Legacy process-log root with 207 old daily logs; current policy keeps only successful outcome logs under `test_log/work_daily/`. | `rg test_logs/work_daily`; active references updated to `test_log/work_daily/`. | Low after `redcap_library/` and project summaries captured reusable evidence. | Deleted in 2026-05-25 cleanup. |
| `test_log/compiler_logs/` | [Promoted + Cleaned] | `4.8G` and `34063` generated runtime/compiler files before cleanup. | Key Paper 07/runtime RCA logs were promoted to `redcap_library/`. Scripts still generate future logs here. | Low after promotion for approved batch. | Cleaned in 2026-05-25 cleanup; use `redcap_library/library_runtime_probe/` and `library_reports_summary/`. |
| `test_log/runtime_artifacts/` | [Promoted + Cleaned] | `471M` generated Docker/runtime evidence before cleanup. | Final M3/M5 results were promoted as summary reports. | Low after promotion for approved batch. | Cleaned in 2026-05-25 cleanup; use `redcap_library/library_reports_summary/`. |
| `test_log/build_logs/` | [Promoted + Cleaned] | `44M` generated build logs before cleanup. | Final 256QAM build/rebuild evidence was promoted. Scripts still generate future logs here. | Low after promotion for approved batch. | Cleaned in 2026-05-25 cleanup; use `redcap_library/library_build_evidence/`. |
| `cmake_targets/ran_build/` | [Generated Artifact] | `3.5G` build output, binaries, libraries, and CMake files. | Build commands write artifacts below `cmake_targets/ran_build/build*`. | High rebuild cost; deletion forces reconfigure/rebuild. | Cleanup only as a separate approved build-tree cleanup batch. |
| `cmake_targets/log/container_5g_flexric_rfsim_redcap.xml.d/` | [Archive Candidate] | `60M` XML scenario runtime logs. | Many daily logs and review docs cite this scenario log path. | High traceability impact if deleted. | Keep or archive with a manifest; do not delete blindly. |
| `scripts/__pycache__/` | [Cleaned] | Python bytecode cache, `2` `.pyc` files. | `find __pycache__`; no source references needed for bytecode. | Low; Python regenerates if scripts run. | Deleted in cleanup batch 1. |
| `ci-scripts/__pycache__/` | [Cleaned] | Python bytecode cache, `18` `.pyc` files. | `find __pycache__`; no source references needed for bytecode. | Low; Python regenerates if scripts run. | Deleted in cleanup batch 1. |
| `openair1/CMakeCache.txt` | [Cleaned] | Source-tree CMake artifact; canonical build output should be under `cmake_targets/ran_build/`. | `rg openair1/CMakeCache.txt`; no references. | Low; may affect only accidental in-tree CMake state. | Deleted in cleanup batch 1. |
| `openair1/CMakeFiles/` | [Cleaned] | Source-tree CMake artifact. | `find` found source-tree CMake folders outside `cmake_targets/`; no references. | Low; should be regenerated only by accidental in-tree CMake use. | Deleted in cleanup batch 1. |
| `openair1/PHY/CMakeFiles/` | [Cleaned] | Source-tree CMake artifact. | `find` found source-tree CMake folders outside `cmake_targets/`; no references. | Low. | Deleted in cleanup batch 1. |
| `openair1/PHY/TOOLS/CMakeFiles/` | [Cleaned] | Source-tree CMake artifact. | `find` found source-tree CMake folders outside `cmake_targets/`; no references. | Low. | Deleted in cleanup batch 1. |
| `openair1/PHY/nr_phy_common/CMakeFiles/` | [Cleaned] | Source-tree CMake artifact. | `find` found source-tree CMake folders outside `cmake_targets/`; no references. | Low. | Deleted in cleanup batch 1. |
| `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/.env.bak.2026-04-12_19-19-24` | [Cleaned] | Tiny `.env` backup. | `rg .env.bak`; no references. | Low if current `.env` is accepted. | Deleted in cleanup batch 1. |
| `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/.env.bak.2026-04-12_19-23-51` | [Cleaned] | Tiny `.env` backup. | `rg .env.bak`; no references. | Low if current `.env` is accepted. | Deleted in cleanup batch 1. |
| `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/.env.bak.2026-04-12_19-24-01` | [Cleaned] | Tiny `.env` backup. | `rg .env.bak`; no references. | Low if current `.env` is accepted. | Deleted in cleanup batch 1. |
| `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/docker-compose.mmtc.yml.backup` | [Archive Candidate] | Backup of original MMTC compose overlay. | Referenced only by `UPDATE_STATUS_REPORT.md` and `VOLUME_PATHS_UPDATE_SUMMARY.md`. | Medium; may be useful to understand April 14 compose rewrite. | Archive with status reports, or keep until compose history is stable. |
| `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/UPDATE_STATUS_REPORT.md` | [Archive Candidate] | One-time status report for compose path rewrite. | `rg UPDATE_STATUS_REPORT`; no active runtime reference found. | Low to medium; loss of historical explanation. | Move to project archive or keep until owner confirms it is no longer needed. |
| `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/VOLUME_PATHS_UPDATE_SUMMARY.md` | [Archive Candidate] | One-time summary for compose volume path rewrite. | Referenced by `UPDATE_STATUS_REPORT.md`. | Low to medium; loss of historical explanation. | Move to project archive or keep with backup until owner approval. |
| `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/.codex` | [Cleaned] | Zero-byte file in runtime YAML folder. | `rg .codex`; no references. | Low. | Deleted in cleanup batch 1. |
| `usermaun/系統化使用步驟.md` | [Moved] | Folder name was misspelled; content is useful system-use manual. | `rg usermaun|系統化使用步驟`; no active runtime reference. | Low after standardized path is documented. | Moved to `redcap_doc/manuals/redcap_mmtc_systematic_usage_steps.md` in 2026-05-25 cleanup. |
| `agent_doc/Project_management/Simluation_mod.Md` | [Archive Candidate] | Older short milestone plan; spelling differs from active project structure. | `rg Simluation_mod`; referenced by one old daily log as fallback plan. | Low to medium; may be historical planning context. | Archive or keep as historical note; do not delete without owner review. |
| `agent_doc/Project_management/Simluation_v2.md` | [Keep] | Baseline archive for RedCap mMTC execution project. | Multiple active docs and daily logs reference it; M7 explicitly says preserve it. | High if deleted. | Keep. |
| `scripts/output/function_index.json` | [Generated Artifact / Keep] | Generated by `scripts/gen_function_index.py`, but referenced by docs as placeholder input. | `rg function_index.json|scripts/output`; referenced by generator, doc skeleton, and reference doc. | Low if regenerated, but docs point to it. | Keep unless docs are updated to regenerate on demand. |

## Gantt And XML Display Check
- `agent_doc/` contains no `*gantt*` files and no XML display files.
- Historical daily logs still reference an old `redcap_mmtc_gantt.html`, but the file is not present.
- Active XML scenario files under `ci-scripts/xml_files/` are runtime validation assets, not Gantt display artifacts.

## Cleanup Batch 1 - 2026-05-21
- Trigger: owner approved cleanup after P6 inventory review.
- Removed low-risk generated or empty candidates:
  - `scripts/__pycache__/`
  - `ci-scripts/__pycache__/`
  - `openair1/CMakeCache.txt`
  - `openair1/CMakeFiles/`
  - `openair1/PHY/CMakeFiles/`
  - `openair1/PHY/TOOLS/CMakeFiles/`
  - `openair1/PHY/nr_phy_common/CMakeFiles/`
  - `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/.env.bak.2026-04-12_19-19-24`
  - `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/.env.bak.2026-04-12_19-23-51`
  - `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/.env.bak.2026-04-12_19-24-01`
  - `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/.codex`
  - `paper_test/`
- Follow-up doc update:
  - `literature/paper_index.md` now records `paper_test/` as removed.
- Verification:
  - `find` checks confirmed the removed paths are absent.

## Cleanup Boundary
- 2026-05-25 approved cleanup deleted generated files under:
  - `test_log/compiler_logs/`
  - `test_log/runtime_artifacts/`
  - `test_log/build_logs/`
  - `test_log/report/`
  - `test_log/runtime_configs/`
  - `test_log/runtime_bins/`
  - `test_log/runtime_libs/`
- Reusable evidence was promoted first into `redcap_library/`.
- Still out of scope without a separate owner-approved batch:
  - `cmake_targets/ran_build/`
  - `cmake_targets/log/container_5g_flexric_rfsim_redcap.xml.d/`
