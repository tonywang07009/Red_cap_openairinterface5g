# CN5G Library

## Contents
| File | Role |
|---|---|
| `oai_cn5g_static_config_backup_final.yaml` | Static CN config backup captured before the accepted 56 UE run |
| `oai_db_mmtc_50ue_final.sql` | Reusable 50 UE subscriber seed |
| `oai_db_mmtc_64ue_final.sql` | Reusable 64 UE subscriber seed |
| `oai_cn5g_mmtc_50ue_override_final.yml` | Compose override for 50 UE mMTC CN setup |
| `oai_cn5g_mmtc_64ue_override_final.yml` | Compose override for 64 UE mMTC CN setup |

## Usage
- Use these files as reference or input templates for `redcap_interface/generate_mmtc_cn_db_overlay.sh`.
- Runtime scripts may still generate temporary SQL and compose overlays under `test_log/runtime_configs/`.
- Do not merge these files into the external `oai-cn5g` repository unless the user explicitly requests a CN5G-side change.
