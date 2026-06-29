## 1. Tooling And Paper Sync

- [x] 1.1 Repair `symdex` MCP command path and verify `redcap_oai` indexing.
- [x] 1.2 Convert the two BWP/SDT PDFs to Markdown with `markitdown`.
- [x] 1.3 Index the converted paper folder with `symdex`.
- [x] 1.4 Add a repeatable paper sync script and metadata index JSON.
- [x] 1.5 Add paper sync watch mode for future PDF additions.

## 2. Project Records

- [x] 2.1 Create `RedCap_BWP_SDT_validation` project folder.
- [x] 2.2 Add `project_BWP_SDT.md` with paper settings, spec mappings, and expected outputs.
- [x] 2.3 Add BWP and SDT experiment step Markdown files.
- [x] 2.4 Add project-local BWP/SDT config matrices and dry-run-first RFsim wrapper scripts.
- [x] 2.5 Add re-runnable OAI source-hook audit for BWP/SDT reproduction readiness.
- [x] 2.6 Align SDT wrapper with the existing `redcap_rrc_inactive_sdt_oran_control_v1` Case A Gate 3 runtime baseline.

## 3. Results And Plots

- [x] 3.1 Add BWP and SDT result CSV placeholders with the required schema.
- [x] 3.2 Add `exp_result_summary.md` with comparison formula and initial conclusions.
- [x] 3.3 Add matplotlib plotting script that saves PNGs to `exp_pictture/`.
- [x] 3.4 Add BWP and SDT log metric extractors.
- [x] 3.5 Run first-pass BWP UE2 minimal RFsim and export local baseline metrics.
- [x] 3.6 Run first-pass SDT UE2 minimal RFsim and export local baseline metrics.
- [x] 3.7 Add paper curve digitization template and apply script.
- [x] 3.8 Add rendered PDF page export for manual paper curve digitization.
- [x] 3.9 Add rendered-page mapping and text-anchor notes for paper digitization.
- [x] 3.10 Apply first coarse paper-side anchors to BWP/SDT result CSVs.
- [x] 3.11 Add reproducible pixel-calibration script and calibration evidence CSV for paper anchors.
- [x] 3.12 Add BWP runtime instrumentation markers and extractor support for switch/interruption/UE RA evidence.
- [x] 3.13 Add runtime log collection and CSV merge flow to BWP/SDT wrappers.
- [x] 3.14 Run BWP local-image marker scenario and export BWP switch evidence metrics.
- [x] 3.15 Refactor shared BWP/SDT runtime helper for image defaults, RF defaults, compose helpers, log collection, and metric merge.
- [x] 3.16 Add BWP matrix runner plus residency, switch-delay, throughput, and estimated-power extraction from timestamped RFsim logs.
- [x] 3.17 Add SDT matrix runner plus repeated-run success/fallback/timeout aggregation.
- [x] 3.18 Re-extract existing BWP/SDT runtime bundles and merge local low-load BWP estimates plus minimal SDT success counters.

## 4. Validation

- [x] 4.1 Validate JSON syntax.
- [x] 4.2 Validate CSV/plot script execution.
- [x] 4.3 Run targeted `git diff --check` on touched files.
- [x] 4.4 Record remaining `[Needs Verification]` standard-clause risks.
- [x] 4.5 Add spec-cited BWP/SDT conclusions and record the TS 38.321 clause 5.9 vs 5.15.1 mismatch.
- [x] 4.6 Record current BWP `bwp-InactivityTimer` implementation gap from source audit.
- [x] 4.7 Add synthetic smoke test for BWP marker extraction.
- [x] 4.8 Validate wrapper alignment with dry-run manifests and update project Markdown/YAML records.
- [x] 4.9 Add synthetic smoke test for SDT success-counter extraction.
- [x] 4.10 Validate BWP/SDT matrix dry-run expansion and SDT aggregate CSV generation.
- [x] 4.11 Perform code review for all implemented RedCap_BWP_SDT_validation project changes before final Gate 7 reporting.
