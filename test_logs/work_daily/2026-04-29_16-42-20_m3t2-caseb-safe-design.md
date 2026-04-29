# Work Daily Log
## Session Metadata
- Date: 2026-04-29 16:42
- Agent Session ID: N/A
- Task Slug: m3t2-caseb-safe-design
- Project Path: agent_doc/Project_management/projects/redcap_mmtc_priority_execution_v1/project_plan.md

## Milestone & Sub-task Reference
- Milestone: [M3-T2 CORESET#0 Case A/B host validation]
- Sub-task: [Safe design for RedCap Case B Msg2 without global RA-RNTI duplicate]
- Status: [IN-PROGRESS]

## What Was Done
- Used [symdex] to inspect [RA process], [Msg2 scheduling], [UE preamble selection], [RedCap SIB1 BWP clone], and ASN.1 support paths.
- Used [filesystem MCP] to inspect latest work log, project docs, local spec summaries, ASN.1 generated headers, and local 3GPP RedCap extract evidence.
- Confirmed global duplicate [RA-RNTI DCI] is unsafe because it regressed [UE1 baseline].
- Confirmed spec-compliant safe path requires [Msg1 RedCap-associated RACH resource/preamble] before [Msg2].
- Wrote design checkpoint: `test_log/report/m3t2_caseb_safe_design_checkpoint_2026-04-29_16-42-20.md`.

## 3GPP Spec Clauses Referenced
- TS 38.300 local RedCap extract — [(e)RedCap] can be associated with a set of [RACH resources], and RedCap UE can be identified by [MSG1/MSGA PRACH occasion/preamble] or [MSG3/MSGA LCID].
- TS 38.321 local MAC extract — [(e)RedCap] UE switches to [initialUplinkBWP-RedCap] / [initialDownlinkBWP-RedCap] for RA when configured.
- TS 38.331 local ASN.1 `nr-rrc-17.3.0.asn1` — [RACH-ConfigCommon.ext2.featureCombinationPreamblesList-r17] and [FeatureCombinationPreambles-r17] provide [redCap-r17] preamble partition fields.

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| C/C++ rebuild | N/A | No source change | Design checkpoint only |
| Unit test | N/A | No source change | To run after implementation slice |
| RFsim runtime | N/A | No runtime change | To run after local image rebuild |

## Known Issues / Blockers
- [gNB Msg2 Case B scheduler gate] still needs implementation.
- [UE RedCap preamble partition selection] still needs implementation.
- [SIB1 featureCombinationPreamblesList-r17 population] still needs implementation.
- Exact final clause numbers for TS 38.331 field descriptions remain [⚠ Needs Verification] unless extracted from the full local TS 38.331 PDF.

## Next Step
- Implement [M3-T2 safe Msg1-gated RedCap Case B Msg2 path]:
  - Populate [featureCombinationPreamblesList-r17].
  - Select RedCap partition in UE [Msg1].
  - Mark gNB RA context from [preamble_index].
  - Gate [coreset_id=1 / BWP51] only for [is_redcap_msg1].
  - Rebuild affected OAI targets immediately after C changes.
