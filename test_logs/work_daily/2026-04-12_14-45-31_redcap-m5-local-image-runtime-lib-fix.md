# Work Daily Log
## Session Metadata
- Date: 2026-04-12 14:45
- Agent Session ID: N/A
- Task Slug: redcap-m5-local-image-runtime-lib-fix

## Milestone & Sub-task Reference
- Milestone: Milestone 5: Integration & UL Throughput Targets
- Sub-task: Local OAI image runtime fix for sanitize-linked binaries during RedCap runtime validation
- Status: COMPLETED

## What Was Done
- Analyzed the latest local-image host run and confirmed the scenario now uses `REGISTRY=""`, `TAG="latest"`, `GNB_IMG="oai-gnb"`, and `NRUE_IMG="oai-nr-ue"`.
- Identified the new blocker from `25-100009-oai-gnb.logs`: `/opt/oai-gnb/bin/nr-softmodem: error while loading shared libraries: libasan.so.8: cannot open shared object file`.
- Concluded the local runtime image contains a sanitize-linked binary while the runtime filesystem lacked the sanitizer runtime libraries.
- Updated `docker/Dockerfile.gNB.ubuntu` to always include `libasan8`, `libubsan1`, and `liblapacke`.
- Updated `docker/Dockerfile.nrUE.ubuntu` to always include `libasan8` and `libubsan1` so local sanitize-linked UE binaries can also start.

## 3GPP Spec Clauses Referenced
- TS 38.306 Section 4.2.21.1 — runtime RedCap verification still depends on successfully booting patched local binaries.
- TS 38.331 Section 5.6.1.3 — UE capability signalling path remains the next runtime checkpoint once local binaries boot.
- TS 38.321 Section 5.1 — random access and Msg3 behavior remain blocked until the local gNB / UE images start successfully.

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| Latest local-image run triage | Pass | N/A | Confirmed `oai-gnb:latest` was selected and failed with missing `libasan.so.8` |
| `rg -n "libasan8|libubsan1|liblapacke"` on runtime Dockerfiles | Pass | N/A | Confirmed sanitizer runtime libs are now present in local gNB / UE image definitions |
| Docker runtime verification in sandbox | Fail | N/A | Not executable here because Docker socket access is blocked in the sandbox |

## Known Issues / Blockers
- Local images must be rebuilt after the Dockerfile changes; otherwise the old `oai-gnb:latest` / `oai-nr-ue:latest` images will still fail or run stale binaries.
- FlexRIC / RC control runtime validation is still blocked until the local gNB and UE images boot and `302002` passes.

## Next Step
- Rebuild local `ran-base`, `ran-build`, `oai-gnb:latest`, and `oai-nr-ue:latest`.
- Re-run the scenario with `REDCAP_USE_LOCAL_OAI_IMAGES=1` and check whether gNB now boots, UE2 emits RedCap fallback markers, and testcase `302002` moves to `OK`.
