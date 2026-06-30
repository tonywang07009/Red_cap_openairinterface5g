# RedCap_BWP_SDT_validation

## Project Metadata

- [Project Name]: RedCap_BWP_SDT_validation
- [Project Path]: `agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/project_BWP_SDT.md`
- [Paper Source]: `redcap_doc/evaluation_papers/redcap_vaildation_BWP_SDT/`
- [Runtime Source of Truth]: `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/`
- [SDT Runtime Baseline]: `agent_doc/Project_management/projects/redcap_rrc_inactive_sdt_oran_control_v1/` [Case A Gate 3]
- [Operator Interface]: `redcap_interface/mmtc.menu.bash`
- [OpenSpec Change]: `openspec/changes/redcap-bwp-sdt-validation/`
- [SymDex Paper Repo]: `redcap_bwp_sdt_papers`
- [Created Date]: 2026-06-25

## Experiment Goals

- [BWP]: Reproduce comparable trends for [application-layer throughput], [Default BWP ratio], [estimated power saving], and [PDU scheduling delay] from the BWP switching paper.
- [SDT]: Reproduce comparable trends for [overall packet transmission success probability] across [4-step RA], [2-step RA], [4-step SDT], and [2-step SDT].
- [Local OAI Goal]: Keep this project as a [paper reproduction layer]; reuse validated RedCap RFsim/FlexRIC runtime paths before changing OAI C code.

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
| [BWP switch delay] | gNB scheduler BWP switch path and active BWP restoration | Added `[RedCap BWP][gNB reconfiguration]` and `[RedCap BWP][gNB interrupt]` runtime markers |
| [Default vs Dedicated BWP] | Existing gNB config fields for initial BWP and OAI BWP structures | Start from `ci-scripts/conf_files/*106prb*` and RFsim RedCap configs |
| [UE RA BWP operation] | UE RA path in TS 38.321 clause 5.15 BWP operation | Added `[RedCap BWP][UE RA]` marker with old/new active BWP IDs |
| [RA-SDT] | Prior [RRC_INACTIVE + SDT] RFsim gates from `redcap_rrc_inactive_sdt_oran_control_v1` | Runtime markers: `RRC_INACTIVE entered`, `RRCResumeRequest received`, `RRCResumeComplete` |
| [CG-SDT] | Existing [Case A Gate 3] configured grant SDT validation hooks | Runtime markers: `configuredGrantConfig parsed`, `cg-SDT PUSCH tx`, `cg-SDT PUSCH rx candidate` |
| [Hook inventory] | Re-runnable source scan | `scripts/audit_oai_hooks.py` writes `exp_result/oai_hook_inventory.md` and `.csv` |

## Runtime Layering

- [Paper reproduction layer]: this project owns paper extraction, scenario matrices, CSV merge, result summaries, plots, and paper-vs-local interpretation.
- [Validated SDT runtime layer]: `redcap_rrc_inactive_sdt_oran_control_v1` owns the [RRC_INACTIVE + SDT] protocol baseline and its Gate 3 runtime semantics.
- [SDT wrapper]: `scripts/run_sdt_validation.sh` defaults to `redcap_interface/mmtc.menu.bash gate3` for the validated baseline; matrix runs set `MMTC_SDT_MENU_SUBCOMMAND=smoke` so per-scenario RA/SDT gate flags are preserved before copying gNB/UE logs for paper-facing metric extraction.
- [BWP wrapper]: `scripts/run_bwp_validation.sh` remains paper-specific because the existing SDT gate project does not own BWP telnet trigger or BWP residency metrics.
- [Shared helper]: `scripts/redcap_runtime_common.sh` centralizes image defaults, RF defaults, compose helpers, and CSV extraction/merge helpers used by the BWP/SDT wrappers.

## Expected Outputs

