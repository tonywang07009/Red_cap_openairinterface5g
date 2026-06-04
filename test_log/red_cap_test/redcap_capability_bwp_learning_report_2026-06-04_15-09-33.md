# RedCap Capability / BWP 證據學習報告

## 1. Technical Background

- 本次測試在同一組 [106PRB] gNB/CN profile 下，比較一個 [normal UE] 與一個 [RedCap UE]。
- [normal UE] 應該能完成註冊與 PDU Session，但只送出 legacy/minimal NR capability，不包含 [redCapParameters-r17]。
- [RedCap UE] 應該讀入 [nrue_recap]，建立 Rel-17 [UE-NR-Capability]，帶出 [redCapParameters-r17/supportOfRedCap-r17]，並讓 gNB 解析成功。
- gNB 保留完整 serving-cell carrier [106PRB]，同時在 SIB1 廣播 RedCap 專用 initial BWP [51PRB]。
- 排程證據分成兩層：
  - [RRC proof]：gNB 對 UE2 解析到 [redCapParameters-r17]，對 UE1 顯示 absent。
  - [MAC proof]：gNB 對 UE2 印出 [RedCap MAC][gNB UE profile] 與 RedCap RA/Msg4 compact allocation。

## 2. Key C Functions / Data Structures

- [nr_rrc_ue_process_ueCapabilityEnquiry()] in `openair2/RRC/NR_UE/rrc_UE.c`
  - 在收到 [UECapabilityEnquiry]、真正 encode 前再次讀取 [nrue_recap]。
  - 若 RedCap 啟用，改用 [nr_rrc_build_redcap_ue_capability()] 建立 capability。
- [nr_rrc_build_redcap_ue_capability()] in `openair2/RRC/NR_UE/rrc_ue_redcap.c`
  - 建立 Rel-17 [NR_UE_NR_Capability_t]。
  - 插入 [redCapParameters-r17] 與 [supportOfRedCap-r17]。
- [handle_ueCapabilityInformation()] in `openair2/RRC/NR/rrc_gNB.c`
  - decode UE capability，並記錄 [redCapParameters-r17] present/absent。
- [NR_UE_info_t.is_redcap] in gNB MAC
  - gNB 收到 RedCap CCCH 48-bit LCID 時設定。
- [redCapInitialBWP_r17] in gNB YAML/SIB1
  - 廣播 RedCap 專用 initial DL/UL BWP。

## 3. Test Results Summary

| Test Item | Evidence | Status |
|---|---|---|
| Local image selection | final override 使用 `oai-gnb:latest`, `oai-nr-ue:latest` | PASS |
| UE1 normal flow | `10.0.0.2`, `cap=no`, `reg=yes`, `pdu=yes` | PASS |
| UE2 RedCap flow | `10.0.0.3`, `cap=yes`, `reg=yes`, `pdu=yes` | PASS |
| UE1 capability | `rel15`, `bandNR=1`, `10 bytes`, gNB parsed RedCap absent | PASS |
| UE2 capability | `rel17`, `bandNR=78`, `redCapParameters-r17`, `supportOfRedCap-r17`, `20 bytes` | PASS |
| gNB parsing | `Parsed UE redCapParameters-r17: UE 2 ... supportOfRedCap-r17=1` | PASS |
| RedCap BWP/SIB1 | gNB config/log 顯示 RedCap initial DL/UL BWP size 51 | PASS |
| RedCap scheduler/profile | `[RedCap MAC][gNB UE profile]` 與 RedCap RA/Msg4 logs | PASS |

## 4. 3GPP Specification Mapping

- [TS 38.306 Section 4] [Needs Verification]
  - 對應 [UE Radio Access Capability Parameters]，包含 [supportOfRedCap-r17] 這類 RedCap capability indication。
- [TS 38.331 Section 5.6.3] [Needs Verification]
  - 對應 [UE capability transfer]，gNB 送出 [UECapabilityEnquiry]，UE 回覆 [UECapabilityInformation]。
- [TS 38.331 Section 6.3.1]
  - 對應 [SIB1] information elements，包含 [redCap-ConfigCommon-r17]、[initialDownlinkBWP-RedCap-r17]、[initialUplinkBWP-RedCap-r17]。
- [TS 38.321 Section 5.1]
  - 對應 [Random Access procedure]，本次 gNB MAC log 中的 RedCap RA evidence 屬於此流程。

## 5. Practice Exercises

- [Basic]
  - 為什麼 gNB config 內有 [redCapInitialBWP_r17]，但 UE1 normal UE 仍然可以註冊成功？
- [Applied]
  - 在 `redcap_ue_capability_evidence_2026-06-04_15-09-33.txt` 中，哪些行可以證明 UE2 送出了 [redCapParameters-r17]？
- [Advanced]
  - 如果要讓論文證據更直觀，你會如何擴充 gNB scheduler log，讓同一行同時印出設定的 [51PRB RedCap BWP] 與實際 RA DCI 使用的 [bwp_size]？

