# Work Daily Log
## Session Metadata
- Date: 2026-04-13 21:02
- Agent Session ID: N/A
- Task Slug: redcap-m5-compose-rebase-telnet-shape

## Milestone & Sub-task Reference
- Milestone: Milestone 5 Compose Architecture, Integration & UL Throughput Targets
- Sub-task: Rebase RedCap compose toward vendor FlexRIC multi-UE service shape
- Status: [COMPLETED]

## What Was Done
- Updated `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/docker-compose.yml`.
- Added an explicit header comment documenting that the file is a [RedCap runtime derivative] of `5g_rfsimulator_flexric/docker-compose.yml`.
- Restored vendor-style per-UE telnet wiring for:
  - `oai-nr-ue1`
  - `oai-nr-ue2`
- Corrected the [telnet listenport] allocation for `oai-nr-ue3` through `oai-nr-ue28` so the RedCap compose now matches the vendor FlexRIC compose sequence:
  - `UE1 -> 8091`
  - `UE2 -> 8092`
  - ...
  - `UE28 -> 8118`
- Preserved the intended [RedCap-specific deltas]:
  - `*_redcap` container names required by CI/runtime tooling
  - RedCap gNB YAML override path
  - RedCap UE YAML selection
  - RedCap RF parameters and `--uecap_file` on `UE2`

## 3GPP Spec Clauses Referenced
- TS 38.306 Section 4.2.21.1 — [RedCap UE capability] remains the reason for keeping RedCap-specific UE deltas in the compose path.
- TS 38.331 Section 5.2.2.4.2 — [SIB1 RedCap] evidence remains tied to the fixed-UE validation path.
- TS 38.331 Section 5.6.1.3 — [RRC capability / attach] evidence still depends on preserving the current fixed `UE1/UE2` runtime path.

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| `docker compose ... config -q` on RedCap compose | Pass | Syntax / structure | Compose file parses successfully |
| `git diff --check` on RedCap compose | Pass | Patch hygiene | No whitespace or format issues |
| Telnet listenport sequence vs vendor FlexRIC compose | Pass | UE1~UE28 | RedCap compose now matches `8091..8118` exactly |

## Known Issues / Blockers
- This sub-task only rebased the [multi-UE instrumentation shape]; it did not yet add the new [mMTC overlay] path.
- The fixed-UE runtime blocker remains unresolved: `UE2` still needs a deeper [user-plane] investigation or further rebase work.

## Next Step
- Continue the [Milestone 5 compose rebase]:
  - extract the next vendor-aligned base layer for scalable UE services
  - design `docker-compose.mmtc.yml`
  - define how per-UE IMSI / YAML / RedCap flags will be generated under a Compose-native flow