| Output | Path | Format |
|---|---|---|
| Paper Markdown | `redcap_doc/evaluation_papers/redcap_vaildation_BWP_SDT/*.md` | Markdown |
| Paper metadata | `redcap_doc/evaluation_papers/redcap_vaildation_BWP_SDT/redcap_vaildation_BWP_SDT_index.json` | JSON |
| Experiment steps | `exp_step/exp_step_BWP.md`, `exp_step/exp_step_SDT.md` | Markdown |
| Experiment configs | `configs/BWP_local_matrix.yaml`, `configs/SDT_local_matrix.yaml` | YAML |
| Experiment wrappers | `scripts/run_bwp_validation.sh`, `scripts/run_sdt_validation.sh`, `scripts/run_bwp_matrix.sh`, `scripts/run_sdt_matrix.sh`, `scripts/redcap_runtime_common.sh` | Bash |
| Metric extractors | `scripts/extract_bwp_metrics.py`, `scripts/extract_sdt_metrics.py`, `scripts/aggregate_sdt_success.py` | Python |
| Extractor smoke tests | `scripts/test_extract_bwp_metrics.py`, `scripts/test_extract_sdt_metrics.py` | Python |
| Paper digitization template | `exp_result/paper_curve_digitization_template.csv` | CSV |
| Rendered paper pages | `scripts/render_paper_figures.sh`, `exp_result/paper_figures/` | Bash / PNG |
| Paper digitization notes | `exp_result/paper_digitization_notes.md` | Markdown |
| Paper calibration evidence | `scripts/calibrate_paper_digitization.py`, `exp_result/paper_digitization_calibration.csv` | Python / CSV |
| Paper value merger | `scripts/apply_digitized_paper_values.py` | Python |
| OAI hook inventory | `scripts/audit_oai_hooks.py`, `exp_result/oai_hook_inventory.md`, `exp_result/oai_hook_inventory.csv` | Python / Markdown / CSV |
| Raw comparison data | `exp_result/BWP_results.csv`, `exp_result/SDT_results.csv` | CSV |
| Repeated-run aggregate data | `exp_result/SDT_repeated_run_aggregate.csv` | CSV |
| Difference report | `exp_result/exp_result_summary.md` | Markdown |
| Spec-cited conclusions | `exp_result/spec_cited_conclusions.md` | Markdown |
| Runtime evidence | `exp_result/BWP_runtime_evidence_20260625_213152.md`, `exp_result/BWP_runtime_evidence_20260626_231100.md`, `exp_result/BWP_runtime_evidence_20260628_151500.md`, `exp_result/SDT_runtime_evidence_20260626_230300.md` | Markdown |
| Figures | `exp_pictture/BWP_paper_vs_local.png`, `exp_pictture/SDT_paper_vs_local.png` | PNG |

## Reproduction Status

| Gate | Status | Notes |
|---|---|---|
| [Gate 0] PDF conversion and SymDex indexing | [x] | `paper1_BWP_switching.md`, `paper2_SDT_small_data.md`, and `redcap_bwp_sdt_papers` index created |
| [Gate 1] Project scaffold | [x] | Project plan, step docs, result schema, and plotting script created |
| [Gate 2] Local RFsim metric execution | [x] | Historical SDT local-image runtime completed at `test_log/redcap_bwp_sdt_validation/20260626_230300_sdt_local_sdt/`; standalone SDT runs default to `redcap_interface/mmtc.menu.bash gate3`, while matrix runs delegate through `smoke`; BWP local-image marker runtime completed at `test_log/redcap_bwp_sdt_validation/20260626_231100_bwp_local_ci_bwp/` |
| [Gate 3] Paper curve digitization / exact point extraction | [~] | 12 paper-side anchors are marked `[text_anchor]` or `[calibrated_visual_digitized]`; Fig. 3 BWP throughput and publication-grade full-curve extraction remain `[TBD]` |
| [Gate 4] 3GPP clause confirmation and OAI hook audit | [~] | `exp_result/spec_cited_conclusions.md` and `exp_result/oai_hook_inventory.md` added; BWP instrumentation markers are audited; SDT 2-step/slot/lambda dimensions are now marked `[wrapper_label]`; TS 38.321 clause 5.9 vs 5.15.1 mismatch remains `[Needs Verification]` |
| [Gate 5] BWP timer/residency/sweep | [~] | `20260630_100615_bwp_matrix_apply_marker` ran 8/8 post-fix matrix rows with `runner_failures = 0`; BWP 1 -> 0 crash is fixed for tested RFsim triggers, but traffic/timer/switch-delay dimensions remain `[wrapper_label]` |
| [Gate 6] SDT success-probability matrix | [~] | `20260627_200958_sdt_matrix` completed 12 scenarios x 3 RFsim samples and `SDT_repeated_run_aggregate.csv` has `run_count = 3` for every scenario; local values are marker-classified; 2-step/slot/lambda dimensions are `[wrapper_label]` |

