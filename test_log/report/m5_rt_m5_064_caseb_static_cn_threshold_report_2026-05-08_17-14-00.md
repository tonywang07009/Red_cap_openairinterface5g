# RT-M5-064 Case B Static CN Threshold Report

## 1. Technical Background
- [RT-M5-064] was run immediately after [RT-M5-056] passed with static CN discovery mitigation.
- The purpose was to test the upper bound directly at 64 sampled RedCap UEs under the same Case B gNB config, 8-second UE start gap, parallel forward ping, and `MMTC_PUCCH_COMMON_FALLBACK_BWP0=1`.
- The run did not fail at the CN auth / SMF discovery boundary. The terminal event was a gNB runtime restart: the gNB main child exited with signal `Killed` before validation, which invalidated final tunnel and ping checks.

## 2. Key Runtime Components / Data Structures
- [gNB runtime config]: `test_log/runtime_configs/gnb.redcap_mmtc_case-b_2026-05-02_12-35-01.yaml`.
- [CN runtime config]: `/home/tonywang/OAI/oai-cn5g/conf/config.yaml`.
- [Static CN mitigation]: `register_nf.general=no`, `enable_smf_selection=no`, static SMF UPF `host=oai-upf port=8805`.
- [mMTC script]: `ci-scripts/redcap_mmtc_smoke_validation.sh`.
- [Docker compose source]: `/home/tonywang/OAI/oai-cn5g/docker-compose.yaml`.

## 3. Test Results Summary
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| [RT-M5-064] summary | FAIL | 64 sampled UEs | `running=4 attach=59 pdu=59 tun=0 forward_ping_ok=0 gnb_restart=1 failures=65` |
| gNB runtime stability | FAIL | gNB Docker state + gNB log | gNB restart count `1`; `[tini] Main child exited with signal 'Killed'` |
| gNB OOM classification | Needs Verification | Docker inspect / dmesg | Docker `OOMKilled=false`; kernel `dmesg` access denied |
| CN auth / SMF-selection blocker | PASS | AMF / SMF / UPF logs | Auth-vector failure, Registration Reject, empty SMF candidate, and NRF markers all `0` |
| Msg2 DCI / CCE | PASS | gNB log | `64 x cce=0 agg=4` |
| Msg2 retry pressure | PASS with observation | gNB + UE logs | Msg2 window fail `53`; UE RAR reception failed `53` |
| Msg2 / Msg4 VRB pressure | PASS | gNB log | Msg2 and Msg4 `vrb_map fail=0` |
| Msg4 contention | FAIL due runtime boundary | gNB log | Msg4 ACK / CBRA success `63/64`; no contention timer expiry |
| UE PUCCH common fallback blocker | PASS | UE logs | `pucch_ResourceCommon is NULL=0`, `fallback=0/1=0/0` |
| Tunnel / ping | FAIL | UE states / tunnel logs | gNB restart caused `UE1..UE60` exit and no `oaitun_ue1` at validation |

## 4. 3GPP Specification Mapping
| Flow | Clause | Mapping |
|------|--------|---------|
| Random Access baseline | TS 38.321 Section 5.1 | Used to classify Msg1/Msg2/Msg3/Msg4 progress before the runtime kill. |
| RAR reception | TS 38.321 Section 5.1.4 [Needs Verification] | Msg2 window and RAR retry counters remain the RA pressure indicators. |
| Contention resolution | TS 38.321 Section 5.1.5 [Needs Verification] | `63/64` Msg4 ACK / CBRA success before gNB restart. |
| RedCap BWP / common config | TS 38.331 Section 6.3.2 [Needs Verification] | Case B RedCap BWP and PUCCH common fallback boundary were checked in logs. |
| NAS registration / PDU session | TS 24.501 exact clauses [Needs Verification] | `59/64` Registration Accept and PDU Session Establishment Accept were observed before restart impact. |
| NRF / NF discovery | TS 29.510 exact clause [Needs Verification] | Static discovery mitigation stayed clean at 64 UE. |

## 5. Practice Exercises
- [Basic] Why does `tun=0` not mean all 64 UEs failed NAS/PDU setup in this run?
- [Applied] Which counters separate [CN pressure] from [gNB runtime restart] in this evidence set?
- [Advanced] Design a 60 UE bracketing run that can tell whether the threshold is between 56 and 64 without changing scheduler code.

## Evidence
- Main log: `test_log/compiler_logs/mmtc_smoke_64ue_caseb_static_cn_2026-05-08_16-55-20_escalated.log`.
- gNB log: `test_log/compiler_logs/mmtc_smoke_2026-05-08_16-55-20_gnb.log`.
- gNB state: `test_log/compiler_logs/mmtc_smoke_2026-05-08_16-55-20_gnb_state.log`.
- gNB restart tail: `test_log/compiler_logs/mmtc_smoke_2026-05-08_16-55-20_gnb_restart_tail300.log`.
- AMF log: `test_log/compiler_logs/mmtc_smoke_2026-05-08_16-55-20_amf.log`.
- SMF log: `test_log/compiler_logs/mmtc_smoke_2026-05-08_16-55-20_smf.log`.
- UPF log: `test_log/compiler_logs/mmtc_smoke_2026-05-08_16-55-20_upf.log`.
- Artifact directory: `test_log/runtime_artifacts/m5_rt_m5_064_caseb_static_cn_2026-05-08_16-55-20/`.
