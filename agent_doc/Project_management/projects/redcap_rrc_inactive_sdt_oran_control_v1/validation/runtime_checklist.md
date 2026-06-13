# RFsim Runtime Checklist for RRC_INACTIVE + SDT

## Source of Truth
- [MUST] Use `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/`.
- [MUST] Treat `docker-compose.yml`, `docker-compose.mmtc.yml`, and directly mounted config/policy files as runtime source of truth.
- [MUST] Use `control/redcap_policy_case_a.yaml` for protocol baseline validation.
- [MUST] Use `control/redcap_policy_case_b.yaml` only for O-RAN dynamic control validation.

## Pre-Run Checks
- [MUST] Confirm active policy file from `REDCAP_POLICY_HOST_FILE`.
- [MUST] Confirm active case from `REDCAP_CASE`.
- [MUST] Confirm gNB config mounted to `/opt/oai-gnb/etc/gnb.yaml`.
- [MUST] Confirm UE config mounted to `/opt/oai-nr-ue/etc/nr-ue.yaml`.
- [MUST] Confirm whether local OAI images were rebuilt after C changes.

## Required Case A Markers
- [T2-1] `RRCRelease suspendConfig received`.
- [T2-1] `RRC_INACTIVE entered`.
- [T2-2] `RRCResumeRequest received`.
- [T2-2] `RRCResume sent`.
- [T2-2] `RRCResume received`.
- [T2-2] `RRCResumeComplete sent`.
- [T2-2] `RRC_CONNECTED`.
- [T2-3] `configuredGrantConfig parsed`.
- [T2-3] `cg-SDT PUSCH tx`.
- [T2-3] `cg-SDT PUSCH rx candidate`.
- [T2-4] `RSRP threshold exceeded`.
- [T2-4] `4-step RA triggered`.

## Required Case B Markers
- [Control] `KPM snapshot`.
- [Control] `policy_version`.
- [Control] `control_request`.
- [Control] `control_path`.
- [Control] `old_value`.
- [Control] `new_value`.
- [Control] `ACK` or `NACK` or `timeout`.
- [Control] `applied_parameter_snapshot`.

## Failure Criteria
- [MUST NOT] `exit 139` appears.
- [MUST NOT] UE asserts on `suspendConfig`.
- [MUST NOT] UE asserts on `configuredGrantConfig`.
- [MUST NOT] Case B dynamic control modifies Case A baseline files.
- [MUST NOT] KPM is reported as directly applying control.

## Pass/Fail Counters
- UE attach count.
- PDU session count.
- Tunnel count.
- Forward ping success count.
- gNB restart count.
- UE restart count.
- `exit 139` count.
- RRC_INACTIVE entry count.
- RRCResumeRequest count.
- CG-SDT PUSCH tx/rx-candidate count.
- 4-step RA fallback count.
