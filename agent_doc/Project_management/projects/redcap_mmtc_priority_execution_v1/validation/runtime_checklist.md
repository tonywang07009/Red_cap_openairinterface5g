# RFsim Runtime Checklist

## Source of Truth
- Use `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/` for RedCap RFsim validation.
- Treat `docker-compose.yml`, `docker-compose.mmtc.yml`, and directly mounted config files as runtime source of truth.
- Do not modify unrelated XML/YAML files.
- Report unused XML/YAML candidates before removal.

## Pre-Run Checks
- Confirm expected image mode:
  - local OAI images when validating C changes,
  - explicit image tag when validating config-only behavior.
- Confirm gNB config path:
  - Case A: `coreset0_redcap_mode_r17=0`
  - Case B: `coreset0_redcap_mode_r17=1`
- Confirm UE config path from compose-mounted files.
- Confirm test target:
  - fixed UE,
  - 30 UE staged,
  - 32/64 UE staged.

## Required gNB Markers
- `[RedCap CORESET#0 Case A type0 CSS]`
- `[RedCap CORESET#0 Case B ...]`
- `[RedCap RA][gNB Msg1]`
- `[RedCap RA][gNB Msg2 gate]`
- `[RedCap RA][gNB Msg2 DCI]`
- `Cannot find free vrb_map for RA RNTI`
- `Cannot find free vrb_map for RNTI`
- `exceeded RA window`
- `RA Procedure failed at Msg4`
- `RA Contention Resolution timer expired`

## Required UE Markers
- `[RedCap RA][UE Msg1] using redCap-r17 preamble partition`
- RA-RNTI monitoring BWP and CORESET markers.
- `Received a RAR-Msg2`
- `RAR reception failed`
- `Received a RAR-Msg2 but LDPC decode failed`
- `PDU Session Establishment successful`
- `Interface oaitun_ue1 successfully configured`

## Pass/Fail Counters
- Attach count.
- PDU session count.
- Tunnel count.
- Forward ping success count.
- Reverse ping success count only when enabled.
- gNB restart count.
- Msg2 RA window failure count.
- Msg2 vrb_map failure count.
- Msg4 vrb_map failure count.
- Msg4 contention failure count.
- UE LDPC decode failure count.

## Case B A/B Rule
- When comparing Case A and Case B, keep all mMTC pacing parameters identical.
- Only change `coreset0_redcap_mode_r17`.
- If Case B improves attach success, prioritize config/runtime path cleanup.
- If Case B does not improve attach success, prioritize RA/Msg4 scheduler instrumentation.
- If Case B introduces LDPC failures, return to DCI/PDSCH BWP domain alignment.
