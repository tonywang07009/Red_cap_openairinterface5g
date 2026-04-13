# RedCap Runtime Validation Summary

## Scope
- [Scenario]：`container_5g_flexric_rfsim_redcap.xml`
- [HTML Report]：`/home/tonywang/OAI/Red_cap_openairinterface5g/ci-scripts/test_results.html`
- [Artifacts Dir]：`/home/tonywang/OAI/Red_cap_openairinterface5g/cmake_targets/log/container_5g_flexric_rfsim_redcap.xml.d`
- [Run Log]：`/home/tonywang/OAI/Red_cap_openairinterface5g/test_log/compiler_logs/redcap_runtime_host_disabled_2026-04-13_14-33-45.log`
- [gNB Config]：`/home/tonywang/OAI/Red_cap_openairinterface5g/test_log/runtime_configs/gnb.redcap_disabled_2026-04-13_14-33-45.yaml`
- [E2 Agent Mode]：`disabled`

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
- [Attach UE2 RedCap] `333332`：[OK] Attach OAI UE 2 (RedCap)
  UE rfsim5g_redcap_ue2: 10.0.0.3
  [Artifacts]：[none]
- [Verify UE2 RedCap] `302002`：[OK] Verify UE 2 is RedCap
  [Artifacts]：[none]
- [Verify SIB1 RedCap initial DL BWP] `302003`：[OK] Verify gNB builds RedCap initial DL BWP into SIB1
  [Artifacts]：[none]
- [Verify SIB1 RedCap initial UL BWP] `302004`：[OK] Verify gNB builds RedCap initial UL BWP into SIB1
  [Artifacts]：[none]
- [Ping both UEs] `020005`：[KO] Ping ext-dn from both UEs
  UE rfsim5g_redcap_ue1 (10.0.0.2)
  Packet Loss: 0%
  RTT(Min)   : 4.485 ms
  RTT(Avg)   : 6.400 ms
  RTT(Max)   : 7.999 ms
           UE rfsim5g_redcap_ue2 (10.0.0.3)
  [Artifacts]：15-020005-ping_rfsim5g_redcap_ue1.log, 15-020005-ping_rfsim5g_redcap_ue2.log
- [Iperf UL 50 Mbps UDP on UE2] `030001`：[SKIP] Iperf RedCap UE2 (UL/50Mbps/UDP)(30 sec)
  [Artifacts]：[none]
- [Apply E2/xApp RedCap UL PRB cap] `302005`：[SKIP] Apply RedCap UL PRB cap to UE 2 via FlexRIC RC control
  [Artifacts]：[none]
- [Verify gNB applied RedCap UL PRB cap] `302006`：[SKIP] Verify gNB applied RedCap UL PRB cap
  [Artifacts]：[none]
- [Iperf UL 20 Mbps UDP on UE2] `030002`：[SKIP] Iperf RedCap UE2 (UL/20Mbps/UDP)(30 sec)
  [Artifacts]：[none]

## Run Log Diagnosis
- [Run log]：`/home/tonywang/OAI/Red_cap_openairinterface5g/test_log/compiler_logs/redcap_runtime_host_disabled_2026-04-13_14-33-45.log`
- [Legacy PUCCH budget assert]：未找到
- [BWP-fit PUCCH budget marker]：未找到
- [Prebuilt image warning]：未找到

## gNB Log Cross-Check
- [gNB log]：`/home/tonywang/OAI/Red_cap_openairinterface5g/cmake_targets/log/container_5g_flexric_rfsim_redcap.xml.d/25-100009-oai-gnb.logs`
- [SIB1 RedCap initial DL BWP]：找到 2 筆範例
  redCapInitialBWP_r17:
  360408.234930 [NR_RRC] I SIB1 RedCap initial DL BWP: start=0 size=51 scs=1 coreset0=10 searchSpace0=0 mode=case-a-full-cell
- [SIB1 RedCap initial UL BWP]：找到 2 筆範例
  initialULPUCCH_ResourceCommonRedCap_r17: 0
  360408.234934 [NR_RRC] I SIB1 RedCap initial UL BWP: start=0 size=51 scs=1 pucch_ResourceCommonRedCap=0
