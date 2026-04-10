# RedCap Runtime Validation Summary

## Scope
- [Scenario]：`container_5g_flexric_rfsim_redcap.xml`
- [HTML Report]：`/home/tonywang/OAI/Red_cap_openairinterface5g/ci-scripts/test_results.html`
- [Artifacts Dir]：`/home/tonywang/OAI/Red_cap_openairinterface5g/cmake_targets/log/container_5g_flexric_rfsim_redcap.xml.d`
- [Run Log]：`/home/tonywang/OAI/Red_cap_openairinterface5g/test_log/compiler_logs/redcap_runtime_host_case-a_2026-04-10_17-14-54.log`
- [Expected CORESET#0 Mode]：`case-a`
- [gNB Config]：`/home/tonywang/OAI/Red_cap_openairinterface5g/test_log/runtime_configs/gnb.redcap.case-a.2026-04-10_17-14-54.yaml`

## Task Mapping
- [Task Name]：[M3 Runtime Close-out / RedCap RFsim validation]
- [3GPP Spec Clause]：[TS 38.306 Clause 4.2.21.1] / [TS 38.331 Clause 5.2.2.4.2] / [TS 38.331 Clause 5.6.1.3]
- [Prerequisite Tasks]：[Milestone 2 SIB1 support] / [Milestone 3 BWP & CORESET#0 code path] / [build recovery]

## Test Case Summary
- [Attach UE1] `333331`：[KO] Attach OAI UE 1
  Could not retrieve UE IP address(es) or MTU(s) wrong!
  [Artifacts]：[none]
- [Verify UE1 non-RedCap] `302001`：[SKIP] Verify UE 1 is normal (no RedCap)
  [Artifacts]：[none]
- [Attach UE2 RedCap] `333332`：[SKIP] Attach OAI UE 2 (RedCap)
  [Artifacts]：[none]
- [Verify UE2 RedCap] `302002`：[SKIP] Verify UE 2 is RedCap
  [Artifacts]：[none]
- [Verify SIB1 RedCap initial DL BWP] `302003`：[SKIP] Verify gNB builds RedCap initial BWP into SIB1
  [Artifacts]：[none]
- [Ping both UEs] `020005`：[SKIP] Ping ext-dn from both UEs
  [Artifacts]：[none]
- [Iperf DL 60 Mbps UDP on UE2] `030001`：[SKIP] Iperf RedCap UE2 (DL/60Mbps/UDP)(30 sec)
  [Artifacts]：[none]
- [Iperf UL 20 Mbps UDP on UE2] `030002`：[SKIP] Iperf RedCap UE2 (UL/20Mbps/UDP)(30 sec)
  [Artifacts]：[none]

## gNB Log Cross-Check
- [gNB log]：未找到 `*-oai-gnb.logs`，無法交叉驗證 [302002] / [302003]。

## UE2 Log Cross-Check
- [UE2 log]：`/home/tonywang/OAI/Red_cap_openairinterface5g/cmake_targets/log/container_5g_flexric_rfsim_redcap.xml.d/22-100009-oai-nr-ue2.logs`
- [UE applied RedCap initial DL BWP]：未在 UE2 log log 中找到
- [UE applied RedCap initial UL BWP]：未在 UE2 log log 中找到

## Exit Criteria
- [302003] 應為 [OK]，且 [gNB log] 內應出現 `SIB1 RedCap initial DL BWP`。
- [302002] 應為 [OK]，且 [gNB log] 內應出現 `UE with RNTI .... is RedCap`。
- [Expected CORESET#0 mode] 應與 `mode=case-a`, `mode=case-a-full-cell` 之一一致。
- [333332] / [302002] 若成功，代表 RedCap UE 已完成 common search space 監聽與 attach，可視為 [PDCCH decode] 的 runtime 證據。
- [030001] / [030002] 應為 [OK]，並可在對應 `iperf_client_rfsim5g_ue2.log` 中看到 [Receiver Bitrate] 與 [Packet Loss]。
- [020005] 應為 [OK]，並可在 `ping_rfsim5g_ue*.log` 中看到 [0% 或可接受門檻內] 的 [packet loss]。

## Notes
- [⚠ Needs Verification]：若 `test_results.html` 或 artifacts 缺失，通常代表 scenario 尚未完整跑完，或在 deploy 前即失敗。
- 若要補完整學習報告，可直接引用這份摘要，再加上 [Technical Background] 與 [Practice Exercises]。

