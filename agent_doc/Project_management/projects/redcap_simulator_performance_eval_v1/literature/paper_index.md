# RedCap Performance Paper Index

## Source Path
- Formal path: `redcap_doc/evaluation_papers/`
- MinerU Markdown cache manifest: `redcap_doc/mineru_markdown/scan_manifest.md`
- Deprecated/unused user-mentioned alias: `paper_refer/`
- Removed empty legacy path after P6 cleanup: `paper_test/`

## Inventory
| ID | File | Initial Role | Extraction Status |
|---|---|---|---|
| PAPER-01 | `redcap_doc/evaluation_papers/5G-A_RedCap_Technology_and_Applications.pdf` | technology/application background | [Extracted in `p1_metric_baseline.md`] |
| PAPER-02 | `redcap_doc/evaluation_papers/5G_Reduced_Capability_Devices_Analysis_of_Blocking_Probability_for_Control_Channels.pdf` | control-channel blocking probability | [Extracted in `p1_metric_baseline.md`] |
| PAPER-03 | `redcap_doc/evaluation_papers/Coverage_Evaluation_for_5G_Reduced_Capability_New_Radio_NR-RedCap.pdf` | coverage evaluation | [Extracted in `p1_metric_baseline.md`] |
| PAPER-04 | `redcap_doc/evaluation_papers/Enhancing_Uplink_Performance_of_NR_RedCap_in_Industrial_5G_B5G_Systems.pdf` | uplink performance | [Extracted in `p1_metric_baseline.md`] |
| PAPER-05 | `redcap_doc/evaluation_papers/How_5G_Can_Support_Worker_Well-Being_The_RedCap_Solution.pdf` | application scenario | [Extracted in `p1_metric_baseline.md`] |
| PAPER-06 | `redcap_doc/evaluation_papers/RedCap_Performance_Analysis_and_Deployment_Strategy_Research.pdf` | performance/deployment strategy | [Extracted in `p1_metric_baseline.md`] |
| PAPER-07 | `redcap_doc/evaluation_papers/paper_07Research_on_5G_RedCap_Standard_and_Key_Technologies.pdf` | standard/key technology background | [Extracted in `p1_metric_baseline.md`] |
| PAPER-08 | `redcap_doc/evaluation_papers/paper_Empirical_Comparison_of_Power_Consumption_and_Data_Rates_for_5G_New_Radio_and_RedCap_Devices.pdf` | power consumption and data rate comparison | [MinerU cache ready; Equation (1) calculator and extended matrix ready] |
| PAPER-09 | `redcap_doc/evaluation_papers/paper_Filling_a_Gap_Performance_Comparison_ofpaper_RedCap_and_eRedCap_for_Mid-Tier_Applications.pdf` | RedCap/eRedCap mid-tier comparison | [MinerU cache ready; metric extraction pending] |
| PAPER-10 | `redcap_doc/evaluation_papers/paper_Performance Analysis and Comparison of.pdf` | performance comparison reference | [MinerU cache ready; platform improvement checklist and extended matrix ready] |
| PAPER-11 | `redcap_doc/evaluation_papers/Research on RedCap UE’s performance indicators in real networkto support iot applications.pdf` | real-network RedCap UE performance indicators for IoT applications | [Extracted in `paper11_research_real_network_redcap_performance.md`; RFsim proxy reproduction flow ready] |

## Extraction Template
| Paper ID | Page/Figure/Table | Metric | Scenario | X-axis | Y-axis | Simulator Equivalent | Confidence |
|---|---|---|---|---|---|---|---|
| See `p1_metric_baseline.md` | See `p1_metric_baseline.md` | See `p1_metric_baseline.md` | See `p1_metric_baseline.md` | See `p1_metric_baseline.md` | See `p1_metric_baseline.md` | See `p1_metric_baseline.md` | See `p1_metric_baseline.md` |

## Reading Rule
- Extract only the pages needed for the active metric.
- Search `redcap_doc/mineru_markdown/scan_manifest.md` before opening a PDF.
- Prefer figures/tables with explicit axes and units.
- If a paper result depends on channel models unavailable in RFsim, mark [Not Directly Comparable].
