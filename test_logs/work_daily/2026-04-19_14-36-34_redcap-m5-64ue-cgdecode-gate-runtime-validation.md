# Work Daily Log
## Session Metadata
- Date: 2026-04-19 14:36
- Agent Session ID: N/A
- Task Slug: redcap-m5-64ue-cgdecode-gate-runtime-validation

## Milestone & Sub-task Reference
- Milestone: [Milestone 5: Compose Rebase & mMTC Scaling]
- Sub-task: [64-UE full attach + parallel ping runtime validation after CellGroupConfig decode gate patch]
- Status: [COMPLETED]

## What Was Done
- Executed full 64-UE runtime validation with:
  - `MMTC_TOTAL_UES=64`
  - `MMTC_SAMPLE_UES=1..64`
  - `MMTC_GNB_WARMUP=10`
  - `MMTC_UE_START_GAP=10`
  - `MMTC_FORWARD_PING_MODE=parallel`
  - `MMTC_RUN_REVERSE_PING=0`
- Collected run artifacts under `test_log/compiler_logs/` prefix:
  - `mmtc_smoke_2026-04-19_14-22-16_*`
- Classified outcome by stage:
  - [Success UE]: `1,2,31,32`
  - [Post-RRCSetup / first CellGroupConfig fail UE]: `33..64` except `31,32`
  - [Pre-RRCSetup fail UE]: `3..30`
- Verified that post-stage failing UEs show:
  - `Received NR_RRCSetup`
  - immediately followed by first `Applying CellGroupConfig from gNodeB`
  - then `Segmentation fault`.
- Checked runtime logs for `[CGDBG]` markers; none were present in container logs in this run.

## 3GPP Spec Clauses Referenced
- TS 38.331 Section 5.3.3.4 — [Reception of the RRCSetup by the UE], used to split pre/post setup failure stage.
- TS 38.331 Section 5.3.5 — [RRCReconfiguration / masterCellGroup handling], used to map first CellGroupConfig apply stage.
- TS 38.321 Section 5.1 — [Random Access], used as the entry-stage context before RRCSetup.

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| 64-UE staged launch + parallel ping smoke | Fail | Runtime smoke | Script exit non-zero; reported `60 failure(s)` |
| Successful UE (RNTI + attach + TUN + ping) | Fail | Runtime smoke | `4/64` success: `UE1, UE2, UE31, UE32` |
| Pre-RRCSetup crash bucket | Fail | Runtime smoke | `28` UE: `UE3..UE30` |
| Post-RRCSetup first CellGroupConfig crash bucket | Fail | Runtime smoke | `32` UE: `UE33..UE64` excluding `UE31,UE32` |
| `[CGDBG]` marker presence in UE container logs | Fail | Runtime smoke | `0` hits in `mmtc_smoke_2026-04-19_14-22-16_ue*_docker.log` |

## Known Issues / Blockers
- Regression vs previous run: failures increased from `59` to `60`; prior survivor `UE35` no longer survives.
- Runtime still exhibits deterministic crash right after first `Applying CellGroupConfig from gNodeB` for `UE33+` failing set.
- `[CGDBG]` markers absent in runtime logs, indicating the patched local binary was not reflected in the executed UE container binary for this run.

## Next Step
- Rebuild and deploy the UE runtime image that contains the patched `nr-uesoftmodem` binary, then rerun the same 64-UE validation.
- On rerun, classify failures with `[CGDBG]` markers first:
  - `decode non-OK reject`,
  - `current_UL_BWP NULL`,
  - other assert/crash signatures.
