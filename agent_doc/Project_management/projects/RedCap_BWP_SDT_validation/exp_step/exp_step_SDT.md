# SDT Small-Data Experiment Steps

## Version Snapshot

- [Git Branch]: `m5-56-ue-ok`
- [Git Commit]: `002d6ff474`
- [Runtime Config Root]: `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/`
- [Experiment Config]: `agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/configs/SDT_local_matrix.yaml`
- [Experiment Wrapper]: `agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/scripts/run_sdt_validation.sh`
- [Runtime Delegate]: `redcap_interface/mmtc.menu.bash gate3`
- [Baseline Project]: `agent_doc/Project_management/projects/redcap_rrc_inactive_sdt_oran_control_v1/` [Case A Gate 3]
- [Paper Source]: `redcap_doc/evaluation_papers/redcap_vaildation_BWP_SDT/paper2_SDT_small_data.md`
- [Status]: historical local-image SDT runtime run complete; matrix runner and repeated-run aggregator added; 12 paper-scenario RFsim repetitions pending

## Experiment Intent

- Reproduce comparable [overall packet transmission success probability] trends for:
  - [4-step RA]
  - [2-step RA]
  - [4-step SDT]
  - [2-step SDT]

## Paper Parameters

| Parameter | Paper value | Local value |
|---|---:|---:|
| Cell model | 0.1 km2 circular single-BS cell | RFsim single-cell baseline first |
| Device distribution | homogeneous PPP | [TBD] |
| Packet arrival | Poisson | [TBD] |
| `mu_new` | 0.1 packets/time-slot | [TBD] |
| `rho` | -90 dBm | [TBD] |
| `sigma_n^2` | -100.4 dBm | [TBD] |
| `gamma_th` | -10 dB | [TBD] |
| Path-loss exponent `alpha` | 4 | [TBD] |
| `N_ZC` | 839 | [TBD] |
| `lambda_th` | -51.5 dBm | [TBD] |
| Device intensity example | `lambda_Dp = 5 devices/preamble` | [TBD] |

## Next Paper-Comparable Scenario Matrix

- [Purpose]: maintain the 12 local SDT success-probability rows with repeated-run evidence.
- [Runtime baseline]: keep standalone `scripts/run_sdt_validation.sh` delegated to `redcap_interface/mmtc.menu.bash gate3`; matrix runs use `MMTC_SDT_MENU_SUBCOMMAND=smoke` so scenario-specific gate flags are preserved.
- [Success-probability definition]: `successful_packet_transmissions / attempted_packet_transmissions` per scenario.
- [Extraction requirements]:
  - [x] record attempted packet count, successful packet count, fallback count, and timeout/failure count per run.
  - [x] keep [normal resume due threshold] separate from [RA-SDT failure].
  - [x] store per-run raw metrics before aggregating the final probability.
  - [x] preserve the copied gNB/UE logs under `test_log/redcap_bwp_sdt_validation/*_sdt/container_logs/full/`.
  - [x] execute repeated RFsim samples for all 12 paper scenarios.
  - [x] verify that 2-step RA, slot10, and `lambda_dp_5` are labels only in the current wrapper/OAI wiring.

| scenario | mode | access steps | sweep point | required local metric |
|---|---|---:|---|---|
| `4_step_ra` | normal RA baseline | 4-step | base paper scenario | packet transmission success probability |
| `2_step_ra` | normal RA baseline | 2-step | base paper scenario | packet transmission success probability |
| `4_step_sdt` | RA-SDT / SDT | 4-step | base paper scenario | packet transmission success probability |
| `2_step_sdt` | RA-SDT / SDT | 2-step | base paper scenario | packet transmission success probability |
| `4_step_ra_slot10` | normal RA baseline | 4-step | slot 10 | packet transmission success probability |
| `2_step_ra_slot10` | normal RA baseline | 2-step | slot 10 | packet transmission success probability |
| `4_step_sdt_slot10` | RA-SDT / SDT | 4-step | slot 10 | packet transmission success probability |
| `2_step_sdt_slot10` | RA-SDT / SDT | 2-step | slot 10 | packet transmission success probability |
| `4_step_ra_lambda_dp_5` | normal RA baseline | 4-step | `lambda_Dp = 5` | packet transmission success probability |
| `2_step_ra_lambda_dp_5` | normal RA baseline | 2-step | `lambda_Dp = 5` | packet transmission success probability |
| `4_step_sdt_lambda_dp_5` | RA-SDT / SDT | 4-step | `lambda_Dp = 5` | packet transmission success probability |
| `2_step_sdt_lambda_dp_5` | RA-SDT / SDT | 2-step | `lambda_Dp = 5` | packet transmission success probability |

