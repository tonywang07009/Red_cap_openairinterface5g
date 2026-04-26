# RedCap Runtime Validation Summary

## Scope
- [Scenario]：`container_5g_flexric_rfsim_redcap.xml`
- [HTML Report]：`/home/tonywang/OAI/Red_cap_openairinterface5g/ci-scripts/test_results.html`
- [Artifacts Dir]：`/home/tonywang/OAI/Red_cap_openairinterface5g/cmake_targets/log/container_5g_flexric_rfsim_redcap.xml.d`
- [Run Log]：`/home/tonywang/OAI/Red_cap_openairinterface5g/test_log/compiler_logs/redcap_runtime_host_case-b_2026-04-26_19-46-51.log`
- [Expected CORESET#0 Mode]：`case-b`
- [gNB Config]：`/home/tonywang/OAI/Red_cap_openairinterface5g/test_log/runtime_configs/gnb.redcap.case-b.2026-04-26_19-42-54.yaml`
- [E2 Agent Mode]：`enabled`

## Task Mapping
- [Task Name]：[M5 Runtime validation / E2 xApp RedCap UL PRB control / UL throughput]
- [3GPP Spec Clause]：[TS 38.306 Clause 4.2.21.1] / [TS 38.331 Clause 5.2.2.4.2] / [TS 38.331 Clause 5.6.1.3]
- [Prerequisite Tasks]：[Milestone 2 SIB1 support] / [Milestone 3 BWP & CORESET#0 code path] / [Milestone 5 E2/xApp UL PRB control plumbing]

## Test Case Summary
- [Attach UE1] `333331`：[OK] Attach OAI UE 1
  UE rfsim5g_redcap_ue1: 10.0.0.2
  [Artifacts]：[none]
- [Verify UE1 non-RedCap] `302001`：[OK] Verify UE 1 is normal (no RedCap)
  [Artifacts]：[none]
- [Attach UE2 RedCap] `333332`：[KO] Attach OAI UE 2 (RedCap)
  Could not retrieve UE IP address(es) or MTU(s) wrong!
  [Artifacts]：[none]
- [Verify UE2 RedCap] `302002`：[SKIP] Verify UE 2 is RedCap
  [Artifacts]：[none]
- [Verify SIB1 RedCap initial DL BWP] `302003`：[SKIP] Verify gNB builds RedCap initial DL BWP into SIB1
  [Artifacts]：[none]
- [Verify SIB1 RedCap initial UL BWP] `302004`：[SKIP] Verify gNB builds RedCap initial UL BWP into SIB1
  [Artifacts]：[none]
- [Ping both UEs] `020005`：[SKIP] Ping ext-dn from both UEs
  [Artifacts]：[none]
- [Iperf UL 50 Mbps UDP on UE2] `030001`：[SKIP] Iperf RedCap UE2 (UL/50Mbps/UDP)(30 sec)
  [Artifacts]：[none]
- [Apply E2/xApp RedCap UL PRB cap] `302005`：[SKIP] Apply RedCap UL PRB cap to UE 2 via FlexRIC RC control
  [Artifacts]：[none]
- [Verify gNB applied RedCap UL PRB cap] `302006`：[SKIP] Verify gNB applied RedCap UL PRB cap
  [Artifacts]：[none]
- [Iperf UL 20 Mbps UDP on UE2] `030002`：[SKIP] Iperf RedCap UE2 (UL/20Mbps/UDP)(30 sec)
  [Artifacts]：[none]

## Run Log Diagnosis
- [Run log]：`/home/tonywang/OAI/Red_cap_openairinterface5g/test_log/compiler_logs/redcap_runtime_host_case-b_2026-04-26_19-46-51.log`
- [Legacy PUCCH budget assert]：未找到
- [BWP-fit PUCCH budget marker]：未找到
- [Prebuilt image warning]：未找到

## gNB Log Cross-Check
- [gNB log]：`/home/tonywang/OAI/Red_cap_openairinterface5g/cmake_targets/log/container_5g_flexric_rfsim_redcap.xml.d/27-100009-oai-gnb.logs`
- [SIB1 RedCap initial DL BWP]：找到 2 筆範例
  redCapInitialBWP_r17:
  81709.508699 [NR_RRC] I SIB1 RedCap initial DL BWP: start=0 size=51 scs=1 coreset0=10 searchSpace0=0 mode=case-b-edge-only
- [SIB1 RedCap initial UL BWP]：找到 2 筆範例
  initialULPUCCH_ResourceCommonRedCap_r17: 0
  81709.508704 [NR_RRC] I SIB1 RedCap initial UL BWP: start=0 size=51 scs=1 pucch_ResourceCommonRedCap=0
- [UE marked as RedCap]：未在 gNB log 中找到
- [Legacy PUCCH budget assert]：未在 gNB log 中找到
- [BWP-fit PUCCH budget marker]：找到 1 筆範例
  81732.551749 [NR_RRC] I Reducing PUCCH reservation budget from 64 to 43 UEs for BWP with 51 PRBs (PUCCH2 per slot 1)
- [RedCap UL PRB control applied]：未在 gNB log 中找到
- [Expected CORESET#0 mode]：找到 1 筆範例
  81709.508699 [NR_RRC] I SIB1 RedCap initial DL BWP: start=0 size=51 scs=1 coreset0=10 searchSpace0=0 mode=case-b-edge-only
- [Case B edge-aligned PRB allocation]：找到 1 筆範例
  81709.508698 [NR_MAC] I RedCap CORESET#0 Case B edge-aligned PRB allocation: start=0 size=51 carrier_bw=106 common_coreset_id=1

## UE2 Log Cross-Check
- [UE2 log]：`/home/tonywang/OAI/Red_cap_openairinterface5g/cmake_targets/log/container_5g_flexric_rfsim_redcap.xml.d/27-100009-oai-nr-ue2.logs`
- [UE applied RedCap initial DL BWP]：找到 3 筆範例
  81735.366184 [NR_MAC] I Applying SIB1 RedCap initial DL BWP: start=0 size=51
  81735.459153 [NR_MAC] I Applying SIB1 RedCap initial DL BWP: start=0 size=51
  81735.549538 [NR_MAC] I Applying SIB1 RedCap initial DL BWP: start=0 size=51
- [UE applied RedCap initial UL BWP]：找到 3 筆範例
  81735.366186 [NR_MAC] I Applying SIB1 RedCap initial UL BWP: start=0 size=51
  81735.459154 [NR_MAC] I Applying SIB1 RedCap initial UL BWP: start=0 size=51
  81735.549540 [NR_MAC] I Applying SIB1 RedCap initial UL BWP: start=0 size=51

## Exit Criteria
- [302003] 應為 [OK]，且 [gNB log] 內應出現 `SIB1 RedCap initial DL BWP`。
- [302004] 應為 [OK]，且 [gNB log] 內應出現 `SIB1 RedCap initial UL BWP`。
- [302002] 應為 [OK]，且 [gNB log] 內應出現 `UE with RNTI .... is RedCap`。
- [302005] / [302006] 應為 [OK]，且 [gNB log] 內應出現 `RedCap UL PRB control RNTI .... requested ... effective ...`。
- [Expected CORESET#0 mode] 應與 `mode=case-b`, `mode=case-b-edge-only` 之一一致。
- [Case B] 應在 [gNB log] 中看到 `RedCap CORESET#0 Case B edge-aligned PRB allocation`。
- [333332] / [302002] 若成功，代表 RedCap UE 已完成 common search space 監聽與 attach，可視為 [PDCCH decode] 的 runtime 證據。
- [UE2 log] 應同時看到 `Applying SIB1 RedCap initial DL BWP` 與 `Applying SIB1 RedCap initial UL BWP`，才算完成 UE 端雙向 RedCap BWP 套用。
- [030001] / [030002] 應為 [OK]，並可在對應 `iperf_client_rfsim5g_redcap_ue2.log` 中看到 [Receiver Bitrate] 與 [Packet Loss]。
- [020005] 應為 [OK]，並可在 `ping_rfsim5g_redcap_ue*.log` 中看到 [0% 或可接受門檻內] 的 [packet loss]。

## Notes
- [⚠ Needs Verification]：若 `test_results.html` 或 artifacts 缺失，通常代表 scenario 尚未完整跑完，或在 deploy 前即失敗。
- 若要補完整學習報告，可直接引用這份摘要，再加上 [Technical Background] 與 [Practice Exercises]。

