# T2B O-RAN Policy Control for RedCap SDT

## Scope
- [Case B] dynamic control after [Case A] T2-1 through T2-4 passes.
- KPM-driven decision flow for RedCap INACTIVE/SDT parameters.
- Policy selection through YAML mounted by `docker-compose.mmtc.yml`.
- Bounded runtime updates through [E2SM-RC], [custom SM], or [dApp local API].

## Out of Scope
- Claiming KPM as a direct control service model.
- Overwriting Case A baseline configs.
- Non-RT RIC production deployment.
- Unbounded AI parameter search.

## Control Model
- [KPM] provides observation only.
- [rApp] provides long-term policy, such as power-saving or latency priority.
- [xApp] subscribes KPM and selects near-real-time actions.
- [dApp/gNB hook] applies validated parameter updates and handles rollback.
- [E2SM-RC] is the preferred control path when the required control item exists.
- [custom SM] or [dApp local API] may be used for RedCap-specific parameters not covered by current OAI/FlexRIC RC support.

## Case B Task List
- [T2B-0] Confirm Case A baseline PASS and freeze its policy/config snapshot.
- [T2B-1] Define `redcap_control_contract.yaml` parameter ownership and range checks.
- [T2B-2] Define `redcap_policy_case_b.yaml` KPM-driven decision policy.
- [T2B-3] Wire xApp control request to E2SM-RC/custom SM/dApp local API.
- [T2B-4] Add gNB/dApp safety guard and applied-parameter log.
- [T2B-5] Validate dynamic control without contaminating Case A baseline.

## Runtime Mutable Parameter Candidates
- [inactive_allowed]
- [sdt_enable]
- [cg_sdt_enable]
- [configured_grant_profile_id]
- [cg_sdt_rsrp_change_threshold_db]
- [sdt_payload_threshold_bytes]
- [drx_profile]
- [force_four_step_ra_on_threshold]

## Boot-Only Parameter Candidates
- [RF frequency]
- [PRB count]
- [numerology]
- [UE IMSI]
- [container topology]
- [xApp command path]

## Required Case B Logs
- [MUST] KPM metric snapshot.
- [MUST] rApp or AI policy version.
- [MUST] xApp control request.
- [MUST] control path: E2SM-RC, custom SM, or dApp local API.
- [MUST] old value and new value.
- [MUST] ACK, NACK, or timeout.
- [MUST] applied parameter snapshot.
- [MUST] rollback marker if guard rejects or runtime apply fails.

## Completion Criteria
- [MUST] Case A remains reproducible with `redcap_policy_case_a.yaml`.
- [MUST] Case B uses `redcap_policy_case_b.yaml` and `redcap_control_contract.yaml`.
- [MUST] Every runtime parameter update passes contract validation.
- [MUST] Dynamic control changes are distinguishable from protocol regressions.
