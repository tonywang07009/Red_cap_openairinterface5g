# M5 mMTC Runtime Scaling

## Scope
- Compose-based RFsim mMTC runtime.
- Fixed-UE and staged multi-UE attach, PDU session, and UL user-plane validation.
- RA/Msg4 scheduler behavior under RedCap mMTC load.

## Out of Scope
- New C scheduler fixes before root-cause confirmation.
- New XML scenario files.
- O-RAN xApp/rApp/dApp SDK implementation.

## 3GPP Spec Mapping
- TS 38.321 Section 5.1 — Random Access procedure.
- TS 38.321 Section 5.1.4 — RAR reception. Exact subsection: [Needs Verification].
- TS 38.321 Section 5.1.5 — Contention Resolution. Exact subsection: [Needs Verification].
- TS 38.331 RedCap initial BWP and RACH feature combination preamble fields: [Needs Verification].

## Runtime Source of Truth
- Primary scenario directory:
  - `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/`
- Primary fixed-UE compose file:
  - `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/docker-compose.yml`
- Primary mMTC compose overlay:
  - `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/docker-compose.mmtc.yml`
- Primary mMTC script:
  - `ci-scripts/redcap_mmtc_smoke_validation.sh`
- Runtime-generated config path:
  - `test_log/runtime_configs/`

## Implementation Tasks
- `M5-T1`: fixed-UE UE2 user-plane blocker RCA.
- `M5-T2`: scalable mMTC staged validation.
- `M5-T3`: RA/Msg4 scheduler instrumentation after Case B A/B confirmation.

## Flow Validation
- Msg1 RedCap preamble marking must be visible in gNB logs.
- Msg2 scheduler path must report Case A or Case B explicitly.
- UE RA-RNTI monitoring must match the gNB Msg2 BWP domain.
- Msg3 and Msg4 must complete contention resolution.
- PDU session and `oaitun_ue1` must exist before ping validation.

## System Unit Tests
- Unit tests are secondary for this milestone.
- Use existing M3 unit tests when C code touches BWP/CORESET/RA helpers.
- Mark `[unit test N/A]` for pure runtime-script validation.

## RFsim Runtime Tests
- `RT-M5-002`: fixed UE1/UE2 RedCap RFsim attach and ping.
- `RT-M5-030`: 30 UE staged mMTC attach, PDU session, tunnel, and forward ping.
- `RT-M5-032`: 32 UE staged mMTC validation.
- `RT-M5-064`: 64 UE staged mMTC validation.
- `RT-M5-CASEB-030`: 30 UE staged mMTC Case B A/B validation.

## Current Evidence
- 2026-05-07 Case B 30 UE rerun:
  - Log: `test_log/compiler_logs/mmtc_smoke_30ue_caseb_rerun_2026-05-07_13-29-43_escalated.log`.
  - gNB log: `test_log/compiler_logs/mmtc_smoke_2026-05-07_13-29-43_gnb.log`.
  - Result: `30/30` running / attach / PDU / tunnel / forward ping.
  - gNB restart count: `0`.
  - UE PUCCH BWP0 common fallback env: `MMTC_PUCCH_COMMON_FALLBACK_BWP0=1`.
  - `[RedCap RA][gNB Msg2 gate]`: `153`.
  - `[RedCap RA][gNB Msg2 DCI]`: `30`.
  - Msg2 CCE allocation for RedCap RA DCI: `30 x cce=0 agg=4`.
  - `[RedCap RA][gNB Msg2 window fail]`: `6`.
  - `[RedCap RA][gNB Msg2 vrb_map fail]`: `0`.
  - `[RedCap RA][gNB Msg4 vrb_map fail]`: `0`.
  - `RA Contention Resolution timer expired`: `0`.
  - `Received Ack of Msg4` / `CBRA procedure succeeded`: `30`.
  - UE `RAR reception failed`: `6` transient retries, with final attach/PDU/tunnel/ping all PASS.
  - UE `pucch_ResourceCommon is NULL`: `0`.
  - `Received a RAR-Msg2 but LDPC decode failed`: `0`.
  - Ping logs: `30/30` show `0% packet loss`.
- Latest staged 30 UE result:
  - `26/30` attach/PDU/tunnel/ping.
  - Failed UEs: `UE11`, `UE20`, `UE26`, `UE29`.
- Latest Case B staged 30 UE result:
  - Runtime config: `test_log/runtime_configs/gnb.redcap_mmtc_case-b_2026-05-02_12-35-01.yaml`.
  - Log: `test_log/compiler_logs/mmtc_smoke_30ue_caseb_2026-05-02_12-36-39.log`.
  - `27/30` attach/PDU/tunnel/ping.
  - Failed UEs: `UE21`, `UE27`, `UE28`.
- gNB failure counters:
  - Msg2 RA window expiry.
  - Msg2 `vrb_map` pressure.
  - Msg4 `vrb_map` pressure.
  - Msg4 contention resolution failure.
- Current config finding:
  - Case B injection confirms `coreset_id=1` / `BWP51` path under 30 UE load.
  - Case B still fails before full 30 UE completion, so the blocker is now classified as RA/Msg4 scheduler load rather than BWP/DCI/LDPC alignment.
- Latest Case B counters:
  - `[RedCap RA][gNB Msg2 gate]`: `23508`.
  - `[RedCap RA][gNB Msg2 DCI]`: `3912`.
  - Msg2 RA `vrb_map` failures: `641`.
  - Msg4 `vrb_map` failures: `121`.
  - RA window expiry: `2148`.
  - UE-side Msg2 LDPC decode failure: `0`.
- Latest instrumented Case B result:
  - Log: `test_log/compiler_logs/mmtc_smoke_30ue_caseb_instrumented_2026-05-02_12-58-04.log`.
  - `27/30` attach/PDU/tunnel/ping.
  - Failed UEs: `UE25`, `UE29`, `UE30`.
  - gNB restart count: `0`.
  - `[RedCap RA][gNB Msg2 DCI]`: `4048`.
  - `[RedCap RA][gNB Msg2 gate]`: `21746`.
  - `[RedCap RA][gNB Msg2 window fail]`: `878`.
  - `[RedCap RA][gNB Msg2 vrb_map fail]`: `488`.
  - `[RedCap RA][gNB Msg4 vrb_map fail]`: `131`.
  - `RA Contention Resolution timer expired`: `518`.
  - UE-side Msg2 LDPC decode failure: `0`.
  - All instrumented `occupied_prbs` samples are `48`, confirming full-symbol PRB pressure rather than BWP/DCI decode mismatch.
  - Msg2 window failures are mostly `diff=21` with `window=20`, indicating that one missed Msg2 opportunity can push the RA attempt outside the configured response window.
  - Msg4 failures show `rb_size=48` / `occupied_prbs=48`, indicating that Msg4 PDSCH allocation is too wide for the loaded RedCap RA slot.

## Completion Criteria
- [RFsim UE/gNB/CN runtime PASS]
- [30 UE staged PASS] Case B 30 UE passed on 2026-05-07.
- [32 UE staged PASS]
- [64 UE staged target evaluated]
- [failure counters summarized]
- [logs preserved under `test_log/compiler_logs/`]
- [daily work log written]