## Next Progress

- [Current confirmed status]: this project is past scaffold and first local RFsim marker runs, but it is not a full paper-curve reproduction.
- [CSV inventory]:
  - `BWP_results.csv`: includes 8 post-fix matrix scenario rows from `20260630_100615_bwp_matrix_apply_marker`; [Default BWP ratio], [estimated power saving], [BWP switch apply delay], and [PDU scheduling delay] are numeric local RFsim values.
  - `SDT_results.csv`: includes marker-classified numeric local success probabilities for all 12 paper scenario rows plus `local_rfsim_ue2_minimal_sdt`; 2-step/slot/lambda semantic mapping is `[wrapper_label]`.
- [Next Gate 5]: BWP timer/residency/sweep
  - [Goal]: produce paper-comparable [Default BWP ratio], [estimated power saving], and [PDU scheduling delay] values.
  - [Blocking prerequisites]:
    - [x] instrument current `bwp-InactivityTimer` gap and marker-derived BWP residency from logs
    - [x] add active/default BWP residency extraction from timestamped `Switching to DL-BWP` events
    - [x] lock [Default BWP] and [Dedicated BWP] sizes in extracted metrics
    - [x] measure BWP switch apply delay and first post-switch scheduled SDU delay
    - [x] run the full high/low wrapper matrix with force-recreate runtime logs
    - [x] fix BWP 1 -> BWP 0 telnet-trigger crash before using the matrix as local runtime evidence
    - [ ] implement or validate real traffic/timer/switch-delay hooks before claiming publication-grade equivalence
  - [Run matrix]: low/high load x `bwp-InactivityTimer` 8/80 ms x switch delay 1/3 ms; current post-fix run is complete, but label-only traffic/timer semantics still block publication-grade equivalence.
- [Next Gate 6]: SDT paper-comparable scenario matrix
  - [Goal]: compute [packet transmission success probability] for [4-step RA], [2-step RA], [4-step SDT], and [2-step SDT].
  - [Runtime baseline]: keep standalone `scripts/run_sdt_validation.sh` delegated to `redcap_interface/mmtc.menu.bash gate3`; use `MMTC_SDT_MENU_SUBCOMMAND=smoke` only for matrix rows that need scenario-specific gate flags.
  - [Required work]:
    - [x] add scenario runner for the RA/SDT mode matrix
    - [x] add repeated-run aggregate script
    - [x] compute success probability from attempted vs successful packet transmissions when runtime rows exist
    - [x] keep threshold-fallback cases separate from failed SDT cases in extracted counters
    - [x] run the 12 paper scenarios with repeated RFsim samples
    - [x] verify that 2-step RA, slot10, and `lambda_dp_5` scenario dimensions are labels only in the current wrapper/OAI wiring
- [Next Gate 7]: final paper curve/report alignment
  - [Goal]: refresh CSVs, plots, and conclusion text after Gate 5 and Gate 6 produce comparable local values.
  - [Required work]:
    - [ ] complete BWP Fig. 3 throughput CDF extraction
    - [ ] improve paper-figure calibration if publication-grade comparison is required
    - [ ] update rows where `paper_value = TBD`
    - [~] regenerate `exp_pictture/BWP_paper_vs_local.png` and `exp_pictture/SDT_paper_vs_local.png`
    - [~] refresh `exp_result/exp_result_summary.md` and `exp_result/spec_cited_conclusions.md`

## Execution Roadmap

