# 2026-06-11 RRC_INACTIVE SDT Gate 3 configuredGrantConfig Parse Slice

- Project Path: `agent_doc/Project_management/projects/redcap_rrc_inactive_sdt_oran_control_v1/project_plan.md`
- [Case]: A
- [Gate]: 3
- [source build PASS/FAIL/NA]: PASS, `nr-uesoftmodem` and `nr-softmodem`
- [unit test PASS/FAIL/NA]: [NA] no focused unit test exists for UE MAC RRC configured grant parsing
- [RFsim runtime PASS/FAIL/NA]: PASS for `configuredGrantConfig parsed` smoke only; full Gate 3 remains not PASS
- [exit 139]: absent in `mmtc_gate3_cg_config_smoke_2026-06-11_15-21-50.log`

## Scope
- [Goal]: Continue from Gate 3 inventory and implement the first UE MAC `configuredGrantConfig` parse/store/release slice plus a safe gNB confirmation trace and RFsim config-parse smoke.
- [Boundary]: This slice removes the UE assert path, stores a deep ASN.1 copy in `NR_UE_UL_BWP.configuredGrantConfig`, adds a validation-only gNB RRC configured grant setup hook, passes the hook through RFsim compose, and logs only the gNB configured grant confirmation MAC CE.
- [Spec Status]: TS 38.321 / TS 38.331 clause mapping remains `[Needs Verification]`.

## Modification 1
- [Modification Point] -> `openair2/LAYER2/NR_MAC_UE/config_ue.c`
- [Reason] -> Gate 3 cannot proceed while `configure_dedicated_BWP_ul()` asserts on `ul_dedicated->configuredGrantConfig`.
- [Before vs. After Comparison] -> Before: UE aborts on `configuredGrantConfig not supported`; After: UE handles `release` and `setup`, deep-copies `NR_ConfiguredGrantConfig`, and logs `configuredGrantConfig parsed`.
- [Discussion Point] -> This proves UE parse/store ownership only; it does not prove `cg-SDT PUSCH tx` or `cg-SDT PUSCH rx`.

## Modification 2
- [Modification Point] -> `openair2/LAYER2/NR_MAC_UE/nr_ue_scheduler.c`
- [Reason] -> The scheduler already returned early when configured grant and SR mask suppress SR, but Gate 3 had no trace separating this from actual CG PUSCH transmission.
- [Before vs. After Comparison] -> Before: silent return on `configuredGrantConfig && lc_SRMask`; After: same behavior with `current_UL_BWP` guard and `configured grant suppresses SR` marker.
- [Discussion Point] -> This marker is a scheduling-decision trace only; it is not `cg-SDT PUSCH tx`.

## Modification 3
- [Modification Point] -> `openair2/LAYER2/NR_MAC_UE/nr_ue_scheduler.c`
- [Reason] -> `cg-SDT PUSCH tx` must not be reported until a real autonomous CG scheduler exists.
- [Before vs. After Comparison] -> Before: SR suppression could be confused with CG-SDT TX progress; After: if the stored configured grant includes `cg_SDT_Configuration_r17`, UE logs `cg-SDT CG scheduler missing`.
- [Discussion Point] -> This is an explicit blocker marker, not a PASS marker.

## Modification 4
- [Modification Point] -> `openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_ulsch.c`
- [Reason] -> Gate 3 needs a gNB-side marker for the configured grant confirmation MAC CE before any later `cg-SDT PUSCH rx` claim.
- [Before vs. After Comparison] -> Before: `UL_SCH_LCID_CONFIGURED_GRANT_CONFIRMATION` was decoded and ignored silently; After: gNB logs `configured grant confirmation received` with RNTI, frame.slot, bytes, and HARQ PID.
- [Discussion Point] -> This proves only TS 38.321 configured grant confirmation CE visibility; it is not a reliable CG-SDT RX classifier.

## Modification 5
- [Modification Point] -> `openair2/LAYER2/NR_MAC_gNB/nr_radio_config.c`
- [Reason] -> UE parse support cannot be exercised in RFsim while gNB always sets `ubwp->bwp_Dedicated->configuredGrantConfig = NULL`.
- [Before vs. After Comparison] -> Before: additional UL BWP dedicated config never carried `configuredGrantConfig`; After: `MMTC_RRC_INACTIVE_GATE3_CG_CONFIG=1` enables a validation-only Type1 configured grant skeleton with `cg_SDT_Configuration_r17` presence.
- [Discussion Point] -> This is an RRC configuration hook only; it does not implement autonomous UE CG PUSCH TX or gNB CG PUSCH RX scheduling.

## Modification 6
- [Modification Point] -> `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/docker-compose.mmtc.yml` and `scripts/generate_mmtc_overlay.sh`
- [Reason] -> RFsim smoke regenerates the mMTC overlay before launch, so the Gate 3 env must exist in both the generated file and the generator template.
- [Before vs. After Comparison] -> Before: `MMTC_RRC_INACTIVE_GATE3_CG_CONFIG` could not reach the gNB container; After: the gNB service receives `MMTC_RRC_INACTIVE_GATE3_CG_CONFIG: ${MMTC_RRC_INACTIVE_GATE3_CG_CONFIG:-0}`.
- [Discussion Point] -> This preserves Case A default behavior because the default value is `0`.

