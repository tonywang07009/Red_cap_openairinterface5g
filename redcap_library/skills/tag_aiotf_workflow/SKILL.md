---
name: tag-aiotf-workflow
description: Run the repository-owned Ambient IoT Tag and AIOTF inventory workflow when validating one or more Tag IDs, the bounded 60-Tag/two-reader policy, RFsim Topology 2, experimental N6 reports, retained evidence, or AIOTF profile readiness. Use for Tag self-tests, AIOTF inventory self-tests, reader/observer runs, capability-gated profile selection, evidence checks, and cleanup; reject unavailable SBI or NEF profiles without fallback.
metadata:
  input: Tag IDs, 1-16 byte payload, normal or diversity reader mode, transport profile, UE runtime ownership, wake window, reader handles, report endpoint, and optional retained evidence path.
  output: Pass or fail, selected profile, correlation when available, selected reader, evidence path and class, cleanup status, missing capability, and next action.
  tool_dependencies:
    - aiot_tag_selftest
    - aiotf_inventory_selftest
    - aiot_topology2_runtime
    - aiot_evidence_check
    - aiot_topology2_cleanup
    - aiot_operator
    - aiot_topology2_demo
  openspec_change: integrate-aiotf-cn5g-tag-workflow
---

# Tag AIOTF Workflow

## Load contracts

1. Read `redcap_library/bash_tool/registry.json` and resolve every dependency above before execution.
2. Read `openspec/changes/integrate-aiotf-cn5g-tag-workflow/review/aiotf_cn5g_profile_v1.yaml` for current profile availability.
3. Read `redcap_doc/specs/A_IoT/README.md` only when RFsim runtime parameters or evidence classes are needed.

Do not execute direct shell commands. Invoke only the declared registry tools with their documented inputs.

## Validate request

Reject before runtime mutation when any condition holds:

- Tag IDs are empty, duplicated, below 1, or above 60.
- Payload is shorter than 1 byte or longer than 16 bytes.
- Reader mode is not `normal` or `diversity`.
- `diversity` targets a Tag outside 21-40 or lacks one primary and one distinct observer handle.
- A UE is assigned both reader and observer roles.
- Wake period or duration is zero, offset is outside the period, or duration exceeds the remaining period after offset.
- Reader handles are not 1 or 2.
- Profile is not `experimental_n6`, `trusted_af_sbi`, or `third_party_af_nef`.
- Cleanup ownership or evidence path cannot be tied to the current workflow.

## Gate profile

| Profile | Action |
|---|---|
| `experimental_n6` | Continue. Label every result diagnostic and leave NRF/SBI/AMF/NGAP/RRC/NEF incomplete. |
| `trusted_af_sbi` | Continue only when the profile contract says `available: true`; otherwise return the listed missing capabilities. |
| `third_party_af_nef` | Continue only when the profile contract says `available: true`; otherwise return the listed missing capabilities. |

Never downgrade an unavailable profile to `experimental_n6`.

## Execute

1. Invoke `aiot_tag_selftest` with `tag-selftest`.
2. Invoke `aiotf_inventory_selftest` with `aiotf-selftest`.
3. If only deterministic validation was requested, stop and return both markers.
4. Before a runtime request, create or update the required `task_log/tasks.json` entry through the runtime workflow owner.
5. Invoke `aiot_topology2_runtime` only for `experimental_n6`, passing the validated UE set, explicit `aiot_t2` RFsim option, one role per UE, Tag, wake window, reader handle, and report endpoint.
6. Invoke `aiot_evidence_check` for the requested evidence class and retained `test_log/` path.
7. Invoke `aiot_operator` for `validate`, `start`, `status`, or `down`; `validate` must not mutate runtime state and `down` must preserve volumes.
8. Invoke `aiot_topology2_demo` only for the fixed `experimental_n6` diagnostic demonstration. Do not relabel its UDP markers as SBI evidence.
9. Invoke `aiot_topology2_cleanup` only when this invocation started the corresponding CN5G/RFsim stack. Do not remove volumes.

Stop at the first failed layer and retain the narrower evidence already produced.

## Return

Return these fields:

| Field | Rule |
|---|---|
| `status` | `pass`, `fail`, or `missing_capability` |
| `profile` | Exact requested profile; never a fallback |
| `tag_ids` | Validated, sorted IDs |
| `correlation` | AIOTF correlation when produced; otherwise `unavailable` |
| `selected_reader` | Primary handle and observer handle when applicable |
| `evidence_class` | `protocol`, `rfsim`, `diagnostic_n6`, `sbi`, or `nef` |
| `evidence_path` | Retained path or `none` |
| `cleanup` | `not_needed`, `passed`, or `failed` |
| `missing_capability` | Exact failed readiness dependency or `none` |
| `next_action` | First unresolved gate or `complete` |

Do not report physical RF, 3GPP conformance, NRF registration, SBI, AMF/RAN round trip, or NEF exposure from a self-test, container health result, attach, ping, RFsim marker, or UDP packet.