| Work item | AI-native phase | 3GPP mapping | Prerequisites | Output artifact |
|---|---|---|---|---|
| [Gate 5.1] BWP source inventory refresh | [Plan] / [Design] | TS 38.321 clause 5.15.1; TS 38.523-1 clause 7.1.1.12 `[Needs Verification]` | Gate 4 hook audit | updated `exp_result/oai_hook_inventory.md` |
| [Gate 5.2] BWP inactivity timer and residency instrumentation | [Build] | TS 38.321 clause 5.15.1 | Gate 5.1 | OAI C marker patch, extractor fields, smoke test |
| [Gate 5.3] BWP low/high load RFsim sweep | [Test] | TS 38.523-1 clause 7.1.1.12 `[Needs Verification]` | Gate 5.2 | updated `BWP_results.csv`, BWP runtime evidence report |
| [Gate 6.1] SDT scenario-runner design | [Plan] / [Design] | TS 38.523-1 clause 7.1.1.13.1 and 7.1.1.13.5; TS 38.300 clause 18 | Gate 2 SDT runtime marker baseline | SDT scenario manifest and wrapper dry-run manifest |
| [Gate 6.2] SDT repeated-run success aggregation | [Test] | TS 38.523-1 clause 7.1.1.13 | Gate 6.1 | updated `SDT_results.csv`, per-run raw evidence |
| [Gate 7.1] Paper digitization refinement | [Review] | Paper figure mapping; spec mapping `[Needs Verification]` | Gate 5.3 or Gate 6.2 | updated `paper_curve_digitization_template.csv` |
| [Gate 7.2] Final report and plot refresh | [Document] | consolidated BWP/SDT mapping | Gate 7.1 | refreshed `exp_result_summary.md`, `spec_cited_conclusions.md`, PNG plots |

## Acceptance Criteria

| Gate | PASS criteria | Cannot claim PASS if |
|---|---|---|
| [Gate 5] BWP paper-comparable local metrics | `BWP_results.csv` has numeric local values for [Default BWP ratio], [estimated power saving], and [PDU scheduling delay]; `bwp-InactivityTimer` and BWP residency evidence are present | only telnet-triggered BWP switch markers exist, or residency remains `[TBD]` |
| [Gate 6] SDT paper-comparable success matrix | `SDT_results.csv` has numeric local values for the 12 success-probability rows; attempted/success/fallback counts are preserved per scenario | only `RRC_INACTIVE` / `configuredGrantConfig` / `cg-SDT` markers exist without repeated-run probability aggregation, or scenario dimensions are treated as paper-equivalent before hook verification |
| [Gate 7] final paper alignment | result CSVs, plots, and conclusion text agree; paper-side values are either numeric with provenance or explicitly `[TBD]` | regenerated plots use stale CSVs, or conclusion text makes claims beyond the available evidence |

## Evidence Update Rules

- [Runtime logs]: keep raw run bundles under `test_log/redcap_bwp_sdt_validation/<run_id>_*`; do not move or delete generated logs in this project pass.
- [Stable evidence]: promote only concise reusable summaries into `exp_result/*runtime_evidence*.md`.
- [CSV source of truth]: use `BWP_results.csv` and `SDT_results.csv` as the canonical metric exchange format.
- [Plot refresh]: regenerate `exp_pictture/*.png` only after CSV changes, then record the command and output path in `exp_result_summary.md`.
- [Spec claims]: keep TS 38.523-1 clause 7.1.1.12 / 7.1.1.13 and TS 38.321 clause 5.15.1 mappings explicit; keep TS 38.321 clause 5.9 as `[Needs Verification]` unless local spec review proves otherwise.
- [Runtime ownership]: SDT protocol behavior remains owned by `redcap_rrc_inactive_sdt_oran_control_v1`; this project owns paper-facing scenario control, metric collation, and comparison reporting.

## Student Handoff Checklist

- [Before editing C code]:
  - [ ] read `exp_result/oai_hook_inventory.md`
  - [ ] identify whether the next change is [BWP timer/residency] or [SDT success aggregation]
  - [ ] record expected metric rows before running or editing anything
