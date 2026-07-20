# Reports Summary Library

## Contents
| Group | Files | Role |
|---|---|---|
| M3-T2 RA/BWP evidence | `m3t2_*.md` | CORESET/BWP/RA diagnosis and partition reports |
| M4B low-power evidence | `m4b_*.md` | DRX/eDRX/PSM boundary and timer decode reports |
| M5 scaling evidence | `m5_*.md` | 30/32/48/56/64 UE runtime scaling reports |
| CN5G runtime migration | `cn5g_runtime_migration_report.md` | Repository ownership, fixed 56-UE seed, boundary/runtime evidence, cleanup inventory |
| AIOTF CN5G diagnostic integration | `aiotf_cn5g_experimental_n6_validation_report.md` | Tag/AIOTF, NRF, and bounded Naiotf evidence plus stopped AMF/RAN/NEF gates |
| M6/M7 closure | `m6_evidence_package_summary.md`, `m7_repo_hygiene_inventory_legacy.md` | Evidence package and legacy hygiene inventory |
| Legacy project summaries | `redcap_*.md` | Earlier simulator and validation summaries |
| Latency RCA | `redcap_mmtc_latency_rca_latest.md` | 50 UE latency/root-cause analysis |
| Cleanup summary | `redcap_test_log_curated_summary.md` | What was promoted, deleted, and retained from `test_log/` |

## Usage
- Start with `m6_evidence_package_summary.md` for the M3-M5 project status.
- Use `m5_caseb_56ue_static_cn_pass_report.md` as the accepted scaling baseline.
- Use `m5_caseb_64ue_static_cn_threshold_report.md` for the upper-bound failure explanation.
- Use `redcap_test_log_curated_summary.md` to understand the 2026-05-25 cleanup result.
- Old `test_log/...` paths inside these reports are historical references. For current lookup, prefer standardized files in `redcap_library/`.
