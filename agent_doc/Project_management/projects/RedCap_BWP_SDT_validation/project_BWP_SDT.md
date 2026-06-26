# RedCap_BWP_SDT_validation

## Project Metadata

- [Project Name]: RedCap_BWP_SDT_validation
- [Project Path]: `agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/project_BWP_SDT.md`
- [Paper Source]: `redcap_doc/evaluation_papers/redcap_vaildation_BWP_SDT/`
- [Runtime Source of Truth]: `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/`
- [OpenSpec Change]: `openspec/changes/redcap-bwp-sdt-validation/`
- [SymDex Paper Repo]: `redcap_bwp_sdt_papers`
- [Created Date]: 2026-06-25

## Experiment Goals

- [BWP]: Reproduce comparable trends for [application-layer throughput], [Default BWP ratio], [estimated power saving], and [PDU scheduling delay] from the BWP switching paper.
- [SDT]: Reproduce comparable trends for [overall packet transmission success probability] across [4-step RA], [2-step RA], [4-step SDT], and [2-step SDT].
- [Local OAI Goal]: Map paper scenarios to available RedCap RFsim/FlexRIC hooks before changing OAI C code.

## 3GPP Mapping

| Area | Clause | Local status |
|---|---|---|
| [BWP conformance] | TS 38.523-1 clause 7.1.1.12 | Converted in `spec_refs/TS_38_523_Rel18_clauses_7_1_1_12_7_1_1_13_subset.md`; interpretation `[Needs Verification]` |
| [BWP MAC behavior] | TS 38.321 clause 5.15.1 | Converted in `spec_refs/TS_38_321_MAC_timers_DRX.md`; local BWP operation clause found |
| [BWP requested clause risk] | TS 38.321 clause 5.9 | Local TS 38.321 V18.2.0 maps this to [Activation/Deactivation of SCells], not primary BWP operation; `[Needs Verification]` |
| [SDT conformance] | TS 38.523-1 clause 7.1.1.13 | Converted in `spec_refs/TS_38_523_Rel18_clauses_7_1_1_12_7_1_1_13_subset.md`; interpretation `[Needs Verification]` |
| [SDT general behavior] | TS 38.300 clause 18 | Converted in `spec_refs/TS_38_300_NR_overall_DRX.md` and `spec_refs/TS_38_300_RedCap_eRedCap_architecture.md`; local SDT general behavior found |
| [RRC_INACTIVE / SDT signaling] | TS 38.331 | [Needs Verification]; local RFsim markers already exist for prior SDT gates |

## Extracted Experiment Settings

| Paper | target_technology | scenario | parameters |
|---|---|---|---|
| `paper1_BWP_switching.md` | [BWP switching with inactivity timer and switch delay] | 7 tri-sector macro sites, 21 macro cells, 3.5 GHz, 20 MHz carrier, 15 kHz SCS, TDD, 105 UE calls | UE category 6-2; 1 Default BWP + 1 Dedicated BWP; FTP3 DL only; Poisson PDU generation; 20 PDUs/s; high load 320 KB PDU (~51.2 Mbps/UE); low load 10 KB PDU (~1.6 Mbps/UE); `bwp-InactivityTimer` = 8 ms / 80 ms; BWP switch delay = 1 ms / 3 ms; 40 runs x 20 s |
| `paper2_SDT_small_data.md` | [4/2-step SDT random access] | Single BS, multiple static IoT devices, RRC Inactive small-data arrival model | Homogeneous PPP device distribution; 0.1 km2 circular cell; Poisson packet arrivals; `mu_new = 0.1 packets/time-slot`; `rho = -90 dBm`; `sigma_n^2 = -100.4 dBm`; `gamma_th = -10 dB`; path-loss exponent `alpha = 4`; `N_ZC = 839`; `lambda_th = -51.5 dBm`; `K = 1`; `B = 0.1`; plotted examples include `lambda_Dp = 5 devices/preamble` |

## Local OAI Mapping

| Paper concept | Local mapping | Evidence / next check |
|---|---|---|
| [BWP switch delay] | gNB scheduler BWP switch path and active BWP restoration | Use `symdex` for `nr_mac_trigger_reconfiguration`, `configure_UE_BWP`, and related BWP switch paths |
| [Default vs Dedicated BWP] | Existing gNB config fields for initial BWP and OAI BWP structures | Start from `ci-scripts/conf_files/*106prb*` and RFsim RedCap configs |
| [RA-SDT] | Prior [RRC_INACTIVE + SDT] RFsim gates | Runtime markers: `RRC_INACTIVE entered`, `RRCResumeRequest received`, `RRCResumeComplete` |
| [CG-SDT] | Existing configured grant SDT validation hooks | Runtime markers: `configuredGrantConfig parsed`, `cg-SDT PUSCH tx`, `cg-SDT PUSCH rx candidate` |
| [Hook inventory] | Re-runnable source scan | `scripts/audit_oai_hooks.py` writes `exp_result/oai_hook_inventory.md` and `.csv` |

## Expected Outputs

