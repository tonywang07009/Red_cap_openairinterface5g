# Work Daily Log
## Session Metadata
- Date: 2026-04-10 12:45
- Agent Session ID: N/A
- Task Slug: redcap-m3-runtime-matrix-prep

## Milestone & Sub-task Reference
- Milestone: Milestone 3: BWP & CORESET#0
- Sub-task: Case A / Case B runtime harness and local sandbox check
- Status: [COMPLETED]

## What Was Done
- Added `ci-scripts/redcap_prepare_runtime_config.py` to generate Case A / Case B gNB YAML variants from the RedCap base config.
- Added `ci-scripts/redcap_runtime_case_matrix.sh` to run `run_locally.sh` twice, once for `[case-a]` and once for `[case-b]`.
- Extended `ci-scripts/redcap_runtime_host_validation.sh` and `ci-scripts/redcap_runtime_summary.py` with `[expected mode]` and `[gNB config]` inputs.
- Updated `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/docker-compose.yml` to accept `GNB_REDCAP_CONFIG` via compose env substitution.
- Added explicit gNB runtime markers in `openair2/LAYER2/NR_MAC_gNB/nr_radio_config.c` for:
  - `RedCap CORESET#0 Case A type0 CSS`
  - `RedCap CORESET#0 Case B edge-aligned PRB allocation`
- Updated `agent_doc/Project_management/Simluation_v2.md` to record that M3 runtime is prepared locally but still blocked by Docker access in the current sandbox.

## 3GPP Spec Clauses Referenced
- TS 38.306 Section 4.2.21.1 — RedCap UE bandwidth and reduced-capability operating assumptions for FR1.
- TS 38.331 Section 5.2.2.4.2 — SIB1 scheduling/configuration context used for RedCap common information.
- TS 38.331 Section 5.6.1.3 — RedCap-specific common configuration usage in system information.

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| `bash -n ci-scripts/redcap_runtime_host_validation.sh ci-scripts/redcap_runtime_case_matrix.sh` | Pass | N/A | Shell syntax check completed |
| `python3 -m py_compile ci-scripts/redcap_runtime_summary.py ci-scripts/redcap_prepare_runtime_config.py` | Pass | N/A | Python helpers validated |
| `cmake --build --preset tests --target nr-softmodem test_nr_redcap_coreset0` | Pass | Existing M3 unit coverage | Log: `test_log/build_logs/redcap_m3_runtime_build_2026-04-10_12-36-09.log` |
| `ctest -R 'test_nr_redcap_coreset0|test_nr_frame_params' --output-on-failure` | Pass | Existing M3 unit coverage | Log: `test_log/compiler_logs/redcap_m3_runtime_ctest_2026-04-10_12-36-09.log` |
| `ci-scripts/redcap_runtime_case_matrix.sh` | Fail | Runtime path exercised to Docker gate | Blocked immediately by `Docker access is required to run CI scenarios locally`; logs: `test_log/compiler_logs/redcap_runtime_matrix_2026-04-10_12-37-16.log`, summaries: `test_log/report/redcap_runtime_host_summary_case-a_2026-04-10_12-37-16.md`, `test_log/report/redcap_runtime_host_summary_case-b_2026-04-10_12-37-16.md` |

## Known Issues / Blockers
- Current sandbox cannot access Docker, so true `[rfsimulation]`, `[PDCCH decode]`, and `[edge-only PRB allocation]` evidence still require a host with Docker socket access.
- The M3 runtime close-out is code-complete locally but not evidence-complete until the host rerun succeeds.

## Next Step
- Implement Milestone 4 `[SDT / RRC_INACTIVE]` minimal scheduler FSM and unit tests, then return to host runtime evidence collection when Docker access is available.
