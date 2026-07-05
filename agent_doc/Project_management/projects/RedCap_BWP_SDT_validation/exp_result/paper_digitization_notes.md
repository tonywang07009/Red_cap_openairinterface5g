# Paper Digitization Notes

## Rendered Figure Map

| Paper | Page image | Figures | Current use |
|---|---|---|---|
| `paper1_BWP_switching.pdf` | `paper_figures/paper1_BWP_switching/page-3.png` | Fig. 2, Table II, Table III | BWP switch delay and inactivity timer context |
| `paper1_BWP_switching.pdf` | `paper_figures/paper1_BWP_switching/page-4.png` | Fig. 3, Fig. 4, Table IV | high-load throughput and high-load Default BWP ratio |
| `paper1_BWP_switching.pdf` | `paper_figures/paper1_BWP_switching/page-5.png` | Fig. 5, Fig. 6, Fig. 7 | low-load Default BWP ratio, power saving, PDU scheduling delay |
| `paper2_SDT_small_data.pdf` | `paper_figures/paper2_SDT_small_data/page-5.png` | Fig. 3, Fig. 4 | SDT success probability curves |

## Confirmed Text Anchors

- [BWP switch delay]: for 15 kHz SCS, paper Table III gives [Type 1 UE] = 1 slot and [Type 2 UE] = 3 slots; with 1 ms slot length this maps to 1 ms and 3 ms.
- [BWP scenario matrix]: paper Table IV uses high load [320 KB PDU, 20 PDU/s, about 51.2 Mbps] and low load [10 KB PDU, 20 PDU/s, about 1.6 Mbps], with `bwp-InactivityTimer` = 8 ms / 80 ms and switch delay = 1 ms / 3 ms.
- [High-load Default BWP ratio]: paper text says about 80% of UEs do not stay in Default BWP and the remaining 20% stay in Default BWP for less than 2% of call time.
- [Low-load Default BWP ratio]: paper text states the 80th percentile shows about 4x more time/adaptations in Default BWP for shorter inactivity timer cases.
- [Power saving]: paper text states UEs with shorter BWP inactivity timers show up to about 25% power savings under the assumed model.
- [SDT deployment constants]: paper text states 0.1 km2 cell area, `mu_new = 0.1`, `rho = -90 dBm`, `sigma_n^2 = -100.4 dBm`, `gamma_th = -10 dB`, `alpha = 4`, `N_ZC = 839`, `lambda_th = -51.5 dBm`, `K = 1`, and `B = 0.1`.

## Reproducible Calibration

- [Calibration script]: `../scripts/calibrate_paper_digitization.py`
- [Calibration output]: `paper_digitization_calibration.csv`
- [Method]: selected anchors use fixed [plot box], [pixel point], and [axis range] on rendered PNG pages.
- [Text anchors]: values that come directly from paper text are marked `text_anchor`.
- [Visual anchors]: values computed from pixel calibration are marked `calibrated_visual_digitized`.

## Values Not Yet Claimed

- [BWP Fig. 3 throughput CDF]: left as `[TBD]` until a full CDF calibration is done.
- [BWP entered anchors]: Fig. 4 high-load Default BWP ratio, Fig. 5 low-load Default BWP ratio, Fig. 6 power saving, and Fig. 7 median scheduling delay have traceable anchors in `paper_curve_digitization_template.csv`.
- [SDT entered anchors]: Fig. 3 slot-10 and Fig. 4 `lambda_Dp = 5` basic-receiver estimates have traceable anchors in `paper_curve_digitization_template.csv`.
- [Rule]: values marked `calibrated_visual_digitized` are coarse visual anchors for plotting and comparison scaffolding; do not treat them as publication-grade digitization.
