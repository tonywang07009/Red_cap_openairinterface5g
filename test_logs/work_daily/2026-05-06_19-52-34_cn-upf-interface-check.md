# Work Daily Log
## Session Metadata
- Date: 2026-05-06 19:52
- Agent Session ID: N/A
- Task Slug: cn-upf-interface-check
- Project Path: agent_doc/Project_management/projects/redcap_mmtc_priority_execution_v1/project_plan.md

## Milestone & Sub-task Reference
- Milestone: M5 mMTC Runtime Scaling
- Sub-task: RT-M5-CASEB-030 CN/UPF runtime blocker inspection
- Status: [COMPLETED]

## What Was Done
- Checked Docker status for CN/RAN containers.
- Inspected `oai-upf`, `oai-nrf`, and `oai-smf` Docker network assignments.
- Verified `oai-upf` can resolve and TCP-connect to `oai-nrf:8080`.
- Inspected `/home/tonywang/OAI/oai-cn5g/conf/config.yaml` and confirmed UPF interface mapping does not match actual Docker interface order.
- Confirmed `oai-upf` is binding GTP-U `2152/udp` and PFCP `8805/udp` on `192.168.72.134`.
- Confirmed `oai-smf` logs show `UPF selection failed` while DNN `oai` matches local subscription data.
- Confirmed `oai-upf` logs repeatedly send NF registration to NRF with `ipv4Addresses:["192.168.72.134"]` and then log `Could not get response from NRF`.

## 3GPP Spec Clauses Referenced
- 3GPP TS 23.501 Section 6.2.3 [Needs Verification] — SMF selects UPF for PDU session user-plane anchoring.
- 3GPP TS 29.510 Section 5.2.2 [Needs Verification] — NRF NF registration and NF profile discovery behavior.

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| Docker CN container health | Pass | Runtime status | `oai-upf`, `oai-smf`, `oai-nrf` are up/healthy, but health does not prove NRF registration. |
| UPF DNS to NRF | Pass | Container network | `oai-upf` resolves `oai-nrf` to `192.168.70.130`. |
| UPF TCP to NRF:8080 | Pass | Container network | Basic TCP connectivity succeeds. |
| UPF NRF registration | Fail | NRF registration path | UPF repeatedly logs `Could not get response from NRF`. |
| SMF UPF selection | Fail | PDU session path | SMF logs `UPF selection failed`, causing PDU session establishment reject. |
| UPF interface binding | Fail | Runtime config | UPF binds N3/N4 on `192.168.72.134`, while SMF/gNB are on `192.168.70.0/23`. |

## Known Issues / Blockers
- `conf/config.yaml` currently maps UPF `sbi`, `n3`, and `n4` to `eth0`, but Docker assigns `eth0=192.168.72.134` traffic net and `eth1=192.168.70.134` public net.
- `n6` is currently mapped to `eth1`, but Docker `eth1` is public net; N6 should likely use traffic net in this compose topology.
- Because UPF is not properly registered/discovered, the previous RT-M5-CASEB-030 dynamic Msg4 result is polluted by CN/UPF failure and should not be used as RA-only evidence.

## Next Step
- Patch `/home/tonywang/OAI/oai-cn5g/conf/config.yaml` UPF interface mapping so `sbi/n3/n4` use the public-net interface and `n6` uses the traffic-net interface, then restart CN and rerun the CN registration checks before rerunning RT-M5-CASEB-030.
