# RRC_INACTIVE SDT Gate 3 Repeat and Sampled Multi-UE Validation

## Conclusion
- Result: Gate 3 Gate2-OFF RFsim repeat passed for sample UE1 and sampled UE1-3.
- Status: Gate 3 is now [RFsim sampled multi-UE PASS].
- Boundary: Full 29 UE stress is optional follow-up; Gate 4 TA / RSRP threshold fallback remains pending.

## Required Project Fields
- Project Path: `agent_doc/Project_management/projects/redcap_rrc_inactive_sdt_oran_control_v1/project_plan.md`
- [Case]: A
- [Gate]: 3
- [source build PASS/FAIL/NA]: NA in this run; prior source build PASS is `test_log/build_logs/build_nr-softmodem_nr-uesoftmodem_2026-06-12_15-14-47_gate3-inactive-only-cg.log`.
- [unit test PASS/FAIL/NA]: NA, no focused unit test exists for CG-SDT scheduler/classifier.
- [Docker image rebuild PASS/FAIL/NA]: NA in this run; reused rebuilt local images from `test_log/build_logs/rebuild_local_oai_images_2026-06-12_15-15-09_gate3-inactive-only-cg.log`.
- [RFsim runtime PASS/FAIL/NA]: PASS for repeat UE1 and sampled UE1-3 Gate2-OFF marker ladder.
- [exit 139]: absent.

## Validation Commands
1. `MMTC_TOTAL_UES=29 MMTC_SAMPLE_UES=1 MMTC_RRC_INACTIVE_GATE1_TRIGGER=1 MMTC_RRC_INACTIVE_GATE2_RESUME_TRIGGER=0 MMTC_RRC_INACTIVE_GATE3_CG_CONFIG=1 MMTC_FORWARD_PING_MODE=parallel MMTC_RUN_REVERSE_PING=0 MMTC_PING_COUNT=10 MMTC_GNB_WARMUP=5 MMTC_SLEEP_AFTER_UP=25 MMTC_UE_START_GAP=0 REDCAP_CASE=case_a bash redcap_interface/redcap_mmtc_smoke_validation.sh`
2. `MMTC_TOTAL_UES=29 MMTC_SAMPLE_UES=1,2,3 MMTC_RRC_INACTIVE_GATE1_TRIGGER=1 MMTC_RRC_INACTIVE_GATE2_RESUME_TRIGGER=0 MMTC_RRC_INACTIVE_GATE3_CG_CONFIG=1 MMTC_FORWARD_PING_MODE=parallel MMTC_RUN_REVERSE_PING=0 MMTC_PING_COUNT=10 MMTC_GNB_WARMUP=5 MMTC_SLEEP_AFTER_UP=25 MMTC_UE_START_GAP=3 REDCAP_CASE=case_a bash redcap_interface/redcap_mmtc_smoke_validation.sh`

## Logs
| Item | Result | Log |
|---|---|---|
| Repeat UE1 RFsim smoke | PASS | `test_log/compiler_logs/mmtc_smoke_2026-06-13_14-49-47_ue1_docker.log` |
| Repeat UE1 gNB log | PASS | `test_log/compiler_logs/mmtc_smoke_2026-06-13_14-49-47_gnb.log` |
| Sampled UE1-3 RFsim smoke | PASS | `test_log/compiler_logs/mmtc_smoke_2026-06-13_14-52-24_ue1_docker.log`, `..._ue2_docker.log`, `..._ue3_docker.log` |
| Sampled UE1-3 gNB log | PASS | `test_log/compiler_logs/mmtc_smoke_2026-06-13_14-52-24_gnb.log` |

## RFsim Summary
| Run | running | attach | PDU session | TUN | forward ping | gNB restart | failures |
|---|---:|---:|---:|---:|---:|---:|---:|
| UE1 repeat | 1 | 1 | 1 | 1 | 1 | 0 | 0 |
| UE1-3 sampled | 3 | 3 | 3 | 3 | 3 | 0 | 0 |

## Marker Counts
| Marker | UE1 repeat |
|---|---:|
| `RRCRelease suspendConfig received` | 1 |
| `RRC_INACTIVE entered` | 1 |
| `configuredGrantConfig parsed` | 3 |
| `entered inactive for cg-SDT scheduling` | 1 |
| `cg-SDT autonomous CG PUSCH scheduled` | 33 |
| `cg-SDT PUSCH tx` | 33 |
| `configuredGrantConfig not supported` | 0 |
| `exit 139` | 0 |
| `RLC E max RETX` | 0 |
| `RRC_CONNECTION_FAILURE` | 0 |
| `RRC moved into IDLE state` | 0 |

| Marker | UE1 | UE2 | UE3 |
|---|---:|---:|---:|
| `RRCRelease suspendConfig received` | 1 | 1 | 1 |
| `RRC_INACTIVE entered` | 1 | 1 | 1 |
| `configuredGrantConfig parsed` | 3 | 3 | 3 |
| `entered inactive for cg-SDT scheduling` | 1 | 1 | 1 |
| `cg-SDT autonomous CG PUSCH scheduled` | 33 | 33 | 33 |
| `cg-SDT PUSCH tx` | 33 | 33 | 33 |
| `configuredGrantConfig not supported` | 0 | 0 | 0 |
| `exit 139` | 0 | 0 | 0 |
| `RLC E max RETX` | 0 | 0 | 0 |
| `RRC_CONNECTION_FAILURE` | 0 | 0 | 0 |
| `RRC moved into IDLE state` | 0 | 0 | 0 |

| gNB Marker | UE1 repeat | UE1-3 sampled |
|---|---:|---:|
| `configuredGrantConfig validation setup` | 2 | 6 |
| `time_domain_offset=112` | 2 | 6 |
| `cg-SDT PUSCH rx candidate` | 144 | 217 |
| `configuredGrantConfig not supported` | 0 | 0 |
| `exit 139` | 0 | 0 |
| `RLC E max RETX` | 0 | 0 |

## Evidence Highlights
- UE1 repeat first ladder:
  - `RRCRelease suspendConfig received` at `mmtc_smoke_2026-06-13_14-49-47_ue1_docker.log:515`.
  - `RRC_INACTIVE entered` at `..._ue1_docker.log:517`.
  - `entered inactive for cg-SDT scheduling` at `..._ue1_docker.log:519`.
  - First `cg-SDT autonomous CG PUSCH scheduled` at `..._ue1_docker.log:10421`.
  - First `cg-SDT PUSCH tx` at `..._ue1_docker.log:10422`.
- Sampled UE1-3 gNB marker:
  - `configuredGrantConfig validation setup` count is `6`.
  - `cg-SDT PUSCH rx candidate` count is `217`.

## Follow-up
- Update project status from Gate 3 in-progress to Gate 3 sampled multi-UE PASS.
- Next protocol gate is Gate 4: TA / RSRP threshold fallback to 4-step RA.
- Keep formal configured-grant classifier semantics as `[Needs Verification]` until spec/code cleanup beyond the validation marker.
