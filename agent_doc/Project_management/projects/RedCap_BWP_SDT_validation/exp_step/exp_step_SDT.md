# SDT Small-Data Experiment Steps

## Version Snapshot

- [Git Branch]: `m5-56-ue-ok`
- [Git Commit]: `002d6ff474`
- [Runtime Config Root]: `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/`
- [Experiment Config]: `agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/configs/SDT_local_matrix.yaml`
- [Experiment Wrapper]: `agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/scripts/run_sdt_validation.sh`
- [Paper Source]: `redcap_doc/evaluation_papers/redcap_vaildation_BWP_SDT/paper2_SDT_small_data.md`
- [Status]: dry-run complete; Docker runtime run pending because 2026-06-25 escalation was rejected with workspace credits unavailable

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

## Local Setup Steps

1. [Build] Confirm gNB and UE binaries are current:
   - `rtk cmake --build --preset default --target nr-softmodem`
   - `rtk cmake --build --preset default --target nr-uesoftmodem`
2. [Config] Use existing RedCap policy files:
   - `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/control/redcap_policy_case_a.yaml`
   - `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/control/redcap_control_contract.yaml`
3. [Runtime markers] Confirm:
   - `RRC_INACTIVE entered`
   - `configuredGrantConfig parsed`
   - `cg-SDT PUSCH tx`
   - `cg-SDT PUSCH rx candidate`
4. [Wrapper dry-run] Record the runnable manifest before starting Docker:
   - `agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/scripts/run_sdt_validation.sh --dry-run`
5. [Runtime execution] Use `--run` only after confirming the local RedCap RFsim environment is idle. The wrapper defaults to the minimal service set `nearRT-RIC oai-gnb oai-nr-ue2 xapp-kpm-rc`; use `SERVICES="..."` only when expanding the UE set:
   - `agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/scripts/run_sdt_validation.sh --run`
6. [Metric extraction] Export local metrics into `exp_result/SDT_results.csv`.

## Required Logs

| Log | Path |
|---|---|
| gNB runtime log | `test_log/compiler_logs/` or runtime-specific timestamped path |
| UE runtime log | `test_log/redcap_bwp_sdt_validation/*_sdt/container_logs/ue2_tail.log` |
| policy snapshot | `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/control/*.yaml` |
| wrapper manifest | `test_log/redcap_bwp_sdt_validation/*_sdt/run_manifest.txt` |
| compose status | `test_log/redcap_bwp_sdt_validation/*_sdt/docker_compose_ps.log` |
| comparison CSV | `agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/exp_result/SDT_results.csv` |

## Runtime Evidence

| Run ID | Result | Evidence |
|---|---|---|
| `20260625_213537_sdt` | dry-run manifest created; Docker `--run` was not executed because escalation was rejected with workspace credits unavailable | `test_log/redcap_bwp_sdt_validation/20260625_213537_sdt/run_manifest.txt` |

- [Stable blocker report]: `agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/exp_result/SDT_runtime_blocker_20260625.md`

## Metric Extraction

- [Extractor]: `agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/scripts/extract_sdt_metrics.py`
- [Status]: ready for the next successful SDT runtime log bundle.
- [Target markers]:
  - `RRC_INACTIVE`
  - `RRCResumeRequest`
  - `RRCResumeComplete`
  - `configuredGrantConfig`
  - `cg-SDT`
- [Hook audit]:
  - `rtk python agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/scripts/audit_oai_hooks.py`
  - Verify [gNB SDT log file hook], [gNB CG-SDT classifier], and [SDT FSM step] remain `[present]`.

## Adjusted 3GPP Parameters

- [sdt-DataVolumeThreshold]: `[TBD]`
- [cg-SDT-TimeAlignmentTime]: `[TBD]`
- [cg-SDT-RSRP-ChangeThreshold]: `[TBD]`
- [configuredGrantConfig]: `[TBD]`
- [Clause mapping]: TS 38.523-1 clause 7.1.1.13 and TS 38.300 clause 18 `[Needs Verification]`