## Local Setup Steps

1. [Build] Confirm gNB and UE binaries are current:
   - `rtk cmake --build --preset default --target nr-softmodem`
   - `rtk cmake --build --preset default --target nr-uesoftmodem`
2. [Config] Use existing RedCap policy files:
   - `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/control/redcap_policy_case_a.yaml`
   - `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/control/redcap_control_contract.yaml`
3. [Runtime baseline] Use the existing [RRC_INACTIVE + SDT] Gate 3 flow:
   - `REDCAP_CASE=case_a`
   - `REDCAP_POLICY_HOST_FILE=ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/control/redcap_policy_case_a.yaml`
   - `MMTC_RRC_INACTIVE_GATE1_TRIGGER=1`
   - `MMTC_RRC_INACTIVE_GATE2_RESUME_TRIGGER=0`
   - `MMTC_RRC_INACTIVE_GATE3_CG_CONFIG=1`
   - `MMTC_RRC_INACTIVE_GATE4_FORCE_FALLBACK=0`
4. [Runtime markers] Confirm:
   - `RRC_INACTIVE entered`
   - `configuredGrantConfig parsed`
   - `cg-SDT PUSCH tx`
   - `cg-SDT PUSCH rx candidate`
5. [Wrapper dry-run] Record the runnable manifest before starting Docker:
   - `agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/scripts/run_sdt_validation.sh --dry-run`
   - Full matrix dry-run:
     - `rtk bash agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/scripts/run_sdt_matrix.sh --dry-run`
6. [Runtime execution] Use `--run` only after confirming the local RedCap RFsim environment is idle. The standalone wrapper defaults to `redcap_interface/mmtc.menu.bash gate3`; the full matrix sets `MMTC_SDT_MENU_SUBCOMMAND=smoke` and defaults to `MMTC_SAMPLE_UES=2` for paper-project continuity:
   - `agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/scripts/run_sdt_validation.sh --run`
   - The delegated runner writes original smoke logs under `test_log/compiler_logs/`.
   - The paper wrapper copies the selected gNB/UE logs into `test_log/redcap_bwp_sdt_validation/*_sdt/container_logs/full/` and merges paper-facing metrics into `SDT_results.csv`.
   - Current delegated run shape:
     ```bash
     rtk env RUN_ID=YYYYMMDD_HHMMSS_sdt_gate3_delegate MMTC_SAMPLE_UES=2 \
       agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/scripts/run_sdt_validation.sh --run
     ```
   - Historical local-image run:
     ```bash
     rtk env RUN_ID=20260626_230300_sdt_local STOP_AFTER_RUN=1 RUN_WAIT_SECONDS=45 \
       agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/scripts/run_sdt_validation.sh --run
     ```
7. [Metric extraction] Export local metrics into `exp_result/SDT_results.csv`.
8. [Repeated-run aggregation] Merge per-run counters into success-probability rows:
   - `rtk python agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/scripts/aggregate_sdt_success.py`

## Required Logs

| Log | Path |
|---|---|
| gNB runtime log | Original: `test_log/compiler_logs/mmtc_smoke_*_gnb.log`; paper copy: `test_log/redcap_bwp_sdt_validation/*_sdt/container_logs/full/gnb.log` |
| UE runtime log | `test_log/redcap_bwp_sdt_validation/*_sdt/container_logs/ue2_tail.log` |
| policy snapshot | `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/control/*.yaml` |
| wrapper manifest | `test_log/redcap_bwp_sdt_validation/*_sdt/run_manifest.txt` |
| delegate console | `test_log/redcap_bwp_sdt_validation/*_sdt/redcap_interface_*_console.log`; 2026-06-27 matrix bundles used the legacy `redcap_interface_gate3_console.log` filename |
| comparison CSV | `agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/exp_result/SDT_results.csv` |

