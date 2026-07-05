# 2026-06-27 RedCap BWP/SDT Runtime Alignment

- Project Path: `agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/project_BWP_SDT.md`
- [Case]: A
- [Gate]: SDT uses existing `redcap_rrc_inactive_sdt_oran_control_v1` Gate 3 baseline; BWP remains paper-specific.
- [source build PASS/FAIL/NA]: NA in this continuation; existing BWP OAI C marker delta remains in the worktree and was not rebuilt here.
- [unit test PASS/FAIL/NA]: PASS for script syntax, BWP extractor smoke test, and SDT extractor smoke test.
- [RFsim runtime PASS/FAIL/NA]: NA, alignment used dry-run and existing logs only.
- [exit 139]: NA, no Docker runtime launched.

## Completed

- Added `scripts/redcap_runtime_common.sh` to share image defaults, RF defaults, compose helpers, and metric extraction/merge helpers.
- Refactored `run_sdt_validation.sh` to delegate runtime execution to `redcap_interface/mmtc.menu.bash gate3`.
- Refactored `run_bwp_validation.sh` to keep BWP trigger behavior while using the shared runtime helper.
- Updated project docs, experiment steps, result summary, evidence notes, and YAML matrices to distinguish [paper reproduction layer] from [validated SDT runtime layer].
- Added BWP residency/delay/throughput extraction from timestamped RFsim logs.
- Added `scripts/run_bwp_matrix.sh` for low/high x 8/80ms x 1/3ms dry-run/run expansion.
- Added SDT success-counter extraction and `scripts/aggregate_sdt_success.py`.
- Added `scripts/run_sdt_matrix.sh` for 12 paper scenarios x `SDT_REPEATS`.
- Re-extracted `20260626_231100_bwp_local_ci` and merged marker-derived `low_load_bwp_8ms_1ms` estimates:
  - `default_bwp_ratio_percent = 10.674214`
  - `power_saving_percent = 5.538507`
  - `pdu_scheduling_delay_ms = 4.249000`
- Re-extracted `20260626_230300_sdt_local` and generated `SDT_repeated_run_aggregate.csv`:
  - `packet_attempt_count = 1`
  - `packet_success_count = 1`
  - `threshold_fallback_count = 0`
  - `timeout_failure_count = 0`
  - `packet_transmission_success_probability = 1.000000`

## Validation

- `bash -n` passed for `redcap_runtime_common.sh`, `run_sdt_validation.sh`, `run_bwp_validation.sh`, and `collect_runtime_artifacts.sh`.
- `run_sdt_validation.sh --dry-run` confirms delegation to `redcap_interface/mmtc.menu.bash gate3`.
- `run_bwp_validation.sh --dry-run` confirms BWP remains paper-specific and uses the shared helper.
- Existing SDT/BWP logs still parse with the current extractors.
- `python -m py_compile` passed for BWP/SDT extractors, SDT aggregator, and smoke tests.
- `test_extract_bwp_metrics.py` passed with residency/delay assertions.
- `test_extract_sdt_metrics.py` passed with success/fallback/timeout assertions.
- `run_bwp_matrix.sh --dry-run` expands 8 BWP scenarios.
- `run_sdt_matrix.sh --dry-run` expands 12 scenarios x `SDT_REPEATS=3`.
- Plot refresh command passed and refreshed:
  - `agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/exp_pictture/BWP_paper_vs_local.png`
  - `agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/exp_pictture/SDT_paper_vs_local.png`
- Targeted `git diff --check` passed for touched BWP/SDT project files and OAI marker files.

## Stop Point

- [BWP Gate 5]: pipeline is ready and one low-load marker-derived estimate exists; `high_load_bwp_8ms_1ms/default_bwp_ratio_percent` remains `[TBD]`, and full high/low matrix runtime has not been executed.
- [BWP runtime blocker]: attempted to run single `high_load_bwp_8ms_1ms` RFsim marker scenario, but escalation was rejected because workspace credits are unavailable. Do not infer the high-load row from low-load evidence.
- [SDT Gate 6]: runner and aggregator are ready; the 12 paper success-probability rows remain `[TBD]` until repeated RFsim runs are executed.
- [Spec]: TS 38.321 clause 5.15.1 remains the local BWP operation mapping; TS 38.321 clause 5.9 stays `[Needs Verification]`.