- [UE marked as RedCap]：找到 1 筆範例
  360431.660526 [MAC]    I UE with RNTI b92c is RedCap
- [Legacy PUCCH budget assert]：未在 gNB log 中找到
- [BWP-fit PUCCH budget marker]：找到 2 筆範例
  360431.590850 [NR_RRC] I Reducing PUCCH reservation budget from 64 to 43 UEs for BWP with 51 PRBs (PUCCH2 per slot 1)
  360431.660571 [NR_RRC] I Reducing PUCCH reservation budget from 64 to 43 UEs for BWP with 51 PRBs (PUCCH2 per slot 1)
- [RedCap UL PRB control applied]：在 [REDCAP_E2_AGENT_MODE=disabled] host health-check 中屬於 [N/A]

## UE2 Log Cross-Check
- [UE2 log]：`/home/tonywang/OAI/Red_cap_openairinterface5g/cmake_targets/log/container_5g_flexric_rfsim_redcap.xml.d/25-100009-oai-nr-ue2.logs`
- [UE applied RedCap initial DL BWP]：找到 1 筆範例
  360431.653969 [NR_MAC] I Applying SIB1 RedCap initial DL BWP: start=0 size=51
- [UE applied RedCap initial UL BWP]：找到 1 筆範例
  360431.653971 [NR_MAC] I Applying SIB1 RedCap initial UL BWP: start=0 size=51

## E2 Disabled Cross-Check
- [xApp log]：`/home/tonywang/OAI/Red_cap_openairinterface5g/cmake_targets/log/container_5g_flexric_rfsim_redcap.xml.d/25-100009-xapp-rc-moni.logs`
- [xApp no registered nodes marker]：找到 3 筆範例
  [xApp]: The nearRT-RIC has no registered nodes. Resending the E42 SETUP-REQUEST in 5s.
  [xApp]: The nearRT-RIC has no registered nodes. Resending the E42 SETUP-REQUEST in 5s.
  [xApp]: The nearRT-RIC has no registered nodes. Resending the E42 SETUP-REQUEST in 5s.

- [nearRT-RIC log]：`/home/tonywang/OAI/Red_cap_openairinterface5g/cmake_targets/log/container_5g_flexric_rfsim_redcap.xml.d/25-100009-nearRT-RIC.logs`
- [nearRT-RIC zero registered nodes marker]：找到 3 筆範例
  [NEAR-RIC]: Registered E2 nodes = 0.
  [NEAR-RIC]: Registered E2 nodes = 0.
  [NEAR-RIC]: Registered E2 nodes = 0.

## Exit Criteria
- [302003] 應為 [OK]，且 [gNB log] 內應出現 `SIB1 RedCap initial DL BWP`。
- [302004] 應為 [OK]，且 [gNB log] 內應出現 `SIB1 RedCap initial UL BWP`。
- [302002] 應為 [OK]，且 [gNB log] 內應出現 `UE with RNTI .... is RedCap`。
- [302005] / [302006]：在 [REDCAP_E2_AGENT_MODE=disabled] host health-check 中屬於 [N/A]；本輪應改看 [xApp no registered nodes] 與 [nearRT-RIC Registered E2 nodes = 0]。
- [333332] / [302002] 若成功，代表 RedCap UE 已完成 common search space 監聽與 attach，可視為 [PDCCH decode] 的 runtime 證據。
- [UE2 log] 應同時看到 `Applying SIB1 RedCap initial DL BWP` 與 `Applying SIB1 RedCap initial UL BWP`，才算完成 UE 端雙向 RedCap BWP 套用。
- [030001] / [030002] 應為 [OK]，並可在對應 `iperf_client_rfsim5g_redcap_ue2.log` 中看到 [Receiver Bitrate] 與 [Packet Loss]。
- [020005] 應為 [OK]，並可在 `ping_rfsim5g_redcap_ue*.log` 中看到 [0% 或可接受門檻內] 的 [packet loss]。

## Notes
- [⚠ Needs Verification]：若 `test_results.html` 或 artifacts 缺失，通常代表 scenario 尚未完整跑完，或在 deploy 前即失敗。
- 若要補完整學習報告，可直接引用這份摘要，再加上 [Technical Background] 與 [Practice Exercises]。

