# AIOTF CN5G `experimental_n6` Validation Report

## Conclusion

| Gate | Result | Claim allowed |
|---|---|---|
| Tag/R2D/D2R deterministic protocol | PASS | Experimental codec and boundary behavior |
| RFsim Topology 2 | PASS from prerequisite evidence | Logical CW/R2D/D2R routing; no physical RF claim |
| AIOTF state and lifecycle | PASS | Bounded 60-Tag/two-reader state and launchable process |
| N6 diagnostic adapter | PASS | Unambiguous 40-byte UDP report association only |
| NRF AIOTF NF registration | PASS | Native AIOTF profile lifecycle and area discovery over HTTP/2 |
| Trusted-AF bounded Naiotf Inventory | PASS; full profile not ready | Explicit-device request, unique correlation, timeout callback, and rejection boundaries |
| AMF/NGAP/RRC UE Reader path | STOP / unavailable | None |
| NEF exposure | NOT RUN | None |
| Physical dual-beam RF | NOT EVALUATED `[Needs Verification]` | None |

The runnable end-to-end implementation profile remains `experimental_n6`. It uses the UE's PDU session to deliver a diagnostic report to an N6-side AIOTF listener; AIOTF does not have its own PDU session. NRF and bounded `Naiotf_AIoT_Inventory` dependencies are now separately evidenced, but the missing AMF/NGAP/RRC path prevents complete `trusted_af_sbi` readiness. None of these results is a 3GPP conformance or physical-RF claim.

## Implemented scope

| Owner | Result |
|---|---|
| `openair3/AIOTF/aiotf_inventory.c` | Single binding/arbitration owner for Tags 1-60, UE1/UE2, serialized transactions, failover, first-valid, duplicate/conflict evidence, and timeout |
| `openair3/AIOTF/aiotf_service.c` | Fail-closed config, liveness/readiness, status cleanup, diagnostic UDP, HTTP/2 NRF client, h2c Naiotf Inventory, bounded correlation, and result callback |
| `docker/Dockerfile.build.ubuntu`, `docker/Dockerfile.gNB.ubuntu` | Explicit `oai-aiotf` target and runtime image |
| `oai-cn5g/docker-compose.yaml` | Disabled `aiot` profile; AIOTF at `192.168.70.141` and `192.168.72.141`; loopback UDP 36900 |
| Registry/skill/menu/display | Registered self-tests, evidence checks, operator commands, fixed demonstration, and idempotent cleanup |

## Boundary coverage

| Boundary | Evidence |
|---|---|
| Empty, duplicate, or out-of-range Tags | Configuration rejects before listener |
| Payload 0, 1, 16, 17 bytes | Zero and over-limit reject; 1 and 16 accepted in focused tests |
| Reader handle outside 1/2 | Wire parser rejects |
| Frame 1023/1024 and slot 159/160 | Parser accepts boundary and rejects boundary+1 in self-test |
| Zero pending context | Diagnostic adapter rejects |
| Multiple matching pending contexts | Rejects as ambiguous before arbitration; state remains unchanged |
| Wrong slot | `no_pending_context` runtime rejection |
| Stale binding epoch and duplicate session | Startup rejects before bind |
| First report, equal second report, conflicting second report | First-valid, duplicate evidence, conflict evidence covered by inventory tests |
| Naiotf 0/1/60/61 and duplicate Tags | 1 and 60 accepted; zero, 61, and duplicate reject before scheduling |
| Trusted-AF authorization | Exact local allow-list accepted; a different `afId` returns 403 |
| HTTP ambiguity | Invalid/missing/duplicate content length, duplicate content type, transfer encoding, and non-JSON media types reject |
| Inventory timeout and restart | Final `NO_SUCC_INV_RESP` callback receives 204; restart generates a different `transId` |
| Repeated cleanup | Two `down` calls pass; volume set remains 42 before and after |
| Static address collision | Initial `.140` attempt failed against gNB; AIOTF moved to unused `.141` addresses and retry passed |

No shared mutable state is accessed concurrently: the current service uses one poll loop and one process-owned pending-context array. Multi-process persistence and concurrent SBI requests are outside the accepted profile.

## Evidence index

| Evidence | Result | Scope |
|---|---|---|
| `test_log/build_logs/build_oai_aiotf_service_2026-07-20_13-08-31.log` | PASS | Minimal service and inventory target build |
| `test_log/build_logs/build_aiotf_experimental_n6_adapter_2026-07-20_13-19-38.log` | PASS | Pending-context adapter and focused tests |
| `test_log/build_logs/rebuild_aiotf_runtime_images_2026-07-20_13-25-00.log` | PASS | `ran-build`, `oai-aiotf`, gNB, and UE images |
| `test_log/compiler_logs/aiotf_evidence_ladder_selftests_2026-07-20_13-39-00.log` | PASS | Tag self-test and serialized 60-Tag AIOTF self-test |
| `test_log/compiler_logs/aiotf_registered_t2_demo_2026-07-20_13-34-00.log` | FAIL retained | Exposed static-IP collision with gNB `.140` |
| `test_log/compiler_logs/aiotf_registered_t2_demo_ip_fix_2026-07-20_13-36-00.log` | PASS | Lifecycle, first-valid, duplicate, wrong-slot rejection, cleanup and volume retention |
| `openspec/changes/integrate-aiotf-cn5g-tag-workflow/review/evidence/capability_probe_2026-07-20.md` | Historical baseline: NRF failed; AMF/RAN/NEF missing | Pre-upgrade stop evidence retained for comparison |
| `openspec/changes/integrate-aiotf-cn5g-tag-workflow/review/evidence/evidence_ladder_2026-07-20.md` | Ladder now stops at AMF/RAN | Layer-by-layer gate classification |
| `test_log/compiler_logs/aiotf_naiotf_inventory_runtime_2026-07-20_16-35-47.log` | PASS | h2c 0/1/60/61, auth, timeout callback, restart, NRF dependency, cleanup |
| `test_log/compiler_logs/aiotf_nrf_client_after_naiotf_2026-07-20_16-41-54.log` | PASS | Post-Naiotf seven-boundary NRF client regression |

## Blockers and next actions

| Blocker | Required next action |
|---|---|
| AMF revision `89e15886` lacks `Namf_AIoT` | Upgrade the selected real AMF owner together with exact Release 20 NGAP contract; do not add a route-only stub |
| NGAP/RRC AIoT endpoints missing | Import verified Stage-3 definitions and add both producer and consumer in their real OAI owners; require correlated round-trip markers |
| OAI NEF revision `358f2131` lacks `Nnef_AIoT_*` | Upgrade the selected NEF owner only after the trusted-AF AMF/RAN path passes |
| Local TS 23.369 V20.0.0 is unapproved | Re-map clauses against an approved baseline before any conformance claim `[Needs Verification]` |

Do not alias AIOTF as another NF type, invent stub standard endpoints, or reinterpret N6 UDP as an AMF/SBI round trip.
