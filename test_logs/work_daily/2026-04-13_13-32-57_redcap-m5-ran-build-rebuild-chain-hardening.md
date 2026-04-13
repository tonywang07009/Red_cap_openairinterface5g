# Work Daily Log
## Session Metadata
- Date: 2026-04-13 13:32
- Agent Session ID: N/A
- Task Slug: redcap-m5-ran-build-rebuild-chain-hardening

## Milestone & Sub-task Reference
- Milestone: [Milestone 5: Integration & UL Throughput Targets]
- Sub-task: [Harden local image rebuild workflow so RedCap runtime uses updated ran-build artifacts instead of stale gNB/UE binaries]
- Status: [COMPLETED]

## What Was Done
- Analyzed the latest host run and confirmed the containers now use local tags:
  - `oai-gnb:latest`
  - `oai-nr-ue:latest`
  but the gNB artifact still crashes with the legacy `MAX_MOBILES_PER_GNB` PUCCH assert.
- Verified the root cause in Dockerfiles:
  - `docker/Dockerfile.gNB.ubuntu` copies `/oai-ran/cmake_targets/ran_build/build/nr-softmodem` from `ran-build:latest`
  - `docker/Dockerfile.nrUE.ubuntu` copies `nr-uesoftmodem` from `ran-build:latest`
  therefore rebuilding only final images is insufficient after C-source changes.
- Added `ci-scripts/redcap_rebuild_local_oai_images.sh` to rebuild the correct chain:
  - `[ran-base:latest]` when missing or explicitly requested
  - `[ran-build:latest]`
  - `[oai-gnb:latest]`
  - `[oai-nr-ue:latest]`
- Updated `ci-scripts/redcap_runtime_host_validation.sh`:
  - added `REDCAP_REBUILD_LOCAL_OAI_IMAGES=1`
  - clarified that local runtime images depend on `[ran-build:latest]`
  - updated the [legacy PUCCH assert] warning to recommend the new rebuild helper and image inspection helper
- Updated `ci-scripts/redcap_inspect_gnb_image.sh` to inspect `nr-softmodem` strings for:
  - `[Reducing PUCCH reservation budget]`
  - `[Cannot allocate all required PUCCH resources for max number of]`
- Updated `ci-scripts/redcap_runtime_summary.py` so the [gNB Log Cross-Check] now flags:
  - `[Legacy PUCCH budget assert]`
  - `[BWP-fit PUCCH budget marker]`
  - a direct diagnosis that `oai-gnb:latest` may still contain stale `ran-build:latest` output

## 3GPP Spec Clauses Referenced
- TS 38.306 Section 4.2.21.1 — [RedCap UE] can legitimately operate with a smaller FR1 initial BWP such as [51 PRBs], so runtime rejection caused by a fixed [64-UE] PUCCH reservation is an implementation/toolchain issue, not a standards-valid deployment issue.
- TS 38.321 Section 5.1 — the failure still occurs after [RA Msg3] reception, confirming the attach path reaches post-RA gNB resource preparation before aborting.
- TS 38.331 Section 5.2.2.4.2 — SIB1-side [RedCap initial DL/UL BWP] evidence is already present in the latest gNB log, so the current blocker is downstream of SIB1 generation.

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| `bash -n ci-scripts/redcap_rebuild_local_oai_images.sh` | Pass | [new rebuild helper syntax] | 新 helper 可正常解析 |
| `bash -n ci-scripts/redcap_inspect_gnb_image.sh` | Pass | [image inspection helper syntax] | 新增 binary marker 檢查後仍通過 |
| `bash -n ci-scripts/redcap_runtime_host_validation.sh` | Pass | [runtime shell helper syntax] | 加入 rebuild hook 與依賴說明後仍通過 |
| `python3 -m py_compile ci-scripts/redcap_runtime_summary.py` | Pass | [runtime summary script syntax] | 新增 gNB-side stale-builder diagnosis 後仍通過 |
| `git diff --check -- ci-scripts/redcap_rebuild_local_oai_images.sh ci-scripts/redcap_inspect_gnb_image.sh ci-scripts/redcap_runtime_host_validation.sh ci-scripts/redcap_runtime_summary.py` | Pass | [modified files formatting] | 無 whitespace / patch format 問題 |
| `python3 ci-scripts/redcap_runtime_summary.py --scenario container_5g_flexric_rfsim_redcap.xml --run-log test_log/compiler_logs/redcap_runtime_host_disabled_2026-04-13_13-24-57.log` | Pass | [latest host artifact diagnosis] | 已正確指出 [legacy PUCCH budget assert] 與 [stale ran-build] 根因 |

## Known Issues / Blockers
- [Host Docker runtime] 仍需使用者在 host 親自執行 rebuild helper；目前 sandbox 無法直接操作 Docker。
- 在 [ran-build:latest] 被重建並重新封裝前，`oai-gnb:latest` / `oai-nr-ue:latest` 仍可能持續使用舊 binary。
- [enabled E2 mode] 的 [FlexRIC plugin ABI mismatch] 仍是後續獨立 blocker，尚未在本次子任務中處理。

## Next Step
- 在 host 執行：
  - `bash ci-scripts/redcap_rebuild_local_oai_images.sh`
  - `bash ci-scripts/redcap_inspect_gnb_image.sh`
  - `REDCAP_USE_LOCAL_OAI_IMAGES=1 REDCAP_E2_AGENT_MODE=disabled bash ci-scripts/redcap_runtime_host_validation.sh`
- 若 inspection 顯示 `nr-softmodem` 已包含 `[Reducing PUCCH reservation budget]`，且新的 gNB log 不再出現舊版 [legacy PUCCH budget assert]，再往下看 [UE attach] / [302002] / [FlexRIC] 後續問題。
