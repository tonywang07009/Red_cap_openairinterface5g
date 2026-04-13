# Work Daily Log
## Session Metadata
- Date: 2026-04-12 14:25
- Agent Session ID: N/A
- Task Slug: redcap-m5-runtime-local-image-override

## Milestone & Sub-task Reference
- Milestone: Milestone 5: Integration & UL Throughput Targets
- Sub-task: Host runtime switch-over path from prebuilt images to local rebuilt OAI images
- Status: COMPLETED

## What Was Done
- Confirmed from the latest UE2 runtime artifact that `--uecap_file /tmp/redcap_force_yaml_fallback/uecap-redcap.xml` now reaches the container command line.
- Confirmed that UE2 still reports legacy `<UE-NR-Capability>` with `rel15` and no `redCapParameters_r17`, and that no `nrue_recap` fallback markers are printed.
- Concluded that the running `oai-nr-ue` container binary does not include the repo's local RedCap fallback patch, because the host scenario still uses prebuilt images tagged `develop-dd52b503`.
- Updated `ci-scripts/redcap_runtime_host_validation.sh` to:
  - preserve and restore an existing compose `.env` file when temporary overrides are used,
  - accept image override inputs `REDCAP_REGISTRY`, `REDCAP_TAG`, `REDCAP_GNB_IMG`, `REDCAP_NRUE_IMG`, `REDCAP_FLEXRIC_TAG`,
  - support `REDCAP_USE_LOCAL_OAI_IMAGES=1` as a shorthand for `REGISTRY=''`, `TAG='latest'`, `GNB_IMG='oai-gnb'`, and `NRUE_IMG='oai-nr-ue'`.

## 3GPP Spec Clauses Referenced
- TS 38.306 Section 4.2.21.1 — runtime UE capability must expose RedCap-specific capability content.
- TS 38.331 Section 5.6.1.3 — UE capability signalling is the runtime evidence path used by testcase `302002`.
- TS 38.321 Section 5.1 — Msg3 / random access relevance for the gNB-side RedCap identification path.

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| Latest UE2 artifact check | Pass | N/A | Verified new `/tmp/redcap_force_yaml_fallback/...` path is on the actual container command line |
| Latest UE2 capability dump check | Pass | N/A | Verified capability is still legacy `rel15`, proving runtime image mismatch remains |
| `bash -n ci-scripts/redcap_runtime_host_validation.sh` | Pass | N/A | Shell syntax valid after local-image override logic |
| `rg -n "REDCAP_USE_LOCAL_OAI_IMAGES|Local OAI image mode active"` | Pass | N/A | Confirmed new override hooks are present |

## Known Issues / Blockers
- Testcase `302002` still fails until the runtime uses locally rebuilt `oai-gnb` / `oai-nr-ue` images that include the repo's RedCap C patches.
- The current host scenario still boots `oai-ci/oai-gnb:develop-dd52b503` and `oai-ci/oai-nr-ue:develop-dd52b503`.
- Until `302002` passes, the FlexRIC RC control and UL throughput tests remain skipped.

## Next Step
- Build local `oai-gnb:latest` and `oai-nr-ue:latest` images from this repo.
- Re-run the scenario with `REDCAP_USE_LOCAL_OAI_IMAGES=1` and verify whether UE2 now emits `trying nrue_recap YAML fallback`, `Built UE NR capability from nrue_recap YAML`, and whether gNB prints `UE with RNTI .... is RedCap`.