| Output | Path | Format |
|---|---|---|
| Paper Markdown | `redcap_doc/evaluation_papers/redcap_vaildation_BWP_SDT/*.md` | Markdown |
| Paper metadata | `redcap_doc/evaluation_papers/redcap_vaildation_BWP_SDT/redcap_vaildation_BWP_SDT_index.json` | JSON |
| Experiment steps | `exp_step/exp_step_BWP.md`, `exp_step/exp_step_SDT.md` | Markdown |
| Experiment configs | `configs/BWP_local_matrix.yaml`, `configs/SDT_local_matrix.yaml` | YAML |
| Experiment wrappers | `scripts/run_bwp_validation.sh`, `scripts/run_sdt_validation.sh` | Bash |
| Metric extractors | `scripts/extract_bwp_metrics.py`, `scripts/extract_sdt_metrics.py` | Python |
| Paper digitization template | `exp_result/paper_curve_digitization_template.csv` | CSV |
| Rendered paper pages | `scripts/render_paper_figures.sh`, `exp_result/paper_figures/` | Bash / PNG |
| Paper digitization notes | `exp_result/paper_digitization_notes.md` | Markdown |
| Paper calibration evidence | `scripts/calibrate_paper_digitization.py`, `exp_result/paper_digitization_calibration.csv` | Python / CSV |
| Paper value merger | `scripts/apply_digitized_paper_values.py` | Python |
| OAI hook inventory | `scripts/audit_oai_hooks.py`, `exp_result/oai_hook_inventory.md`, `exp_result/oai_hook_inventory.csv` | Python / Markdown / CSV |
| Raw comparison data | `exp_result/BWP_results.csv`, `exp_result/SDT_results.csv` | CSV |
| Difference report | `exp_result/exp_result_summary.md` | Markdown |
| Spec-cited conclusions | `exp_result/spec_cited_conclusions.md` | Markdown |
| Runtime evidence | `exp_result/BWP_runtime_evidence_20260625_213152.md`, `exp_result/SDT_runtime_blocker_20260625.md` | Markdown |
| Figures | `exp_pictture/BWP_paper_vs_local.png`, `exp_pictture/SDT_paper_vs_local.png` | PNG |

## Reproduction Status

| Gate | Status | Notes |
|---|---|---|
| [Gate 0] PDF conversion and SymDex indexing | [x] | `paper1_BWP_switching.md`, `paper2_SDT_small_data.md`, and `redcap_bwp_sdt_papers` index created |
| [Gate 1] Project scaffold | [x] | Project plan, step docs, result schema, and plotting script created |
| [Gate 2] Local RFsim metric execution | [~] | BWP UE2 minimal run completed at `test_log/redcap_bwp_sdt_validation/20260625_213152_bwp/`; SDT Docker run pending because the 2026-06-25 approval attempt was rejected with workspace credits unavailable |
| [Gate 3] Paper curve digitization / exact point extraction | [~] | 12 paper-side anchors are marked `[text_anchor]` or `[calibrated_visual_digitized]`; Fig. 3 BWP throughput and publication-grade full-curve extraction remain `[TBD]` |
| [Gate 4] 3GPP clause confirmation and OAI hook audit | [~] | `exp_result/spec_cited_conclusions.md` and `exp_result/oai_hook_inventory.md` added; TS 38.321 clause 5.9 vs 5.15.1 mismatch remains `[Needs Verification]` |

## Paper Sync Automation

- [One-shot sync]:
  - `rtk python redcap_doc/evaluation_papers/redcap_vaildation_BWP_SDT/sync_redcap_bwp_sdt_papers.py`
- [Watch mode]:
  - `rtk python redcap_doc/evaluation_papers/redcap_vaildation_BWP_SDT/sync_redcap_bwp_sdt_papers.py --watch`
- [Behavior]:
  - polls `redcap_doc/evaluation_papers/redcap_vaildation_BWP_SDT/` for PDF name/mtime/size changes
  - converts missing or stale PDFs with `markitdown`
  - refreshes `redcap_vaildation_BWP_SDT_index.json`
  - refreshes `redcap_bwp_sdt_papers` SymDex index unless `--skip-symdex` is used

## Paper Curve Digitization Workflow

- [Template]: `agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/exp_result/paper_curve_digitization_template.csv`
- [Rendered paper pages]:
  - `rtk bash agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/scripts/render_paper_figures.sh`
  - output root: `agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/exp_result/paper_figures/`
- [Apply script]:
  - `rtk python agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/scripts/apply_digitized_paper_values.py`
- [Calibration script]:
  - `rtk python agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/scripts/calibrate_paper_digitization.py`
  - output: `agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/exp_result/paper_digitization_calibration.csv`
- [Behavior]:
  - rows with `paper_value = TBD` are skipped by default
  - once a digitized numeric value is entered, the script updates `BWP_results.csv` or `SDT_results.csv`
  - `diff_absolute` and `diff_percent` are computed only when both paper and local values are numeric
- [Current status]:
  - 12 paper-side anchors have been applied to `BWP_results.csv` / `SDT_results.csv`
  - local comparison values remain `[TBD]` where no matching RFsim metric has been generated
  - `calibrated_visual_digitized` values are coarse anchors, not publication-grade curve digitization
- [Source figures]:
  - BWP paper: Fig.3 application-layer throughput, Fig.4/Fig.5 Default BWP ratio, Fig.6 power saving, Fig.7 PDU scheduling delay `[Needs Verification]`
  - SDT paper: Fig.3 time-slot success probability, Fig.4 device-intensity success probability
