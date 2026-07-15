# RedCap Interface 文件

[English](./README.en.md) | [繁體中文](./README.zh-TW.md)

## 用途
- 這裡放 RedCap / mMTC 操作者會直接使用的 shell 入口。
- RFsim、paper demo、介面驗證都從這裡開始。

## Bash 主入口
| 腳本 | 用途 |
|---|---|
| `../../mmtc.menu.bash` | 唯一公開入口：專案介紹、已驗證效能、experiment profile、進階 RFsim |
| `../mmtc.menu.bash` | 供既有呼叫者使用的相容 shim |
| `mmtc.display.bash` | 由主入口明確委派的 Paper demo/live panel dispatcher；保留直接呼叫相容性 |
| `validate_redcap_interface.sh` | 非破壞性語法與依賴檢查 |

## Step-by-Step Recap
```bash
./mmtc.menu.bash
./mmtc.menu.bash intro
./mmtc.menu.bash performance
bash redcap_interface/validate_redcap_interface.sh
```

## Experiment Profile v1

```bash
# 互動建立；只寫入 test_log/runtime_configs/，不啟動 Docker。
./mmtc.menu.bash experiment

# 檢查正規化內容，不產生 overlay。
./mmtc.menu.bash preview-profile test_log/runtime_configs/<run-id>.profile.env

# 明確執行既有 smoke path。
./mmtc.menu.bash run-profile test_log/runtime_configs/<run-id>.profile.env smoke
```

Profile v1 固定 `REDCAP_TOPOLOGY=single_gnb_rfsim`、`REDCAP_GNB_COUNT=1`、`REDCAP_CU_DU_SPLIT=0`、`MMTC_TOTAL_UES=56`。可設定 active UE、51/106 PRB、gNB/CN/policy/contract 路徑、`case_a/case_b` 與既有 xApp/dApp flags。多 gNB 與 CU/DU split 尚未支援。

## Profile Trace

| Step | File / symbol | Input | Output / owner | Marker | Next | Status |
|---|---|---|---|---|---|---|
| 1 | `mmtc.menu.bash:create_experiment_profile` | 互動輸入 | version-1 profile / operator | `[OK] Experiment profile created` | preview | implemented |
| 2 | `mmtc.menu.bash:load_profile` | profile | allowlisted normalized fields / main menu | normalized `KEY=value` output | adapter | implemented |
| 3 | `mmtc.menu.bash:apply_loaded_profile` | validated fields | existing environment-variable state / runtime wrapper | main menu header and smoke info | `run_smoke` | implemented |
| 4 | `fc_mmtc_smoke_validation.sh` | active UE、RF、xApp/dApp flags | Compose services and overlay / smoke runner | `[INFO] Active UE selection` | gNB/xApp/dApp runtime | implemented |
| 5 | `redcap_control_contract.yaml` + policy | existing control selection | xApp hint、dApp/gNB accept/reject/apply boundary | feature-specific ACK/apply markers | checker/report | implemented; no new control semantics |

## 相關公開手冊
- 從零安裝：`redcap_doc/manuals/install/redcap_begin_from_zero.zh-TW.md`。
- 修改後重建：`redcap_doc/manuals/install/redcap_rebuild_after_changes.zh-TW.md`。
- Paper recovery 教學：`redcap_doc/evluation_recover/README.zh-TW.md`。
