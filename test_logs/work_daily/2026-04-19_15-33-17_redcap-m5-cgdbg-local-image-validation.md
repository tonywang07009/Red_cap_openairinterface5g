# Work Daily Log
## Session Metadata
- Date: 2026-04-19 15:33
- Agent Session ID: N/A
- Task Slug: redcap-m5-cgdbg-local-image-validation

## Milestone & Sub-task Reference
- Milestone: RedCap mMTC M5 [UE CellGroupConfig SIGSEGV RCA]
- Sub-task: Verify [CGDBG] instrumentation on runtime UE image and re-run 64-UE validation
- Status: [COMPLETED]

## What Was Done
- Validated first 64-UE run (`mmtc_smoke_2026-04-19_14-57-24_*`) used remote image `oaisoftwarealliance/oai-nr-ue:develop`, not local patched image.
- Rebuilt local runtime images (`oai-gnb:latest`, `oai-nr-ue:latest`) and confirmed local image IDs.
- Re-ran 64-UE with `REGISTRY=` and `TAG=latest` so UE/gNB use local rebuilt images.
- Confirmed runtime UE containers use `oai-nr-ue:latest` via `docker inspect`.
- Parsed UE docker logs and confirmed `[CGDBG]` markers appear in all UE logs.
- Observed dominant failure signature: `CGDBG exit` then `free CellGroupConfig` then immediate `Segmentation fault`.

## 3GPP Spec Clauses Referenced
- TS 38.331 Section 5.3.5 — RRC reconfiguration / CellGroupConfig delivery and application context
- TS 38.321 Section 5.1 / 5.4 — MAC behavior after RRC-driven configuration update

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| 64-UE run with default image selection (`2026-04-19_14-57-24`) | Fail | Runtime smoke | 59 failures, success UE: 1/2/31/33/54 |
| Image source verification | Pass | UE container image ref | Confirmed default run used `oaisoftwarealliance/oai-nr-ue:develop` |
| 64-UE run with local image override (`REGISTRY=`, `TAG=latest`, `2026-04-19_15-17-13`) | Fail | Runtime smoke | 63 failures, success UE: only UE1 full ping pass |
| CGDBG marker visibility in local-image run | Pass | 64/64 UE docker logs | `CGDBG_COUNT=64` |

## Known Issues / Blockers
- With local image applied, failures increase to 63/64 and collapse mostly to first CellGroupConfig apply phase.
- Crash occurs after `nr_rrc_mac_config_req_cg()` logs `exit` and after `free CellGroupConfig`, indicating likely post-apply race/use-after-free path.
- No native backtrace is printed on SIGSEGV yet; stack owner thread still unknown.

## Next Step
- Add minimal gated diagnostic patch to test [delayed/no-free CellGroupConfig] hypothesis and add SIGSEGV backtrace hook for UE process, then re-run focused UE set around UE4/UE31-UE35.
