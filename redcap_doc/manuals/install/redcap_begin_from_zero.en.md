# RedCap Begin From Zero

[English](./redcap_begin_from_zero.en.md) | [繁體中文](./redcap_begin_from_zero.zh-TW.md)

## Goal

- Start from the repository root.
- Validate the public RedCap operator interface.
- Build the local gNB and NR UE binaries.
- Rebuild the local RFsim Docker images.
- Run a 29 UE RedCap/mMTC RFsim validation.
- Judge the run by summary markers, not by raw log length.

## 1. Enter The Repository

```bash
cd /home/tonywang/OAI/Red_cap_openairinterface5g
pwd
```

Expected path:

```text
/home/tonywang/OAI/Red_cap_openairinterface5g
```

Check the public entry files:

```bash
ls README.md README.en.md redcap_interface/README.md redcap_doc/manuals/install/README.en.md
```

## 2. Check Host Services

Docker and Docker Compose must work before RFsim can run:

```bash
docker ps
docker compose version
```

Check the local CN5G compose file used by the RedCap RFsim scripts:

```bash
ls /home/tonywang/OAI/oai-cn5g/docker-compose.yaml
```

If the CN5G file is missing, stop and restore the local CN5G workspace before running the 29 UE validation.

## 3. Validate The RedCap Interface

This check should not start RFsim.

```bash
bash redcap_interface/validate_redcap_interface.sh
```

Expected result:

- Public shell entrypoints exist.
- Python helpers parse successfully.
- Required RedCap interface paths are present.
- FlexRIC and RFsim scenario files are found.

## 4. Install Or Refresh OAI Dependencies

Use the upstream OAI wrapper if the machine has not built OAI before:

```bash
cd cmake_targets
./build_oai -I --install-optional-packages -w USRP
cd ..
```

Notes:

- This step can require package-manager privileges.
- Run it once per machine or when system dependencies are missing.
- For upstream details, read `doc/BUILD.md`.

## 5. Configure And Build gNB + NR UE

Configure the default build tree:

```bash
cmake --preset default
```

Build the two RFsim modem targets:

```bash
cmake --build --preset default --target nr-softmodem
cmake --build --preset default --target nr-uesoftmodem
```

Expected result:

- `nr-softmodem` builds successfully.
- `nr-uesoftmodem` builds successfully.
- Build artifacts are under `cmake_targets/ran_build/build/`.

If ccache temp-path errors appear, retry with:

```bash
CCACHE_DIR=/tmp/ccache CCACHE_TEMPDIR=/tmp/ccache-tmp cmake --build --preset default --target nr-softmodem
CCACHE_DIR=/tmp/ccache CCACHE_TEMPDIR=/tmp/ccache-tmp cmake --build --preset default --target nr-uesoftmodem
```

## 6. Rebuild Local RFsim Images

RFsim containers use local images, so rebuild them after a fresh build:

```bash
bash redcap_interface/redcap_rebuild_local_oai_images.sh
```

This should refresh:

- `oai-gnb:latest`
- `oai-nr-ue:latest`

Inspect the gNB image:

```bash
bash redcap_interface/redcap_inspect_gnb_image.sh
```

## 7. Run The 29 UE RFsim Validation

This stage scan checks attach, PDU session, tunnel creation, and forward ping without iperf:

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

## 8. Read The Summary

Find the latest summary log:

```bash
ls -1t test_log/compiler_logs/mmtc_stage_scan_*_summary.log | head -n 1
```

Print the summary:

```bash
cat test_log/compiler_logs/<summary-log-name>
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

## 9. Next Step

After the 29 UE path works, use the daily operator menu:

```bash
bash redcap_interface/mmtc.menu.bash
```

For rebuilds after changes, use [redcap_rebuild_after_changes.en.md](./redcap_rebuild_after_changes.en.md).
