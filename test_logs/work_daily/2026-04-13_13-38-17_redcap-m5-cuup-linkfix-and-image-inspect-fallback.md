# Work Daily Log
## Session Metadata
- Date: 2026-04-13 13:38
- Agent Session ID: N/A
- Task Slug: redcap-m5-cuup-linkfix-and-image-inspect-fallback

## Milestone & Sub-task Reference
- Milestone: [Milestone 5: Integration & UL Throughput Targets]
- Sub-task: [Unblock local RedCap image rebuild by fixing CU-UP RC link failure and make gNB image inspection work without `strings`]
- Status: [COMPLETED]

## What Was Done
- Diagnosed the `ran-build:latest` failure during Docker rebuild:
  - `nr-cuup` linked `openair2/E2AP/RAN_FUNCTION/O-RAN/ran_func_rc.c`
  - the new [RedCap UL PRB control] branch referenced gNB-MAC-only symbol `find_nr_UE()`
  - pure [CU-UP] builds do not link gNB MAC scheduler objects, so link failed
- Updated `openair2/E2AP/RAN_FUNCTION/O-RAN/ran_func_rc.c`:
  - limited gNB MAC includes to builds with `[NGRAN_GNB_DU]`
  - added `apply_redcap_ul_prb_control()` as a gNB/DU-only helper
  - made [CU-UP-only] RC builds reject [RedCap UL PRB control] at compile/runtime boundary instead of linking to gNB-only symbols
- Updated `ci-scripts/redcap_inspect_gnb_image.sh`:
  - replaced `strings ... | grep ...` with `grep -aF ... /opt/oai-gnb/bin/nr-softmodem`
  - avoids failure when the image lacks the `strings` utility

## 3GPP Spec Clauses Referenced
- TS 38.306 Section 4.2.21.1 — [RedCap] bandwidth/BWP constraints remain the runtime objective; this sub-task unblocks the build chain needed to validate the earlier [PUCCH budget] fix.
- TS 38.321 Section 5.1 — the attach path still fails after [RA Msg3] in the current runtime evidence; therefore build-chain correctness remains a prerequisite before further MAC/RRC runtime analysis.
- TS 38.331 Section 5.6.1.3 — [UE capability] and later [302002] checks remain downstream of successful local image rebuild and gNB boot.

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| `bash -n ci-scripts/redcap_inspect_gnb_image.sh` | Pass | [helper syntax] | 已移除對 `strings` 的依賴 |
| `git diff --check -- openair2/E2AP/RAN_FUNCTION/O-RAN/ran_func_rc.c ci-scripts/redcap_inspect_gnb_image.sh` | Pass | [modified files formatting] | 無 whitespace / patch format 問題 |
| `cmake --build --preset default --target nr-cuup -j2` | Pass | [CU-UP link path] | 產出 `test_log/build_logs/nr-cuup_redcap_cuup_linkfix_2026-04-13_13-38-00.log` |
| `cmake --build --preset default --target nr-softmodem -j2` | Pass | [gNB regression sanity] | 產出 `test_log/build_logs/nr-softmodem_redcap_cuup_linkfix_regression_2026-04-13_13-38-00.log` |

## Known Issues / Blockers
- 仍需在 [host Docker] 端重新跑 `ci-scripts/redcap_rebuild_local_oai_images.sh`，因目前 sandbox 無法直接 build Docker images。
- 在新的 image 真正生成前，`oai-gnb:latest` 可能仍然帶著舊版 [PUCCH budget assert] binary。
- [enabled E2 mode] 的 [FlexRIC plugin ABI mismatch] 尚未處理。

## Next Step
- 在 host 執行：
  - `bash ci-scripts/redcap_rebuild_local_oai_images.sh`
  - `bash ci-scripts/redcap_inspect_gnb_image.sh`
  - `REDCAP_USE_LOCAL_OAI_IMAGES=1 REDCAP_E2_AGENT_MODE=disabled bash ci-scripts/redcap_runtime_host_validation.sh`
- 確認 `redcap_inspect_gnb_image.sh` 是否能在 image 內找到：
  - `[Reducing PUCCH reservation budget]`
  - 且不再只看到 `[Cannot allocate all required PUCCH resources for max number of ...]`
