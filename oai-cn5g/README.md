# Repository-owned CN5G runtime

## 繁體中文

- 本目錄是 RedCap mMTC 現行 CN5G runtime 的唯一 repo 內來源。
- 已佈建並支援 UE1..UE56；`MMTC_ACTIVE_UES` 選擇本次啟動的 UE，固定上限為 56。
- MySQL 乾淨初始化會依序載入 `database/oai_db.sql` 與 `database/oai_db_mmtc_56.sql`。
- 已存在的 MySQL data volume 不會重新執行 init scripts。不得為了套用 seed 自動刪除既有 volume。
- 日常操作從 `redcap_interface/mmtc.menu.bash` 進入；run-specific 產物放在 `test_log/runtime_configs/`。

## English

- This directory is the repository-owned source of truth for the active RedCap mMTC CN5G runtime.
- UE1 through UE56 are provisioned and supported. `MMTC_ACTIVE_UES` selects the UEs activated for a run; the fixed ceiling is 56.
- A clean MySQL initialization loads `database/oai_db.sql` followed by `database/oai_db_mmtc_56.sql`.
- Existing MySQL data volumes do not rerun init scripts. Never delete an existing volume automatically to apply the seed.
- Use `redcap_interface/mmtc.menu.bash` for daily operation. Store run-specific output under `test_log/runtime_configs/`.

```bash
docker compose -f oai-cn5g/docker-compose.yaml config --services
MMTC_ACTIVE_UES="1" redcap_interface/mmtc.menu.bash smoke
MMTC_ACTIVE_UES="1 29 56" redcap_interface/mmtc.menu.bash smoke
```

## Trace-code guide

| Step | File / symbol | Input | Output / state owner | Expected marker | Next point | Status |
|---:|---|---|---|---|---|---|
| 1 | `redcap_interface/mmtc.menu.bash`: `DEFAULT_CN_COMPOSE`, `run_smoke()` | Optional `MMTC_CN_COMPOSE` | `CN_COMPOSE`; menu process owns the resolved path | `CN compose : .../oai-cn5g/docker-compose.yaml` | Step 2 | Verified |
| 2 | `mmtc.menu.bash`: `validate_active_ues()`; `fc_mmtc_smoke_validation.sh`: active-set validation block | `MMTC_ACTIVE_UES`, fixed `TOTAL_UES=56` | Validated ordered UE-index array; no Docker state exists yet | Bilingual error on invalid input or `Active UE selection` on success | Step 3 | Verified |
| 3 | `redcap_interface/bash_library/generate_mmtc_overlay.sh` | Ceiling `56`, run-specific output path | Base Compose owns UE1..UE28; generated overlay owns UE29..UE56 | `Generated mMTC overlay: ... (UE1..UE56)` | Step 4 | Verified |
| 4 | `fc_mmtc_smoke_validation.sh`: `SERVICE_LIST`, `start_sample_ues()` | Validated active array | Docker owns only the selected UE services plus gNB/nearRT-RIC | `Service list` and `Starting active UE service` | Step 5 | Verified |
| 5 | `redcap_interface/bash_library/ue_mmtc_entrypoint.sh`; `ci-scripts/conf_files/nrue_recap/nrue<N>.uicc.yaml` | `MMTC_UE_INDEX`, UE-specific UICC file | UE process owns the effective IMSI | `UICC simulation: IMSI=001010...` | Step 6 | Verified |
| 6 | `oai-cn5g/database/oai_db.sql`, `oai_db_mmtc_56.sql`; UDM/UDR lookup | SUPI/IMSI and DNN `oai` | MySQL owns authentication/session rows; AMF owns registered SUPI | MySQL boundary row plus AMF `Received IMSI` / Registration Accept | Step 7 | Verified |
| 7 | `fc_mmtc_smoke_validation.sh`: UE marker and TUN checks | Active UE container logs | UE container owns `oaitun_ue1`; SMF/UPF own PDU/tunnel state | `PDU Session Establishment Accept`, `successfully configured`, successful forward ping | Step 8 | Verified |
| 8 | `fc_mmtc_smoke_validation.sh`: final summary | Per-UE counters and gNB restart state | Timestamped logs under `test_log/compiler_logs/` | `[SUMMARY] active=... failures=0` and `gnb_restart=0` | Report | Verified |

The seed stores the accepted UE1..UE56 static-address metadata. In the current CN runtime, an isolated UE56 session receives the first free SMF pool address (`10.0.0.2`), while the ordered 56 UE run produces `10.0.0.2..10.0.0.57`. Therefore, static-address enforcement by SMF is `[Needs Verification]`; subscriber identity is verified through UICC IMSI, MySQL, and AMF SUPI instead of container name or runtime address alone.
