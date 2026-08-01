# RedCap Rebuild After Changes

[English](./redcap_rebuild_after_changes.en.md) | [繁體中文](./redcap_rebuild_after_changes.zh-TW.md)

## Goal

Use this workflow after changing OAI C code, RedCap scripts, xApp/rApp/dApp integration files, configs, or local libraries.

## 1. Classify The Change

| Change Type | Minimum Rebuild Or Check |
|---|---|
| Documentation only | Static documentation gate and `git diff --check`. |
| Shell or Python interface script | `bash redcap_interface/validate_redcap_interface.sh`. |
| gNB C code | Build `nr-softmodem`, rebuild local RFsim images, then run the 29 UE marker gate. |
| NR UE C code | Build `nr-uesoftmodem`, rebuild local RFsim images, then run the 29 UE marker gate. |
| Shared C code used by both sides | Build both modem targets and rebuild images. |
| xApp control source | Build with `REDCAP_CTRL_BUILD_ONLY=1 bash redcap_interface/redcap_send_ul_prb_control.sh`. |
| RFsim YAML or CN5G overlay | Validate interface, regenerate overlays through the menu or stage scan, then run the gate. |

## 2. Preflight

Run from the repository root:

```bash
pwd
bash redcap_interface/validate_redcap_interface.sh
```

If the interface validator fails, fix that before rebuilding images or running RFsim.

## 3. Rebuild C Targets

For gNB changes:

```bash
cmake --build --preset default --target nr-softmodem
```

For NR UE changes:

```bash
cmake --build --preset default --target nr-uesoftmodem
```

For shared changes:

```bash
cmake --build --preset default --target nr-softmodem
cmake --build --preset default --target nr-uesoftmodem
```

If ccache temp-path errors appear:

```bash
CCACHE_DIR=/tmp/ccache CCACHE_TEMPDIR=/tmp/ccache-tmp cmake --build --preset default --target nr-softmodem
CCACHE_DIR=/tmp/ccache CCACHE_TEMPDIR=/tmp/ccache-tmp cmake --build --preset default --target nr-uesoftmodem
```

## 4. Rebuild Local RFsim Images

Run this after any C build that must be visible inside containers:

```bash
bash redcap_interface/redcap_rebuild_local_oai_images.sh
bash redcap_interface/redcap_inspect_gnb_image.sh
```

Expected refreshed images:

- `oai-gnb:latest`
- `oai-nr-ue:latest`

## 5. Rebuild The RedCap xApp Control Binary

Use this when `ci-scripts/redcap_ul_prb_ctrl_xapp.c` or FlexRIC control integration changed:

```bash
REDCAP_CTRL_BUILD_ONLY=1 bash redcap_interface/redcap_send_ul_prb_control.sh
```

Expected output:

- Build log under `test_log/build_logs/`.
- Runtime binary under `test_log/runtime_bins/redcap_ul_prb_ctrl_xapp`.

For a live control test, RFsim and FlexRIC must already be running. Then use the public control scripts:

```bash
bash redcap_interface/redcap_send_ul_prb_control.sh
bash redcap_interface/redcap_verify_ul_prb_control.sh
```

## 6. Run The 29 UE Marker Gate

Use the same stage scan as the beginner path:

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

Pass markers:

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

## 7. Record Evidence

For a completed rebuild, record:

- Changed area.
- Build command.
- Image rebuild command.
- Stage scan summary path.
- Pass/fail markers.
- Any `[Needs Verification]` spec mapping.
