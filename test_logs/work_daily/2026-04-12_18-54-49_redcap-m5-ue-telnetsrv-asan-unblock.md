# Work Daily Log
## Session Metadata
- Date: 2026-04-12 18:54
- Agent Session ID: N/A
- Task Slug: redcap-m5-ue-telnetsrv-asan-unblock

## Milestone & Sub-task Reference
- Milestone: [Milestone 5: Integration & UL Throughput Targets]
- Sub-task: [A/B isolate gNB E2 crash and unblock UE runtime startup]
- Status: [COMPLETED]

## What Was Done
- [A/B Test] 確認 [enabled] 模式下 [oai-gnb] 於 deploy 階段即 [Exited (1)]。
- [A/B Test] 確認 [disabled] 模式下 [gNB_REDCAP_CONFIG] 已切到自動產生的無 `e2_agent` YAML，且 [oai-gnb] 可進入 [Up (healthy)]。
- 讀取 [gNB artifact log]，確認 runtime 顯示 `E2 agent is DISABLED`，因此 [gNB 開機 crash] 已與 [FlexRIC plugin loading] 建立直接因果。
- 讀取 [UE1/UE2 artifact logs]，確認新的阻塞點是 [AddressSanitizer odr-violation]，來源為 `libtelnetsrv.so` 與 `nr-uesoftmodem` 的 `g_log` 重複定義。
- 修改 [ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/docker-compose.yml]，移除 [oai-nr-ue1] / [oai-nr-ue2] 的 `--telnetsrv` 啟動參數，避免本 scenario 再次在 UE 啟動前期被 [libtelnetsrv.so] 阻塞。

## 3GPP Spec Clauses Referenced
- TS 38.306 Section 4.2.21.1 — [RedCap UE] 能力與本 scenario 的 [FR1 20 MHz / reduced capability] 驗證範圍。
- TS 38.331 Section 5.2.2.4.2 — [RedCap SIB1] cell access / half-duplex / barred 判定條件，屬於本次 runtime 驗證的 attach 前提。
- TS 38.331 Section 5.6.1.3 — [RRCReconfiguration] 與後續 [E2/xApp RedCap UL PRB cap] 驗證路徑相關。

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| [A/B enabled gNB deploy] | [Fail] | [Runtime deploy path] | [oai-gnb] 於 [FlexRIC enabled] 時再次 [Exited (1)] |
| [A/B disabled gNB deploy] | [Pass] | [Runtime deploy path] | [oai-gnb] 進入 [Up (healthy)]，並載入 [disabled YAML] |
| [UE1 startup after gNB disabled] | [Fail] | [UE runtime startup] | `AddressSanitizer: odr-violation` in [`/usr/local/lib/libtelnetsrv.so`] |
| [UE2 startup after gNB disabled] | [Fail] | [UE runtime startup] | 與 [UE1] 相同的 [ASAN ODR] 問題 |
| [Compose patch syntax sanity] | [Pass] | [Edited file] | `git diff --check -- ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/docker-compose.yml` |

## Known Issues / Blockers
- [Confirmed Root Cause]：[enabled] 與 [disabled] 差異已證明 [gNB 原始 crash] 來自 [FlexRIC plugin loading / ABI path]。
- [Current Blocker]：[UE1/UE2] 在本地 image 下會因 [telnetsrv shared library] 觸發 [ASAN ODR violation] 而提前退出。
- [⚠ Needs Verification]：移除 [UE telnet] 後，需重新確認 [RF simulator role / attach path] 是否仍有後續 runtime wiring 問題。

## Next Step
- 以目前 patch 重新執行 [REDCAP_USE_LOCAL_OAI_IMAGES=1 bash ci-scripts/redcap_runtime_e2_ab_test.sh]。
- 若 [disabled] 模式下 [UE1/UE2] 可啟動，下一步就鎖定回 [enabled] 模式的 [FlexRIC plugin inventory / ABI mismatch]。
