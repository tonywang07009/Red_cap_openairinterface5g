# Validation Notes

## Static Validation

| Check | Result |
|---|---|
| `bash -n redcap_interface/bash_library/fc_doc_newcomer_gate_check.sh` | PASS |
| `bash redcap_interface/bash_library/fc_doc_newcomer_gate_check.sh` | PASS |
| `bash redcap_interface/validate_redcap_interface.sh` | PASS |
| `openspec validate redcap-docs-bilingual-onboarding-v2` | PASS |
| `git diff --check -- README.md README.en.md README.zh-TW.md openspec/changes/redcap-docs-bilingual-onboarding-v2 redcap_doc redcap_interface redcap_library` | PASS |

## Runtime Gate Status

The full 29 UE newcomer runtime gate was executed and passed on 2026-06-30.

## Runtime Gate Evidence

| Check | Evidence |
|---|---|
| Docker/CN5G preflight | `docker ps -a` succeeded; `/home/tonywang/OAI/oai-cn5g/docker-compose.yaml` exists. |
| gNB local build | `test_log/build_logs/build_nr-softmodem_2026-06-30_14-53-06_docgate.log` |
| nrUE local build | `test_log/build_logs/build_nr-uesoftmodem_2026-06-30_14-53-13_docgate.log` |
| Local image rebuild | `test_log/build_logs/rebuild_local_oai_images_2026-06-30_14-53-58_docgate.log` |
| gNB image inspection | `bash redcap_interface/redcap_inspect_gnb_image.sh` passed. |
| 29 UE stage scan summary | `test_log/compiler_logs/mmtc_stage_scan_2026-06-30_14-57-26_summary.log` |
| 29 UE detailed log | `test_log/compiler_logs/mmtc_stage_scan_2026-06-30_14-57-26_ue29.log` |

## Runtime Gate Result

```text
[STAGE] ue=29 status=PASS rc=0 [SUMMARY] sample=29 running=29 attach=29 pdu=29 tun=29 forward_ping_ok=29 reverse_ping_ok=0 iperf_ul_ok=0 iperf_ul_run=0 gnb_restart=0 failures=0 mode=parallel
```

## Newcomer Feedback

- Step: full newcomer runtime gate.
- Command: documented 29 UE stage scan from `redcap_newcomer_runtime_gate.zh-TW.md`.
- Expected: static documentation gate passes and runtime summary contains all required markers.
- Actual: PASS.
- Log path: `test_log/compiler_logs/mmtc_stage_scan_2026-06-30_14-57-26_summary.log`.
- Unclear wording: none observed during this run.
- Suggested document fix: none required from this run.
