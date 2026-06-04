# 2026-06-04 RRC_INACTIVE SDT Gate 1 RFsim Validation

## Scope
- Project Path: `agent_doc/Project_management/projects/redcap_rrc_inactive_sdt_oran_control_v1/project_plan.md`
- [Case]: A
- [Gate]: 1
- [Task]: T2-1 `RRCRelease.suspendConfig` to UE `[RRC_INACTIVE]`
- [Runtime Source]: `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/`
- [Runtime Command]:
  ```bash
  MMTC_TOTAL_UES=29 MMTC_SAMPLE_UES="1" MMTC_USE_EXISTING_CN_DB=0 MMTC_RESET_CN=1 MMTC_PING_COUNT=1 MMTC_RUN_REVERSE_PING=0 MMTC_REVERSE_PING_COUNT=0 MMTC_IPERF_ENABLE=0 MMTC_START_XAPP=0 MMTC_GNB_WARMUP=5 MMTC_SLEEP_AFTER_UP=30 MMTC_UE_START_GAP=0 MMTC_FAIL_ON_GNB_RESTART=1 MMTC_AUTO_RECOVER_AFTER_GNB_RESTART=0 MMTC_AUTO_RECOVER_MISSING_UES=0 MMTC_RRC_INACTIVE_GATE1_TRIGGER=1 REDCAP_CASE=case_a REDCAP_POLICY_HOST_FILE=./control/redcap_policy_case_a.yaml MMTC_IMAGE_TAG=latest MMTC_GNB_IMAGE_NAME=oai-gnb MMTC_NRUE_IMAGE_NAME=oai-nr-ue bash redcap_interface/redcap_mmtc_smoke_validation.sh
  ```

## Required Status
- [source build PASS/FAIL/NA]: PASS
- [unit test PASS/FAIL/NA]: NA
- [container image rebuilt or not]: rebuilt
- [RFsim runtime PASS/FAIL/NA]: PASS
- [exit 139]: absent
- [Code Coverage]: NA

## Evidence
- [Build Log]: `test_log/build_logs/build_nr-softmodem_nr-uesoftmodem_2026-06-04_rrc-inactive-gate1-trigger.log`
- [Image Rebuild Log]: `test_log/build_logs/rebuild_local_oai_images_2026-06-04_rrc-inactive-gate1.log`
- [Image Marker Log]: `test_log/compiler_logs/rrc_inactive_gate1_image_markers_2026-06-04.log`
- [RFsim Console Log]: `test_log/compiler_logs/rrc_inactive_gate1_rfsim_2026-06-04.log`
- [Generated CN DB Overlay]: `test_log/runtime_configs/oai_db_mmtc_29.sql`
- [Generated CN Compose Overlay]: `test_log/runtime_configs/oai-cn5g_mmtc_29.override.yml`
- [gNB Docker Log]: `test_log/compiler_logs/mmtc_smoke_2026-06-04_08-45-25_gnb.log`
- [UE1 Docker Log]: `test_log/compiler_logs/mmtc_smoke_2026-06-04_08-45-25_ue1_docker.log`
- [gNB State Log]: `test_log/compiler_logs/mmtc_smoke_2026-06-04_08-45-25_gnb_state.log`
- [UE1 State Log]: `test_log/compiler_logs/mmtc_smoke_2026-06-04_08-45-25_ue1_state.log`

## Marker Result
| Marker | Source | Result |
|---|---|---|
| `MMTC Gate 1 trigger` | gNB log line 563 | PASS |
| `RRCRelease suspendConfig selected` | gNB log line 564 | PASS |
| `RRCRelease suspendConfig received` | UE1 log line 482 | PASS |
| `RRC_INACTIVE entered` | UE1 log line 483 | PASS |
| `exit 139` / `SIGSEGV` / `child exit rc=139` | negative scan | PASS, no match |

## Runtime Summary
- [Smoke Summary]: `sample=1 running=1 attach=1 pdu=1 tun=1 forward_ping_ok=1 reverse_ping_ok=0 iperf_ul_ok=0 iperf_ul_run=0 gnb_restart=0 failures=0 mode=serial`
- [UE TUN]: `10.0.0.2/24`
- [Forward Ping]: `1 packets transmitted, 1 received, 0% packet loss`
- [gNB State]: running, healthy, `RestartCount=0`, `ExitCode=0`
- [UE1 State]: running, healthy, `ExitCode=0`

## Modification Record
- [Modification Point] -> `openair2/RRC/NR/rrc_gNB_NGAP.c`
  [Reason] -> RFsim needed a deterministic Gate 1 trigger to emit `RRCRelease.suspendConfig`.
  [Before vs. After Comparison] -> Before: no caller reached `rrc_gNB_generate_RRCRelease_suspend()` in smoke validation; After: `MMTC_RRC_INACTIVE_GATE1_TRIGGER=1` sends suspend release after PDU session setup response.
  [Discussion Point] -> Trigger is validation-only and default disabled; Gate 2 must replace this with normal Resume/Reestablishment behavior.
- [Modification Point] -> `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/scripts/generate_mmtc_overlay.sh`
  [Reason] -> The smoke script regenerates `docker-compose.mmtc.yml` before runtime.
  [Before vs. After Comparison] -> Before: regenerated overlay could drop policy/control mounts and Gate 1 env; After: generated overlay preserves `[Case A]` policy mount, control contract mount, and `MMTC_RRC_INACTIVE_GATE1_TRIGGER`.
  [Discussion Point] -> Keep `docker-compose.mmtc.yml` as runtime entrypoint only; policy content remains in `control/redcap_policy_case_a.yaml`.

## 3GPP Specification Mapping
- [RRC_INACTIVE]: TS 38.331 `⚠ Needs Verification` for exact clause number in local spec cache.
- [RRCRelease suspendConfig]: TS 38.331 `⚠ Needs Verification` for exact clause number in local spec cache.
- [RedCap UE capability context]: TS 38.306 `⚠ Needs Verification`; not directly changed in Gate 1.

## Educational Learning Report
- [Technical Background]: `RRCRelease.suspendConfig` is the RRC message element that moves a UE from `[RRC_CONNECTED]` toward `[RRC_INACTIVE]` while preserving enough context for later resume. Gate 1 validates only the controlled transition and crash removal. It does not yet prove full Resume, configured grant SDT, or TA/RSRP fallback behavior.
- [Key C Functions / Data Structures]:
  - `do_NR_RRCRelease_suspend()`
  - `rrc_gNB_generate_RRCRelease_suspend()`
  - `nr_rrc_enter_inactive_from_suspend()`
  - `NR_RRCRelease_t`
  - `NR_SuspendConfig_t`
- [Test Results Summary Table]:
  - [Build]: PASS
  - [Image Rebuild]: PASS
  - [RFsim Marker]: PASS
  - [Crash Scan]: PASS
- [Practice Exercises]:
  - [Basic] Explain why replacing `AssertFatal` with a controlled state transition is required before testing Resume.
  - [Applied] Trace the log sequence from PDU session setup to `RRC_INACTIVE entered`.
  - [Advanced] Propose the next Gate 2 validation marker set for `RRCResumeRequest`, `RRCResume`, and `RRCResumeComplete`.
