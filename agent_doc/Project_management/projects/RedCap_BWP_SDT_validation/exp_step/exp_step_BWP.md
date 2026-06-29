# BWP Switching Experiment Steps

## Version Snapshot

- [Git Branch]: `m5-56-ue-ok`
- [Git Commit]: `35e94d9b55`
- [Working Tree Delta]: BWP runtime instrumentation and extractor updates are present but not committed.
- [Runtime Config Root]: `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/`
- [Experiment Config]: `agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/configs/BWP_local_matrix.yaml`
- [Experiment Wrapper]: `agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/scripts/run_bwp_validation.sh`
- [Shared Runtime Helper]: `agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/scripts/redcap_runtime_common.sh`
- [Paper Source]: `redcap_doc/evaluation_papers/redcap_vaildation_BWP_SDT/paper1_BWP_switching.md`
- [Status]: BWP matrix runtime executed; Gate 5 blocked by BWP 0 telnet-trigger gNB crash

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

## Next Paper-Comparable Run Matrix

- [Purpose]: fill the four remaining local `[TBD]` BWP rows with values comparable to the BWP switching paper.
- [Blocking prerequisites]:
  - [x] [bwp-InactivityTimer instrumentation]: current gap is exported as `bwp_inactivity_timer_gap_seen`.
  - [x] [Default/Dedicated BWP size]: extractor records both BWP sizes from gNB config logs.
  - [x] [BWP residency counters]: extractor derives Default/Dedicated residency from timestamped `Switching to DL-BWP` events.
  - [x] [Switch-delay measurement]: extractor measures reconfiguration marker to BWP apply and first post-switch scheduled SDU.
  - [x] [Wrapper matrix execution]: run all high/low scenario rows with force-recreate logs.
  - [ ] [Crash fix]: fix BWP 1 -> BWP 0 telnet-trigger crash before claiming Gate 5 PASS.
  - [ ] [Full paper sweep]: implement or validate real traffic and timer behavior before claiming publication-grade reproduction.

| scenario | load profile | `bwp-InactivityTimer` | switch delay target | required local metrics |
|---|---|---:|---:|---|
| `low_load_bwp_8ms_1ms` | 10 KB PDU, 20 PDUs/s | 8 ms | 1 ms | default BWP ratio, power saving, PDU scheduling delay |
| `low_load_bwp_8ms_3ms` | 10 KB PDU, 20 PDUs/s | 8 ms | 3 ms | throughput, default BWP ratio, power saving, PDU scheduling delay |
| `low_load_bwp_80ms_1ms` | 10 KB PDU, 20 PDUs/s | 80 ms | 1 ms | throughput, default BWP ratio, power saving, PDU scheduling delay |
| `low_load_bwp_80ms_3ms` | 10 KB PDU, 20 PDUs/s | 80 ms | 3 ms | throughput, default BWP ratio, power saving, PDU scheduling delay |
| `high_load_bwp_8ms_1ms` | 320 KB PDU, 20 PDUs/s | 8 ms | 1 ms | default BWP ratio, throughput |
| `high_load_bwp_8ms_3ms` | 320 KB PDU, 20 PDUs/s | 8 ms | 3 ms | throughput, default BWP ratio |
| `high_load_bwp_80ms_1ms` | 320 KB PDU, 20 PDUs/s | 80 ms | 1 ms | throughput, default BWP ratio |
| `high_load_bwp_80ms_3ms` | 320 KB PDU, 20 PDUs/s | 80 ms | 3 ms | throughput, default BWP ratio |

## Local Setup Steps

1. [Build] Confirm gNB and UE binaries are current:
   - `rtk cmake --build --preset default --target nr-softmodem`
   - `rtk cmake --build --preset default --target nr-uesoftmodem`
   - If local `ccache` points at read-only `/run/user/1000`, use:
     - `rtk bash -lc 'CCACHE_DIR=/tmp/ccache CCACHE_TEMPDIR=/tmp/ccache-tmp cmake --build --preset default --target nr-softmodem'`
     - `rtk bash -lc 'CCACHE_DIR=/tmp/ccache CCACHE_TEMPDIR=/tmp/ccache-tmp cmake --build --preset default --target nr-uesoftmodem'`
