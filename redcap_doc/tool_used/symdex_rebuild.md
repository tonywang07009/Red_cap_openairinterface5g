# SymDex 重建索引

## 1. 確認目前環境

若目前已在 `basic`（或其他含有 SymDex 的）環境，直接使用該環境的指令：

```bash
command -v symdex
symdex --version
```

若目前環境沒有 `symdex`，使用已確認可用的 base 版本：

```bash
SYMDEX_BIN=/home/tonywang/miniforge3/bin/symdex
"$SYMDEX_BIN" --version
```

## 2. 建立新的 index state

```bash
REPO_ROOT=/home/tonywang/OAI/Red_cap_openairinterface5g_exp
SYMDEX_BIN="${SYMDEX_BIN:-$(command -v symdex || true)}"
SYMDEX_BIN="${SYMDEX_BIN:-/home/tonywang/miniforge3/bin/symdex}"
STATE_DIR=$(mktemp -d /tmp/redcap-symdex-rebuild-XXXXXX)
```

## 3. 重建本次 DRL xApp 所需索引

```bash
"$SYMDEX_BIN" --state-dir "$STATE_DIR" \
  index "$REPO_ROOT/redcap_library/drl_xapp" \
  --repo redcap-exp --no-embed

"$SYMDEX_BIN" --state-dir "$STATE_DIR" \
  index "$REPO_ROOT/redcap_library/bash_tool/scripts" \
  --repo redcap-exp --no-embed

"$SYMDEX_BIN" --state-dir "$STATE_DIR" \
  index "$REPO_ROOT/openair2/E2AP/flexric/src/xApp" \
  --repo redcap-exp --no-embed
```

## 4. 驗證索引

```bash
"$SYMDEX_BIN" --state-dir "$STATE_DIR" repos
"$SYMDEX_BIN" --state-dir "$STATE_DIR" find NativeFlexric --repo redcap-exp
"$SYMDEX_BIN" --state-dir "$STATE_DIR" find run_model --repo redcap-exp
"$SYMDEX_BIN" --state-dir "$STATE_DIR" find send_control_request --repo redcap-exp
```

`STATE_DIR` 只在目前 shell session 有效；要重新建立索引時，重新執行第 2 節。
