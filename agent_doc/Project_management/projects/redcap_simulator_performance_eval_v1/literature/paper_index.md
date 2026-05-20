# RedCap Performance Paper Index

## Source Path
- Formal path: `evaluation_paper/`
- Deprecated/unused user-mentioned alias: `paper_refer/`
- Empty observed path: `paper_test/`

## Inventory
| ID | File | Initial Role | Extraction Status |
|---|---|---|---|
| PAPER-01 | `evaluation_paper/5G-A_RedCap_Technology_and_Applications.pdf` | technology/application background | [Extracted in `p1_metric_baseline.md`] |
| PAPER-02 | `evaluation_paper/5G_Reduced_Capability_Devices_Analysis_of_Blocking_Probability_for_Control_Channels.pdf` | control-channel blocking probability | [Extracted in `p1_metric_baseline.md`] |
| PAPER-03 | `evaluation_paper/Coverage_Evaluation_for_5G_Reduced_Capability_New_Radio_NR-RedCap.pdf` | coverage evaluation | [Extracted in `p1_metric_baseline.md`] |
| PAPER-04 | `evaluation_paper/Enhancing_Uplink_Performance_of_NR_RedCap_in_Industrial_5G_B5G_Systems.pdf` | uplink performance | [Extracted in `p1_metric_baseline.md`] |
| PAPER-05 | `evaluation_paper/How_5G_Can_Support_Worker_Well-Being_The_RedCap_Solution.pdf` | application scenario | [Extracted in `p1_metric_baseline.md`] |
| PAPER-06 | `evaluation_paper/RedCap_Performance_Analysis_and_Deployment_Strategy_Research.pdf` | performance/deployment strategy | [Extracted in `p1_metric_baseline.md`] |
| PAPER-07 | `evaluation_paper/Research_on_5G_RedCap_Standard_and_Key_Technologies.pdf` | standard/key technology background | [Extracted in `p1_metric_baseline.md`] |

## Extraction Template
| Paper ID | Page/Figure/Table | Metric | Scenario | X-axis | Y-axis | Simulator Equivalent | Confidence |
|---|---|---|---|---|---|---|---|
| See `p1_metric_baseline.md` | See `p1_metric_baseline.md` | See `p1_metric_baseline.md` | See `p1_metric_baseline.md` | See `p1_metric_baseline.md` | See `p1_metric_baseline.md` | See `p1_metric_baseline.md` | See `p1_metric_baseline.md` |

## Reading Rule
- Extract only the pages needed for the active metric.
- Prefer figures/tables with explicit axes and units.
- If a paper result depends on channel models unavailable in RFsim, mark [Not Directly Comparable].