2. [Config inventory] Use `symdex` before raw search for BWP source paths:
   - `rtk /home/tonywang/miniforge3/bin/symdex --state-dir .symdex search nr_mac_trigger_reconfiguration --repo redcap_oai`
   - `rtk /home/tonywang/miniforge3/bin/symdex --state-dir .symdex search configure_UE_BWP --repo redcap_oai`
3. [Runtime] Start from `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/docker-compose.mmtc.yml`.
   - `run_bwp_validation.sh` remains a paper-specific wrapper because BWP telnet trigger and BWP residency metrics are not owned by the SDT Gate 3 project.
   - Shared compose/image/default extraction behavior is centralized in `scripts/redcap_runtime_common.sh`.
4. [Wrapper dry-run] Record the runnable manifest before starting Docker:
   - `agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/scripts/run_bwp_validation.sh --dry-run`
   - Full matrix dry-run:
     - `rtk bash agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/scripts/run_bwp_matrix.sh --dry-run`
5. [Runtime execution] Use `--run` only after confirming the local RedCap RFsim environment is idle. The wrapper defaults to the minimal service set `nearRT-RIC oai-gnb oai-nr-ue2 xapp-kpm-rc`; use `SERVICES="..."` only when expanding the UE set:
   - `agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/scripts/run_bwp_validation.sh --run`
   - For BWP marker validation:
     ```bash
     rtk env RUN_ID=20260626_231100_bwp_local_ci STOP_AFTER_RUN=1 RUN_WAIT_SECONDS=45 \
       BWP_TRIGGER_SEQUENCE='1 0' BWP_TRIGGER_DELAY_SECONDS=5 \
       RUNTIME_SCENARIO=local_rfsim_ue2_bwp_trigger_1_0 \
       agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/scripts/run_bwp_validation.sh --run
     ```
6. [Metric extraction] Export local metrics into `exp_result/BWP_results.csv`.
7. [Extractor smoke test] Validate BWP marker parsing without Docker:
   - `rtk python agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/scripts/test_extract_bwp_metrics.py`

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
| `20260626_231100_bwp_local_ci` | Local-image BWP marker run completed; BWP 0 trigger succeeded, BWP 1 trigger failed because UE was already on BWP 1 | `test_log/redcap_bwp_sdt_validation/20260626_231100_bwp_local_ci_bwp/` |
| `20260628_151500_bwp_matrix_recreate` | 8/8 matrix rows executed with force-recreate logs; every BWP 0 trigger crashed gNB | `test_log/redcap_bwp_sdt_validation/20260628_151500_bwp_matrix_recreate_*_bwp/` |
| `20260628_154000_bwp_trigger0_bt` | Backtrace run confirms crash frame `update_cellGroupConfig_for_BWP_switch+0x151` | `test_log/redcap_bwp_sdt_validation/20260628_154000_bwp_trigger0_bt_bwp/` |

- [Stable evidence report]: `agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/exp_result/BWP_runtime_evidence_20260625_213152.md`
- [Stable BWP marker report]: `agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/exp_result/BWP_runtime_evidence_20260626_231100.md`
- [Stable BWP matrix report]: `agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/exp_result/BWP_runtime_evidence_20260628_151500.md`

## Source Validation

| Date | Item | Result |
|---|---|---|
| 2026-06-26 | `nr-softmodem` build with `/tmp` ccache | [PASS] |
| 2026-06-26 | `nr-uesoftmodem` build with `/tmp` ccache | [PASS] |
| 2026-06-26 | `scripts/test_extract_bwp_metrics.py` | [PASS] |
| 2026-06-26 | `scripts/audit_oai_hooks.py` | [PASS] |
| 2026-06-26 | extractor CLI dry run on old `20260625_213152_bwp` logs | [PASS]; new marker counts are `0` because the log predates instrumentation |
| 2026-06-26 | local-image BWP marker run `20260626_231100_bwp_local_ci` | [PASS]; `bwp_gnb_reconfiguration_count = 1`, `bwp_ue_ra_operation_count = 2` |
| 2026-06-28 | BWP force-recreate matrix `20260628_151500_bwp_matrix_recreate` | [BLOCKED]; 8/8 rows generated runtime CSVs, but all 8 hit gNB `Segmentation fault` after BWP 0 trigger |
| 2026-06-28 | BWP backtrace `20260628_154000_bwp_trigger0_bt` | [PASS]; captured `update_cellGroupConfig_for_BWP_switch+0x151` crash frame |