## Runtime Evidence

| Run ID | Result | Evidence |
|---|---|---|
| `20260625_213537_sdt` | dry-run manifest created; Docker `--run` was not executed because escalation was rejected with workspace credits unavailable | `test_log/redcap_bwp_sdt_validation/20260625_213537_sdt/run_manifest.txt` |
| `20260626_230300_sdt_local` | Local-image SDT marker run completed and merged 15 runtime rows into `SDT_results.csv` | `test_log/redcap_bwp_sdt_validation/20260626_230300_sdt_local_sdt/` |
| `20260627_200958_sdt_matrix` | 12 scenarios x 3 RFsim samples completed; 36 runtime CSVs aggregated into `SDT_repeated_run_aggregate.csv`; many smoke runner rc failures were ping-only limitations | `test_log/redcap_bwp_sdt_validation/20260627_200958_sdt_matrix_*_sdt/` |

- [Stable blocker report]: `agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/exp_result/SDT_runtime_blocker_20260625.md`
- [Stable runtime report]: `agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/exp_result/SDT_runtime_evidence_20260626_230300.md`
- [Current runner alignment]: new SDT runtime runs should use the delegated Gate 3 path; the paper project remains responsible for metric extraction and CSV merge only.

## Metric Extraction

- [Extractor]: `agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/scripts/extract_sdt_metrics.py`
- [Status]: runtime extraction completed for `20260626_230300_sdt_local`.
- [Target markers]:
  - `RRC_INACTIVE`
  - `RRCResumeRequest`
  - `RRCResumeComplete`
  - `configuredGrantConfig`
  - `cg-SDT`
- [Hook audit]:
  - `rtk python agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/scripts/audit_oai_hooks.py`
  - Verify [gNB SDT log file hook], [gNB CG-SDT classifier], and [SDT FSM step] remain `[present]`.
- [Observed local values]:
  - `active_ue_count = 1`
  - `ue_in_sync_seen = 1`
  - `rrc_inactive_marker_seen = 1`
  - `configured_grant_marker_seen = 1`
  - `cg_sdt_marker_seen = 1`
  - `rrc_resume_request_seen = 0`
  - `rrc_resume_complete_seen = 0`
  - `packet_attempt_count = 1`
  - `packet_success_count = 1`
  - `threshold_fallback_count = 0`
  - `timeout_failure_count = 0`
  - `packet_transmission_success_probability = 1.000000`
- [Aggregate output]:
  - `agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/exp_result/SDT_repeated_run_aggregate.csv`
- [Current boundary]:
  - The aggregate now covers the local minimal CG-SDT marker scenario and the 12 matrix scenarios.
  - The 12 canonical paper scenario rows have numeric local marker-classified values.
  - `MMTC_RA_ACCESS_STEPS`, `slot10`, and `lambda_dp_5` are `[wrapper_label]` dimensions; targeted source scan found no OAI C or compose hook that changes RA steps, slot timing, or device intensity.

## Adjusted 3GPP Parameters

- [sdt-DataVolumeThreshold]: policy matrix records 256 bytes; exact RRC conformance `[Needs Verification]`
- [cg-SDT-TimeAlignmentTime]: policy matrix records `infinity`; exact RRC conformance `[Needs Verification]`
- [cg-SDT-RSRP-ChangeThreshold]: policy matrix records 6 dB; exact RRC conformance `[Needs Verification]`
- [configuredGrantConfig]: local marker seen; full paper-equivalent multi-device sweep `[TBD]`
- [Clause mapping]: TS 38.523-1 clause 7.1.1.13 and TS 38.300 clause 18 `[Needs Verification]`
