# 2026-06-26 RedCap BWP/SDT Validation Runtime Handoff

## Result

- [Project]: `agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/`
- [SDT runtime]: `20260626_230300_sdt_local_sdt`
  - `oai-gnb:latest` / `oai-nr-ue:latest`
  - 15 runtime rows merged into `exp_result/SDT_results.csv`
  - markers: `rrc_inactive_marker_seen=1`, `configured_grant_marker_seen=1`, `cg_sdt_marker_seen=1`
  - resume markers: `RRCResumeRequest=0`, `RRCResumeComplete=0`
- [BWP runtime]: `20260626_231100_bwp_local_ci_bwp`
  - `oai-gnb:latest` / `oai-nr-ue:latest`
  - 21 runtime rows merged into `exp_result/BWP_results.csv`
  - markers: `bwp_gnb_reconfiguration_count=1`, `bwp_gnb_reconfiguration_last_new_bwp_id=0`, `bwp_ue_ra_operation_count=2`
  - `bwp_gnb_interrupt_count=0`, `bwp_inactivity_timer_gap_seen=1`

## Implementation Notes

- Added BWP instrumentation in:
  - `openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_primitives.c`
  - `openair2/LAYER2/NR_MAC_UE/nr_ra_procedures.c`
- Added runtime collection/merge flow:
  - `scripts/collect_runtime_artifacts.sh`
  - `scripts/merge_runtime_metrics.py`
  - BWP/SDT wrappers now collect logs and merge CSV rows.
- BWP wrapper now defaults to local images and enables `--telnetsrv.shrmod ci`.

## Validation

- `nr-softmodem` build: PASS.
- `nr-uesoftmodem` build: PASS.
- Local Docker image rebuild: PASS.
- `python syntax ok`: PASS.
- `bash -n` wrappers/helpers: PASS.
- `test_extract_bwp_metrics.py`: PASS.
- `plot_paper_vs_local.py`: PASS.
- `openspec status --change redcap-bwp-sdt-validation`: PASS.
- `git diff --check`: PASS.
- Docker after run: 0 running containers.

## Remaining

- [BWP]: `bwp-InactivityTimer` remains not implemented; paper-equivalent delay/power/throughput curves remain `[TBD]`.
- [SDT]: single-UE marker run is complete; paper-equivalent stochastic success-probability sweep remains `[TBD]`.
- [Spec]: TS 38.321 clause 5.9 vs 5.15.1 mismatch remains `[Needs Verification]`.
