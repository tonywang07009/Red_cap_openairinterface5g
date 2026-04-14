# Work Daily Log
## Session Metadata
- Date: 2026-04-14 14:25
- Agent Session ID: N/A
- Task Slug: mmtc-template-mode-split

## Milestone & Sub-task Reference
- Milestone: Compose Rebase & mMTC Scaling
- Sub-task: Clean normal-vs-RedCap template split for generated UE A/B validation
- Status: [COMPLETED]

## What Was Done
- [Updated] `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/scripts/ue_mmtc_entrypoint.sh` to select a real [normal UE template] when `MMTC_REDCAP_ENABLE=0`, while preserving [RedCap template] selection for the default path.
- [Added] explicit [legacy fallback] to `/opt/oai-nr-ue/etc/nr-ue.yaml` so previously generated overlays remain runnable if the new split mounts are absent.
- [Updated] `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/scripts/generate_mmtc_overlay.sh` so each generated UE now mounts both:
  - [RedCap template] `../../conf_files/nrue_recap/nrue30.uicc.yaml`
  - [normal template] `../../conf_files/nrue/nrue1.uicc.yaml`
- [Added] explicit environment wiring:
  - `MMTC_TEMPLATE_CONFIG_REDCAP=/opt/oai-nr-ue/etc/nr-ue-redcap.yaml`
  - `MMTC_TEMPLATE_CONFIG_NORMAL=/opt/oai-nr-ue/etc/nr-ue-normal.yaml`
- [Regenerated] `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/docker-compose.mmtc.yml` for [UE29..UE64] using the new split-template model.
- [Analyzed] latest [case A / case B] smoke evidence and concluded the prior [case B] was not a clean baseline because it still used `[nrue_recap YAML fallback]`.

## 3GPP Spec Clauses Referenced
- TS 38.306 Section 4.2.21.1 — [RedCap UE capability] path must be isolated cleanly from [normal UE baseline] when doing runtime A/B validation.
- TS 38.331 Section 5.6.1.3 — [PDU Session / radio bearer runtime validation] should be interpreted only after the UE capability/profile baseline is unambiguous.

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| `bash -n ue_mmtc_entrypoint.sh` | Pass | N/A | Shell syntax valid after template selection split |
| `bash -n generate_mmtc_overlay.sh` | Pass | N/A | Overlay generator syntax valid |
| `generate_mmtc_overlay.sh 64 .../docker-compose.mmtc.yml` | Pass | N/A | Regenerated [UE29..UE64] overlay |
| `docker compose -f docker-compose.yml -f docker-compose.mmtc.yml config -q` | Pass | N/A | Static compose validation passed |
| `git diff --check` | Pass | N/A | No whitespace / patch formatting issues |
| Prior host [case A / case B] runtime evidence | Fail | N/A | Both had [100% packet loss], but [case B] was not a clean [normal UE] baseline before this fix |

## Known Issues / Blockers
- [Unresolved] Generated UE [user-plane connectivity] is still failing; only the [A/B baseline validity] issue was fixed in this sub-task.
- [Unresolved] [UE29] still has a separate [segmentation fault / exit 139] path and must be debugged independently from [UE32/UE64 ping failure].
- [Needs Verification] A fresh host rerun is required to determine whether the failure is truly [generic generated-UE path] or still tied to [RedCap-specific template/runtime deltas].

## Next Step
- Re-run single-UE smoke with the new split-template overlay:
  - [case A] `MMTC_TOTAL_UES=64 MMTC_SAMPLE_UES="32" MMTC_RESET_CN=1 bash ci-scripts/redcap_mmtc_smoke_validation.sh`
  - [case B] `MMTC_REDCAP_ENABLE=0 MMTC_TOTAL_UES=64 MMTC_SAMPLE_UES="32" MMTC_RESET_CN=1 bash ci-scripts/redcap_mmtc_smoke_validation.sh`
- Compare whether [case B] still shows [100% packet loss] after it truly uses the [normal UE template].