## Metric Extraction

- [Extractor]: `agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/scripts/extract_bwp_metrics.py`
- [Command]:
  ```bash
  rtk python agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/scripts/extract_bwp_metrics.py \
    --gnb-log test_log/redcap_bwp_sdt_validation/20260625_213152_bwp/container_logs/full/gnb.log \
    --ric-log test_log/redcap_bwp_sdt_validation/20260625_213152_bwp/container_logs/full/nearRT-RIC.log \
    --xapp-log test_log/redcap_bwp_sdt_validation/20260625_213152_bwp/container_logs/full/xapp_kpm_rc.log \
    --ue-log test_log/redcap_bwp_sdt_validation/20260625_213152_bwp/container_logs/full/ue2.log \
    --scenario local_rfsim_ue2_minimal_bwp \
    --output agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/exp_result/BWP_results.csv
  ```
- [Observed local markers]:
  - `active_ue_count = 1`
  - `ue_in_sync_seen = 1`
  - `dlsch_errors = 0`
  - `ulsch_errors = 0`
  - `ric_e2_setup_seen = 1`
  - `xapp_e42_setup_seen = 1`
- [New BWP instrumentation markers for the next RFsim run]:
  - `[RedCap BWP][gNB reconfiguration]`
  - `[RedCap BWP][gNB interrupt]`
  - `[RedCap BWP][UE RA]`
- [New extractor fields]:
  - `bwp_gnb_reconfiguration_count`
  - `bwp_gnb_reconfiguration_last_new_bwp_id`
  - `bwp_gnb_interrupt_count`
  - `bwp_gnb_interrupt_last_slots`
  - `bwp_ue_ra_operation_count`
  - `bwp_ue_ra_bwp_change_count`
  - `bwp_inactivity_timer_gap_seen`
  - `default_bwp_size_prb`
  - `dedicated_bwp_size_prb`
  - `default_bwp_residency_ms`
  - `dedicated_bwp_residency_ms`
  - `default_bwp_ratio_percent`
  - `bwp_switch_apply_delay_ms`
  - `pdu_scheduling_delay_ms`
  - `power_saving_percent`
  - `gnb_mac_total_throughput_mbps`
- [Observed BWP marker run values]:
  - `bwp_gnb_reconfiguration_count = 1`
  - `bwp_gnb_reconfiguration_last_new_bwp_id = 0`
  - `bwp_gnb_interrupt_count = 0`
  - `bwp_ue_ra_operation_count = 2`
  - `bwp_inactivity_timer_gap_seen = 1`
  - `default_bwp_ratio_percent = 10.674214`
  - `power_saving_percent = 5.538507`
  - `pdu_scheduling_delay_ms = 4.249000`

## Adjusted 3GPP Parameters

- [BWP inactivity timer]: not implemented in local UE MAC; marker exports `bwp_inactivity_timer=not_implemented`
- [BWP switch delay]: current 2026-06-28 matrix does not produce switch-delay or PDU-delay metrics because BWP 0 trigger crashes gNB.
- [BWP telnet trigger]: wrapper enables `--telnetsrv.shrmod ci`; BWP switch evidence uses `ci trigger_bwp_switch`
- [BWP matrix labels]: `MMTC_BWP_TRAFFIC_PROFILE`, `MMTC_BWP_INACTIVITY_TIMER_MS`, and `MMTC_BWP_SWITCH_DELAY_MS` are runner/manifest labels until OAI runtime hooks are implemented.
- [Default BWP size]: `51` PRB from runtime gNB log
- [Dedicated BWP size]: `106` PRB from runtime gNB log
- [Clause mapping]: TS 38.523-1 clause 7.1.1.12 and TS 38.321 clause 5.15.1; requested TS 38.321 clause 5.9 remains `[Needs Verification]`
- [Hook audit]:
  - `rtk python agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/scripts/audit_oai_hooks.py`
  - Expected outputs: `exp_result/oai_hook_inventory.md`, `exp_result/oai_hook_inventory.csv`
  - Current BWP gap to watch: `[UE bwp-InactivityTimer implementation] = [gap_present]`
