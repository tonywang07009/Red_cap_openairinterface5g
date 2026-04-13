# Work Daily Log
## Session Metadata
- Date: 2026-04-13 13:21
- Agent Session ID: N/A
- Task Slug: redcap-m5-pucch-runtime-image-diagnosis-hardening

## Milestone & Sub-task Reference
- Milestone: [Milestone 5: Integration & UL Throughput Targets]
- Sub-task: [Harden PUCCH budget fix visibility and runtime stale-image diagnosis for RedCap RFsim SA attach]
- Status: [COMPLETED]

## What Was Done
- Confirmed the current workspace already contains the [BWP-fit PUCCH budget] fix in `openair2/LAYER2/NR_MAC_gNB/nr_radio_config.c`, while `HEAD` still points to the legacy [MAX_MOBILES_PER_GNB] assert path.
- Added a runtime [info marker] in `get_nb_pucch2_per_slot()` so patched gNB binaries now log:
  - [Reducing PUCCH reservation budget from ... to ...]
- Updated `ci-scripts/redcap_runtime_host_validation.sh` to detect the legacy:
  - `Cannot allocate all required PUCCH resources for max number of ... UEs in BWP with ... PRBs`
  and print an explicit [rebuild local images] warning plus concrete docker build commands.
- Updated `ci-scripts/redcap_runtime_summary.py` to add a new [Run Log Diagnosis] section that cross-checks:
  - [legacy PUCCH assert]
  - [BWP-fit PUCCH marker]
  - [prebuilt image warning]
  and emits a [stale runtime image] diagnosis when appropriate.

## 3GPP Spec Clauses Referenced
- TS 38.306 Section 4.2.21.1 — [RedCap UE] operates with reduced FR1 bandwidth / BWP assumptions; [51-PRB initial BWP] must remain a valid deployment target.
- TS 38.321 Section 5.1 — the observed failure occurs after [RA Msg3] handling, so the fix targets post-RA gNB resource preparation rather than synchronization / PBCH / RAR.
- TS 38.331 Section 5.6.1.3 — [UE capability transfer] remains the downstream runtime evidence path once attach progresses past the previous gNB abort.

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| `bash -n ci-scripts/redcap_runtime_host_validation.sh` | Pass | [runtime shell helper syntax] | 新增 [legacy PUCCH assert] 偵測後仍通過 |
| `python3 -m py_compile ci-scripts/redcap_runtime_summary.py` | Pass | [runtime summary script syntax] | 新增 [Run Log Diagnosis] 邏輯後仍通過 |
| `git diff --check -- openair2/LAYER2/NR_MAC_gNB/nr_radio_config.c ci-scripts/redcap_runtime_host_validation.sh ci-scripts/redcap_runtime_summary.py` | Pass | [modified files formatting] | 無 whitespace / patch format 問題 |
| `cmake --build --preset default --target nr-softmodem -j2` | Pass | [nr-softmodem incremental rebuild] | 產出 `test_log/build_logs/nr-softmodem_redcap_pucch_runtime_hardening_2026-04-13_13-21-06.log` |

## Known Issues / Blockers
- [Host Docker runtime] 不可於目前 sandbox 直接驗證；仍需在 host 重新 build / run 才能取得新的 attach evidence。
- 若 host 仍執行舊版 `oai-gnb` image，仍可能再次看到 [legacy PUCCH assert]；但新的 host helper 已可更明確指出根因。
- [enabled E2 mode] 的 [FlexRIC plugin ABI mismatch] 仍是後續 blocker，與本次 [PUCCH budget] 修補屬不同問題鏈。

## Next Step
- 在 host 執行：
  - `docker build . -f docker/Dockerfile.gNB.ubuntu -t oai-gnb:latest`
  - `docker build . -f docker/Dockerfile.nrUE.ubuntu -t oai-nr-ue:latest`
  - `REDCAP_USE_LOCAL_OAI_IMAGES=1 REDCAP_E2_AGENT_MODE=disabled bash ci-scripts/redcap_runtime_host_validation.sh`
- 檢查新的 [Run Log Diagnosis] 是否出現 [BWP-fit PUCCH marker]，並確認舊的 [legacy PUCCH assert] 不再出現。
