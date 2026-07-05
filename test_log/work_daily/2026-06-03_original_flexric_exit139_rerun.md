# 2026-06-03 Original FlexRIC Exit 139 Rerun

## Project
- Project Path: `agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/project_plan.md`
- Scenario: `ci-scripts/yaml_files/5g_rfsimulator_flexric/docker-compose.yml`
- CN Source: `/home/tonywang/OAI/oai-cn5g/docker-compose.yaml`

## Work Completed
- [Rerun Target]: re-ran the original FlexRIC RFsim single-UE scenario to check whether UE1 still reproduces `exit=139`.
- [Services Started]: OAI CN5G, `nearRT-RIC`, `oai-gnb`, and `oai-nr-ue1`.
- [Observation Window]: `2026-06-03 10:32:41-10:37:16 Asia/Taipei`.
- [Cleanup]: stopped the started CN/RAN/RIC services after evidence capture; no containers were deleted and no repo source files were changed.

## Validation
- [Container State Before Stop]:
  - `rfsim5g-oai-nr-ue1`: `running`, `exit=0`, `health=healthy`.
  - `rfsim5g-oai-gnb`: `running`, `exit=0`, `health=healthy`.
  - `nearRT-RIC`: `running`, `exit=0`, `health=healthy`.
  - `oai-amf`, `oai-smf`, `oai-upf`: `running`, `exit=0`, `health=healthy`.
- [RIC Marker]: `E2 SETUP-REQUEST rx` and accepted KPM/RC/MAC/RLC/PDCP/GTP service models.
- [gNB Markers]:
  - `Received NGSetupResponse from AMF`.
  - `E2 SETUP RESPONSE rx`.
  - `Received Ack of Msg4. CBRA procedure succeeded`.
  - `Received RRCSetupComplete`.
  - `NGAP_PDUSESSION_SETUP_RESP`.
- [UE Markers]:
  - `Connection to 192.168.70.140:4043 established`.
  - `Received NR_RRCSetup`.
  - `Received Registration Accept with result 3GPP`.
  - `Received PDU Session Establishment Accept, UE IPv4: 10.0.0.2`.
  - `TUN Interface oaitun_ue1 successfully configured`.
- [Tunnel Check]: `oaitun_ue1` had `10.0.0.2/24`.
- [User Plane Check]: `ping -I oaitun_ue1 -c 3 10.0.0.1` passed with `3/3` received, `0%` packet loss, average RTT `3.696 ms`.

## Result
- [Exit 139]: not reproduced during the short smoke rerun.
- [Segmentation Fault Marker]: not observed in the rerun log slice.
- [Interpretation]: original FlexRIC bring-up, E2 setup, UE attach, PDU session, tunnel setup, and short user-plane ping passed.

## Follow-Up
- [Needs Verification]: the previous `exit=139` may be a long-run/soak issue rather than an immediate attach/PDU failure.
- Recommended next check: run a longer soak window if the owner wants to classify whether `exit=139` is caused by prolonged UE runtime, stop timing, or resource pressure.
