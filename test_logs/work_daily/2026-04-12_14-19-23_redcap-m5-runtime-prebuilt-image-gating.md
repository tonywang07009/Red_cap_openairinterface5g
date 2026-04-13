# Work Daily Log
## Session Metadata
- Date: 2026-04-12 14:19
- Agent Session ID: N/A
- Task Slug: redcap-m5-runtime-prebuilt-image-gating

## Milestone & Sub-task Reference
- Milestone: Milestone 5: Integration & UL Throughput Targets
- Sub-task: Runtime blocker hardening for RedCap UE capability fallback and prebuilt-image warning
- Status: COMPLETED

## What Was Done
- Updated `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/docker-compose.yml` so `oai-nr-ue2` now uses `--uecap_file /tmp/redcap_force_yaml_fallback/uecap-redcap.xml` instead of `/opt/oai-nr-ue/etc/uecap-redcap.xml`.
- Confirmed from latest host artifact that the previous `--uecap_file` argument was already reaching the container, but UE2 still exposed a legacy `<UE-NR-Capability>` without `redCapParameters_r17`.
- Confirmed from `openair2/RRC/NR_UE/rrc_UE.c` that `nrue_recap` fallback is only taken when `fopen(uecap_file)` fails.
- Updated `ci-scripts/redcap_runtime_host_validation.sh` to print a runtime note before execution and a concrete warning after the run when the log shows prebuilt images such as `oai-ci/oai-nr-ue:develop-*` or `oai-ci/oai-gnb:develop-*`.

## 3GPP Spec Clauses Referenced
- TS 38.306 Section 4.2.21.1 — RedCap UE capability scope that must be reflected in runtime capability signalling.
- TS 38.331 Section 5.6.1.3 — UE capability transfer behavior used during runtime verification.
- TS 38.321 Section 5.1 — Random access procedure relevance for Msg3-based RedCap identification path.

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| `bash -n ci-scripts/redcap_runtime_host_validation.sh` | Pass | N/A | Shell syntax valid after warning logic was added |
| `rg -n "redcap_force_yaml_fallback|Prebuilt OAI image tag detected|Runtime note"` | Pass | N/A | Confirmed compose path and warning strings are present |
| Latest host artifact triage | Pass | N/A | Verified `302002` remains the first failing testcase and UE2 still reports non-RedCap capability |

## Known Issues / Blockers
- Latest host run still fails at `302002` because gNB log does not contain `UE with RNTI .... is RedCap`.
- UE2 runtime log shows the new `--uecap_file` option, but the old path likely existed inside the image, so YAML fallback did not trigger.
- Host runtime is still using prebuilt images (`oai-ci/oai-nr-ue:develop-dd52b503` / `oai-ci/oai-gnb:develop-dd52b503`), so local C patches are not yet present inside the running containers.

## Next Step
- Re-run `ci-scripts/redcap_runtime_host_validation.sh` on the host and confirm whether UE2 now prints `trying nrue_recap YAML fallback` / `Built UE NR capability from nrue_recap YAML`.
- If `302002` still fails after the new missing-path change, rebuild and retag local `oai-nr-ue` and `oai-gnb` images so the repo's RedCap C patches are actually used at runtime.
