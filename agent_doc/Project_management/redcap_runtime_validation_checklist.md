# RedCap [Runtime Validation] Checklist

## [Task Definition]
- [Task Name]：[RedCap RFsim + FlexRIC end-to-end validation]
- [Corresponding 3GPP Spec Clause]：
  - [TS 38.306 Clause 4.2.21.1]：[RedCap FR1 capability / reduced bandwidth scope]
  - [TS 38.331 Clause 5.2.2.4.2]：[SIB1 中的 `redCap-ConfigCommon-r17` / `halfDuplexRedCapAllowed-r17` / RedCap access barring]
  - [TS 38.331 Clause 5.6.1.3]：[UE capability signaling，供 gNB 判斷 UE 是否為 RedCap]
  - [TS 38.321 Clause 5.1]：[Random Access attach path] ⚠ [Needs Verification：建議再對照本地 PDF 條文原文]
- [Prerequisite Tasks]：
  - [Milestone 2]：[RRC / SIB1 Support]
  - [Milestone 3]：[BWP & CORESET#0]
  - [Build Recovery]：[offline CMake / parser-UICC decoupling]

## [Host Execution]
- [Environment]：需在有 [docker socket] 權限的 host 執行。
- [Python Dependencies]：
  - `cd /home/tonywang/OAI/Red_cap_openairinterface5g/ci-scripts`
  - `python3 -m pip install -r requirements.txt`
- [Recommended Command]：
  - `./redcap_runtime_host_validation.sh`
- [Equivalent Split Commands]：
  - `./run_locally.sh container_5g_flexric_rfsim_redcap.xml`
  - `python3 redcap_runtime_summary.py --scenario container_5g_flexric_rfsim_redcap.xml --output ../test_log/report/redcap_runtime_manual_summary.md`

## [Expected Artifacts]
- [HTML Report]：
  - `/home/tonywang/OAI/Red_cap_openairinterface5g/ci-scripts/test_results.html`
- [Scenario Artifacts]：
  - `/home/tonywang/OAI/Red_cap_openairinterface5g/cmake_targets/log/container_5g_flexric_rfsim_redcap.xml.d/`
- [Host Run Log]：
  - `/home/tonywang/OAI/Red_cap_openairinterface5g/test_log/compiler_logs/redcap_runtime_host_<timestamp>.log`
- [Markdown Summary]：
  - `/home/tonywang/OAI/Red_cap_openairinterface5g/test_log/report/redcap_runtime_host_summary_<timestamp>.md`

## [Validation Gates]
- [333331]：[Attach OAI UE 1]
  - [Pass Condition]：`test_results.html` 中為 [OK]，並顯示 `UE rfsim5g_ue: <IP>`。
- [302001]：[Verify UE 1 is normal (no RedCap)]
  - [Pass Condition]：`test_results.html` 中為 [OK]。
- [333332]：[Attach OAI UE 2 (RedCap)]
  - [Pass Condition]：`test_results.html` 中為 [OK]，並顯示 `UE rfsim5g_ue2: <IP>`。
- [302002]：[Verify UE 2 is RedCap]
  - [Pass Condition]：`test_results.html` 中為 [OK]。
  - [Cross-check]：`*-oai-gnb.logs` 中至少一筆 `UE with RNTI .... is RedCap`。
- [302003]：[Verify gNB builds RedCap initial BWP into SIB1]
  - [Pass Condition]：`test_results.html` 中為 [OK]。
  - [Cross-check]：`*-oai-gnb.logs` 中至少一筆 `SIB1 RedCap initial DL BWP`。
- [020005]：[Ping ext-dn from both UEs]
  - [Pass Condition]：`test_results.html` 中為 [OK]。
  - [Cross-check]：`*-020005-ping_rfsim5g_ue*.log` 中 [packet loss] 不超過 XML 門檻。
- [030001]：[Iperf RedCap UE2 DL 60 Mbps UDP]
  - [Pass Condition]：`test_results.html` 中為 [OK]。
  - [Cross-check]：`*-030001-iperf_client_rfsim5g_ue2.log` 中 [Receiver Bitrate] 與 [Packet Loss] 符合 XML 門檻。
- [030002]：[Iperf RedCap UE2 UL 20 Mbps UDP]
  - [Pass Condition]：`test_results.html` 中為 [OK]。
  - [Cross-check]：`*-030002-iperf_client_rfsim5g_ue2.log` 中 [Receiver Bitrate] 與 [Packet Loss] 符合 XML 門檻。

## [Failure Triage Order]
- [Step 1]：先看 `test_results.html`，確認失敗停在哪個 [Test ID]。
- [Step 2]：看 `cmake_targets/log/container_5g_flexric_rfsim_redcap.xml.d/*-oai-gnb.logs`，優先查：
  - `SIB1 RedCap initial DL BWP`
  - `UE with RNTI`
  - `Assertion`
  - `Segmentation fault`
- [Step 3]：若 attach 失敗，看 `*-oai-nr-ue1.logs` / `*-oai-nr-ue2.logs` 是否有 [IP assign] 或 [RRC reject]。
- [Step 4]：若 throughput 失敗，看 `*-iperf_client_rfsim5g_ue2.log` 的 [Receiver Bitrate] 與 [Packet Loss]。
- [Step 5]：若整體在 deploy 前失敗，先檢查：
  - [docker image] 是否存在
  - [requirements.txt] 是否已安裝
  - [docker socket] 權限是否可用

## [Educational Notes]
- [302003] 重點不是單純印 log，而是驗證 [gNB 已把 RedCap 專用 initial DL BWP 廣播進 SIB1]。
- [302002] 重點是 [gNB 依 UE capability / access path 將 UE2 判定為 RedCap]。
- [030001] / [030002] 是 [Milestone 5] 的整合驗證，不單看吞吐，也是在驗證前面 [SIB1 / BWP / capability wiring] 是否真的能支撐完整資料面。
