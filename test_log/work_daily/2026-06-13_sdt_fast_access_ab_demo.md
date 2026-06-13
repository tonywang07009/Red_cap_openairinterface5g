# SDT Fast Access A/B Demo

## Conclusion
- Result: A/B live demo script implemented and RFsim live run passed for UE1.
- Case A: [Connected UE] with Gate1/2/3 off.
- Case B: [SDT UE] with Gate1 on, Gate2 off, Gate3 on.
- Boundary: [Case B data_path_ms] is measured from `cg-SDT autonomous CG PUSCH scheduled` to `cg-SDT PUSCH tx`; `inactive_wait_ms` is reported separately because it includes inactive dwell before small data arrives.

## Required Project Fields
- Project Path: `agent_doc/Project_management/projects/redcap_rrc_inactive_sdt_oran_control_v1/project_plan.md`
- [Case]: A
- [Gate]: 3 display/demo support
- [source build PASS/FAIL/NA]: NA, no C source changed in this task.
- [unit test PASS/FAIL/NA]: NA, shell interface/parser only.
- [Docker image rebuild PASS/FAIL/NA]: NA, reused existing local images.
- [RFsim runtime PASS/FAIL/NA]: PASS for A/B UE1 live demo.
- [exit 139]: absent in required marker checks.

## Validation Commands
1. `bash -n redcap_interface/bash_library/fc_ab_sdt_fast_access_demo.sh`
2. `bash -n redcap_interface/mmtc.display.bash`
3. `AB_SDT_RUN_ID=live_ab_2026-06-13_sdt_fast_access AB_SDT_TOTAL_UES=29 AB_SDT_SAMPLE_UE=1 AB_SDT_PING_COUNT=10 AB_SDT_SLEEP_AFTER_UP=25 AB_SDT_GNB_WARMUP=5 bash redcap_interface/mmtc.display.bash sdt-ab`
4. `AB_SDT_RUN_EXPERIMENTS=0 AB_SDT_RUN_A=1 AB_SDT_RUN_B=1 AB_SDT_RUN_ID=live_ab_2026-06-13_sdt_fast_access ... bash redcap_interface/mmtc.display.bash sdt-ab`

## A/B Result
| Case | Name | Status | Data path ms | Inactive wait ms | Packet bytes | TBS | gNB rx bytes | Ping avg ms |
|---|---|---|---:|---:|---:|---:|---:|---:|
| A | connected | PASS | 63.706 | NA | 33 | NA | NA | 4.752 |
| B | sdt-inactive | PASS | 0.005 | 4826.119 | 53 | 72 | 20 | 4.961 |

## Logs
| Item | Result | Log |
|---|---|---|
| A/B summary | PASS | `test_log/ab_sdt_fast_access/live_ab_2026-06-13_sdt_fast_access_summary.md` |
| A/B CSV | PASS | `test_log/ab_sdt_fast_access/live_ab_2026-06-13_sdt_fast_access_metrics.csv` |
| Case A gNB | PASS | `test_log/compiler_logs/mmtc_smoke_2026-06-13_15-14-47_gnb.log` |
| Case A UE1 | PASS | `test_log/compiler_logs/mmtc_smoke_2026-06-13_15-14-47_ue1_docker.log` |
| Case A ping | PASS | `test_log/compiler_logs/mmtc_smoke_2026-06-13_15-14-47_ue1_ping.log` |
| Case B gNB | PASS | `test_log/compiler_logs/mmtc_smoke_2026-06-13_15-16-10_gnb.log` |
| Case B UE1 | PASS | `test_log/compiler_logs/mmtc_smoke_2026-06-13_15-16-10_ue1_docker.log` |
| Case B ping | PASS | `test_log/compiler_logs/mmtc_smoke_2026-06-13_15-16-10_ue1_ping.log` |

## Follow-up
- Use `bash redcap_interface/mmtc.display.bash sdt-ab` for future live demonstrations.
- Use `AB_SDT_RUN_EXPERIMENTS=0` plus explicit log paths to regenerate a report without rerunning Docker.
- If a formal report claims 3GPP SDT compliance, add exact TS 38.331/38.321 clause mapping as `[Needs Verification]`.
