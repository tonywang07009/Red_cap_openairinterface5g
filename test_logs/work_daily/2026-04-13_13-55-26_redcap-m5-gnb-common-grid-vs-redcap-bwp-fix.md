# Work Daily Log
## Session Metadata
- Date: 2026-04-13 13:55
- Agent Session ID: N/A
- Task Slug: redcap-m5-gnb-common-grid-vs-redcap-bwp-fix

## Milestone & Sub-task Reference
- Milestone: [Milestone 5: Integration & UL Throughput Targets]
- Sub-task: [Fix gNB PHY RedCap validation so a 106-PRB serving-cell grid is not rejected when RedCap uses a separate 51-PRB initial BWP]
- Status: [COMPLETED]

## What Was Done
- Analyzed the latest host gNB artifact and confirmed the previous [PUCCH budget] assert is gone.
- Located the new abort in `openair1/PHY/INIT/nr_parms.c`:
  - `nr_assert_redcap_fr1_grid_size()`
  - triggered from `nr_validate_redcap_gnb_frame_parms()`
  - host log showed `gNB RedCap FR1 DL grid size 106 PRBs exceeds 20 MHz limit for mu 1 (max 51 PRBs)`
- Cross-checked against existing config logic:
  - `openair2/GNB_APP/gnb_config.c` already treats `bwp_list` / `carrierBandwidth` as [cell/common BWPs]
  - `openair2/LAYER2/NR_MAC_gNB/nr_mac_redcap_bwp.c` already enforces the [RedCap initial BWP <= 20 MHz] rule
- Updated `nr_validate_redcap_gnb_frame_parms()` so gNB RedCap validation now:
  - still enforces [FR1 only]
  - still enforces [SCS 15/30 kHz only]
  - still enforces [DL antenna ports <= 2]
  - no longer rejects a [106-PRB common grid] solely because RedCap support is enabled
  - instead logs that the full serving-cell carrier may exceed the RedCap 20 MHz limit because that limit is enforced on [RedCap-specific initial BWPs] and [UE frame parms]

## 3GPP Spec Clauses Referenced
- TS 38.306 Section 4.2.21.1 — [RedCap UE] in [FR1] is limited to 20 MHz and may use separate initial BWPs; this limit applies to the RedCap operating bandwidth, not necessarily to the entire serving-cell carrier advertised by the gNB.
- TS 38.331 Section 5.2.2.4.2 — [initialDownlinkBWP-RedCap-r17] and [initialUplinkBWP-RedCap-r17] are signaled separately in SIB1, which matches the current project architecture of [106-PRB cell/common carrier] plus [51-PRB RedCap initial BWP].
- TS 38.321 Section 5.1 — the runtime path had already progressed far enough that this PHY init validation became the next blocker before attach verification could continue.

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| `git diff --check -- openair1/PHY/INIT/nr_parms.c` | Pass | [modified file formatting] | 無 whitespace / patch format 問題 |
| `cmake --build --preset default --target nr-softmodem -j2` | Pass | [gNB runtime target] | 產出 `test_log/build_logs/nr-softmodem_redcap_common_grid_fix_2026-04-13_13-55-07.log` |
| `cmake --build --preset default --target nr-cuup -j2` | Pass | [previous rebuild-chain regression sanity] | 產出 `test_log/build_logs/nr-cuup_redcap_common_grid_fix_regression_2026-04-13_13-55-07.log` |

## Known Issues / Blockers
- 仍需在 [host Docker] 端重建 image 並重跑 runtime scenario，因目前 sandbox 無法直接操作 Docker。
- 下一個 runtime blocker 目前尚未知；需要新的 host run 才能觀察 attach 是否已走到 [UE1 IP assignment] / [UE2 RedCap identification] / [FlexRIC] 階段。
- [enabled E2 mode] 的 [FlexRIC plugin ABI mismatch] 仍未處理。

## Next Step
- 在 host 執行：
  - `REDCAP_REBUILD_LOCAL_OAI_IMAGES=1 REDCAP_USE_LOCAL_OAI_IMAGES=1 REDCAP_E2_AGENT_MODE=disabled bash ci-scripts/redcap_runtime_host_validation.sh`
- 期待新的 gNB log：
  - 不再出現 `gNB RedCap FR1 DL grid size 106 PRBs exceeds 20 MHz limit`
  - 應出現新的 info marker：
    - `gNB RedCap common grid uses DL/UL 106/106 PRBs ...`
- 若 attach 再往前走，下一步檢查 [UE1 IP assignment]、[UE2 is RedCap] 與 [302002/302003/302004]。
