# RRC_INACTIVE SDT Gate 3 Rebuilt RFsim Gate2-OFF Validation

## Conclusion
- Result: Gate 3 Gate2-OFF RFsim sample UE1 now shows the full validation marker ladder.
- Status: PASS for single-sample RFsim validation; keep broader Gate 3 status as sample-validated until repeated and multi-UE runs are done.
- Scope: Rebuilt `oai-gnb:latest` and `oai-nr-ue:latest`, reran Gate 2 OFF with `MMTC_RRC_INACTIVE_GATE3_CG_CONFIG=1`, and checked crash/error markers.

## Required Project Fields
- Project Path: `agent_doc/Project_management/projects/redcap_rrc_inactive_sdt_oran_control_v1/project_plan.md`
- [Case]: A
- [Gate]: 3
- [source build PASS/FAIL/NA]: PASS
- [unit test PASS/FAIL/NA]: NA, no focused unit test exists for CG-SDT scheduler/classifier.
- [Docker image rebuild PASS/FAIL/NA]: PASS
- [RFsim runtime PASS/FAIL/NA]: PASS for sample UE1 Gate2-OFF marker ladder.
- [exit 139]: absent.

## Validation Commands
1. `rtk bash -lc 'CCACHE_DIR=/tmp/ccache CCACHE_TEMPDIR=/tmp/ccache-tmp cmake --build --preset default --target nr-softmodem nr-uesoftmodem ...'`
2. `rtk bash -lc 'redcap_interface/redcap_rebuild_local_oai_images.sh ...'`
3. `rtk bash -lc 'MMTC_TOTAL_UES=29 MMTC_SAMPLE_UES="1" MMTC_RRC_INACTIVE_GATE1_TRIGGER=1 MMTC_RRC_INACTIVE_GATE2_RESUME_TRIGGER=0 MMTC_RRC_INACTIVE_GATE3_CG_CONFIG=1 ... bash redcap_interface/redcap_mmtc_smoke_validation.sh ...'`

## Logs
| Item | Result | Log |
|---|---|---|
| Source build | PASS | `test_log/build_logs/build_nr-softmodem_nr-uesoftmodem_2026-06-12_15-14-47_gate3-inactive-only-cg.log` |
| Docker image rebuild | PASS | `test_log/build_logs/rebuild_local_oai_images_2026-06-12_15-15-09_gate3-inactive-only-cg.log` |
| Gate2-OFF RFsim smoke | PASS | `test_log/compiler_logs/mmtc_gate3_inactive_cg_gate2off_inactive_only_2026-06-12_15-17-34.log` |
| UE runtime log | PASS | `test_log/compiler_logs/mmtc_smoke_2026-06-12_15-17-34_ue1_docker.log` |
| gNB runtime log | PASS | `test_log/compiler_logs/mmtc_smoke_2026-06-12_15-17-34_gnb.log` |

## RFsim Summary
| Metric | Result |
|---|---:|
| sample | 1 |
| running | 1 |
| attach | 1 |
| PDU session | 1 |
| TUN | 1 |
| forward ping | 1 |
| gNB restart | 0 |
| failures | 0 |

## Marker Counts
| UE Marker | Count |
|---|---:|
| `RRCRelease suspendConfig received` | 1 |
| `RRC_INACTIVE entered` | 1 |
| `configuredGrantConfig parsed` | 3 |
| `entered inactive for cg-SDT scheduling` | 1 |
| `inactive probe no cg-SDT config` | 0 |
| `inactive probe no CG occasion` | 205 |
| `CG occasion has no pending LCID data` | 3763 |
| `cg-SDT autonomous CG PUSCH scheduled` | 33 |
| `cg-SDT PUSCH tx` | 33 |
| `configuredGrantConfig not supported` | 0 |
| `exit 139` | 0 |
| `RLC E max RETX` | 0 |
| `RRC moved into IDLE state` | 0 |
| `RRC_CONNECTION_FAILURE` | 0 |

| gNB Marker | Count |
|---|---:|
| `configuredGrantConfig validation setup` | 2 |
| `time_domain_offset=112` | 2 |
| `cg-SDT PUSCH rx candidate` | 173 |
| `configuredGrantConfig not supported` | 0 |
| `exit 139` | 0 |
| `RLC E max RETX` | 0 |

## Key Evidence
- UE sequence:
  - `RRCRelease suspendConfig received` at UE log line 517.
  - `RRC_INACTIVE entered` at UE log line 519.
  - `entered inactive for cg-SDT scheduling ... current_bwp_id 1 has_cg_sdt 1 periodicity 9 time_domain_offset 112` at UE log line 521.
  - First `cg-SDT autonomous CG PUSCH scheduled` at UE log line 9877.
  - First `cg-SDT PUSCH tx` at UE log line 9878.
- gNB sequence:
  - `configuredGrantConfig validation setup ... time_domain_offset=112` at gNB log line 494.
  - `cg-SDT PUSCH rx candidate` begins at gNB log line 513.
- Safety markers:
  - No `exit 139`.
  - No `RLC E max RETX`.
  - No `RRC_CONNECTION_FAILURE`.

## Changes Validated
- [Modification Point] -> gNB Gate 3 validation configured grant offset.
- [Reason] -> Offset `0` placed the CG occasion on a slot the UE UL scheduler did not process in the RFsim TDD pattern.
- [Before vs. After Comparison] -> Before: `timeDomainOffset=0`, UE repeatedly logged `inactive probe no CG occasion`; After: `timeDomainOffset=112` aligns the validation CG occasion to slot offset 8 and UE emits CG schedule/tx markers.
- [Discussion Point] -> This is validation-oriented alignment for the local RFsim TDD profile; broader profile handling still needs a scheduler/config abstraction before upstream-quality cleanup.

- [Modification Point] -> UE autonomous CG scheduling gate.
- [Reason] -> The offset fix exposed premature CG scheduling while UE was still connected, which disrupted SRB1 attach/setup.
- [Before vs. After Comparison] -> Before: `nr_ue_try_schedule_cg_sdt_pusch()` could run in `UE_CONNECTED`; After: it only runs when the UE MAC has inactive state plus cg-SDT config.
- [Discussion Point] -> Final RFsim shows CG schedule/tx only after `RRC_INACTIVE entered`, preserving attach and ping baseline.

## Follow-up
- Run at least one repeated sample UE1 Gate2-OFF validation to check stability.
- Run a small sampled multi-UE validation before promoting Gate 3 beyond sample-validated.
- If stability holds, update the project plan/milestone status from Gate 3 in-progress to a stronger validation state.
