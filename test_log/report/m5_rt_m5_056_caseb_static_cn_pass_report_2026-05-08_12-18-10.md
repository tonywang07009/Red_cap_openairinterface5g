# RT-M5-056 Case B Static CN Pass Report

## 1. Technical Background
- [RT-M5-056] previously failed after the RAN random-access path had completed for all 56 UEs. The failed UEs reached late NAS/PDU stages, with AMF authentication-vector and SMF-selection pressure markers visible in CN logs.
- This rerun keeps the same Case B gNB RedCap runtime and 56 sampled UEs, but reduces CN discovery pressure by using static CN discovery boundaries: NRF registration is disabled for the local CN config, AMF SMF selection is disabled, and SMF uses a static UPF N4 endpoint.
- Result: the CN/NAS/PDU blocker is cleared at 56 UE. RAN still shows elevated but non-terminal Msg2 window / UE RAR retry pressure, which should remain the primary risk counter for [RT-M5-060] and [RT-M5-064].

## 2. Key Runtime Components / Data Structures
- [gNB runtime config]: `test_log/runtime_configs/gnb.redcap_mmtc_case-b_2026-05-02_12-35-01.yaml`.
- [CN runtime config]: `/home/tonywang/OAI/oai-cn5g/conf/config.yaml`.
- [CN backup]: `test_log/runtime_configs/oai-cn5g_config_pre_static_2026-05-08_12-05-00.yaml`.
- [mMTC script]: `ci-scripts/redcap_mmtc_smoke_validation.sh`.
- [Docker compose source]: `/home/tonywang/OAI/oai-cn5g/docker-compose.yaml`.

## 3. Test Results Summary
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| [RT-M5-056] summary | PASS | 56 sampled UEs | `56/56` running / attach / PDU / tunnel / forward ping |
| CN auth / SMF-selection blocker | PASS | AMF / SMF / UPF logs | `Request Authentication Vectors failure=0`, `Registration Reject=0`, `SMF Selection, no SMF candidate=0` |
| NRF pressure markers | PASS | AMF / SMF / UPF logs | `Could not get response from NRF=0`, `HTTP Code: 0/400=0`, `NF Instance Registration=0` |
| Msg2 DCI / CCE | PASS | gNB log | `56 x cce=0 agg=4` |
| Msg2 retry pressure | PASS with observation | gNB + UE logs | Msg2 window fail `55`; UE RAR reception failed `55`; all affected UEs later completed |
| Msg2 / Msg4 VRB pressure | PASS | gNB log | Msg2 `vrb_map fail=0`, Msg4 `vrb_map fail=0` |
| Msg4 contention | PASS | gNB log | Msg4 ACK / CBRA success `56`, contention timer expired `0` |
| UE PUCCH common fallback blocker | PASS | UE logs | `pucch_ResourceCommon is NULL=0`, `fallback=0/1=0/0` |
| Ping | PASS | 56 UE ping logs | `56/56` logs show `0% packet loss` |

## 4. 3GPP Specification Mapping
| Flow | Clause | Mapping |
|------|--------|---------|
| Random Access baseline | TS 38.321 Section 5.1 | UE contention-based RA must progress through Msg1/Msg2/Msg3/Msg4. |
| RAR reception | TS 38.321 Section 5.1.4 [Needs Verification] | Msg2 / RAR retry counters are used to classify RA response-window pressure. |
| Contention resolution | TS 38.321 Section 5.1.5 [Needs Verification] | Msg4 ACK / CBRA success confirms contention resolution completion. |
| RedCap BWP / common config | TS 38.331 Section 6.3.2 [Needs Verification] | Case B RedCap BWP and common PUCCH boundary are checked through runtime logs. |
| NAS registration / PDU session | TS 24.501 exact clauses [Needs Verification] | Registration Accept and PDU Session Establishment Accept are used as CN-side pass markers. |
| NRF / NF discovery | TS 29.510 exact clause [Needs Verification] | Static discovery mitigation changes CN discovery pressure, not RAN behavior. |

## 5. Practice Exercises
- [Basic] Why can [Msg2 window fail] appear in logs while the final [RT-M5-056] result still passes?
- [Applied] Compare the failed `11:20:59` run and the static CN `12:03:22` run. Which counters prove the terminal blocker moved away from RAN?
- [Advanced] For [RT-M5-060], design a decision rule that separates [CN discovery pressure] from [RA response-window pressure].

## Evidence
- Main log: `test_log/compiler_logs/mmtc_smoke_56ue_caseb_static_cn_2026-05-08_12-03-21_escalated.log`.
- gNB log: `test_log/compiler_logs/mmtc_smoke_2026-05-08_12-03-22_gnb.log`.
- AMF log: `test_log/compiler_logs/mmtc_smoke_2026-05-08_12-03-22_amf.log`.
- SMF log: `test_log/compiler_logs/mmtc_smoke_2026-05-08_12-03-22_smf.log`.
- UPF log: `test_log/compiler_logs/mmtc_smoke_2026-05-08_12-03-22_upf.log`.
- Artifact directory: `test_log/runtime_artifacts/m5_rt_m5_056_caseb_static_cn_2026-05-08_12-03-22/`.
