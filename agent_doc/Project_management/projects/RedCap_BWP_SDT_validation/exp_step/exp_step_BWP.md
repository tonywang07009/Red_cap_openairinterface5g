# BWP Switching Experiment Steps

## Version Snapshot

- [Git Branch]: `m5-56-ue-ok`
- [Git Commit]: `002d6ff474`
- [Runtime Config Root]: `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/`
- [Experiment Config]: `agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/configs/BWP_local_matrix.yaml`
- [Experiment Wrapper]: `agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/scripts/run_bwp_validation.sh`
- [Paper Source]: `redcap_doc/evaluation_papers/redcap_vaildation_BWP_SDT/paper1_BWP_switching.md`
- [Status]: first-pass UE2 RFsim run complete; paper curve extraction and BWP-specific timer wiring pending

## Experiment Intent

- Reproduce comparable [BWP switching] trends from the paper:
  - [application-layer throughput]
  - [Default BWP ratio]
  - [estimated power saving]
  - [PDU scheduling delay]

## Paper Parameters

| Parameter | Paper value | Local value |
|---|---:|---:|
| Carrier frequency | 3.5 GHz | 3.63036 GHz RFsim baseline |
| Carrier bandwidth | 20 MHz | 106 PRB RFsim baseline `[Needs Verification]` |
| SCS | 15 kHz | numerology 1 / 30 kHz |
| Duplex | TDD | gNB log: 8 DL slots, 3 UL slots, 10 slots/period |
| Macro cells | 21 | RFsim single-cell baseline first |
| UE calls | 105 | 1 RedCap UE baseline (`oai-nr-ue2`) |
| Traffic model | FTP3, Poisson PDU generation | [TBD] |
| PDU rate | 20 PDUs/s | [TBD] |
| Low load | 10 KB PDU, ~1.6 Mbps/UE | [TBD] |
| High load | 320 KB PDU, ~51.2 Mbps/UE | [TBD] |
| `bwp-InactivityTimer` | 8 ms / 80 ms | [TBD] |
| BWP switch delay | 1 ms / 3 ms | [TBD] |

## Local Setup Steps

1. [Build] Confirm gNB and UE binaries are current:
   - `rtk cmake --build --preset default --target nr-softmodem`
   - `rtk cmake --build --preset default --target nr-uesoftmodem`
2. [Config inventory] Use `symdex` before raw search for BWP source paths:
   - `rtk /home/tonywang/miniforge3/bin/symdex --state-dir .symdex search nr_mac_trigger_reconfiguration --repo redcap_oai`
   - `rtk /home/tonywang/miniforge3/bin/symdex --state-dir .symdex search configure_UE_BWP --repo redcap_oai`
3. [Runtime] Start from `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/docker-compose.mmtc.yml`.
4. [Wrapper dry-run] Record the runnable manifest before starting Docker:
   - `agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/scripts/run_bwp_validation.sh --dry-run`
5. [Runtime execution] Use `--run` only after confirming the local RedCap RFsim environment is idle. The wrapper defaults to the minimal service set `nearRT-RIC oai-gnb oai-nr-ue2 xapp-kpm-rc`; use `SERVICES="..."` only when expanding the UE set:
   - `agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/scripts/run_bwp_validation.sh --run`
6. [Metric extraction] Export local metrics into `exp_result/BWP_results.csv`.

## Required Logs

| Log | Path |
|---|---|
| gNB runtime log | `test_log/compiler_logs/` or runtime-specific timestamped path |
| UE runtime log | `test_log/redcap_bwp_sdt_validation/*_bwp/container_logs/ue2_tail.log` |
| build log | `test_log/build_logs/` |
| wrapper manifest | `test_log/redcap_bwp_sdt_validation/*_bwp/run_manifest.txt` |
| compose status | `test_log/redcap_bwp_sdt_validation/*_bwp/docker_compose_ps.log` |
| comparison CSV | `agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/exp_result/BWP_results.csv` |

## Runtime Evidence

| Run ID | Result | Evidence |
|---|---|---|
| `20260625_212853_bwp` | UE1 RedCap attempt failed with `Segmentation fault`; matches known UE1 `cells:` override crash path | `test_log/redcap_bwp_sdt_validation/20260625_212853_bwp/container_logs/ue1_tail.log` |
| `20260625_213152_bwp` | UE2 RedCap minimal run completed with gNB/UE healthy; xApp reached E42 setup then exited 139 | `test_log/redcap_bwp_sdt_validation/20260625_213152_bwp/container_logs/full/` |

- [Stable evidence report]: `agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/exp_result/BWP_runtime_evidence_20260625_213152.md`

## Metric Extraction

- [Extractor]: `agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/scripts/extract_bwp_metrics.py`
- [Command]:
  - `rtk python agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/scripts/extract_bwp_metrics.py --gnb-log test_log/redcap_bwp_sdt_validation/20260625_213152_bwp/container_logs/full/gnb.log --ric-log test_log/redcap_bwp_sdt_validation/20260625_213152_bwp/container_logs/full/nearRT-RIC.log --xapp-log test_log/redcap_bwp_sdt_validation/20260625_213152_bwp/container_logs/full/xapp_kpm_rc.log --scenario local_rfsim_ue2_minimal_bwp --output agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/exp_result/BWP_results.csv`
- [Observed local markers]:
  - `active_ue_count = 1`
  - `ue_in_sync_seen = 1`
  - `dlsch_errors = 0`
  - `ulsch_errors = 0`
  - `ric_e2_setup_seen = 1`
  - `xapp_e42_setup_seen = 1`

## Adjusted 3GPP Parameters

- [BWP inactivity timer]: `[TBD]`
- [BWP switch delay]: `[TBD]`
- [Default BWP size]: `[TBD]`
- [Dedicated BWP size]: `[TBD]`
- [Clause mapping]: TS 38.523-1 clause 7.1.1.12 and TS 38.321 clause 5.15.1; requested TS 38.321 clause 5.9 remains `[Needs Verification]`
- [Hook audit]:
  - `rtk python agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/scripts/audit_oai_hooks.py`
  - Expected outputs: `exp_result/oai_hook_inventory.md`, `exp_result/oai_hook_inventory.csv`
  - Current BWP gap to watch: `[UE bwp-InactivityTimer implementation] = [gap_present]`
