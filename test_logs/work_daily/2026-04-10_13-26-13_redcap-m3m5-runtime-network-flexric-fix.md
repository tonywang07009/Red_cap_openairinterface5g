# Work Daily Log
## Session Metadata
- Date: 2026-04-10 13:26
- Agent Session ID: N/A
- Task Slug: redcap-m3m5-runtime-network-flexric-fix

## Milestone & Sub-task Reference
- Milestone: Milestone 3 / Milestone 5
- Sub-task: Host runtime blocker fix for UE network subnet, nearRT-RIC startup, and undeploy log analysis
- Status: [COMPLETED]

## What Was Done
- Analyzed the latest host runtime logs and confirmed the first failing step was [000004 Deploy 2 OAI 5G NR-UEs in RedCap RF sim SA].
- Confirmed the direct deploy error was `no configured subnet contains IP address 192.168.71.150/151` because `oai-cn5g-public-net` only exposed `192.168.70.128/26`.
- Expanded `doc/tutorial_resources/oai-cn5g/docker-compose.yaml` network subnet to `192.168.70.0/23` so the shared CN/RAN network can host both `192.168.70.x` and `192.168.71.x`.
- Restored actual nearRT-RIC startup in `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/docker-compose.yml` by removing the `sleep infinity` override and switching healthcheck back to `pgrep nearRT-RIC`.
- Hardened `ci-scripts/cls_containerize.py` so empty xApp / nearRT-RIC logs are reported as explicit [KO] instead of crashing the CI runner with `IndexError`.
- Updated `agent_doc/Project_management/Simluation_v2.md` with the currently identified and patched host runtime blockers.

## 3GPP Spec Clauses Referenced
- TS 38.306 Section 4.2.21.1 — runtime scenario remains tied to FR1 RedCap reduced-bandwidth validation.
- TS 38.331 Section 5.2.2.4.2 — host runtime still targets RedCap SIB1 and initial BWP validation.
- TS 38.331 Section 5.6.1.3 — attach/runtime evidence still serves as the current RedCap capability validation gate.

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| `python3 -m py_compile ci-scripts/cls_containerize.py` | Pass | syntax | Updated container deploy / undeploy helper parses correctly |
| `docker compose -f ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/docker-compose.yml config` | Pass | compose syntax | Confirmed nearRT-RIC healthcheck and UE IP definitions remain valid |
| `docker compose -f doc/tutorial_resources/oai-cn5g/docker-compose.yaml config` | Pass | compose syntax | Confirmed `oai-cn5g-public-net` now resolves to `192.168.70.0/23` |
| Host log root-cause analysis | Pass | failure path | Confirmed blocker moved from `jq/NameError` to UE subnet mismatch and nearRT-RIC boot override |

## Known Issues / Blockers
- Host rerun is still required to verify whether [333332] / [302002] / [302003] / [020005] / [030001] / [030002] now execute successfully.
- Current gNB / runtime configs still use nearRT-RIC IP `192.168.70.180`, while the plan text in `Simluation_v2.md` still contains `192.168.70.155`. [⚠ Needs Verification]
- The current xApp log showed repeated [E2 SETUP timeout], so [M5 FlexRIC evidence] still needs confirmation after nearRT-RIC startup is restored.

## Next Step
- Re-run `ci-scripts/redcap_runtime_case_matrix.sh` on the Docker-capable host and inspect the first non-green test row in `ci-scripts/test_results.html`.