- [Before runtime]:
  - [ ] run the relevant wrapper with `--dry-run`
  - [ ] confirm Docker/RFsim environment is idle
  - [ ] choose a unique `RUN_ID`
- [After runtime]:
  - [ ] copy or collect gNB/UE logs into the project run bundle
  - [ ] run the relevant metric extractor
  - [ ] update the CSV and preserve per-run raw values
  - [ ] refresh the evidence report only if the run adds reusable proof
- [Before reporting PASS]:
  - [ ] verify the CSV rows that the gate claims to satisfy
  - [ ] run targeted `git diff --check`
  - [ ] confirm no stale blocker wording remains in project Markdown

## Educational Report Template

Use this template after each unit test or RFsim validation slice:

1. [Technical Background]: under 300 words; state the BWP or SDT behavior being tested.
2. [Key C Functions / Data Structures]: list only touched or observed functions, source paths, and marker names.
3. [Test Results Summary Table]: include [Test Item], [Pass-Fail Status], [Code Coverage or Scope], and [Modification Logs].
4. [3GPP Specification Mapping]: include clause number and a brief local interpretation; mark uncertain mappings as `[Needs Verification]`.
5. [Practice Exercises]: provide 1 [Basic], 1 [Applied], and 1 [Advanced] question for student review.

## BWP Runtime Instrumentation

- [gNB reconfiguration marker]: `[RedCap BWP][gNB reconfiguration]`
  - [Source]: `openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_primitives.c`
  - [Purpose]: count requested BWP switch attempts and capture the target BWP ID.
- [gNB interruption marker]: `[RedCap BWP][gNB interrupt]`
  - [Source]: `openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_primitives.c`
  - [Purpose]: capture interruption slots used as local switch-delay evidence.
- [UE RA BWP marker]: `[RedCap BWP][UE RA]`
  - [Source]: `openair2/LAYER2/NR_MAC_UE/nr_ra_procedures.c`
  - [Purpose]: capture old/new active DL/UL BWP IDs and keep the `bwp-InactivityTimer` gap explicit.
- [Extractor smoke test]:
  - `rtk python agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/scripts/test_extract_bwp_metrics.py`
- [Matrix dry-run]:
  - `rtk bash agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/scripts/run_bwp_matrix.sh --dry-run`
- [New extracted local estimates from `20260626_231100_bwp_local_ci`]:
  - `default_bwp_ratio_percent = 10.674214`
  - `power_saving_percent = 5.538507` using `default_ratio_x_prb_delta`
  - `pdu_scheduling_delay_ms = 4.249000` from reconfiguration marker to first post-switch scheduled SDU
- [Current boundary]:
  - This instrumentation is [behavior-neutral]; it exposes the current `bwp-InactivityTimer` gap and derives residency from observed BWP state changes.
  - `20260628_151500_bwp_matrix_recreate` reproduced a gNB crash on every BWP 0 telnet trigger; paper-comparable BWP delay/power curves require fixing this crash plus real high/low traffic and timer hooks.

## SDT Repeated-Run Aggregation

- [Scenario runner]:
  - `rtk bash agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/scripts/run_sdt_matrix.sh --dry-run`
- [Aggregator]:
  - `rtk python agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/scripts/aggregate_sdt_success.py`
- [Extracted counters]:
  - `packet_attempt_count`
  - `packet_success_count`
  - `threshold_fallback_count`
  - `timeout_failure_count`
  - `sdt_failure_count`
  - `packet_transmission_success_probability`
- [Current local aggregate]:
  - `local_rfsim_ue2_minimal_sdt`: `1/1` success, `threshold_fallback_count = 0`, `timeout_failure_count = 0`
  - `20260627_200958_sdt_matrix`: 12 scenarios x 3 repeats, marker-classified `3/3` success for every scenario, `threshold_fallback_count = 0`, `timeout_failure_count = 0`
- [Current boundary]:
  - The 12 canonical paper scenario rows now have numeric local marker-classified values.
  - `MMTC_RA_ACCESS_STEPS`, `slot10`, and `lambda_dp_5` are `[wrapper_label]` dimensions in the current implementation, not proven OAI runtime behavior.

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
