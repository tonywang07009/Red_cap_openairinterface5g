# RedCap Library

[English](./Doc/README.en.md) | [繁體中文](./Doc/README.zh-TW.md)

## Purpose
- This folder is the curated replacement for high-value artifacts previously scattered under `test_log/`.
- Use it as the first lookup point for reusable RedCap runtime configs, runtime probes, build evidence, and summarized reports.
- Generated timestamped logs should still be written to `test_log/`; only promote final or reusable evidence into this library.

## Fast Lookup
| Need | Path | Contents |
|---|---|---|
| Active CN5G runtime and baseline | `../oai-cn5g/` | Repository-owned Compose, configuration, and UE1..UE56 seed |
| gNB runtime configs | `library_gnb_config/` | Final Case A/B, E2-disabled, and mMTC Case B configs |
| Runtime probes | `library_runtime_probe/` | Paper 07 iperf/ping/gNB/UE logs, RedCap vs non-RedCap live probe, FlexRIC service-model libs |
| Build evidence | `library_build_evidence/` | Final build/rebuild logs tied to retained runtime claims |
| Report summaries | `library_reports_summary/` | Curated M3-M7 reports, M5 scaling evidence, latency RCA, validation rerun |
| AIOTF CN5G diagnostic report | `library_reports_summary/aiotf_cn5g_experimental_n6_validation_report.md` | Implemented Tag/AIOTF, NRF and bounded Naiotf scope; evidence index; stopped AMF/RAN/NEF gates |
| A-IoT two-week course | `../redcap_doc/manuals/aiot_redcap_to_aiotf_two_week_course.zh-TW.md` | GPT 5.6 Luna route from RedCap source owners through Tag, UE Reader, AIOTF, CN5G, and service diagnosis |
| Documentation workflow | `redcap_doc_writer_skill/SKILL.md` | Bilingual docs, API guides, OpenSpec doc changes, and canonical-path migration workflow |
| Research wiki workflow | `skills/redcap_research_wiki/SKILL.md` | Source ingestion, research queries, simulator decision contracts, review gates, and wiki lint |

## Retention Rule
- Keep: configs that can reproduce a scenario, final accepted reports, current Paper 07 raw evidence, FlexRIC service-model libraries used by runtime probe scripts.
- Delete: one-off timestamped logs, duplicate runtime host summaries, generated runtime artifact folders, generated xApp binaries that can be rebuilt.
- Keep the active runtime under `../oai-cn5g/`. Generate run-specific temporary overlays under `test_log/runtime_configs/`; do not recreate a parallel CN5G asset library.

## Key Results Preserved
| Scope | Preserved Result | Primary File |
|---|---|---|
| Paper 07 TDD UL 106PRB | 35.0 Mbits/sec receiver, 0% UDP loss, 3.904 ms avg ping | `library_runtime_probe/paper07_tdd_ul_iperf_106prb_final.log` |
| Paper 07 TDD UL 51PRB | 35.0 Mbits/sec receiver, 0% UDP loss, 2.795 ms avg ping | `library_runtime_probe/paper07_tdd_ul_iperf_51prb_final.log` |
| Paper 07 TDD UL 256QAM enabled | UE capability marker present; gNB still reports UL `Qm 2`; 35.0 Mbits/sec receiver, 0% UDP loss | `library_runtime_probe/paper07_tdd_gnb_256qam_final.log` |
| Paper 07 TDD DL menu run | 141 Mbits/sec receiver, 0.061% UDP loss | `library_runtime_probe/paper07_tdd_dl_iperf_menu_final.log` |
| M5 scaling accepted baseline | 56/56 UE attach/PDU/tunnel/ping PASS | `library_reports_summary/m5_caseb_56ue_static_cn_pass_report.md` |
| M5 upper boundary | 64 UE run identified gNB runtime SIGKILL threshold | `library_reports_summary/m5_caseb_64ue_static_cn_threshold_report.md` |
| CN5G runtime migration | Repository-owned runtime, UE1/UE56 boundaries, and 56/56 regression | `library_reports_summary/cn5g_runtime_migration_report.md` |
| Latency RCA | 50 UE pass, RTT avg 808 ms, p95 1099 ms, TCP UL 20 Mbps | `library_reports_summary/redcap_mmtc_latency_rca_latest.md` |

## Navigation Rule
- For a new task, read this file first, then only the target subfolder `README.md`.
- For daily runtime execution, use root `mmtc.menu.bash`; its default gNB config points to `library_gnb_config/gnb_redcap_mmtc_case_b_final.yaml`.
- For paper/demo panels, use `redcap_interface/mmtc.display.bash`.
- Legacy script paths such as `redcap_interface/redcap_runtime_menu.sh` are compatibility shims unless a historical report says otherwise.
- For historical report interpretation, old `test_log/...` paths inside moved reports are original evidence references. Prefer this folder's standardized paths for current work.
