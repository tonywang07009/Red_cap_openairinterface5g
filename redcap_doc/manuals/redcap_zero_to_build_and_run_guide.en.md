# RedCap Zero-to-Build and 29 UE Run Guide

## Goal
- Start from the repository root.
- Build the local gNB and NR UE binaries.
- Rebuild the local Docker images used by RFsim.
- Run a 29 UE RedCap/mMTC RFsim validation.
- Confirm the summary markers instead of reading raw logs first.

## Scope
- This guide is for first-time local users of this RedCap/OAI workspace.
- Commands are written for a normal shell, not for Codex internal execution.
- Run every command from the repository root unless the step changes directory.

## 1. Enter the Repository

```bash
cd /home/tonywang/OAI/Red_cap_openairinterface5g
```

Check the main entry files:

```bash
ls AGENTS.md README.md redcap_interface/README.md redcap_doc/manuals/README.md
```

## 2. Check Required Services

Docker and Docker Compose must work before RFsim can run:

```bash
docker ps
docker compose version
```

Check the local CN5G compose file used by the RedCap RFsim scripts:

```bash
ls /home/tonywang/OAI/oai-cn5g/docker-compose.yaml
```

If this file is missing, stop here and restore the local CN5G workspace before running the 29 UE test.

## 3. Validate the RedCap Interface

This is a non-invasive check. It should not start RFsim.

```bash
bash redcap_interface/validate_redcap_interface.sh
```

Expected result:

- Shell entrypoints are found.
- Python helpers parse successfully.
- Required RedCap interface paths are present.

## 4. Install or Refresh OAI Build Dependencies

Use the upstream OAI wrapper when the machine has not built OAI before:

```bash
cd cmake_targets
./build_oai -I --install-optional-packages -w USRP
cd ..
```

Notes:

- This step can require package-manager privileges.
- Run it once per machine or when system dependencies are missing.
- For deeper upstream build details, read `doc/BUILD.md`.

## 5. Configure and Build gNB + NR UE

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

## 6. Rebuild Local Docker Images

RFsim containers use local images, so rebuild them after C code changes:

```bash
bash redcap_interface/redcap_rebuild_local_oai_images.sh
```

This should refresh:

- `oai-gnb:latest`
- `oai-nr-ue:latest`

Inspect the gNB image after rebuilding:

```bash
bash redcap_interface/redcap_inspect_gnb_image.sh
```

## 7. Run the 29 UE RedCap RFsim Validation

This command runs a 29 UE stage scan without iperf. It checks attach, PDU session, tunnel creation, and forward ping.

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

## 8. Read the Summary

Find the latest summary log:

```bash
ls -1t test_log/compiler_logs/mmtc_stage_scan_*_summary.log | head -n 1
```

Print it:

```bash
cat test_log/compiler_logs/<summary-log-name>
```

The pass line should contain:

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

## 9. Open the Daily Operator Menu

After the build path is working, use the daily RedCap/mMTC menu:

```bash
bash redcap_interface/mmtc.menu.bash
```

Common menu uses:

| Need | Route |
|---|---|
| Check mounted gNB config | `mmtc.menu.bash` daily menu |
| Set RedCap RX mode | `mmtc.menu.bash` daily menu |
| Toggle 256QAM flags | `mmtc.menu.bash` daily menu |
| Configure DRX/eDRX/PSM knobs | `mmtc.menu.bash` daily menu |
| Paper/demo display work | `bash redcap_interface/mmtc.display.bash` |

## 10. Troubleshooting

| Symptom | First Check | Fix Direction |
|---|---|---|
| `docker ps` permission denied | Docker group or daemon | Fix Docker access before RFsim |
| CN5G compose missing | `/home/tonywang/OAI/oai-cn5g/docker-compose.yaml` | Restore local CN5G workspace |
| CMake configure fails | `doc/BUILD.md` and dependency install step | Re-run `build_oai -I` dependency install |
| Build fails with ccache temp path errors | ccache temp directory | Retry with `CCACHE_DIR=/tmp/ccache CCACHE_TEMPDIR=/tmp/ccache-tmp` |
| 29 UE summary is not PASS | Latest `mmtc_stage_scan_*_summary.log` | Check gNB restart, UE attach, tunnel, then ping markers |

## Next Reading

- RedCap operator routes: `redcap_interface/README.md`
- Manual index: `redcap_doc/manuals/README.md`
- L1/L2 protocol guide: `redcap_doc/specs/redcap_l1_l2_protocol_guide.md`
- Function lookup: `redcap_doc/specs/function_reference/redcap_l1_l3_function_lookup.md`
