# CN5G Library Docs

## Purpose
- CN5G overlays, DB seeds, and reusable compose fragments live here.

## Bash Link
- Generation helpers are called through `redcap_interface/mmtc.menu.bash` or compatibility shims.
- Implementation lives in `redcap_interface/bash_library/fc_generate_mmtc_cn_db_overlay.sh`.

## Rule
- Do not directly mutate `/home/tonywang/OAI/oai-cn5g` from docs.
- Generate temporary runtime overlays through scripts.
