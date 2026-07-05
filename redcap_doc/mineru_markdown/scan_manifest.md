# RedCap MinerU Markdown Scan Manifest

## Purpose
- Track Markdown cache generated from RedCap specs and evaluation papers.
- Use Markdown cache for quick lookup; use source PDFs for exact wording and final clause verification.
- Status `[PENDING_LARGE_PDF]` means the source is too large for an interactive MinerU OCR run.

## Inventory
| Kind | Pages | Source PDF | Markdown Cache | Status | Note |
|---|---:|---|---|---|---|
| `paper` | 4 | `redcap_doc/evaluation_papers/5G-A_RedCap_Technology_and_Applications.pdf` | `redcap_doc/mineru_markdown/evaluation_papers/5G-A_RedCap_Technology_and_Applications.pdf/auto/5G-A_RedCap_Technology_and_Applications.pdf.md` | [CACHED] | existing Markdown cache |
| `paper` | 6 | `redcap_doc/evaluation_papers/5G_Reduced_Capability_Devices_Analysis_of_Blocking_Probability_for_Control_Channels.pdf` | `redcap_doc/mineru_markdown/evaluation_papers/5G_Reduced_Capability_Devices_Analysis_of_Blocking_Probability_for_Control_Channels.pdf/auto/5G_Reduced_Capability_Devices_Analysis_of_Blocking_Probability_for_Control_Channels.pdf.md` | [PARSED] | MinerU pipeline markdown |
| `paper` | 13 | `redcap_doc/evaluation_papers/Coverage_Evaluation_for_5G_Reduced_Capability_New_Radio_NR-RedCap.pdf` | `redcap_doc/mineru_markdown/evaluation_papers/Coverage_Evaluation_for_5G_Reduced_Capability_New_Radio_NR-RedCap.pdf/auto/Coverage_Evaluation_for_5G_Reduced_Capability_New_Radio_NR-RedCap.pdf.md` | [PARSED] | MinerU pipeline markdown |
| `paper` | 6 | `redcap_doc/evaluation_papers/Enhancing_Uplink_Performance_of_NR_RedCap_in_Industrial_5G_B5G_Systems.pdf` | `redcap_doc/mineru_markdown/evaluation_papers/Enhancing_Uplink_Performance_of_NR_RedCap_in_Industrial_5G_B5G_Systems.pdf/auto/Enhancing_Uplink_Performance_of_NR_RedCap_in_Industrial_5G_B5G_Systems.pdf.md` | [PARSED] | MinerU pipeline markdown |
| `paper` | 6 | `redcap_doc/evaluation_papers/How_5G_Can_Support_Worker_Well-Being_The_RedCap_Solution.pdf` | `redcap_doc/mineru_markdown/evaluation_papers/How_5G_Can_Support_Worker_Well-Being_The_RedCap_Solution.pdf/auto/How_5G_Can_Support_Worker_Well-Being_The_RedCap_Solution.pdf.md` | [PARSED] | MinerU pipeline markdown |
| `paper` | 5 | `redcap_doc/evaluation_papers/RedCap_Performance_Analysis_and_Deployment_Strategy_Research.pdf` | `redcap_doc/mineru_markdown/evaluation_papers/RedCap_Performance_Analysis_and_Deployment_Strategy_Research.pdf/auto/RedCap_Performance_Analysis_and_Deployment_Strategy_Research.pdf.md` | [PARSED] | MinerU pipeline markdown |
| `paper` | 4 | `redcap_doc/evaluation_papers/paper_07Research_on_5G_RedCap_Standard_and_Key_Technologies.pdf` | `redcap_doc/mineru_markdown/evaluation_papers/paper_07Research_on_5G_RedCap_Standard_and_Key_Technologies.pdf/auto/paper_07Research_on_5G_RedCap_Standard_and_Key_Technologies.pdf.md` | [PARSED] | MinerU pipeline markdown |
| `paper` | 8 | `redcap_doc/evaluation_papers/paper_Empirical_Comparison_of_Power_Consumption_and_Data_Rates_for_5G_New_Radio_and_RedCap_Devices.pdf` | `redcap_doc/mineru_markdown/evaluation_papers/paper_Empirical_Comparison_of_Power_Consumption_and_Data_Rates_for_5G_New_Radio_and_RedCap_Devices.pdf/auto/paper_Empirical_Comparison_of_Power_Consumption_and_Data_Rates_for_5G_New_Radio_and_RedCap_Devices.pdf.md` | [PARSED] | MinerU pipeline markdown |
| `paper` | 6 | `redcap_doc/evaluation_papers/paper_Filling_a_Gap_Performance_Comparison_ofpaper_RedCap_and_eRedCap_for_Mid-Tier_Applications.pdf` | `redcap_doc/mineru_markdown/evaluation_papers/paper_Filling_a_Gap_Performance_Comparison_ofpaper_RedCap_and_eRedCap_for_Mid-Tier_Applications.pdf/auto/paper_Filling_a_Gap_Performance_Comparison_ofpaper_RedCap_and_eRedCap_for_Mid-Tier_Applications.pdf.md` | [PARSED] | MinerU pipeline markdown |
| `paper` | 12 | `redcap_doc/evaluation_papers/paper_Performance Analysis and Comparison of.pdf` | `redcap_doc/mineru_markdown/evaluation_papers/paper_Performance Analysis and Comparison of.pdf/auto/paper_Performance Analysis and Comparison of.pdf.md` | [PARSED] | MinerU pipeline markdown |
| `paper` | 10 | `redcap_doc/evaluation_papers/Research on RedCap UE’s performance indicators in real networkto support iot applications.pdf` | `redcap_doc/mineru_markdown/evaluation_papers/Research_on_RedCap_UEs_performance_indicators_in_real_network_to_support_iot_applications.pdf/Research on RedCap UE’s performance indicators in real networkto support iot applications.pdf/auto/Research on RedCap UE’s performance indicators in real networkto support iot applications.pdf.md` | [PARSED] | MinerU unique output directory; first auto-cache attempt matched an older PAPER-02 cache, so use this explicit route |
| `spec` | 5774 | `redcap_doc/specs/redcap_3gpp/DRX/TS_38_133_RRC_Conetion_DRX要求_RRM限制_流程定義(DRX).pdf` | - | [PENDING_LARGE_PDF] | 5774 pages exceeds threshold 150 |
| `spec` | 316 | `redcap_doc/specs/redcap_3gpp/DRX/TS_38_213_PDCCH_喚醒(DRX).pdf` | - | [PENDING_LARGE_PDF] | 316 pages exceeds threshold 150 |
| `spec` | 313 | `redcap_doc/specs/redcap_3gpp/DRX/TS_38_300_架構整體描述(DRX).pdf` | - | [PENDING_LARGE_PDF] | 313 pages exceeds threshold 150 |
| `spec` | 334 | `redcap_doc/specs/redcap_3gpp/DRX/TS_38_321_計時器_流程定義(DRX).pdf` | - | [PENDING_LARGE_PDF] | 334 pages exceeds threshold 150 |
| `spec` | 1668 | `redcap_doc/specs/redcap_3gpp/DRX/TS_38_331_RRC_長短DRX Cycle設定(DRX).pdf` | - | [PENDING_LARGE_PDF] | 1668 pages exceeds threshold 150 |
| `spec` | 412 | `redcap_doc/specs/redcap_3gpp/PSM/TS 23.401_MME_PSM.pdf` | - | [PENDING_LARGE_PDF] | 412 pages exceeds threshold 150 |
| `spec` | 722 | `redcap_doc/specs/redcap_3gpp/PSM/TS_23_501_5GS 中 PSM 的系統架構支援.pdf` | - | [PENDING_LARGE_PDF] | 722 pages exceeds threshold 150 |
| `spec` | 981 | `redcap_doc/specs/redcap_3gpp/PSM/TS_24_501_PSM_程序_計時器設定機制.pdf` | - | [PENDING_LARGE_PDF] | 981 pages exceeds threshold 150 |
| `spec` | 58 | `redcap_doc/specs/redcap_3gpp/PSM/TS_38_304_NR_IDle_PSM_situation.pdf` | `redcap_doc/mineru_markdown/specs/redcap_3gpp/PSM/TS_38_304_NR_IDle_PSM_situation.pdf/auto/TS_38_304_NR_IDle_PSM_situation.pdf.md` | [CACHED] | existing Markdown cache |
| `spec` | 5774 | `redcap_doc/specs/redcap_3gpp/RRM/TS_38_133_RRM_量測要求.pdf` | - | [PENDING_LARGE_PDF] | 5774 pages exceeds threshold 150 |
| `spec` | 1990 | `redcap_doc/specs/redcap_3gpp/Redcap/TS_138_521_1_RedCap RF 測試.pdf` | - | [PENDING_LARGE_PDF] | 1990 pages exceeds threshold 150 |
| `spec` | 718 | `redcap_doc/specs/redcap_3gpp/Redcap/TS_23_501_5gs_對redcap的系統架構支援.pdf` | - | [PENDING_LARGE_PDF] | 718 pages exceeds threshold 150 |
| `spec` | 698 | `redcap_doc/specs/redcap_3gpp/Redcap/TS_38_101_1_RedCap_FR1_RF_Requsetion.pdf` | - | [PENDING_LARGE_PDF] | 698 pages exceeds threshold 150 |
| `spec` | 253 | `redcap_doc/specs/redcap_3gpp/Redcap/TS_38_101_2_RedCap_FR2_RF_Requsetion.pdf` | - | [PENDING_LARGE_PDF] | 253 pages exceeds threshold 150 |
| `spec` | 326 | `redcap_doc/specs/redcap_3gpp/Redcap/TS_38_104_基地台對redcpap的rf支援要求.pdf` | - | [PENDING_LARGE_PDF] | 326 pages exceeds threshold 150 |
| `spec` | 171 | `redcap_doc/specs/redcap_3gpp/Redcap/TS_38_211_Redcap_NCD_SSN.pdf` | - | [PENDING_LARGE_PDF] | 171 pages exceeds threshold 150 |
| `spec` | 294 | `redcap_doc/specs/redcap_3gpp/Redcap/TS_38_212_RedcapUE_DCI_UCI.pdf` | - | [PENDING_LARGE_PDF] | 294 pages exceeds threshold 150 |
| `spec` | 236 | `redcap_doc/specs/redcap_3gpp/Redcap/TS_38_214_RedCap的PDSCH_PUSCH資源分配.pdf` | - | [PENDING_LARGE_PDF] | 236 pages exceeds threshold 150 |
| `spec` | 267 | `redcap_doc/specs/redcap_3gpp/Redcap/TS_38_300_Redcap與eRedcao整體架構_識別機制.pdf` | - | [PENDING_LARGE_PDF] | 267 pages exceeds threshold 150 |
| `spec` | 6002 | `redcap_doc/specs/redcap_3gpp/Redcap/TS_38_523_Rel-17 起含 RedCap 協定測試.pdf` | - | [PENDING_LARGE_PDF] | 6002 pages exceeds threshold 150 |
| `spec` | 6143 | `redcap_doc/specs/redcap_3gpp/Redcap/TS_38_533_RedCap RRM 一致性測試.pdf` | - | [PENDING_LARGE_PDF] | 6143 pages exceeds threshold 150 |
| `spec` | 294 | `redcap_doc/specs/redcap_3gpp/WUS/TS_38_212_DCI_2-6_Payload.pdf` | - | [PENDING_LARGE_PDF] | 294 pages exceeds threshold 150 |
| `spec` | 316 | `redcap_doc/specs/redcap_3gpp/WUS/TS_38_213_WUS_PS_RNTI(DRX).pdf` | - | [PENDING_LARGE_PDF] | 316 pages exceeds threshold 150 |
| `spec` | 334 | `redcap_doc/specs/redcap_3gpp/WUS/TS_38_321_UE收到WUS_流程定義(DRX).pdf` | - | [PENDING_LARGE_PDF] | 334 pages exceeds threshold 150 |
| `spec` | 140 | `redcap_doc/specs/redcap_3gpp/eDRX/TS_23_682_eDRX架構_PTW_eDRX迴圈.pdf` | `redcap_doc/mineru_markdown/specs/redcap_3gpp/eDRX/TS_23_682_eDRX架構_PTW_eDRX迴圈.pdf/auto/TS_23_682_eDRX架構_PTW_eDRX迴圈.pdf.md` | [CACHED] | existing Markdown cache |
| `spec` | 834 | `redcap_doc/specs/redcap_3gpp/eDRX/TS_24_008_跟NAS協商參數.pdf` | - | [PENDING_LARGE_PDF] | 834 pages exceeds threshold 150 |
| `spec` | 610 | `redcap_doc/specs/redcap_3gpp/eDRX/TS_24_301_TAU_Attach_相關參數.pdf` | - | [PENDING_LARGE_PDF] | 610 pages exceeds threshold 150 |
| `spec` | 981 | `redcap_doc/specs/redcap_3gpp/eDRX/TS_24_501_5G 系統下的 eDRX 參數協商.pdf` | - | [PENDING_LARGE_PDF] | 981 pages exceeds threshold 150 |
| `spec` | 72 | `redcap_doc/specs/redcap_3gpp/eDRX/TS_36_304_Paging_windows_計算(edrx).pdf` | `redcap_doc/mineru_markdown/specs/redcap_3gpp/eDRX/TS_36_304_Paging_windows_計算(edrx).pdf/auto/TS_36_304_Paging_windows_計算(edrx).pdf.md` | [PARSED] | MinerU pipeline markdown |
| `spec` | 58 | `redcap_doc/specs/redcap_3gpp/eDRX/TS_38_304_NR_Idle_inactiavt_DRX_edrx_paging設定.pdf` | `redcap_doc/mineru_markdown/specs/redcap_3gpp/eDRX/TS_38_304_NR_Idle_inactiavt_DRX_edrx_paging設定.pdf/auto/TS_38_304_NR_Idle_inactiavt_DRX_edrx_paging設定.pdf.md` | [PARSED] | MinerU pipeline markdown |
