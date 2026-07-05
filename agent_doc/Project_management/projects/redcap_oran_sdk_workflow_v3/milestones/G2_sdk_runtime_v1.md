# G2 SDK Runtime V1

## Scope

- Implement one minimal runtime SDK path after G1 is complete.
- Prefer one runtime-mutable RedCap parameter with existing marker support.
- Preserve Case A baseline behavior.

## Candidate Runtime Parameters

- `redcap_ul_prb_cap` [contract-backed; existing xApp seed; wrapper validator wired]
- `configured_grant_enable`
- `cg_sdt_enable`
- `configured_grant_profile_id`
- `sdt_payload_threshold_bytes`
- `force_four_step_ra_on_threshold`
- `drx_profile`

## Required Evidence

- [source build]: target depends on touched xApp/OAI files.
- [unit/static test]: contract validation or closest available parser/checker.
- [runtime marker]: KPM snapshot, control request, ACK/NACK, applied snapshot, rollback if rejected.
- [Case isolation]: Case A policy remains unchanged.

## Out of Scope

- Broad SDK framework.
- Production Non-RT RIC deployment.
- GUI or dashboard.
- SLM evaluation.

## Status

- [x] Runtime parameter selected: `redcap_ul_prb_cap`.
- [x] SDK wrapper validates contract/policy before dry-run or live control.
- [x] Build-only and dry-run validation passed on 2026-07-04.
- [!] RFsim validation attempted; blocked by UE1 exit 139 before attach.
