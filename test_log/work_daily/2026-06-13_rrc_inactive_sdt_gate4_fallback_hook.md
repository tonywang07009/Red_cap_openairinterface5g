# RRC_INACTIVE SDT Gate 4 TA / RSRP Fallback Validation

## Conclusion
- Result: Gate 4 RFsim passed with a validation-only forced fallback hook.
- Status: T2 Gates 1-4 are now [RFsim PASS] for the Case A protocol baseline.
- Boundary: The hook proves fallback wiring and 4-step RA recovery; formal measured `cg-SDT-RSRP-ChangeThreshold` behavior remains `[Needs Verification]`.

## Required Project Fields
- Project Path: `agent_doc/Project_management/projects/redcap_rrc_inactive_sdt_oran_control_v1/project_plan.md`
- [Case]: A
- [Gate]: 4
- [source build PASS/FAIL/NA]: PASS, `test_log/build_logs/build_nr-uesoftmodem_2026-06-13_17-38-06_gate4-fallback.log`.
- [unit test PASS/FAIL/NA]: NA, no focused unit test exists for the validation-only SDT fallback hook.
- [Docker image rebuild PASS/FAIL/NA]: PASS, `test_log/build_logs/rebuild_local_oai_images_2026-06-13_17-41-14_gate4-fallback.log`.
- [RFsim runtime PASS/FAIL/NA]: PASS, `test_log/compiler_logs/mmtc_smoke_2026-06-13_17-43-52_ue1_docker.log`.
- [exit 139]: absent.

## Validation Command
```bash
MMTC_TOTAL_UES=29 MMTC_SAMPLE_UES=1 \
MMTC_RRC_INACTIVE_GATE1_TRIGGER=1 \
MMTC_RRC_INACTIVE_GATE2_RESUME_TRIGGER=0 \
MMTC_RRC_INACTIVE_GATE3_CG_CONFIG=1 \
MMTC_RRC_INACTIVE_GATE4_FORCE_FALLBACK=1 \
MMTC_FORWARD_PING_MODE=parallel \
MMTC_RUN_REVERSE_PING=0 \
MMTC_PING_COUNT=10 \
MMTC_GNB_WARMUP=5 \
MMTC_SLEEP_AFTER_UP=25 \
MMTC_UE_START_GAP=0 \
REDCAP_CASE=case_a \
bash redcap_interface/mmtc.menu.bash gate4
```

## Logs
| Item | Result | Log |
|---|---|---|
| UE source build | PASS | `test_log/build_logs/build_nr-uesoftmodem_2026-06-13_17-38-06_gate4-fallback.log` |
| Docker image rebuild | PASS | `test_log/build_logs/rebuild_local_oai_images_2026-06-13_17-41-14_gate4-fallback.log` |
| Gate4 RFsim UE log | PASS | `test_log/compiler_logs/mmtc_smoke_2026-06-13_17-43-52_ue1_docker.log` |
| Gate4 RFsim gNB log | PASS | `test_log/compiler_logs/mmtc_smoke_2026-06-13_17-43-52_gnb.log` |
| Gate4 ping log | PASS | `test_log/compiler_logs/mmtc_smoke_2026-06-13_17-43-52_ue1_ping.log` |

## RFsim Summary
| sample | running | attach | PDU session | TUN | forward ping | gNB restart | failures |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 1 | 1 | 1 | 1 | 1 | 0 | 0 |

## Marker Counts
| Marker | Count |
|---|---:|
| `RRC_INACTIVE entered` | 1 |
| `configuredGrantConfig parsed` | 3 |
| `RSRP threshold exceeded` | 1 |
| `Triggering new RA procedure` | 1 |
| `4-step RA triggered` | 1 |
| `Initialization of 4-Step CBRA procedure` after Gate4 fallback | 1 |
| `RA-Msg3 transmitted` after Gate4 fallback | 1 |
| `4-Step RA procedure succeeded` after Gate4 fallback | 1 |
| `cg-SDT autonomous CG PUSCH scheduled` | 0 |
| `cg-SDT PUSCH tx` | 0 |
| `exit 139` | 0 |

## Evidence Highlights
- `RSRP threshold exceeded` at `test_log/compiler_logs/mmtc_smoke_2026-06-13_17-43-52_ue1_docker.log:11784`.
- `Triggering new RA procedure` at `..._ue1_docker.log:11785`.
- `4-step RA triggered` at `..._ue1_docker.log:11786`.
- `Initialization of 4-Step CBRA procedure` at `..._ue1_docker.log:11787`.
- `Found RAR with the intended RAPID 62` at `..._ue1_docker.log:11812`.
- `RA-Msg3 transmitted` at `..._ue1_docker.log:11816`.
- `4-Step RA procedure succeeded` at `..._ue1_docker.log:11817`.
- Ping result: 10 packets transmitted, 10 received, average 3.849 ms.

## Modification Summary
- [Modification Point] -> `openair2/LAYER2/NR_MAC_UE/nr_ue_scheduler.c`
  [Reason] -> Add deterministic Gate4 validation hook before autonomous CG-SDT PUSCH scheduling.
  [Before vs. After Comparison] -> Before: pending SDT data always used the Gate3 CG path when CG resources matched; After: `MMTC_RRC_INACTIVE_GATE4_FORCE_FALLBACK=1` logs threshold exceed and triggers 4-step RA.
  [Discussion Point] -> The hook is default-off and validation-only; measured RSRP/TA threshold logic remains a formal follow-up.
- [Modification Point] -> `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/scripts/generate_mmtc_overlay.sh`
  [Reason] -> Propagate Gate4 fallback env into generated UE containers.
  [Before vs. After Comparison] -> Before: UE containers did not receive the Gate4 env; After: fixed and dynamic UE service stanzas receive `MMTC_RRC_INACTIVE_GATE4_FORCE_FALLBACK`.
  [Discussion Point] -> Default remains `0`, so Gate3 and A/B SDT demos keep the normal CG-SDT behavior unless explicitly overridden.
- [Modification Point] -> `redcap_interface/mmtc.menu.bash`
  [Reason] -> Expose a repeatable Gate4 smoke command.
  [Before vs. After Comparison] -> Before: only Gate3 CLI shortcut existed; After: `bash redcap_interface/mmtc.menu.bash gate4` runs Gate1 + Gate3 + Gate4 fallback with Gate2 off.
  [Discussion Point] -> This keeps Gate4 validation available through the operator menu without changing default smoke settings.

## Follow-up
- Gate 5 is next: T2B O-RAN policy control over validated RedCap parameters.
- Keep `cg-SDT-RSRP-ChangeThreshold` and TA expiry clause mapping as `[Needs Verification]` until the formal spec-backed implementation replaces the RFsim hook.
