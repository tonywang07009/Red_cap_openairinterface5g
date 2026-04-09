---

# Work Daily Log

## Session Metadata
- Date: 2026-04-09 21:33
- Agent Session ID: N/A
- Task Slug: redcap-runtime-runner-hardening

## Milestone & Sub-task Reference
- Milestone: Milestone 5 [Integration & Throughput Targets]
- Sub-task: [local RedCap RFsim runner hardening] + [runtime preflight validation]
- Status: [COMPLETED]

## What Was Done
- [`ci-scripts/run_locally.sh`] 新增 [testcase path normalization]，統一使用 `xml_files/<scenario>.xml`，避免 README 與 runner 對 XML 路徑約定不一致。
- [`ci-scripts/run_locally.sh`] 新增 [docker access] 與 [Python dependency] preflight，缺少 `docker` / `PyYAML` / `paramiko` 時提早失敗並輸出明確訊息。
- [`ci-scripts/run_locally.sh`] 將 `oai-nr-cuup` 改為 [optional tag]，避免 [monolithic RedCap RFsim] 場景因不需要的 image 而提前失敗。
- 新增 [`ci-scripts/requirements.txt`]，顯式記錄本地執行 `main.py` 所需的最小 Python 依賴。
- 更新 [`ci-scripts/README.md`] 的 [local runner] 使用方式，修正 testcase 呼叫格式，並補上 [RedCap RFsim + FlexRIC] 執行範例。

## 3GPP Spec Clauses Referenced
- TS 38.306 Clause 4.2.21.1 — 本輪未改變 [RedCap FR1 20 MHz] 能力處理；runner 修補目的是讓後續 runtime 驗證可穩定啟動。
- TS 38.331 Clause 5.2.2.4.2 — 本輪未改變 [SIB1 RedCap access control] 判斷；runner 修補目的是支撐後續 `302003` 與 attach 驗證。
- TS 38.331 Clause 5.6.1.3 — 本輪未改變 [UE capability signaling / RedCap detection]；runner 修補目的是支撐後續 `302002` 與 gNB RedCap detection 驗證。

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| `bash -n ci-scripts/run_locally.sh` | Pass | N/A | log: `test_log/compiler_logs/run_locally_shellcheck_2026-04-09_21-31-00.log` |
| `./run_locally.sh container_5g_flexric_rfsim_redcap.xml` | Fail | N/A | 預期失敗；已確認會在缺少 [docker access] 時提早退出，log: `test_log/compiler_logs/run_locally_redcap_preflight_2026-04-09_21-31-10.log` |

## Known Issues / Blockers
- [Sandbox docker denial] 目前環境對 `/var/run/docker.sock` 無權限，因此無法在此 session 內完成 [Core + gNB + UE + FlexRIC] attach / ping / iperf。
- [Python packages absent in current environment] 目前 shell 缺少 `PyYAML` 與 `paramiko`；雖已補 `requirements.txt`，但此 session 不能保證立即安裝成功。⚠ Needs Verification
- [Full Milestone 5 evidence pending] `302003`、`030001`、`030002` 以及 attach / ping 結果尚待具備 docker 權限的 host 執行。

## Next Step
- 在具備 [docker socket] 權限的 host 上，先執行 `python3 -m pip install -r ci-scripts/requirements.txt`，再於 `ci-scripts/` 下執行 `./run_locally.sh container_5g_flexric_rfsim_redcap.xml`，收集 [attach log]、[gNB RedCap detection]、[`302003`]、[`030001`]、[`030002`] 結果。
