# RedCap 新手複現 Gate

[English](./redcap_newcomer_runtime_gate.en.md) | [繁體中文](./redcap_newcomer_runtime_gate.zh-TW.md)

## 目標

這個 gate 用來測試新手，或一個新的 Codex 視窗扮演新手時，是否能只依照公開文件，從 0 安裝到完成 29 UE RFsim 驗證。

## Gate 規則

- 只依照公開文件操作。
- 不使用 Codex 內部 wrapper 或私人筆記。
- 遇到第一個不清楚或失敗的步驟就停下來記錄 evidence。
- 如果主機依賴缺失，請回報為文件或環境 blocker。

## 1. Static documentation gate

從 repository root 執行：

```bash
bash redcap_interface/bash_library/fc_doc_newcomer_gate_check.sh
```

預期結果：

- English 與繁體中文 install files 都存在。
- 公開 Markdown 不包含 Codex-only command wrappers。
- 公開 Markdown 不包含明顯編碼 replacement characters。
- Install 與 gate 文件包含必要 29 UE markers。

## 2. 從零開始

打開並照著執行：

```bash
sed -n '1,240p' redcap_doc/manuals/install/redcap_begin_from_zero.zh-TW.md
```

必要 checkpoints：

- Repository root 正確。
- Docker 與 Docker Compose 可用。
- 本機 CN5G compose file 存在。
- RedCap interface validator 通過。
- `nr-softmodem` 編譯成功。
- `nr-uesoftmodem` 編譯成功。
- 本地 RFsim images 重建完成。
- gNB image inspection 通過。

## 3. 執行 29 UE stage scan

執行 beginner guide 中的指令：

```bash
env MMTC_TOTAL_UES_TARGET=29 \
    MMTC_STAGE_LIST=29 \
    MMTC_REBUILD_IMAGES_BEFORE_SCAN=0 \
    MMTC_FORWARD_PING_MODE=parallel \
    MMTC_RUN_REVERSE_PING=0 \
    MMTC_IPERF_ENABLE=0 \
    MMTC_UE_START_GAP=3 \
    MMTC_GNB_WARMUP=10 \
    MMTC_SLEEP_AFTER_UP=25 \
    bash redcap_interface/redcap_mmtc_stage_scan.sh
```

## 4. 通過標準

最新 summary log 必須包含：

```text
sample=29
running=29
attach=29
pdu=29
tun=29
forward_ping_ok=29
gnb_restart=0
failures=0
```

## 5. 回饋格式

如果 gate 失敗或文件不清楚，請回報：

```markdown
## Newcomer Gate Feedback

- Step:
- Command:
- Expected:
- Actual:
- Log path:
- Unclear wording:
- Suggested document fix:
```

## 6. 完成判定

只有兩項都成立，才算 gate 完成：

- Static documentation gate 通過。
- Runtime summary 包含所有 pass markers。
