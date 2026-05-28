# RedCap Interface

## Purpose
- Keep RedCap/mMTC operator-facing shell entry points out of `ci-scripts/`.
- Leave Python/C/YAML/XML implementation assets in `ci-scripts/`.
- Run commands from the repository root unless a script states otherwise.

## Entry Points
| Script | Role |
|---|---|
| `mmtc.menu.bash` | Compatibility menu launcher |
| `mmtc.ment.bash` | Compatibility launcher using the user-requested spelling |
| `redcap_runtime_menu.sh` | Interactive Paper 07 / RFsim runtime menu |
| `paper11_iperf_live_demo.sh` | PAPER-11 service-gate iperf/ping reproduction wrapper |
| `paper11_table3_peak_reproduction.sh` | PAPER-11 Table 3 RedCap peak-rate target proxy runner |
| `iperf_live_panel.py` | Standalone live UL/DL iperf3 display panel |
| `redcap_mmtc_smoke_validation.sh` | mMTC smoke validation runner |
| `redcap_mmtc_stage_scan.sh` | staged UE load scan runner |
| `redcap_runtime_host_validation.sh` | host-side RFsim validation runner |
| `redcap_runtime_case_matrix.sh` | Case A / Case B runtime matrix |
| `redcap_runtime_e2_ab_test.sh` | E2 enabled/disabled A/B validation |
| `generate_mmtc_cn_db_overlay.sh` | CN5G subscriber overlay generator |
| `redcap_send_ul_prb_control.sh` | FlexRIC RC UL PRB cap sender |
| `redcap_verify_ul_prb_control.sh` | UL PRB cap marker verifier |
| `redcap_rebuild_local_oai_images.sh` | local OAI Docker image rebuild helper |
| `redcap_inspect_gnb_image.sh` | local gNB image marker inspector |
| `validate_redcap_interface.sh` | non-invasive dependency and syntax validator |

## Validation
```bash
bash redcap_interface/validate_redcap_interface.sh
```