## Implementation Details
- Added `configure_configured_grant()`.
- On `NR_SetupRelease_ConfiguredGrantConfig_PR_release`:
  - free previous `bwp->configuredGrantConfig`;
  - set the pointer to `NULL`;
  - log `configuredGrantConfig released`.
- On `NR_SetupRelease_ConfiguredGrantConfig_PR_setup`:
  - free previous `bwp->configuredGrantConfig`;
  - copy `configured_grant->choice.setup` with `asn_copy(&asn_DEF_NR_ConfiguredGrantConfig, ...)`;
  - log `configuredGrantConfig parsed` with BWP id, periodicity, resource allocation, and `cg_sdt` presence.

## Validation
- [Generated Header Parity]: PASS
  - default build has `cmake_targets/ran_build/build/openair2/RRC/NR/MESSAGES/NR_ConfiguredGrantConfig.h`
  - default build has `cmake_targets/ran_build/build/openair2/RRC/NR/MESSAGES/NR_SDT-MAC-PHY-CG-Config-r17.h`
  - default build has `cmake_targets/ran_build/build/openair2/RRC/NR/MESSAGES/NR_BWP-UplinkDedicated.h`
- [Static Check]: PASS
  - `rtk git diff --check -- openair2/LAYER2/NR_MAC_UE/config_ue.c`
- [Sandbox Build]: FAIL due sandbox-only ccache temp path
  - `test_log/build_logs/build_nr-uesoftmodem_2026-06-11_14-52-42_gate3-cg-parse.log`
  - failure marker: `ccache: error: Failed to create temporary file for /run/user/1000/ccache-tmp`
- [Escalated Build]: PASS
  - `test_log/build_logs/build_nr-uesoftmodem_2026-06-11_14-52-59_gate3-cg-parse_escalated.log`
- [Second Escalated Build]: PASS
  - `test_log/build_logs/build_nr-uesoftmodem_2026-06-11_14-55-55_gate3-sr-cg-trace_escalated.log`
- [Third Escalated Build]: FAIL then PASS
  - `test_log/build_logs/build_nr-uesoftmodem_2026-06-11_15-02-21_gate3-cg-sdt-tx-blocker_escalated.log`: FAIL, helper was declared after first use.
  - `test_log/build_logs/build_nr-uesoftmodem_2026-06-11_15-03-10_gate3-cg-sdt-tx-blocker_fix_escalated.log`: PASS.
- [gNB Static Check]: PASS
  - `rtk git diff --check -- openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_ulsch.c`
- [gNB Sandbox Build]: PASS
  - `test_log/build_logs/build_nr-softmodem_2026-06-11_15-06-59_gate3-gnb-cg-confirmation.log`
- [gNB RRC Config Hook Static Check]: PASS
  - `rtk git diff --check -- openair2/LAYER2/NR_MAC_gNB/nr_radio_config.c`
- [gNB RRC Config Hook Sandbox Build]: PASS
  - `test_log/build_logs/build_nr-softmodem_2026-06-11_15-14-57_gate3-cg-config-hook.log`
- [Runtime Image Rebuild]: PASS
  - `test_log/build_logs/rebuild_local_oai_images_2026-06-11_15-17-36_gate3-cg-config-hook.log`
  - rebuilt `ran-build:latest`, `oai-gnb:latest`, and `oai-nr-ue:latest`
- [Runtime Image Marker Check]: PASS
  - gNB image contains `configuredGrantConfig validation setup`
  - gNB image contains `configured grant confirmation received`
  - UE image contains `configuredGrantConfig parsed`
  - UE image contains `cg-SDT CG scheduler missing`
- [RFsim Smoke]: PASS for config parse only
  - command log: `test_log/compiler_logs/mmtc_gate3_cg_config_smoke_2026-06-11_15-21-50.log`
  - gNB log: `test_log/compiler_logs/mmtc_smoke_2026-06-11_15-21-50_gnb.log`
  - UE log: `test_log/compiler_logs/mmtc_smoke_2026-06-11_15-21-50_ue1_docker.log`
  - summary: `sample=1 running=1 attach=1 pdu=1 tun=1 forward_ping_ok=1 gnb_restart=0 failures=0`
  - gNB marker: `configuredGrantConfig validation setup bwp_size=106 rb_start=0 rb_size=8 riv=742 periodicity=9 time_domain_allocation=0 cg_sdt=1`
  - UE marker: `configuredGrantConfig parsed bwp_id=1 periodicity=9 resourceAllocation=1 cg_sdt=1`
  - failure markers absent: `configuredGrantConfig not supported`, `exit 139`
  - Gate 3 tx/rx markers absent: `cg-SDT PUSCH tx`, `cg-SDT PUSCH rx`

## Remaining Gate 3 Work
- [Step 3A] Completed: RFsim smoke with `MMTC_RRC_INACTIVE_GATE3_CG_CONFIG=1` proves `configuredGrantConfig parsed`.
- [Step 4] UE TX path is explicitly blocked on the missing autonomous CG scheduler; do not mark `cg-SDT PUSCH tx` PASS.
- [Step 5] gNB can now observe the configured grant confirmation MAC CE, but still needs a reliable CG-SDT classifier before logging `cg-SDT PUSCH rx`.
- [Gate Status]: still [in progress], not PASS.
