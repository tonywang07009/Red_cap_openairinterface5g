# Work Daily Log
## Session Metadata
- Date: 2026-05-06 20:06
- Agent Session ID: N/A
- Task Slug: rt-m5-caseb-030-after-upf-interface-fix
- Project Path: agent_doc/Project_management/projects/redcap_mmtc_priority_execution_v1/project_plan.md

## Milestone & Sub-task Reference
- Milestone: M5 mMTC Runtime Scaling
- Sub-task: RT-M5-CASEB-030 30 UE Case B rerun after CN/UPF interface fix
- Status: [COMPLETED]

## What Was Done
- Updated `/home/tonywang/OAI/oai-cn5g/conf/config.yaml`:
  - `upf.sbi.interface_name: eth0`
  - `upf.n3.interface_name: eth0`
  - `upf.n4.interface_name: eth0`
  - `upf.n6.interface_name: eth1`
- Updated `/home/tonywang/OAI/oai-cn5g/docker-compose.yaml`:
  - pinned `oai-upf.public_net.interface_name: eth0`
  - pinned `oai-upf.traffic_net.interface_name: eth1`
- Recreated `oai-upf` so the fixed interface names were applied.
- Verified `oai-upf` runtime interfaces:
  - `eth0 = 192.168.70.134/23`
  - `eth1 = 192.168.72.134/23`
- Verified `oai-upf` N3/N4 sockets bind to `192.168.70.134`.
- Verified UPF NRF registration succeeds with `ipv4Addresses:["192.168.70.134"]`.
- Reran `RT-M5-CASEB-030` with:
  - `GNB_REDCAP_CONFIG=test_log/runtime_configs/gnb.redcap_mmtc_case-b_2026-05-02_12-35-01.yaml`
  - `MMTC_TOTAL_UES=50`
  - `MMTC_SAMPLE_UES=1..30`
  - `MMTC_CN_COMPOSE=/home/tonywang/OAI/oai-cn5g/docker-compose.yaml`
  - `MMTC_USE_EXISTING_CN_DB=1`
  - `MMTC_RESET_CN=1`
  - `MMTC_UE_START_GAP=8`
  - `MMTC_FORWARD_PING_MODE=parallel`
  - `MMTC_RUN_REVERSE_PING=0`
  - `MMTC_IPERF_ENABLE=0`

## 3GPP Spec Clauses Referenced
- TS 23.501 Section 6.2.3 [Needs Verification] — SMF selection and use of UPF for PDU Session user plane.
- TS 29.510 Section 5.2.2 [Needs Verification] — NRF NF registration and NF profile discovery.
- TS 38.321 Section 5.1.4 [Needs Verification] — Random Access Response / Msg2 reception timing.
- TS 38.321 Section 5.1.5 [Needs Verification] — Contention resolution / Msg4 behavior.

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| Compose config validation | PASS | CN compose syntax | `docker compose ... config --services` accepted `interface_name`. |
| UPF interface binding | PASS | CN runtime | N3/N4 bind to `192.168.70.134`; N6 remains traffic-side. |
| UPF NRF registration | PASS | CN runtime | UPF receives NRF response and heartbeat success; `UPF selection failed=0`. |
| RT-M5-CASEB-030 RFsim runtime | FAIL | 30 sampled UEs | `sample=30 running=30 attach=27 pdu=27 tun=27 forward_ping_ok=27 gnb_restart=0 failures=3`. |
| Failed UE list | FAIL | UE runtime | UE23, UE29, UE30 have no `oaitun_ue1`. |
| Msg2 window counter | FAIL | gNB RA pressure | `Msg2 window fail=298`. |
| Msg2 CCE counter | WARN | gNB RA pressure | strict CCE-fail marker count `14`; broad scheduler `CCE fail` stats are noisy. |
| Msg4 vrb_map counter | PASS/WARN | gNB RA allocation | `Msg4 vrb_map fail=4`. |
| Contention timer counter | FAIL | gNB RA contention | `contention timer expired=376`; `RA Procedure failed at Msg4=376`. |

## Known Issues / Blockers
- CN/UPF blocker is resolved for this run.
- Remaining failures are RA/RRC-side, not UPF selection:
  - UE23, UE29, UE30 repeatedly show `RAR reception failed` / `Contention resolution failed`.
  - Failed UE logs include `[CGDBG][PUCCH] pucch_ResourceCommon is NULL ... fallback=0` after RRCSetup/CellGroupConfig on BWP1.
- Msg4 `vrb_map` failures are low after the dynamic compact-first allocation, but Msg4 NACK/contention remains high.

## Next Step
- Investigate RedCap UE PUCCH common fallback behavior after RRCSetup/CellGroupConfig on BWP1, because the failed UE logs show `pucch_ResourceCommon is NULL` with fallback disabled.
- Compare UE23/29/30 against successful UE logs around RRCSetupComplete, PUCCH ACK generation, and Msg4 contention resolution.
