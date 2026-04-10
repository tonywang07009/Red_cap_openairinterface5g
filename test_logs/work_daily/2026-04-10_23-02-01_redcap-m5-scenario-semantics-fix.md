# Work Daily Log
## Session Metadata
- Date: 2026-04-10 23:02
- Agent Session ID: N/A
- Task Slug: redcap-m5-scenario-semantics-fix

## Milestone & Sub-task Reference
- Milestone: Milestone 5
- Sub-task: Reconcile RedCap compose defaults, runtime summary text, and XML expectations for `[UE1 non-RedCap]` / `[UE2 RedCap]`
- Status: COMPLETED

## What Was Done
- Re-checked the active RedCap RF-sim XML scenario with SymDex and confirmed it explicitly expects:
  - `[302001]` → `UE1 non-RedCap`
  - `[302002]` → `UE2 RedCap`
- Corrected [`ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/docker-compose.yml`](/home/tonywang/OAI/Red_cap_openairinterface5g/ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/docker-compose.yml) so the default UE mounts now match the scenario semantics:
  - `oai-nr-ue1` default path → [`ci-scripts/conf_files/nrue/nrue1.uicc.yaml`](/home/tonywang/OAI/Red_cap_openairinterface5g/ci-scripts/conf_files/nrue/nrue1.uicc.yaml)
  - `oai-nr-ue2` default path → [`ci-scripts/conf_files/nrue_recap/nrue2.uicc.yaml`](/home/tonywang/OAI/Red_cap_openairinterface5g/ci-scripts/conf_files/nrue_recap/nrue2.uicc.yaml)
- Renamed the compose override variables to the more accurate generic names:
  - `NRUE_CONFIG_1`
  - `NRUE_CONFIG_2`
- Updated [`ci-scripts/redcap_runtime_host_validation.sh`](/home/tonywang/OAI/Red_cap_openairinterface5g/ci-scripts/redcap_runtime_host_validation.sh) so it now writes `NRUE_CONFIG_1` / `NRUE_CONFIG_2` into the temporary compose `.env`, while still accepting the earlier compatibility env vars `REDCAP_NRUE1_CONFIG_PATH` / `REDCAP_NRUE2_CONFIG_PATH`.
- Updated [`ci-scripts/redcap_runtime_summary.py`](/home/tonywang/OAI/Red_cap_openairinterface5g/ci-scripts/redcap_runtime_summary.py) so:
  - `030001` is labeled as `[Iperf UL 50 Mbps UDP on UE2]`
  - artifact hints now reference `iperf_client_rfsim5g_redcap_ue2.log`
  - ping artifact hints now reference `ping_rfsim5g_redcap_ue*.log`

## 3GPP Spec Clauses Referenced
- TS 38.331 Section 5.6.1.3 — runtime attach and UE capability evidence still define the RedCap/non-RedCap distinction used by `[302001]` and `[302002]`.
- TS 38.306 Section 4.2.21.1 — the RedCap runtime path remains anchored to the FR1 reduced-capability profile.

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| SymDex search for `Verify UE 1 is normal (no RedCap)` / `Verify UE 2 is RedCap` | Pass | scenario semantics | Confirmed the active XML scenario requires UE1 non-RedCap and UE2 RedCap |
| `bash -n ci-scripts/redcap_runtime_host_validation.sh` | Pass | shell syntax | Host validation wrapper remains syntactically valid after the env-var rename |
| `docker compose ... config` default-path check | Pass | compose defaults | Confirmed defaults resolve to `conf_files/nrue/nrue1.uicc.yaml` for UE1 and `conf_files/nrue_recap/nrue2.uicc.yaml` for UE2 |
| `env ... docker compose ... config` override-path check | Pass | compose overrides | Confirmed `/tmp/gnb.yaml`, `/tmp/ue1.yaml`, `/tmp/ue2.yaml` override paths all resolve correctly |
| `python3 -m py_compile ci-scripts/redcap_runtime_summary.py` | Pass | Python syntax | Summary helper parses cleanly after runtime-label updates |

## Known Issues / Blockers
- The sandbox still cannot execute the Docker runtime scenario, so these checks validate semantics and config expansion only, not live attach success.
- The wide `nrue_recap/*.yaml` RedCap alignment done earlier remains in the tree, but the active compose default now deliberately uses the non-RedCap UE1 asset to preserve scenario intent.

## Next Step
- Continue Milestone 5 local cleanup by reviewing whether any remaining RedCap runtime helper text or summary logic still assumes the old UE IDs or throughput profile before requesting the next Docker-host rerun.
