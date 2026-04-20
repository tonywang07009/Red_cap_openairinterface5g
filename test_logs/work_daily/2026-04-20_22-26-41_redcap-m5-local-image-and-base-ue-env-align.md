# Work Daily Log
## Session Metadata
- Date: 2026-04-20 22:26
- Agent Session ID: N/A
- Task Slug: redcap-m5-local-image-and-base-ue-env-align

## Milestone & Sub-task Reference
- Milestone: M5 RCA / Runtime Validation Pipeline
- Sub-task: Fix image/compose mismatch and align MMTC env injection for UE1~UE28
- Status: [COMPLETED]

## What Was Done
- Updated `ci-scripts/redcap_mmtc_smoke_validation.sh`:
  - Added local image selection defaults (`MMTC_IMAGE_REGISTRY=''`, `MMTC_IMAGE_TAG=latest`) and unified `compose_with_images()` wrapper.
  - Ensured compose lifecycle uses local rebuilt images (`oai-gnb:latest`, `oai-nr-ue:latest`) by default.
- Updated `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/scripts/generate_mmtc_overlay.sh`:
  - Added UE1~UE28 service overrides to inject `MMTC_CGCFG_NOFREE`, `MMTC_CGCFG_DEFER_FREE_SLOTS`, `MMTC_PUCCH_COMMON_FALLBACK_BWP0`, `MMTC_SEGV_BACKTRACE`, `MMTC_PDCP_TRACE`.
  - Kept UE29+ generation and printed `UE1..UE<TOTAL>` in generation summary.
- Re-ran stage52 validation multiple times and compared behavior:
  - Old path (remote/develop image): heavy segfault collapse.
  - Local-latest path after image fix: segfault storm removed.
  - After base-UE env alignment: attach/tun recovery improved significantly.

## 3GPP Spec Clauses Referenced
- TS 38.331 Section 5.3.5 (RRC connection setup/reconfiguration signaling flow relevance)
- TS 38.321 Section 5.1 (Random Access procedure relevance to repeated RA retrigger)
- ⚠ Needs Verification: exact clause granularity for initial PUCCH common resource behavior is in TS 38.213/38.211 mapping.

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| stage52 before local-image fix (`22:03:21`) | Fail | Runtime smoke | `[SUMMARY] running=5 attach=5 tun=5 failures=47` |
| stage52 after local-image selection fix (`22:16:36`) | Fail | Runtime smoke | `[SUMMARY] running=52 attach=3 tun=3 failures=49`; `segfault_count=0` |
| stage52 after UE1~28 MMTC env alignment (`22:22:44`) | Fail | Runtime smoke | `[SUMMARY] running=52 attach=19 tun=19 failures=33`; `pucch_common_null_count=0`, `fallback_used_count=39` |

## Known Issues / Blockers
- Remaining 33/52 UEs still fail to complete attach/tunnel in high-concurrency start.
- Many failed UEs show RA retrigger loops after initial signaling; bottleneck shifted from crash to access/retention stability under load.

## Next Step
- Focus next minimal patch on post-setup RA retrigger path (survivor vs failed around first `CellGroupConfig` + first RA re-entry), then re-run stage52 and stage56.
