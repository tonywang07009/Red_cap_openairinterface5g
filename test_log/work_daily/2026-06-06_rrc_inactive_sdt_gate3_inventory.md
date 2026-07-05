# 2026-06-06 RRC_INACTIVE SDT Gate 3 Inventory

- Project Path: `agent_doc/Project_management/projects/redcap_rrc_inactive_sdt_oran_control_v1/project_plan.md`
- [Case]: A
- [Gate]: 3
- [source build PASS/FAIL/NA]: [NA] inventory-only, no C source changed
- [unit test PASS/FAIL/NA]: [NA] inventory-only
- [RFsim runtime PASS/FAIL/NA]: [NA] inventory-only
- [exit 139]: not exercised in this gate

## Scope
- [Goal]: Check whether Gate 3 can start from existing ASN.1 / UE MAC / gNB MAC hooks before implementing `configuredGrantConfig + cg-SDT`.
- [Boundary]: First round only; no C code edit, no RFsim rerun, no milestone PASS update.
- [Spec Status]: TS 38.321 / TS 38.331 clause mapping remains `[Needs Verification]`.

## Inventory Result
- [ASN.1 configuredGrantConfig]
  - Rel-17 ASN.1 source has `ConfiguredGrantConfig`: `openair2/RRC/NR/MESSAGES/ASN.1/nr-rrc-17.3.0.asn1:4312`.
  - `rrc-ConfiguredUplinkGrant` includes `cg-SDT-Configuration-r17`: `openair2/RRC/NR/MESSAGES/ASN.1/nr-rrc-17.3.0.asn1:4358`.
  - Generated `build_test` header includes `NR_BWP_UplinkDedicated.configuredGrantConfig`: `cmake_targets/ran_build/build_test/openair2/RRC/NR/MESSAGES/NR_BWP-UplinkDedicated.h:58`.
  - [Conclusion]: ASN.1 definition exists; runtime/default generated header parity is `[Needs Verification]` because current scan only found generated CG-SDT headers under `build_test`.

- [ASN.1 cg-SDT]
  - Rel-17 ASN.1 source has `SDT-MAC-PHY-CG-Config-r17`: `openair2/RRC/NR/MESSAGES/ASN.1/nr-rrc-17.3.0.asn1:1121`.
  - Rel-17 ASN.1 source has `BWP-UplinkDedicatedSDT-r17` with `configuredGrantConfigToAddModList-r17`: `openair2/RRC/NR/MESSAGES/ASN.1/nr-rrc-17.3.0.asn1:1146`.
  - Rel-17 ASN.1 source has `CG-SDT-Configuration-r17`: `openair2/RRC/NR/MESSAGES/ASN.1/nr-rrc-17.3.0.asn1:4439`.
  - Generated `build_test` header has `NR_SDT_MAC_PHY_CG_Config_r17_t`: `cmake_targets/ran_build/build_test/openair2/RRC/NR/MESSAGES/NR_SDT-MAC-PHY-CG-Config-r17.h:34`.
  - Generated `build_test` `NR_ConfiguredGrantConfig` has `cg_SDT_Configuration_r17`: `cmake_targets/ran_build/build_test/openair2/RRC/NR/MESSAGES/NR_ConfiguredGrantConfig.h:230`.
  - [Conclusion]: `cg-SDT` ASN.1 types exist, but source wiring and validation markers are not implemented yet.

- [UE assert location]
  - Exact assert: `AssertFatal(!ul_dedicated->configuredGrantConfig, "configuredGrantConfig not supported\n");`
  - Location: `openair2/LAYER2/NR_MAC_UE/config_ue.c:1730`, inside `configure_dedicated_BWP_ul()`.
  - UE MAC already has a storage slot: `NR_UE_UL_BWP.configuredGrantConfig` at `openair2/LAYER2/NR_MAC_COMMON/nr_mac.h:570`.
  - UE scheduler already checks `mac->current_UL_BWP->configuredGrantConfig` in SR logic: `openair2/LAYER2/NR_MAC_UE/nr_ue_scheduler.c:1292`.
  - [Conclusion]: first implementation slice should replace the assert with a controlled parse/store/release path and add `configuredGrantConfig parsed` only after ownership/lifetime is safe.

- [gNB CG PUSCH receive path]
  - gNB BWP config can copy `configuredGrantConfig` when present: `openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_primitives.c:2745`.
  - gNB default radio config currently sets `configuredGrantConfig = NULL`: `openair2/LAYER2/NR_MAC_gNB/nr_radio_config.c:2041`.
  - gNB UL receive entry `_nr_rx_sdu()` calls `nr_process_mac_pdu()` then `nr_redcap_sdt_maybe_complete_ul_burst()`: `openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_ulsch.c:1157`.
  - Existing RedCap SDT FSM hooks log scheduler-side transitions only when `radio_config.redcap` and `UE->is_redcap` are true: `openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_ulsch.c:84`.
  - Existing UL grant hook is dynamic-grant oriented: `nr_redcap_sdt_note_ul_grant()` at `openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_ulsch.c:2602`.
  - `UL_SCH_LCID_CONFIGURED_GRANT_CONFIRMATION` case exists but is empty: `openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_ulsch.c:658`.
  - [Conclusion]: gNB has a general PUSCH/MAC SDU receive path and SDT FSM hooks, but no proven CG-SDT-specific receive classifier or `cg-SDT PUSCH rx` marker yet.

## Marker Scan
- `configuredGrantConfig parsed`: expected only in checklist/YAML; not present in source.
- `cg-SDT PUSCH tx`: expected only in checklist/YAML; not present in source.
- `cg-SDT PUSCH rx`: expected only in checklist/YAML/milestone; not present in source.
- `configuredGrantConfig not supported`: present in UE assert and expected failure marker.

## Gate 3 Work Split
- [Step 1] Verify generated ASN.1 headers for the actual default/runtime build target, not only `build_test`.
- [Step 2] UE MAC: parse/store/release `configuredGrantConfig` in `configure_dedicated_BWP_ul()` without leaking ASN.1 ownership.
- [Step 3] UE MAC scheduler: distinguish configured grant availability from SR suppression; do not claim `cg-SDT PUSCH tx` until actual CG PUSCH selection is traceable.
- [Step 4] gNB MAC: decide marker point between `_nr_rx_sdu()`, `nr_process_mac_pdu()`, and SDT FSM after a reliable CG-SDT classifier exists.
- [Step 5] Update validation markers only after RFsim proves `configuredGrantConfig parsed`, `cg-SDT PUSCH tx`, and `cg-SDT PUSCH rx`.

## Updated Effort Estimate
- [Inventory completed]: Gate 3 is feasible to start because ASN.1 types exist and gNB has a general receive path.
- [Remaining uncertainty]: high, because CG-specific scheduling/receive classification is not proven.
- [Implementation estimate]: first parser/store slice about `25k-45k` tokens; full Gate 3 with UE TX, gNB RX marker, build, RFsim, and docs about `80k-140k` tokens `[Needs Verification]`.
