# 2026-06-03 RRC_INACTIVE + SDT Gate 0 Inventory

- Project Path: `agent_doc/Project_management/projects/redcap_rrc_inactive_sdt_oran_control_v1/project_plan.md`
- [Case]: A
- [Gate]: 0
- [source build PASS/FAIL/NA]: [NA] no C source changed
- [unit test PASS/FAIL/NA]: [NA] inventory-only gate
- [RFsim runtime PASS/FAIL/NA]: [NA] inventory-only gate
- [exit 139]: not exercised in this gate

## Inventory Result
- [RRC_INACTIVE state]
  - UE enum exists: `openair2/RRC/NR_UE/rrc_defs.h:86`
  - RA trigger enum includes `RRC_RESUME_REQUEST` and `TRANSITION_FROM_RRC_INACTIVE`: `openair2/RRC/NR_UE/rrc_defs.h:93`
  - Scheduler-side RedCap SDT FSM maps SDT inactive state to `NR_REDCAP_RRC_INACTIVE`: `openair2/LAYER2/NR_MAC_gNB/nr_mac_sdt_fsm.c:62`
  - [Conclusion] State names/hooks exist, but full UE/gNB RRC_INACTIVE protocol behavior is not complete.

- [RRCRelease.suspendConfig]
  - ASN.1 field exists: `openair2/RRC/NR/MESSAGES/ASN.1/nr-rrc-17.3.0.asn1:988`
  - UE currently asserts on `suspendConfig`: `openair2/RRC/NR_UE/rrc_UE.c:3039`
  - UE idle path documents missing inactive AS context: `openair2/RRC/NR_UE/rrc_UE.c:3124`
  - gNB release encoder currently builds regular `RRCRelease` without `suspendConfig`: `openair2/RRC/NR/MESSAGES/asn1_msg.c:475`
  - gNB release path also sends F1 UE context release command: `openair2/RRC/NR/rrc_gNB.c:3274`
  - [Conclusion] Gate 1 must add a suspend release path and avoid immediate context purge.

- [RRCResume / RRCReestablishment]
  - gNB `rrcResumeRequest` branch is present but not implemented: `openair2/RRC/NR/rrc_gNB.c:2169`
  - UE DL-DCCH `rrcResume` branch is present but not handled: `openair2/RRC/NR_UE/rrc_UE.c:2510`
  - No UE-side `generate_RRCResumeRequest` / `generate_RRCResumeComplete` implementation was found.
  - `RRCSetup` fallback for Resume/Reestablishment exists but discards context: `openair2/RRC/NR_UE/rrc_UE.c:1982`
  - [Conclusion] Gate 2 requires both message generation and handler work, not just log replacement.

- [configuredGrantConfig + cg-SDT]
  - UE MAC currently rejects `configuredGrantConfig`: `openair2/LAYER2/NR_MAC_UE/config_ue.c:1730`
  - gNB side stores `configuredGrantConfig` pointer when present: `openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_primitives.c:2745`
  - `cg-SDT` / SDT fields exist in NR RRC 17.3.0 ASN.1: `openair2/RRC/NR/MESSAGES/ASN.1/nr-rrc-17.3.0.asn1:1112`
  - Generated SDT / CG-SDT headers exist in `cmake_targets/ran_build/build*/openair2/RRC/NR/MESSAGES/`.
  - Source tree `openair2/RRC/NR/MESSAGES/` does not directly contain generated `NR_CG-SDT*.h` files.
  - [Conclusion] Gate 3 can rely on existing ASN.1 definitions/build generation, but UE MAC/RRC parsing and CG PUSCH behavior must be implemented.

- [TA / RSRP threshold]
  - ASN.1 has `cg-SDT-TimeAlignmentTimer-r17`, `cg-SDT-RSRP-ThresholdSSB-r17`, and `cg-SDT-TA-ValidationConfig-r17`: `openair2/RRC/NR/MESSAGES/ASN.1/nr-rrc-17.3.0.asn1:1128`
  - ASN.1 has `cg-SDT-RSRP-ChangeThreshold-r17`: `openair2/RRC/NR/MESSAGES/ASN.1/nr-rrc-17.3.0.asn1:1135`
  - [Conclusion] Gate 4 should use deterministic RFsim trigger for repeatable validation.

## Spec Status
- [RRC_INACTIVE]: TS 38.331 [Needs Verification]
- [RRCRelease suspendConfig]: TS 38.331 [Needs Verification]
- [RRCResume]: TS 38.331 [Needs Verification]
- [SDT / CG-SDT]: TS 38.321 / TS 38.331 [Needs Verification]
- [RedCap capability]: TS 38.306 [Needs Verification]

## Next Gate
- [Gate 1] Implement `RRCRelease.suspendConfig -> RRC_INACTIVE`.
- [Gate 1 MUST] replace the UE assert with controlled inactive transition.
- [Gate 1 MUST] introduce gNB suspend release generation without normal UE context purge.
- [Gate 1 MUST] preserve PDCP/security/context expectations or explicitly mark remaining gaps.
