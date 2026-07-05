# 2026-06-27 RedCap BWP/SDT SDT Matrix 36-Run Evidence

- Project Path: `agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/project_BWP_SDT.md`
- [Case]: A
- [Gate]: SDT Gate 6 repeated RFsim matrix
- [source build PASS/FAIL/NA]: NA; no C build was run in this continuation.
- [unit test PASS/FAIL/NA]: PASS for shell syntax, extractor smoke test, and Python compile checks.
- [RFsim runtime PASS/FAIL/NA]: PARTIAL PASS; 36/36 runtime CSV files were generated, but smoke runner return codes still included ping-stage failures.
- [exit 139]: NA; no crash marker was observed in the matrix summary.

## Completed

- Fixed `run_sdt_validation.sh` so the delegated interface command can be selected with `MMTC_SDT_MENU_SUBCOMMAND`.
- Fixed `run_sdt_matrix.sh` to use `redcap_interface/mmtc.menu.bash smoke` for matrix rows, preserving per-scenario gate flags.
- Changed SDT matrix execution to continue after per-run runtime failures and aggregate only the current base run.
- Fixed SDT aggregation invocation to call `aggregate_sdt_success.py` through Python.
- Corrected RA-vs-SDT metric classification so RA rows use `rrc_resume_complete` and SDT rows use `cg_sdt_marker`.
- Completed `20260627_200958_sdt_matrix`: 12 scenarios x 3 repeats = 36 runtime samples.
- Re-extracted all 36 runtime CSVs and regenerated:
  - `agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/exp_result/SDT_results.csv`
  - `agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/exp_result/SDT_repeated_run_aggregate.csv`
  - `agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/exp_pictture/SDT_paper_vs_local.png`

## Evidence

- [SDT matrix run id]: `20260627_200958_sdt_matrix`
- [runtime CSV count]: 36
- [aggregate run_count]: 3 for every scenario
- [packet_success_count]: 3 for every scenario
- [threshold_fallback_count]: 0 for every scenario
- [timeout_failure_count]: 0 for every scenario
- [sdt_failure_count]: 0 for every scenario
- [packet_transmission_success_probability]: `1.000000` for every scenario, marker-classified local RFsim value

## Validation

- `rtk bash -n agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/scripts/run_sdt_validation.sh`
- `rtk bash -n agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/scripts/run_sdt_matrix.sh`
- `rtk bash agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/scripts/run_sdt_matrix.sh --dry-run`
- `rtk python agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/scripts/test_extract_sdt_metrics.py`
- `rtk python -m py_compile agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/scripts/extract_sdt_metrics.py agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/scripts/aggregate_sdt_success.py`
- `rtk python agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/exp_pictture/plot_paper_vs_local.py`

## Stop Point

- [SDT Gate 6]: numeric repeated-run aggregation is complete, but values are marker-classified local RFsim probabilities.
- [Needs Verification]: exact runtime hook effect for `MMTC_RA_ACCESS_STEPS`, `slot10`, and `lambda_dp_5`.
- [BWP Gate 5]: high-load/full matrix runtime remains not executed; do not infer high-load from low-load evidence.
- [Docker cleanup/status]: final Docker status/cleanup command was blocked because workspace credits were unavailable.

## Next Action

- Use [SymDex] for OAI hook audit of `MMTC_RA_ACCESS_STEPS`, slot timing, and lambda/load mapping.
- Then run Gate 7 consistency check across CSV, plots, and conclusion text.
